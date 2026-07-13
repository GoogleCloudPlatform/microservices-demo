package hipstershop.frontend.tracing;

import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.baggage.propagation.W3CBaggagePropagator;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.propagation.W3CTraceContextPropagator;
import io.opentelemetry.context.propagation.ContextPropagators;
import io.opentelemetry.context.propagation.TextMapPropagator;
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import io.opentelemetry.sdk.trace.samplers.Sampler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Ports the Go frontend's {@code initTracing} in main.go: when ENABLE_TRACING=1,
 * spans are batched and exported over OTLP/gRPC to COLLECTOR_SERVICE_ADDR with
 * an always-on sampler; otherwise tracing is a no-op.
 */
@Configuration
public class TracingConfig {

    private static final Logger log = LoggerFactory.getLogger(TracingConfig.class);
    private static final String INSTRUMENTATION_NAME = "hipstershop.frontend";

    @Value("${ENABLE_TRACING:0}")
    private String enableTracing;

    @Value("${COLLECTOR_SERVICE_ADDR:}")
    private String collectorServiceAddr;

    @Bean
    public OpenTelemetry openTelemetry() {
        OpenTelemetry openTelemetry;
        if ("1".equals(enableTracing)) {
            log.info("Tracing enabled.");
            if (collectorServiceAddr == null || collectorServiceAddr.isBlank()) {
                throw new IllegalStateException("environment variable \"COLLECTOR_SERVICE_ADDR\" not set");
            }
            OtlpGrpcSpanExporter exporter = OtlpGrpcSpanExporter.builder()
                    .setEndpoint("http://" + collectorServiceAddr)
                    .build();

            SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
                    .addSpanProcessor(BatchSpanProcessor.builder(exporter).build())
                    .setSampler(Sampler.alwaysOn())
                    .build();

            TextMapPropagator propagator = TextMapPropagator.composite(
                    W3CTraceContextPropagator.getInstance(), W3CBaggagePropagator.getInstance());

            openTelemetry = OpenTelemetrySdk.builder()
                    .setTracerProvider(tracerProvider)
                    .setPropagators(ContextPropagators.create(propagator))
                    .build();
        } else {
            log.info("Tracing disabled.");
            openTelemetry = OpenTelemetry.noop();
        }
        GlobalOpenTelemetry.set(openTelemetry);
        return openTelemetry;
    }

    @Bean
    public Tracer tracer(OpenTelemetry openTelemetry) {
        return openTelemetry.getTracer(INSTRUMENTATION_NAME);
    }
}
