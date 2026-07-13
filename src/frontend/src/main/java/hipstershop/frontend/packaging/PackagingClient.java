package hipstershop.frontend.packaging;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * As part of an optional Google Cloud demo, an additional "packaging"
 * microservice (HTTP server) can be run. This mirrors packaging_info.go.
 */
@Service
public class PackagingClient {

    private static final Logger log = LoggerFactory.getLogger(PackagingClient.class);

    private final String packagingServiceUrl;
    private final HttpClient httpClient = HttpClient.newHttpClient();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public PackagingClient(@Value("${PACKAGING_SERVICE_URL:}") String packagingServiceUrl) {
        this.packagingServiceUrl = packagingServiceUrl;
    }

    public boolean isConfigured() {
        return packagingServiceUrl != null && !packagingServiceUrl.isEmpty();
    }

    public PackagingInfo getPackagingInfo(String productId) {
        String url = packagingServiceUrl + "/" + productId;
        log.info("Requesting packaging info from URL: {}", url);
        try {
            HttpRequest request = HttpRequest.newBuilder().uri(URI.create(url)).GET().build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200) {
                log.error("Unexpected status code: {}", response.statusCode());
                return null;
            }
            return objectMapper.readValue(response.body(), PackagingInfo.class);
        } catch (Exception e) {
            log.error("Failed to obtain product's packaging info", e);
            return null;
        }
    }
}
