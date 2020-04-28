package hipstershop;

import com.newrelic.telemetry.Attributes;
import com.newrelic.telemetry.opentelemetry.export.NewRelicSpanExporter;
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
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.trace.TracerSdkProvider;
import io.opentelemetry.sdk.trace.export.BatchSpansProcessor;
import io.opentelemetry.sdk.trace.export.SpanExporter;

public class OpenTelemetryUtils {
  public static void initializeSdk(String serviceName) {
    TracerSdkProvider tracerSdkProvider = OpenTelemetrySdk.getTracerProvider();
    SpanExporter spanExporter = NewRelicSpanExporter.newBuilder()
        .apiKey(System.getenv("NEW_RELIC_API_KEY"))
        .enableAuditLogging()
        .commonAttributes(new Attributes().put("service.name", serviceName))
        .build();
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
