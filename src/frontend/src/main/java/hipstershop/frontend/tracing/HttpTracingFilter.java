package hipstershop.frontend.tracing;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Context;
import io.opentelemetry.context.Scope;
import io.opentelemetry.context.propagation.TextMapGetter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Collections;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * Server-side HTTP span, mirroring the Go frontend's
 * {@code otelhttp.NewHandler(handler, "frontend")} wrapper: extracts any
 * incoming W3C trace context and starts a single "frontend" span per request.
 */
@Component
@Order(1)
public class HttpTracingFilter extends OncePerRequestFilter {

    private static final TextMapGetter<HttpServletRequest> GETTER = new TextMapGetter<>() {
        @Override
        public Iterable<String> keys(HttpServletRequest carrier) {
            return Collections.list(carrier.getHeaderNames());
        }

        @Override
        public String get(HttpServletRequest carrier, String key) {
            return carrier == null ? null : carrier.getHeader(key);
        }
    };

    private final OpenTelemetry openTelemetry;
    private final Tracer tracer;

    public HttpTracingFilter(OpenTelemetry openTelemetry, Tracer tracer) {
        this.openTelemetry = openTelemetry;
        this.tracer = tracer;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        Context extracted = openTelemetry.getPropagators().getTextMapPropagator()
                .extract(Context.current(), request, GETTER);

        Span span = tracer.spanBuilder("frontend")
                .setParent(extracted)
                .setSpanKind(SpanKind.SERVER)
                .setAttribute("http.method", request.getMethod())
                .setAttribute("http.target", request.getRequestURI())
                .startSpan();

        try (Scope scope = extracted.with(span).makeCurrent()) {
            chain.doFilter(request, response);
            span.setAttribute("http.status_code", response.getStatus());
            if (response.getStatus() >= 500) {
                span.setStatus(StatusCode.ERROR);
            }
        } catch (Exception e) {
            span.setStatus(StatusCode.ERROR, e.getMessage());
            throw e;
        } finally {
            span.end();
        }
    }
}
