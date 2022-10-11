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

import com.google.common.collect.ImmutableListMultimap;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Iterables;
import hipstershop.Demo.Ad;
import hipstershop.Demo.AdRequest;
import hipstershop.Demo.AdResponse;
import io.grpc.Server;
import io.grpc.*;
import io.grpc.ServerBuilder;
import io.grpc.ServerCall.Listener;
import io.grpc.StatusRuntimeException;
import io.grpc.health.v1.HealthCheckResponse.ServingStatus;
import io.grpc.services.*;
import io.grpc.stub.StreamObserver;
import io.opencensus.common.Duration;
import io.opencensus.contrib.grpc.metrics.RpcViews;
import io.opencensus.exporter.stats.stackdriver.StackdriverStatsConfiguration;
import io.opencensus.exporter.stats.stackdriver.StackdriverStatsExporter;
import io.opencensus.exporter.trace.jaeger.JaegerExporterConfiguration;
import io.opencensus.exporter.trace.jaeger.JaegerTraceExporter;
import io.opencensus.exporter.trace.stackdriver.StackdriverTraceConfiguration;
import io.opencensus.exporter.trace.stackdriver.StackdriverTraceExporter;
import io.opencensus.trace.AttributeValue;
import io.opencensus.trace.Span;
import io.opencensus.trace.Tracer;
import io.opencensus.trace.Tracing;
import java.io.IOException;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.time.Instant;
import java.lang.Thread;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public final class AdService {

  private static final Logger logger = LogManager.getLogger(AdService.class);
  private static final Tracer tracer = Tracing.getTracer();

  @SuppressWarnings("FieldCanBeLocal")
  private static int MAX_ADS_TO_SERVE = 2;

  private Server server;
  private HealthStatusManager healthMgr;

  private static final AdService service = new AdService();

  public static class MetadataInterceptor implements ServerInterceptor {
    public static Context.Key<Object> REQUEST_ID = Context.key("RequestID");
    public static Context.Key<Object> SERVICE_NAME = Context.key("ServiceName");

    @Override
    public <ReqT, RespT> Listener<ReqT> interceptCall(ServerCall<ReqT, RespT> call, Metadata headers,
        ServerCallHandler<ReqT, RespT> next) {

      Object RequestID = headers.get(Metadata.Key.of("requestid", Metadata.ASCII_STRING_MARSHALLER));
      Object ServiceName = headers.get(Metadata.Key.of("servicename", Metadata.ASCII_STRING_MARSHALLER));

      if (RequestID == null && ServiceName == null) {
        AdService.emitLog(ADSERVICE + ": SessionID not found in header.", "ERROR");
        return new ServerCall.Listener() {
        };
      }

      Context context = Context.current().withValues(REQUEST_ID, RequestID, SERVICE_NAME, ServiceName);

      return Contexts.interceptCall(context, call, headers, next);
    }
  }

  private void start() throws IOException {
    int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "9555"));
    healthMgr = new HealthStatusManager();

    server = ServerBuilder.forPort(port)
        .addService(ServerInterceptors.intercept(new AdServiceImpl(), new MetadataInterceptor()))
        .addService(healthMgr.getHealthService())
        .build()
        .start();
    logger.info("Ad Service started, listening on " + port);
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  // Use stderr here since the logger may have been reset by its JVM shutdown
                  // hook.
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

  public static String ADSERVICE = "adservice";

  // NOTE: logLevel must be a GELF valid severity value (WARN or ERROR), INFO if
  // not specified
  public static void emitLog(String event, String logLevel) {
    try {
	Date date = new Date(System.currentTimeMillis());
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS");
        String timestamp = sdf.format(date);

	switch (logLevel) {
      	case "ERROR":
        	logger.log(Level.ERROR, timestamp + " - ERROR - " + ADSERVICE + " - " + event);
        break;

      	case "WARN":
        	logger.log(Level.WARN, timestamp + " - WARN - " + ADSERVICE + " - " + event);
        break;

      	default:
        	logger.log(Level.INFO, timestamp + " - INFO - " + ADSERVICE + " - " + event);
        break;
	}
    } catch(Exception err) { logger.log(Level.ERROR, "adservice: Impossible to parse current timestamp."); }
  }

  private static class AdServiceImpl extends hipstershop.AdServiceGrpc.AdServiceImplBase {

    /**
     * Retrieves ads based on context provided in the request {@code AdRequest}.
     *
     * @param req              the request containing context.
     * @param responseObserver the stream observer which gets notified with the
     *                         value of {@code
     *     AdResponse}
     */
    @Override
    public void getAds(AdRequest req, StreamObserver<AdResponse> responseObserver) {
      AdService service = AdService.getInstance();
      Span span = tracer.getCurrentSpan();

      try {
        Object RequestID = MetadataInterceptor.REQUEST_ID.get();
        Object ServiceName = MetadataInterceptor.SERVICE_NAME.get();

        String event = "Received request from " + ServiceName.toString() + " (request_id: " + RequestID.toString()
            + ")";
        AdService.emitLog(event, "INFO");

        span.putAttribute("method", AttributeValue.stringAttributeValue("getAds"));
        List<Ad> allAds = new ArrayList<>();
        logger.info("received ad request (context_words=" + req.getContextKeysList() + ")");
        if (req.getContextKeysCount() > 0) {
          span.addAnnotation(
              "Constructing Ads using context",
              ImmutableMap.of(
                  "Context Keys",
                  AttributeValue.stringAttributeValue(req.getContextKeysList().toString()),
                  "Context Keys length",
                  AttributeValue.longAttributeValue(req.getContextKeysCount())));
          for (int i = 0; i < req.getContextKeysCount(); i++) {
            Collection<Ad> ads = service.getAdsByCategory(req.getContextKeys(i));
            allAds.addAll(ads);
          }
        } else {
          span.addAnnotation("No Context provided. Constructing random Ads.");
          allAds = service.getRandomAds();
        }
        if (allAds.isEmpty()) {
          // Serve random ads.
          span.addAnnotation("No Ads found based on context. Constructing random Ads.");
          allAds = service.getRandomAds();
        }

        event = "Answered request from " + ServiceName.toString() + " (request_id: " + RequestID.toString() + ")";
        AdService.emitLog(event, "INFO");

        AdResponse reply = AdResponse.newBuilder().addAllAds(allAds).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();

      } catch (StatusRuntimeException e) {
        AdService.emitLog("GetAds Failed with status" + e.getStatus(), "ERROR");
        logger.log(Level.WARN, "GetAds Failed with status {}", e.getStatus());
        responseObserver.onError(e);
      }
    }
  }

  private static final ImmutableListMultimap<String, Ad> adsMap = createAdsMap();

  private Collection<Ad> getAdsByCategory(String category) {
    return adsMap.get(category);
  }

  private static final Random random = new Random();

  private List<Ad> getRandomAds() {
    List<Ad> ads = new ArrayList<>(MAX_ADS_TO_SERVE);
    Collection<Ad> allAds = adsMap.values();
    for (int i = 0; i < MAX_ADS_TO_SERVE; i++) {
      ads.add(Iterables.get(allAds, random.nextInt(allAds.size())));
    }
    return ads;
  }

  private static AdService getInstance() {
    return service;
  }

  /**
   * Await termination on the main thread since the grpc library uses daemon
   * threads.
   */
  private void blockUntilShutdown() throws InterruptedException {
    if (server != null) {
      server.awaitTermination();
    }
  }

  private static ImmutableListMultimap<String, Ad> createAdsMap() {
    Ad hairdryer = Ad.newBuilder()
        .setRedirectUrl("/product/2ZYFJ3GM2N")
        .setText("Hairdryer for sale. 50% off.")
        .build();
    Ad tankTop = Ad.newBuilder()
        .setRedirectUrl("/product/66VCHSJNUP")
        .setText("Tank top for sale. 20% off.")
        .build();
    Ad candleHolder = Ad.newBuilder()
        .setRedirectUrl("/product/0PUK6V6EV0")
        .setText("Candle holder for sale. 30% off.")
        .build();
    Ad bambooGlassJar = Ad.newBuilder()
        .setRedirectUrl("/product/9SIQT8TOJO")
        .setText("Bamboo glass jar for sale. 10% off.")
        .build();
    Ad watch = Ad.newBuilder()
        .setRedirectUrl("/product/1YMWWN1N4O")
        .setText("Watch for sale. Buy one, get second kit for free")
        .build();
    Ad mug = Ad.newBuilder()
        .setRedirectUrl("/product/6E92ZMYYFZ")
        .setText("Mug for sale. Buy two, get third one for free")
        .build();
    Ad loafers = Ad.newBuilder()
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

  private static void initStats() {
    if (System.getenv("DISABLE_STATS") != null) {
      logger.info("Stats disabled.");
      return;
    }
    logger.info("Stats enabled");

    long sleepTime = 10; /* seconds */
    int maxAttempts = 5;
    boolean statsExporterRegistered = false;
    for (int i = 0; i < maxAttempts; i++) {
      try {
        if (!statsExporterRegistered) {
          StackdriverStatsExporter.createAndRegister(
              StackdriverStatsConfiguration.builder()
                  .setExportInterval(Duration.create(60, 0))
                  .build());
          statsExporterRegistered = true;
        }
      } catch (Exception e) {
        if (i == (maxAttempts - 1)) {
          logger.log(
              Level.WARN,
              "Failed to register Stackdriver Exporter."
                  + " Stats data will not reported to Stackdriver. Error message: "
                  + e.toString());
        } else {
          logger.info("Attempt to register Stackdriver Exporter in " + sleepTime + " seconds ");
          try {
            Thread.sleep(TimeUnit.SECONDS.toMillis(sleepTime));
          } catch (Exception se) {
            logger.log(Level.WARN, "Exception while sleeping" + se.toString());
          }
        }
      }
    }
    logger.info("Stats enabled - Stackdriver Exporter initialized.");
  }

  private static void initTracing() {
    if (System.getenv("DISABLE_TRACING") != null) {
      logger.info("Tracing disabled.");
      return;
    }
    logger.info("Tracing enabled");

    long sleepTime = 10; /* seconds */
    int maxAttempts = 5;
    boolean traceExporterRegistered = false;

    for (int i = 0; i < maxAttempts; i++) {
      try {
        if (!traceExporterRegistered) {
          StackdriverTraceExporter.createAndRegister(
              StackdriverTraceConfiguration.builder().build());
          traceExporterRegistered = true;
        }
      } catch (Exception e) {
        if (i == (maxAttempts - 1)) {
          logger.log(
              Level.WARN,
              "Failed to register Stackdriver Exporter."
                  + " Tracing data will not reported to Stackdriver. Error message: "
                  + e.toString());
        } else {
          logger.info("Attempt to register Stackdriver Exporter in " + sleepTime + " seconds ");
          try {
            Thread.sleep(TimeUnit.SECONDS.toMillis(sleepTime));
          } catch (Exception se) {
            logger.log(Level.WARN, "Exception while sleeping" + se.toString());
          }
        }
      }
    }
    logger.info("Tracing enabled - Stackdriver exporter initialized.");
  }

  private static void initJaeger() {
    String jaegerAddr = System.getenv("JAEGER_SERVICE_ADDR");
    if (jaegerAddr != null && !jaegerAddr.isEmpty()) {
      String jaegerUrl = String.format("http://%s/api/traces", jaegerAddr);
      // Register Jaeger Tracing.
      JaegerTraceExporter.createAndRegister(
          JaegerExporterConfiguration.builder()
              .setThriftEndpoint(jaegerUrl)
              .setServiceName("adservice")
              .build());
      logger.info("Jaeger initialization complete.");
    } else {
      logger.info("Jaeger initialization disabled.");
    }
  }

  /** Main launches the server from the command line. */
  public static void main(String[] args) throws IOException, InterruptedException {
    // Registers all RPC views.
    RpcViews.registerAllGrpcViews();

    new Thread(
        () -> {
          initStats();
          initTracing();
        })
        .start();

    // Register Jaeger
    initJaeger();

    // Start the RPC server. You shouldn't see any output from gRPC before this.
    logger.info("AdService starting.");
    final AdService service = AdService.getInstance();
    service.start();
    service.blockUntilShutdown();
  }
}
