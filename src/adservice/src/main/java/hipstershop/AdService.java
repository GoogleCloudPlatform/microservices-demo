/*
 * Copyright 2018, Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package hipstershop;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableListMultimap;
import hipstershop.Demo.Ad;
import hipstershop.Demo.AdRequest;
import hipstershop.Demo.AdResponse;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.Status;
import io.grpc.StatusRuntimeException;
import io.grpc.health.v1.HealthCheckResponse.ServingStatus;
import io.grpc.services.HealthStatusManager;
import io.grpc.stub.StreamObserver;
import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.metrics.*;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import io.opentelemetry.exporter.otlp.metrics.OtlpGrpcMetricExporter;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.metrics.common.InstrumentType;
import io.opentelemetry.sdk.metrics.data.AggregationTemporality;
import io.opentelemetry.sdk.metrics.export.IntervalMetricReader;
import io.opentelemetry.sdk.metrics.internal.view.AttributesProcessor;
import io.opentelemetry.sdk.metrics.view.Aggregation;
import io.opentelemetry.sdk.metrics.view.InstrumentSelector;
import io.opentelemetry.sdk.metrics.view.View;
import io.opentelemetry.sdk.resources.Resource;
import java.io.IOException;
import java.net.InetAddress;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Random;
import java.util.concurrent.Executor;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.SingleConnectionDataSource;

public final class AdService {

  private static final Logger logger = LogManager.getLogger(AdService.class);

  private static final int MAX_ADS_TO_SERVE = 2;
  private final MeterProvider meterProvider;
  private final JdbcTemplate jdbcTemplate;

  private Server server;
  private HealthStatusManager healthMgr;

  public AdService(MeterProvider meterProvider, JdbcTemplate jdbcTemplate) {
    this.meterProvider = meterProvider;
    this.jdbcTemplate = jdbcTemplate;
  }

  private static String getHost() {
    try {
      return InetAddress.getLocalHost().getHostName();
    } catch (java.net.UnknownHostException e) {
      return "";
    }
  }

  private void start() throws IOException {
    int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "9555"));
    healthMgr = new HealthStatusManager();

    server =
        ServerBuilder.forPort(port)
            .addService(new AdServiceImpl(this))
            .addService(healthMgr.getHealthService())
            .build()
            .start();
    logger.info("Ad Service started, listening on " + port);
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  // Use stderr here since the logger may have been reset by its JVM shutdown hook.
                  System.err.println(
                      "*** shutting down gRPC ads server since JVM is shutting down");
                  AdService.this.stop();
                  System.err.println("*** server shut down");
                }));
    healthMgr.setStatus("", ServingStatus.SERVING);
  }

  private void stop() {
    if (server != null) {
      healthMgr.clearStatus("");
      server.shutdown();
    }
  }

  private static class AdServiceImpl extends hipstershop.AdServiceGrpc.AdServiceImplBase {
    private final Executor backgroundJobber =
        new ThreadPoolExecutor(
            1,
            5,
            100,
            TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(),
            new ThreadPoolExecutor.CallerRunsPolicy());
    private final Random random = new Random();
    private final AdService service;

    // note: these two instruments should be updated to match semantic conventions, when they are
    // defined.
    private final DoubleHistogram getAdsRequestLatency;
    private final DoubleHistogram backgroundLatency;
    private final LongUpDownCounter numberOfAdsRequested;
    // used for doing some manual span instrumentation.
    private final Tracer tracer = GlobalOpenTelemetry.getTracer("hipstershop.adservice");

    public AdServiceImpl(AdService service) {
      this.service = service;
      Meter meter = service.meterProvider.get(AdService.class.getName());
      // note: preliminary spec discussion has things leaning toward this for the instrument name.
      // see https://github.com/open-telemetry/opentelemetry-specification/pull/657 for discussion
      getAdsRequestLatency =
          meter
              .histogramBuilder("rpc.server.duration")
              .setDescription("Timings of gRPC requests to a service")
              .setUnit("ms")
              .build();

      // this is a custom "business" metric, outside the scope of semantic conventions
      numberOfAdsRequested =
          meter
              .upDownCounterBuilder("ads_requested")
              .setUnit("one")
              .setDescription("Number of Ads Requested per Request")
              .build();

      // custom timer for the background job.
      backgroundLatency =
          meter
              .histogramBuilder("background.job.duration")
              .setDescription("Background job timings")
              .setUnit("ms")
              .build();
    }

    /**
     * Retrieves ads based on context provided in the request {@code AdRequest}.
     *
     * @param req the request containing context.
     * @param responseObserver the stream observer which gets notified with the value of {@code
     *     AdResponse}
     */
    @Override
    public void getAds(AdRequest req, StreamObserver<AdResponse> responseObserver) {
      // note: these could be pulled into constants to reduce allocations
      String methodName = "hipstershop.AdService/GetAds";
      Attributes nonErrorLabels =
          Attributes.of(
              AttributeKey.stringKey("method.name"),
              methodName,
              AttributeKey.stringKey("span.name"),
              methodName,
              AttributeKey.stringKey("error"),
              "false",
              AttributeKey.stringKey("span.kind"),
              SpanKind.SERVER.name());
      Attributes errorLabels =
          Attributes.of(
              AttributeKey.stringKey("method.name"),
              methodName,
              AttributeKey.stringKey("span.name"),
              methodName,
              AttributeKey.stringKey("error"),
              "true",
              AttributeKey.stringKey("span.kind"),
              SpanKind.SERVER.name());

      long startTime = System.currentTimeMillis();
      numberOfAdsRequested.add(req.getContextKeysCount(), Attributes.empty());
      Attributes labels = nonErrorLabels;
      try {
        List<Ad> allAds = chooseAds(req);
        reportAdsToBackgroundService(allAds);
        AdResponse reply = AdResponse.newBuilder().addAllAds(allAds).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
      } catch (StatusRuntimeException e) {
        logger.log(Level.WARN, "GetAds Failed with status {}", e.getStatus());
        labels = errorLabels;
        responseObserver.onError(e);
      } finally {
        getAdsRequestLatency.record((System.currentTimeMillis() - startTime), labels);
      }
    }

    private void reportAdsToBackgroundService(List<Ad> allAds) {
      backgroundJobber.execute(() -> reportAdsRequest(allAds));
    }

    private void reportAdsRequest(List<Ad> allAds) {
      long startTime = System.currentTimeMillis();
      String spanName = "ReportRequestedAds";
      Span span =
          tracer
              .spanBuilder(spanName)
              .setNoParent()
              .setAttribute("numberOfAds", allAds.size())
              .startSpan();
      try (Scope ignored = span.makeCurrent()) {
        anotherSpan();
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      } finally {
        backgroundLatency.record(
            (System.currentTimeMillis() - startTime),
            Attributes.of(
                AttributeKey.stringKey("span.name"), spanName, AttributeKey.stringKey("error"), "false", AttributeKey.stringKey("span.kind"), SpanKind.INTERNAL.name()));
        span.end();
      }
    }

    private void anotherSpan() throws InterruptedException {
      Span innerSpan = tracer.spanBuilder("InnerBackgroundThing").startSpan();
      try (Scope ignored = innerSpan.makeCurrent()) {
        Thread.sleep(random.nextInt(200));
      } finally {
        innerSpan.end();
      }
    }

    private List<Ad> chooseAds(AdRequest req) {
      Span getSomeAds = tracer.spanBuilder("chooseAds").startSpan();
      try (Scope ignored = getSomeAds.makeCurrent()) {
        List<Ad> allAds = new ArrayList<>();
        logger.info("received ad request (context_words=" + req.getContextKeysCount() + ")");
        if (req.getContextKeysCount() > 0) {
          for (int i = 0; i < req.getContextKeysCount(); i++) {
            Collection<Ad> ads = service.getAdsByCategory(req.getContextKeys(i));
            allAds.addAll(ads);
          }
        } else {
          allAds = service.getRandomAds();
        }
        if (allAds.isEmpty()) {
          // Serve random ads.
          allAds = service.getRandomAds();
        }
        if (random.nextInt(100) == 1) {
          throw new StatusRuntimeException(Status.RESOURCE_EXHAUSTED);
        }
        return allAds;
      } finally {
        getSomeAds.end();
      }
    }
  }

  private Collection<Ad> getAdsByCategory(String category) {
    return jdbcTemplate.query(
        "select redirectUrl, text from ads where category = ?",
        (rs, rowNum) ->
            Ad.newBuilder()
                .setRedirectUrl(rs.getString("redirectUrl"))
                .setText(rs.getString("text"))
                .build(),
        category);
  }

  private List<Ad> getRandomAds() {
    return jdbcTemplate.query(
        "select redirectUrl, text from ads order by rand() limit " + MAX_ADS_TO_SERVE,
        (rs, rowNum) ->
            Ad.newBuilder()
                .setRedirectUrl(rs.getString("redirectUrl"))
                .setText(rs.getString("text"))
                .build());
  }

  /** Await termination on the main thread since the grpc library uses daemon threads. */
  private void blockUntilShutdown() throws InterruptedException {
    if (server != null) {
      server.awaitTermination();
    }
  }

  private static ImmutableListMultimap<String, Ad> createAdsMap() {
    Ad camera =
        Ad.newBuilder()
            .setRedirectUrl("/product/2ZYFJ3GM2N")
            .setText("Film camera for sale. 50% off.")
            .build();
    Ad lens =
        Ad.newBuilder()
            .setRedirectUrl("/product/66VCHSJNUP")
            .setText("Vintage camera lens for sale. 20% off.")
            .build();
    Ad recordPlayer =
        Ad.newBuilder()
            .setRedirectUrl("/product/0PUK6V6EV0")
            .setText("Vintage record player for sale. 30% off.")
            .build();
    Ad bike =
        Ad.newBuilder()
            .setRedirectUrl("/product/9SIQT8TOJO")
            .setText("City Bike for sale. 10% off.")
            .build();
    Ad baristaKit =
        Ad.newBuilder()
            .setRedirectUrl("/product/1YMWWN1N4O")
            .setText("Home Barista kitchen kit for sale. Buy one, get second kit for free")
            .build();
    Ad airPlant =
        Ad.newBuilder()
            .setRedirectUrl("/product/6E92ZMYYFZ")
            .setText("Air plants for sale. Buy two, get third one for free")
            .build();
    Ad terrarium =
        Ad.newBuilder()
            .setRedirectUrl("/product/L9ECAV7KIM")
            .setText("Terrarium for sale. Buy one, get second one for free")
            .build();
    return ImmutableListMultimap.<String, Ad>builder()
        .putAll("photography", camera, lens)
        .putAll("vintage", camera, lens, recordPlayer)
        .put("cycling", bike)
        .put("cookware", baristaKit)
        .putAll("gardening", airPlant, terrarium)
        .build();
  }

  /** Main launches the server from the command line. */
  public static void main(String[] args)
      throws IOException, InterruptedException, ClassNotFoundException {
    JdbcTemplate jdbcTemplate = setUpDatabase();

    String serviceName = "AdService";
    Resource resource = Resource.create(Attributes.of(AttributeKey.stringKey("service.name"), serviceName));
    InstrumentSelector selectorUpDownCounter = InstrumentSelector.builder().setInstrumentType(InstrumentType.UP_DOWN_COUNTER).build();
    InstrumentSelector selectorHistogram = InstrumentSelector.builder().setInstrumentType(InstrumentType.HISTOGRAM).build();

    // TODO: Generate resource from OTEL_RESOURCE_ATTRIBUTES
    SdkMeterProvider meterProvider = SdkMeterProvider.builder()
        .setResource(resource)
        .registerView(selectorUpDownCounter, View.builder()
            .setAggregation(Aggregation.sum(AggregationTemporality.DELTA))
            .build())
        .registerView(selectorHistogram, View.builder()
            .setAggregation(Aggregation.explictBucketHistogram(AggregationTemporality.DELTA))
            .build())
        .buildAndRegisterGlobal();

    IntervalMetricReader.builder()
        .setExportIntervalMillis(2000)
        .setMetricExporter(OtlpGrpcMetricExporter.builder()
            .setEndpoint(System.getenv("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"))
            .addHeader("api-key", System.getenv("NEW_RELIC_API_KEY"))
            .build())
        .setMetricProducers(List.of(meterProvider))
        .buildAndStart();

    // Start the RPC server. You shouldn't see any output from gRPC before this.
    logger.info("AdService starting.");
    AdService adService = new AdService(meterProvider, jdbcTemplate);
    adService.start();
    adService.blockUntilShutdown();
  }

  private static JdbcTemplate setUpDatabase() throws ClassNotFoundException {
    Class.forName("org.h2.Driver");
    SingleConnectionDataSource dataSource =
        new SingleConnectionDataSource("jdbc:h2:mem:myDb;DB_CLOSE_DELAY=-1", "sa", "sa", true);

    JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
    jdbcTemplate.update(
        "create table ads( id identity, category varchar(30), redirectUrl varchar(255), text varchar(255))");
    ImmutableListMultimap<String, Ad> adsMap = createAdsMap();
    for (String category : adsMap.keys()) {
      ImmutableList<Ad> ads = adsMap.get(category);
      for (Ad ad : ads) {
        jdbcTemplate.update(
            "insert into ads(category, redirectUrl, text) values (?,?,?)",
            category,
            ad.getRedirectUrl(),
            ad.getText());
      }
    }
    Integer count = jdbcTemplate.queryForObject("select count(*) from ads", Integer.class);
    System.out.println("Created the Ads Database with " + count + " records.");
    return jdbcTemplate;
  }
}
