package hipstershop;

import static java.util.Collections.singleton;

import com.newrelic.telemetry.opentelemetry.export.NewRelicMetricExporter;
import com.newrelic.telemetry.opentelemetry.export.NewRelicSpanExporter;
import com.newrelic.telemetry.opentelemetry.export.NewRelicSpanExporter.Builder;
import io.grpc.CallOptions;
import io.grpc.Channel;
import io.grpc.ClientCall;
import io.grpc.ClientInterceptor;
import io.grpc.Context;
import io.grpc.Contexts;
import io.grpc.ForwardingClientCall;
import io.grpc.Metadata;
import io.grpc.Metadata.Key;
import io.grpc.MethodDescriptor;
import io.grpc.ServerCall;
import io.grpc.ServerCall.Listener;
import io.grpc.ServerCallHandler;
import io.grpc.ServerInterceptor;
import io.opentelemetry.OpenTelemetry;
import io.opentelemetry.exporters.logging.LoggingMetricExporter;
import io.opentelemetry.exporters.logging.LoggingSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.metrics.export.IntervalMetricReader;
import io.opentelemetry.sdk.metrics.export.MetricExporter;
import io.opentelemetry.sdk.trace.TracerSdkProvider;
import io.opentelemetry.sdk.trace.export.BatchSpansProcessor;
import io.opentelemetry.sdk.trace.export.SpanExporter;
import java.net.URI;

public class OpenTelemetryUtils {
  //seems like docker/k8s/skaffold/something passes in this value when the env var is missing.
  public static final String NO_VALUE_ENV_VAR = "<no value>";
  private static IntervalMetricReader intervalMetricReader;

  public static void initializeForNewRelic() {
    TracerSdkProvider tracerSdkProvider = OpenTelemetrySdk.getTracerProvider();
    String newRelicApiKey = System.getenv("NEW_RELIC_API_KEY");

    SpanExporter spanExporter;
    if (apiKeyIsMissing(newRelicApiKey)) {
      System.out
          .println("NEW_RELIC_API_KEY not present. Falling back to the logging span exporter.");
      spanExporter = new LoggingSpanExporter();
    } else {
      Builder builder = NewRelicSpanExporter.newBuilder()
          .apiKey(newRelicApiKey)
          .enableAuditLogging();
      String traceEndpoint = System.getenv("NEW_RELIC_TRACE_URL");
      if (traceEndpoint != null && !NO_VALUE_ENV_VAR.equals(traceEndpoint)) {
        builder.uriOverride(URI.create(traceEndpoint));
      }
      spanExporter = builder.build();
    }
    tracerSdkProvider.addSpanProcessor(BatchSpansProcessor.newBuilder(spanExporter).build());

    MetricExporter metricExporter;
    if (apiKeyIsMissing(newRelicApiKey)) {
      System.out
          .println("NEW_RELIC_API_KEY not present. Falling back to the logging metrics exporter.");
      metricExporter = new LoggingMetricExporter();
    } else {
      NewRelicMetricExporter.Builder builder = NewRelicMetricExporter.newBuilder()
          .apiKey(newRelicApiKey)
          .enableAuditLogging();
      String metricEndpoint = System.getenv("NEW_RELIC_METRIC_URL");
      if (metricEndpoint != null && !NO_VALUE_ENV_VAR.equals(metricEndpoint)) {
        builder.uriOverride(URI.create(metricEndpoint));
      }
      metricExporter = builder.build();
    }
    intervalMetricReader = IntervalMetricReader.builder()
        .setMetricProducers(singleton(OpenTelemetrySdk.getMeterProvider().getMetricProducer()))
        .setExportIntervalMillis(5000)
        .setMetricExporter(metricExporter)
        .build();
  }

  private static boolean apiKeyIsMissing(String newRelicApiKey) {
    return newRelicApiKey == null || newRelicApiKey.isEmpty() || NO_VALUE_ENV_VAR
        .equals(newRelicApiKey);
  }

  public static void shutdownSdk() {
    OpenTelemetrySdk.getTracerProvider().shutdown();
    intervalMetricReader.shutdown();
  }

  static class HttpTextFormatClientInterceptor implements ClientInterceptor {
    @Override
    public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(
        MethodDescriptor<ReqT, RespT> method, CallOptions callOptions, Channel next) {

      return new ForwardingClientCall.SimpleForwardingClientCall<ReqT, RespT>(
          next.newCall(method, callOptions)) {
        @Override
        public void start(Listener<RespT> responseListener, Metadata headers) {
          OpenTelemetry.getPropagators().getHttpTextFormat()
              .inject(Context.current(), headers, (carrier, key, value) ->
                  carrier.put(Key.of(key, Metadata.ASCII_STRING_MARSHALLER), value));
          super.start(responseListener, headers);
        }
      };
    }
  }

  static class HttpTextFormatServerInterceptor implements ServerInterceptor {
    @Override
    public <ReqT, RespT> Listener<ReqT> interceptCall(ServerCall<ReqT, RespT> call,
        Metadata headers, ServerCallHandler<ReqT, RespT> next) {
      Context updatedContext = OpenTelemetry.getPropagators().getHttpTextFormat()
          .extract(Context.current(), headers,
              (carrier, key) -> carrier.get(Key.of(key, Metadata.ASCII_STRING_MARSHALLER)));

      return Contexts.interceptCall(updatedContext, call, headers, next);
    }
  }
}
