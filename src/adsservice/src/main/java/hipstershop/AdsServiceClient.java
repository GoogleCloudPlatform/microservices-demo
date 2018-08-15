
package hipstershop;


import com.google.common.collect.ImmutableMap;
import hipstershop.Demo.Ads;
import hipstershop.Demo.AdsRequest;
import hipstershop.Demo.AdsResponse;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.StatusRuntimeException;
import io.grpc.stub.StreamObserver;
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
import io.opencensus.trace.Status.CanonicalCode;
import io.opencensus.trace.Tracer;
import io.opencensus.trace.Tracing;
import io.opencensus.trace.samplers.Samplers;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.annotation.Nullable;

/** A simple client that requests ads from the Ads Service. */
public class AdsServiceClient {
  private static final Logger logger = Logger.getLogger(AdsServiceClient.class.getName());

  private static final Tracer tracer = Tracing.getTracer();

  private final ManagedChannel channel;
  private final hipstershop.AdsServiceGrpc.AdsServiceBlockingStub blockingStub;

  /** Construct client connecting to Ad Service at {@code host:port}. */
  public AdsServiceClient(String host, int port) {
    this(
        ManagedChannelBuilder.forAddress(host, port)
            // Channels are secure by default (via SSL/TLS). For the example we disable TLS to avoid
            // needing certificates.
            .usePlaintext(true)
            .build());
  }

  /** Construct client for accessing RouteGuide server using the existing channel. */
  AdsServiceClient(ManagedChannel channel) {
    this.channel = channel;
    blockingStub = hipstershop.AdsServiceGrpc.newBlockingStub(channel);
  }

  public void shutdown() throws InterruptedException {
    channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
  }

  /** Get Ads from Server. */
  public void getAds(String contextKey) {
    logger.info("Get Ads with context " + contextKey + " ...");
    AdsRequest request = AdsRequest.newBuilder().addContextKeys(contextKey).build();
    AdsResponse response;

    SpanBuilder spanBuilder =
        tracer.spanBuilder("AdsClient").setRecordEvents(true).setSampler(Samplers.alwaysSample());
    try (Scope scope = spanBuilder.startScopedSpan()) {
      tracer.getCurrentSpan().addAnnotation("Getting Ads");
      response = blockingStub.getAds(request);
      tracer.getCurrentSpan().addAnnotation("Received response from Ads Service.");
    } catch (StatusRuntimeException e) {
      tracer
          .getCurrentSpan()
          .setStatus(
              CanonicalCode.valueOf(e.getStatus().getCode().name())
                  .toStatus()
                  .withDescription(e.getMessage()));
      logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
      return;
    }
    for(Ads ads: response.getAdsList()) {
      logger.info("Ads: " + ads.getText());
    }
  }

  static int getPortOrDefaultFromArgs(String[] args, int index, int defaultPort) {
    int portNumber = defaultPort;
    if (index < args.length) {
      try {
        portNumber = Integer.parseInt(args[index]);
      } catch (NumberFormatException e) {
        logger.warning(
            String.format("Port %s is invalid, use default port %d.", args[index], defaultPort));
      }
    }
    return portNumber;
  }


  static String getStringOrDefaultFromArgs(
      String[] args, int index, @Nullable String defaultString) {
    String s = defaultString;
    if (index < args.length) {
      s = args[index];
    }
    return s;
  }

  /**
   * Ads Service Client main. If provided, the first element of {@code args} is the context key to
   * get the ads from the Ads Service
   */
  public static void main(String[] args) throws IOException, InterruptedException {
    // Add final keyword to pass checkStyle.
    final String contextKeys = getStringOrDefaultFromArgs(args, 0, "camera");
    final String host = getStringOrDefaultFromArgs(args, 1, "localhost");
    final int serverPort = getPortOrDefaultFromArgs(args, 2, 9555);
    final String cloudProjectId = getStringOrDefaultFromArgs(args, 3, null);
    //final int zPagePort = getPortOrDefaultFromArgs(args, 4, 3001);

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
    //PrometheusStatsCollector.createAndRegister();

    AdsServiceClient client = new AdsServiceClient(host, serverPort);
    try {
      client.getAds(contextKeys);
    } finally {
      client.shutdown();
    }

    logger.info("Exiting AdsServiceClient...");
  }
}
