package hipstershop.frontend.logging;

import hipstershop.frontend.session.SessionContext;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingResponseWrapper;

/** Ports {@code logHandler} from the Go frontend's middleware.go. */
@Component
@Order(3)
public class RequestLoggingFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger("hipstershop.frontend.request");

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String requestId = UUID.randomUUID().toString();
        request.setAttribute(SessionContext.REQUEST_ID_ATTR, requestId);
        String sessionId = SessionContext.sessionId(request);

        MDC.put("http.req.path", request.getRequestURI());
        MDC.put("http.req.method", request.getMethod());
        MDC.put("http.req.id", requestId);
        if (sessionId != null && !sessionId.isEmpty()) {
            MDC.put("session", sessionId);
        }
        log.debug("request started");

        long start = System.currentTimeMillis();
        ContentCachingResponseWrapper wrapped = new ContentCachingResponseWrapper(response);
        try {
            chain.doFilter(request, wrapped);
        } finally {
            long tookMs = System.currentTimeMillis() - start;
            MDC.put("http.resp.took_ms", String.valueOf(tookMs));
            MDC.put("http.resp.status", String.valueOf(wrapped.getStatus()));
            MDC.put("http.resp.bytes", String.valueOf(wrapped.getContentSize()));
            log.debug("request complete");
            wrapped.copyBodyToResponse();
            MDC.clear();
        }
    }
}
