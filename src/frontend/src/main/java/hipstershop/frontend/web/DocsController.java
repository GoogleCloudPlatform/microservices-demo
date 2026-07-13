package hipstershop.frontend.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * Convenience redirects so the doc URLs the Go frontend used
 * ({@code /swagger/}, {@code /swagger.json}) keep working, backed by
 * springdoc-openapi's generated spec and Swagger UI.
 */
@Controller
public class DocsController {

    @GetMapping("/swagger.json")
    public String swaggerJson() {
        return "redirect:/v3/api-docs";
    }

    @GetMapping("/swagger/")
    public String swaggerUi() {
        return "redirect:/swagger-ui.html";
    }
}
