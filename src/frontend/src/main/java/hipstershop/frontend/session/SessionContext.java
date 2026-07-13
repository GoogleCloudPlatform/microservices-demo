package hipstershop.frontend.session;

import jakarta.servlet.http.HttpServletRequest;

/** Request-attribute keys shared between {@link SessionIdFilter} and controllers. */
public final class SessionContext {

    public static final String SESSION_ID_ATTR = "hipstershop.sessionId";
    public static final String REQUEST_ID_ATTR = "hipstershop.requestId";

    private SessionContext() {
    }

    public static String sessionId(HttpServletRequest request) {
        Object v = request.getAttribute(SESSION_ID_ATTR);
        return v == null ? "" : v.toString();
    }

    public static String requestId(HttpServletRequest request) {
        Object v = request.getAttribute(REQUEST_ID_ATTR);
        return v == null ? "" : v.toString();
    }
}
