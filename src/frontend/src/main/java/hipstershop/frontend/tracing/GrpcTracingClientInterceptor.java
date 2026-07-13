package hipstershop.frontend.tracing;

import io.grpc.CallOptions;
import io.grpc.Channel;
import io.grpc.ClientCall;
import io.grpc.ClientInterceptor;
import io.grpc.ForwardingClientCall.SimpleForwardingClientCall;
import io.grpc.ForwardingClientCallListener.SimpleForwardingClientCallListener;
import io.grpc.Metadata;
import io.grpc.MethodDescriptor;
import io.grpc.Status;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Context;
import io.opentelemetry.context.Scope;
import io.opentelemetry.context.propagation.TextMapSetter;

/**
 * Client-side gRPC span, mirroring the Go frontend's
 * {@code grpc.WithStatsHandler(otelgrpc.NewClientHandler())}: wraps every
 * outgoing call in a span and propagates the W3C trace context in metadata.
 */
public class GrpcTracingClientInterceptor implements ClientInterceptor {

    private static final TextMapSetter<Metadata> SETTER =
            (carrier, key, value) -> carrier.put(Metadata.Key.of(key, Metadata.ASCII_STRING_MARSHALLER), value);

    private final OpenTelemetry openTelemetry;
    private final Tracer tracer;

    public GrpcTracingClientInterceptor(OpenTelemetry openTelemetry, Tracer tracer) {
        this.openTelemetry = openTelemetry;
        this.tracer = tracer;
    }

    @Override
    public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(
            MethodDescriptor<ReqT, RespT> method, CallOptions callOptions, Channel next) {
        Span span = tracer.spanBuilder(method.getFullMethodName())
                .setSpanKind(SpanKind.CLIENT)
                .setParent(Context.current())
                .startSpan();
        Context ctx = Context.current().with(span);

        ClientCall<ReqT, RespT> call = next.newCall(method, callOptions);
        return new SimpleForwardingClientCall<>(call) {
            @Override
            public void start(Listener<RespT> responseListener, Metadata headers) {
                try (Scope ignored = ctx.makeCurrent()) {
                    openTelemetry.getPropagators().getTextMapPropagator().inject(ctx, headers, SETTER);
                    super.start(
                            new SimpleForwardingClientCallListener<>(responseListener) {
                                @Override
                                public void onClose(Status status, Metadata trailers) {
                                    if (!status.isOk()) {
                                        span.setStatus(StatusCode.ERROR, status.getDescription());
                                    }
                                    span.end();
                                    super.onClose(status, trailers);
                                }
                            },
                            headers);
                }
            }
        };
    }
}
