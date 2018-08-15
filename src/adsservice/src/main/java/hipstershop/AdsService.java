package hipstershop;

import com.google.common.collect.ImmutableMap;
import hipstershop.Demo.Ads;
import hipstershop.Demo.AdsRequest;
import hipstershop.Demo.AdsResponse;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import io.opencensus.common.Duration;
import io.opencensus.contrib.grpc.metrics.RpcViews;
import io.opencensus.exporter.stats.prometheus.PrometheusStatsCollector;
import io.opencensus.exporter.trace.logging.LoggingTraceExporter;
import io.opencensus.exporter.stats.stackdriver.StackdriverStatsConfiguration;
import io.opencensus.exporter.stats.stackdriver.StackdriverStatsExporter;
import io.opencensus.exporter.trace.stackdriver.StackdriverTraceConfiguration;
import io.opencensus.exporter.trace.stackdriver.StackdriverTraceExporter;
import io.opencensus.trace.AttributeValue;
import io.opencensus.trace.Span;
import io.opencensus.trace.Tracer;
import io.opencensus.trace.Tracing;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

public class AdsService {
  private static final Logger logger = Logger.getLogger(AdsService.class.getName());

  private static final Tracer tracer = Tracing.getTracer();

  private int MAX_ADS_TO_SERVE = 2;
  private Server server;

  static final AdsService service = new AdsService();
  private void start() throws IOException {
    int port = Integer.parseInt(System.getenv("PORT"));
    server = ServerBuilder.forPort(port).addService(new AdsServiceImpl()).build().start();
    logger.info("Server started, listening on " + port);
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread() {
              @Override
              public void run() {
                // Use stderr here since the logger may have been reset by its JVM shutdown hook.
                System.err.println("*** shutting down gRPC ads server since JVM is shutting down");
                AdsService.this.stop();
                System.err.println("*** server shut down");
              }
            });
  }

  private void stop() {
    if (server != null) {
      server.shutdown();
    }
  }

  static class AdsServiceImpl extends hipstershop.AdsServiceGrpc.AdsServiceImplBase {

    /**
     * Retrieves ads based on context provided in the request {@code AdsRequest}.
     *
     * @param req the request containing context.
     * @param responseObserver the stream observer which gets notified with the value of
     *     {@code AdsResponse}
     */
    @Override
    public void getAds(AdsRequest req, StreamObserver<AdsResponse> responseObserver) {
      logger.info("Servicing getAds");
      AdsService service = AdsService.getInstance();
      Span span = tracer.getCurrentSpan();
      span.putAttribute("method", AttributeValue.stringAttributeValue("getAds"));
      span.addAnnotation(
          "Constructing Ads Request.",
          ImmutableMap.of(
              "Context Keys", AttributeValue.stringAttributeValue(req.getContextKeysList().toString()),
              "Context Keys length", AttributeValue.longAttributeValue(req.getContextKeysCount())));
      List<Ads> ads = new ArrayList<>();
      if (req.getContextKeysCount() > 0) {
        span.addAnnotation("Getting Ads by context.");
        for (int i = 0; i<req.getContextKeysCount(); i++) {
          Ads ad = service.getAdsByKey(req.getContextKeys(i));
          if (ad != null) {
            ads.add(ad);
          }
        }
      } else {
        span.addAnnotation("Getting default Ads.");
        ads = service.getDefaultAds();
      }
      if (ads.isEmpty()) {
        // Serve default ads.
        span.addAnnotation("NoGetting default Ads.");
        ads = service.getDefaultAds();
      }
      AdsResponse reply = AdsResponse.newBuilder().addAllAds(ads).build();
      responseObserver.onNext(reply);
      responseObserver.onCompleted();
      logger.info("Responded to getAds");
    }
  }

  static final HashMap<String, Ads> cacheMap = new HashMap<String, Ads>();

  Ads getAdsByKey(String key) {
    return cacheMap.get(key);
  }


  public List<Ads> getDefaultAds() {
    List<Ads> ads = new ArrayList<>();
    Iterator iterator = cacheMap.entrySet().iterator();
    while (iterator.hasNext()) {
      Map.Entry pair = (Map.Entry)iterator.next();
      ads.add((Ads)pair.getValue());
      if (ads.size() >= MAX_ADS_TO_SERVE) {
        break;
      }
    }
    return ads;
  }

  public static AdsService getInstance() {
    return service;
  }

  /** Await termination on the main thread since the grpc library uses daemon threads. */
  private void blockUntilShutdown() throws InterruptedException {
    if (server != null) {
      server.awaitTermination();
    }
  }

  static void initializeAds() {
    // TODO: Replace localhost with
    String adsUrl = System.getenv("ADS_URL");
    cacheMap.put("camera", Ads.newBuilder().setRedirectUrl(adsUrl + "/camera")
        .setText("MyPro camera for sale. 50% off.").build());
    cacheMap.put("bike", Ads.newBuilder().setRedirectUrl(adsUrl + "/bike")
        .setText("ZoomZoom bike for sale. 10% off.").build());
    cacheMap.put("kitchen", Ads.newBuilder().setRedirectUrl(adsUrl + "/kitchen")
        .setText("CutPro knife for sale. Buy one, get second set for free").build());
    logger.info("Default Ads initialized");
  }

  /** Main launches the server from the command line. */
  public static void main(String[] args) throws IOException, InterruptedException {
    // Add final keyword to pass checkStyle.
    final String cloudProjectId = System.getenv("GCP_PROJECT_ID");
    logger.info("GCP Project ID is " + cloudProjectId);

    initializeAds();

    // Registers all RPC views.
    RpcViews.registerAllViews();

    // Registers logging trace exporter.
    LoggingTraceExporter.register();


    // Registers Stackdriver exporters.
    if (cloudProjectId != null) {
      StackdriverTraceExporter.createAndRegister(
          StackdriverTraceConfiguration.builder().setProjectId(cloudProjectId).build());
      StackdriverStatsExporter.createAndRegister(
          StackdriverStatsConfiguration.builder()
              .setProjectId(cloudProjectId)
              .setExportInterval(Duration.create(15, 0))
              .build());
    }

    // Register Prometheus exporters and export metrics to a Prometheus HTTPServer.
    PrometheusStatsCollector.createAndRegister();

    // Start the RPC server. You shouldn't see any output from gRPC before this.
    logger.info("AdsService starting.");
    final AdsService service = AdsService.getInstance();
    service.start();
    service.blockUntilShutdown();
  }
}