package hipstershop.frontend.web;

import hipstershop.Demo;
import hipstershop.frontend.grpc.FrontendGrpcClient;
import java.util.List;
import java.util.Random;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/** Ports {@code chooseAd} from handlers.go. */
@Component
public class AdChooser {

    private static final Logger log = LoggerFactory.getLogger(AdChooser.class);

    private final FrontendGrpcClient grpcClient;
    private final Random random = new Random();

    public AdChooser(FrontendGrpcClient grpcClient) {
        this.grpcClient = grpcClient;
    }

    public Demo.Ad choose(List<String> contextKeys) {
        try {
            List<Demo.Ad> ads = grpcClient.getAd(contextKeys);
            if (ads.isEmpty()) {
                return null;
            }
            return ads.get(random.nextInt(ads.size()));
        } catch (Exception e) {
            log.warn("failed to retrieve ads", e);
            return null;
        }
    }
}
