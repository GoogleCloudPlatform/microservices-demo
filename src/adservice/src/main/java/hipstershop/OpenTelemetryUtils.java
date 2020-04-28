package hipstershop;

import com.newrelic.telemetry.Attributes;
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
import io.opentelemetry.exporters.logging.LoggingSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.trace.TracerSdkProvider;
import io.opentelemetry.sdk.trace.export.BatchSpansProcessor;
import io.opentelemetry.sdk.trace.export.SpanExporter;
import java.net.URI;

public class OpenTelemetryUtils {
  //seems like docker/k8s/skaffold/something passes in this value when the env var is missing.
  public static final String NO_VALUE_ENV_VAR = "<no value>";

  public static void initializeForNewRelic(String serviceName) {
    TracerSdkProvider tracerSdkProvider = OpenTelemetrySdk.getTracerProvider();
    String newRelicApiKey = System.getenv("NEW_RELIC_API_KEY");
    String traceEndpoint = System.getenv("NEW_RELIC_TRACE_URL");
    //todo: wire up metrics
    String metricEndpoint = System.getenv("NEW_RELIC_METRIC_URL");
    SpanExporter spanExporter;
    if (newRelicApiKey == null || newRelicApiKey.isEmpty() || NO_VALUE_ENV_VAR.equals(newRelicApiKey)) {
      System.out.println("NEW_RELIC_API_KEY not present. Falling back to the logging exporter.");
      spanExporter = new LoggingSpanExporter();
    } else {
      Builder builder = NewRelicSpanExporter.newBuilder()
          .apiKey(newRelicApiKey)
          .enableAuditLogging()
          .commonAttributes(new Attributes().put("service.name", serviceName));
      if (traceEndpoint != null && !NO_VALUE_ENV_VAR.equals(traceEndpoint)) {
        builder.uriOverride(URI.create(traceEndpoint));
      }
      spanExporter = builder.build();
    }
    tracerSdkProvider.addSpanProcessor(BatchSpansProcessor.newBuilder(spanExporter).build());
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
