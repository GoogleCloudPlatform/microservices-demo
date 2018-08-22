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

import com.google.common.collect.ImmutableMap;
import hipstershop.Demo.Ad;
import hipstershop.Demo.AdRequest;
import hipstershop.Demo.AdResponse;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.StatusRuntimeException;
import io.grpc.health.v1.HealthCheckResponse.ServingStatus;
import io.grpc.stub.StreamObserver;
import io.grpc.services.*;
import io.opencensus.common.Duration;
import io.opencensus.common.Scope;
import io.opencensus.contrib.grpc.metrics.RpcViews;
import io.opencensus.exporter.stats.prometheus.PrometheusStatsCollector;
import io.opencensus.exporter.trace.logging.LoggingTraceExporter;
import io.opencensus.exporter.stats.stackdriver.StackdriverStatsConfiguration;
import io.opencensus.exporter.stats.stackdriver.StackdriverStatsExporter;
import io.opencensus.exporter.trace.stackdriver.StackdriverTraceConfiguration;
import io.opencensus.exporter.trace.stackdriver.StackdriverTraceExporter;
import io.opencensus.trace.AttributeValue;
import io.opencensus.trace.Span;
import io.opencensus.trace.SpanBuilder;
import io.opencensus.trace.Tracer;
import io.opencensus.trace.Tracing;
import io.opencensus.trace.samplers.Samplers;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

public class AdService {
  private static final Logger logger = Logger.getLogger(AdService.class.getName());

  private static final Tracer tracer = Tracing.getTracer();

  private int MAX_ADS_TO_SERVE = 2;
  private Server server;
  private HealthStatusManager healthMgr;

  static final AdService service = new AdService();
  private void start() throws IOException {
    int port = Integer.parseInt(System.getenv("PORT"));
    healthMgr = new HealthStatusManager();

    server = ServerBuilder.forPort(port).addService(new AdServiceImpl())
        .addService(healthMgr.getHealthService()).build().start();
    logger.info("Ad Service started, listening on " + port);
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread() {
              @Override
              public void run() {
                // Use stderr here since the logger may have been reset by its JVM shutdown hook.
                System.err.println("*** shutting down gRPC ads server since JVM is shutting down");
                AdService.this.stop();
                System.err.println("*** server shut down");
              }
            });
    healthMgr.setStatus("", ServingStatus.SERVING);
  }

  private void stop() {
    if (server != null) {
      healthMgr.clearStatus("");
      server.shutdown();
    }
  }

  static class AdServiceImpl extends hipstershop.AdServiceGrpc.AdServiceImplBase {

    /**
     * Retrieves ads based on context provided in the request {@code AdRequest}.
     *
     * @param req the request containing context.
     * @param responseObserver the stream observer which gets notified with the value of
     *     {@code AdResponse}
     */
    @Override
    public void getAds(AdRequest req, StreamObserver<AdResponse> responseObserver) {
      AdService service = AdService.getInstance();
      Span parentSpan = tracer.getCurrentSpan();
      SpanBuilder spanBuilder =
          tracer
              .spanBuilderWithExplicitParent("Retrieve Ads", parentSpan)
              .setRecordEvents(true)
              .setSampler(Samplers.alwaysSample());
      try (Scope scope = spanBuilder.startScopedSpan()) {
        Span span = tracer.getCurrentSpan();
        span.putAttribute("method", AttributeValue.stringAttributeValue("getAds"));
        List<Ad> ads = new ArrayList<>();
        logger.info("received ad request (context_words=" + req.getContextKeysCount() + ")");
        if (req.getContextKeysCount() > 0) {
          span.addAnnotation(
              "Constructing Ads using context",
              ImmutableMap.of(
                  "Context Keys",
                  AttributeValue.stringAttributeValue(req.getContextKeysList().toString()),
                  "Context Keys length",
                  AttributeValue.longAttributeValue(req.getContextKeysCount())));
          for (int i = 0; i < req.getContextKeysCount(); i++) {
            Ad ad = service.getAdsByKey(req.getContextKeys(i));
            if (ad != null) {
              ads.add(ad);
            }
          }
        } else {
          span.addAnnotation("No Context provided. Constructing random Ads.");
          ads = service.getDefaultAds();
        }
        if (ads.isEmpty()) {
          // Serve default ads.
          span.addAnnotation("No Ads found based on context. Constructing random Ads.");
          ads = service.getDefaultAds();
        }
        AdResponse reply = AdResponse.newBuilder().addAllAds(ads).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
      } catch (StatusRuntimeException e) {
        logger.log(Level.WARNING, "GetAds Failed", e.getStatus());
        return;
      }
    }
  }

  static final HashMap<String, Ad> cacheMap = new HashMap<String, Ad>();

  Ad getAdsByKey(String key) {
    return cacheMap.get(key);
  }


  public List<Ad> getDefaultAds() {
    List<Ad> ads = new ArrayList<>(MAX_ADS_TO_SERVE);
    Object[] keys = cacheMap.keySet().toArray();
    for (int i=0; i<MAX_ADS_TO_SERVE; i++) {
      ads.add(cacheMap.get(keys[new Random().nextInt(keys.length)]));
    }
    return ads;
  }

  public static AdService getInstance() {
    return service;
  }

  /** Await termination on the main thread since the grpc library uses daemon threads. */
  private void blockUntilShutdown() throws InterruptedException {
    if (server != null) {
      server.awaitTermination();
    }
  }

  static void initializeAds() {
    cacheMap.put("camera", Ad.newBuilder().setRedirectUrl( "/product/2ZYFJ3GM2N")
        .setText("Film camera for sale. 50% off.").build());
    cacheMap.put("bike", Ad.newBuilder().setRedirectUrl("/product/9SIQT8TOJO")
        .setText("City Bike for sale. 10% off.").build());
    cacheMap.put("kitchen", Ad.newBuilder().setRedirectUrl("/product/1YMWWN1N4O")
        .setText("Home Barista kitchen kit for sale. Buy one, get second kit for free").build());
    logger.info("Default Ads initialized");
  }

  public static void initStackdriver() {
    logger.info("Initialize StackDriver");

    // Registers all RPC views.
    RpcViews.registerAllViews();

    // Registers logging trace exporter.
    LoggingTraceExporter.register();
    long sleepTime = 10; /* seconds */
    int maxAttempts = 3;

    for (int i=0; i<maxAttempts; i++) {
      try {
        StackdriverTraceExporter.createAndRegister(
            StackdriverTraceConfiguration.builder().build());
        StackdriverStatsExporter.createAndRegister(
            StackdriverStatsConfiguration.builder()
                .setExportInterval(Duration.create(15, 0))
                .build());
      } catch (Exception e) {
        if (i==(maxAttempts-1)) {
          logger.log(Level.WARNING, "Failed to register Stackdriver Exporter." +
              " Tracing and Stats data will not reported to Stackdriver. Error message: " + e
              .toString());
        } else {
          logger.info("Attempt to register Stackdriver Exporter in " + sleepTime + " seconds ");
          try {
            Thread.sleep(TimeUnit.SECONDS.toMillis(sleepTime));
          } catch (Exception se) {
            logger.log(Level.WARNING, "Exception while sleeping" + se.toString());
          }
        }
      }
    }
    logger.info("StackDriver initialization complete.");
  }

  /** Main launches the server from the command line. */
  public static void main(String[] args) throws IOException, InterruptedException {
    // Add final keyword to pass checkStyle.

    initializeAds();

    new Thread( new Runnable() {
      public void run(){
        initStackdriver();
      }
    }).start();

    // Register Prometheus exporters and export metrics to a Prometheus HTTPServer.
    PrometheusStatsCollector.createAndRegister();

    // Start the RPC server. You shouldn't see any output from gRPC before this.
    logger.info("AdService starting.");
    final AdService service = AdService.getInstance();
    service.start();
    service.blockUntilShutdown();
  }
}