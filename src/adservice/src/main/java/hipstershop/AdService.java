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
import io.opentelemetry.api.metrics.LongHistogram;
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
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
  private final JdbcTemplate jdbcTemplate;

  private Server server;
  private HealthStatusManager healthMgr;

  public AdService(JdbcTemplate jdbcTemplate) {
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

    // used for doing some manual span instrumentation.
    private final Tracer tracer = GlobalOpenTelemetry.getTracer("hipstershop.adservice");
    private final LongHistogram backgroundLatency;
    private final LongHistogram numberOfAdsRequested;

    public AdServiceImpl(AdService service) {
      this.service = service;

      // this is a custom "business" metric, outside the scope of semantic conventions
      Meter meter = GlobalOpenTelemetry.getMeter("hipstershop.adservice");
      numberOfAdsRequested =
          meter
              .histogramBuilder("ads_requested")
              .setDescription("Number of Ads Requested per Request")
              .ofLongs()
              .build();

      // custom timer for the background job.
      backgroundLatency =
          meter
              .histogramBuilder("background.job.duration")
              .setDescription("Background job timings")
              .setUnit("ms")
              .ofLongs()
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
      numberOfAdsRequested.record(req.getContextKeysCount());
      try {
        List<Ad> allAds = chooseAds(req);
        reportAdsToBackgroundService(allAds);
        AdResponse reply = AdResponse.newBuilder().addAllAds(allAds).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
      } catch (StatusRuntimeException e) {
        logger.log(Level.WARN, "GetAds Failed with status {}", e.getStatus());
        responseObserver.onError(e);
      }
    }

    private void reportAdsToBackgroundService(List<Ad> allAds) {
      backgroundJobber.execute(() -> reportAdsRequest(allAds));
    }

    private void reportAdsRequest(List<Ad> allAds) {
      long startTime = System.currentTimeMillis();
      String spanName = "ReportRequestedAds";
      Span span =
          tracer.spanBuilder(spanName).setAttribute("numberOfAds", allAds.size()).startSpan();
      try (Scope ignored = span.makeCurrent()) {
        anotherSpan();
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      } finally {
        backgroundLatency.record((System.currentTimeMillis() - startTime));
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
    Ad hairdryer =
        Ad.newBuilder()
            .setRedirectUrl("/product/2ZYFJ3GM2N")
            .setText("Hairdryer for sale. 50% off.")
            .build();
    Ad tankTop =
        Ad.newBuilder()
            .setRedirectUrl("/product/66VCHSJNUP")
            .setText("Tank top for sale. 20% off.")
            .build();
    Ad candleHolder =
        Ad.newBuilder()
            .setRedirectUrl("/product/0PUK6V6EV0")
            .setText("Candle holder for sale. 30% off.")
            .build();
    Ad bambooGlassJar =
        Ad.newBuilder()
            .setRedirectUrl("/product/9SIQT8TOJO")
            .setText("Bamboo glass jar for sale. 10% off.")
            .build();
    Ad watch =
        Ad.newBuilder()
            .setRedirectUrl("/product/1YMWWN1N4O")
            .setText("Watch for sale. Buy one, get second kit for free")
            .build();
    Ad mug =
        Ad.newBuilder()
            .setRedirectUrl("/product/6E92ZMYYFZ")
            .setText("Mug for sale. Buy two, get third one for free")
            .build();
    Ad loafers =
        Ad.newBuilder()
            .setRedirectUrl("/product/L9ECAV7KIM")
            .setText("Loafers for sale. Buy one, get second one for free")
            .build();
    return ImmutableListMultimap.<String, Ad>builder()
        .putAll("clothing", tankTop)
        .putAll("accessories", watch)
        .putAll("footwear", loafers)
        .putAll("hair", hairdryer)
        .putAll("decor", candleHolder)
        .putAll("kitchen", bambooGlassJar, mug)
        .build();
  }

  /** Main launches the server from the command line. */
  public static void main(String[] args)
      throws IOException, InterruptedException, ClassNotFoundException {
    JdbcTemplate jdbcTemplate = setUpDatabase();
    // Start the RPC server. You shouldn't see any output from gRPC before this.
    logger.info("AdService starting.");
    AdService adService = new AdService(jdbcTemplate);
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
