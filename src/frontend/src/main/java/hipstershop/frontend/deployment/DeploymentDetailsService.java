package hipstershop.frontend.deployment;

import jakarta.annotation.PostConstruct;
import java.net.InetAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * Ports deployment_details.go: best-effort lookup of the Pod's hostname plus,
 * when running on GCE/GKE, its cluster name and zone via the metadata server.
 * Runs on a background thread at startup so non-GCP deployments aren't blocked.
 */
@Service
public class DeploymentDetailsService {

    private static final Logger log = LoggerFactory.getLogger(DeploymentDetailsService.class);
    private static final String METADATA_HOST = "metadata.google.internal";
    private static final Duration TIMEOUT = Duration.ofMillis(500);

    private volatile Map<String, String> deploymentDetails = Map.of();

    @PostConstruct
    public void init() {
        Thread t = new Thread(this::loadDeploymentDetails, "deployment-details-loader");
        t.setDaemon(true);
        t.start();
    }

    public Map<String, String> getDeploymentDetails() {
        return deploymentDetails;
    }

    private void loadDeploymentDetails() {
        Map<String, String> details = new LinkedHashMap<>();
        try {
            details.put("HOSTNAME", InetAddress.getLocalHost().getHostName());
        } catch (Exception e) {
            log.error("Failed to fetch the hostname for the Pod", e);
        }

        String cluster = fetchMetadata("/computeMetadata/v1/instance/attributes/cluster-name");
        if (cluster != null) {
            details.put("CLUSTERNAME", cluster);
        }
        String zone = fetchMetadata("/computeMetadata/v1/instance/zone");
        if (zone != null) {
            // GCE returns "projects/<num>/zones/<zone>"; keep only the zone segment.
            int idx = zone.lastIndexOf('/');
            details.put("ZONE", idx >= 0 ? zone.substring(idx + 1) : zone);
        }

        this.deploymentDetails = Map.copyOf(details);
        log.debug("Loaded deployment details: {}", this.deploymentDetails);
    }

    private String fetchMetadata(String path) {
        try {
            HttpClient client = HttpClient.newBuilder().connectTimeout(TIMEOUT).build();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://" + METADATA_HOST + path))
                    .header("Metadata-Flavor", "Google")
                    .timeout(TIMEOUT)
                    .GET()
                    .build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                return response.body();
            }
            return null;
        } catch (Exception e) {
            log.error("Failed to fetch metadata: " + path, e);
            return null;
        }
    }

    public boolean isRunningOnGcp() {
        try {
            InetAddress.getAllByName(METADATA_HOST + ".");
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
