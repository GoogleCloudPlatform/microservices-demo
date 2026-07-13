package hipstershop.frontend.web;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import hipstershop.frontend.grpc.FrontendGrpcClient;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;

/** Ports {@code assistantHandler}/{@code chatBotHandler} from handlers.go. */
@Controller
public class AssistantController {

    private static final Logger log = LoggerFactory.getLogger(AssistantController.class);

    private final FrontendGrpcClient grpcClient;
    private final ErrorRenderer errorRenderer;
    private final HttpClient httpClient = HttpClient.newHttpClient();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${SHOPPING_ASSISTANT_SERVICE_ADDR}")
    private String shoppingAssistantSvcAddr;

    public AssistantController(FrontendGrpcClient grpcClient, ErrorRenderer errorRenderer) {
        this.grpcClient = grpcClient;
        this.errorRenderer = errorRenderer;
    }

    @GetMapping("/assistant")
    public String assistant(HttpServletRequest request, HttpServletResponse response, Model model) {
        List<String> currencies;
        try {
            currencies = grpcClient.getCurrencies();
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve currencies", e, 500);
        }
        model.addAttribute("show_currency", false);
        model.addAttribute("currencies", currencies);
        return "assistant";
    }

    @PostMapping("/bot")
    @ResponseBody
    public ResponseEntity<Map<String, String>> chatBot(@RequestBody(required = false) String body) {
        try {
            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create("http://" + shoppingAssistantSvcAddr))
                    .header("Content-Type", "application/json")
                    .header("Accept", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(body == null ? "" : body))
                    .build();
            HttpResponse<String> res = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
            JsonNode json = objectMapper.readTree(res.body());
            String content = json.has("content") ? json.get("content").asText() : "";
            return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(Map.of("message", content));
        } catch (Exception e) {
            log.error("shopping assistant proxy failed", e);
            return ResponseEntity.internalServerError().build();
        }
    }
}
