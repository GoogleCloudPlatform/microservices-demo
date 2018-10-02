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


import hipstershop.Demo.Ad;
import hipstershop.Demo.AdRequest;
import hipstershop.Demo.AdResponse;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusRuntimeException;
import io.opencensus.common.Duration;
import io.opencensus.common.Scope;
import io.opencensus.contrib.grpc.metrics.RpcViews;
import io.opencensus.exporter.trace.logging.LoggingTraceExporter;
import io.opencensus.exporter.stats.stackdriver.StackdriverStatsConfiguration;
import io.opencensus.exporter.stats.stackdriver.StackdriverStatsExporter;
import io.opencensus.exporter.trace.stackdriver.StackdriverTraceConfiguration;
import io.opencensus.exporter.trace.stackdriver.StackdriverTraceExporter;
import io.opencensus.trace.SpanBuilder;
import io.opencensus.trace.Status.CanonicalCode;
import io.opencensus.trace.Tracer;
import io.opencensus.trace.Tracing;
import io.opencensus.trace.samplers.Samplers;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import javax.annotation.Nullable;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

/** A simple client that requests ads from the Ads Service. */
public class AdServiceClient {
  private static final Logger logger = LogManager.getLogger(AdServiceClient.class);

  private static final Tracer tracer = Tracing.getTracer();

  private final ManagedChannel channel;
  private final hipstershop.AdServiceGrpc.AdServiceBlockingStub blockingStub;

  /** Construct client connecting to Ad Service at {@code host:port}. */
  public AdServiceClient(String host, int port) {
    this(
        ManagedChannelBuilder.forAddress(host, port)
            // Channels are secure by default (via SSL/TLS). For the example we disable TLS to avoid
            // needing certificates.
            .usePlaintext(true)
            .build());
  }

  /** Construct client for accessing RouteGuide server using the existing channel. */
  AdServiceClient(ManagedChannel channel) {
    this.channel = channel;
    blockingStub = hipstershop.AdServiceGrpc.newBlockingStub(channel);
  }

  public void shutdown() throws InterruptedException {
    channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
  }

  /** Get Ads from Server. */
  public void getAds(String contextKey) {
    logger.info("Get Ads with context " + contextKey + " ...");
    AdRequest request = AdRequest.newBuilder().addContextKeys(contextKey).build();
    AdResponse response;

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
      logger.log(Level.WARN, "RPC failed: {0}", e.getStatus());
      return;
    }
    for(Ad ads: response.getAdsList()) {
      logger.info("Ads: " + ads.getText());
    }
  }

  static int getPortOrDefaultFromArgs(String[] args, int index, int defaultPort) {
    int portNumber = defaultPort;
    if (index < args.length) {
      try {
        portNumber = Integer.parseInt(args[index]);
      } catch (NumberFormatException e) {
        logger.warn(
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
      long sleepTime = 10; /* seconds */
      int maxAttempts = 3;

      for (int i=0; i<maxAttempts; i++) {
        try {
          StackdriverTraceExporter.createAndRegister(
              StackdriverTraceConfiguration.builder().setProjectId(cloudProjectId).build());
          StackdriverStatsExporter.createAndRegister(
              StackdriverStatsConfiguration.builder()
                  .setProjectId(cloudProjectId)
                  .setExportInterval(Duration.create(15, 0))
                  .build());
        } catch (Exception e) {
          if (i==(maxAttempts-1)) {
            logger.log(Level.WARN, "Failed to register Stackdriver Exporter." +
                " Tracing and Stats data will not reported to Stackdriver. Error message: " + e
                .toString());
          } else {
            logger.info("Attempt to register Stackdriver Exporter in " + sleepTime + " seconds");
            try {
              Thread.sleep(TimeUnit.SECONDS.toMillis(sleepTime));
            } catch (Exception se) {
              logger.log(Level.WARN, "Exception while sleeping" + e.toString());
            }
          }
        }
      }
    }

    // Register Prometheus exporters and export metrics to a Prometheus HTTPServer.
    //PrometheusStatsCollector.createAndRegister();

    AdServiceClient client = new AdServiceClient(host, serverPort);
    try {
      client.getAds(contextKeys);
    } finally {
      client.shutdown();
    }

    logger.info("Exiting AdServiceClient...");
  }
}
