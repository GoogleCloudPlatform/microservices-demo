package hipstershop.frontend.session;

import hipstershop.frontend.config.ShopProperties;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.UUID;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/** Ports {@code ensureSessionID} from the Go frontend's middleware.go. */
@Component
@Order(2)
public class SessionIdFilter extends OncePerRequestFilter {

    public static final String SHARED_SESSION_ID = "12345678-1234-1234-1234-123456789123";

    private final ShopProperties shopProperties;

    public SessionIdFilter(ShopProperties shopProperties) {
        this.shopProperties = shopProperties;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String sessionId = null;
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (Cookie c : cookies) {
                if (ShopProperties.COOKIE_SESSION_ID.equals(c.getName())) {
                    sessionId = c.getValue();
                    break;
                }
            }
        }
        if (sessionId == null) {
            sessionId = shopProperties.isSingleSharedSession() ? SHARED_SESSION_ID : UUID.randomUUID().toString();
            Cookie cookie = new Cookie(ShopProperties.COOKIE_SESSION_ID, sessionId);
            cookie.setMaxAge(ShopProperties.COOKIE_MAX_AGE);
            cookie.setPath("/");
            response.addCookie(cookie);
        }
        request.setAttribute(SessionContext.SESSION_ID_ATTR, sessionId);
        chain.doFilter(request, response);
    }
}
