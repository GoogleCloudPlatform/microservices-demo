package hipstershop.frontend.web;

import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.ui.Model;

/** Ports {@code renderHTTPError} from handlers.go. */
@Component
public class ErrorRenderer {

    private static final Logger log = LoggerFactory.getLogger(ErrorRenderer.class);

    public String render(HttpServletResponse response, Model model, String message, Throwable cause, int code) {
        String errMsg = formatError(message, cause);
        log.error("request error: {}", errMsg);
        response.setStatus(code);
        model.addAttribute("error", errMsg);
        model.addAttribute("status_code", code);
        model.addAttribute("status", HttpStatus.valueOf(code).getReasonPhrase());
        return "error";
    }

    private String formatError(String message, Throwable cause) {
        StringBuilder sb = new StringBuilder(message);
        Throwable cur = cause;
        while (cur != null) {
            sb.append(": ").append(cur.getMessage() != null ? cur.getMessage() : cur.toString());
            cur = cur.getCause();
        }
        return sb.toString();
    }
}
