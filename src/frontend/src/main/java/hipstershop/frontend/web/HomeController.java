package hipstershop.frontend.web;

import hipstershop.Hipstershop;
import hipstershop.frontend.config.ShopProperties;
import hipstershop.frontend.deployment.DeploymentDetailsService;
import hipstershop.frontend.grpc.FrontendGrpcClient;
import hipstershop.frontend.session.SessionContext;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

/** Ports {@code homeHandler} from handlers.go. */
@Controller
public class HomeController {

    private static final Logger log = LoggerFactory.getLogger(HomeController.class);

    private final FrontendGrpcClient grpcClient;
    private final ShopProperties shopProperties;
    private final DeploymentDetailsService deploymentDetailsService;
    private final PlatformDetailsHolder platformDetailsHolder;
    private final AdChooser adChooser;
    private final ErrorRenderer errorRenderer;

    @Value("${ENV_PLATFORM:}")
    private String envPlatformOverride;

    @Value("${BANNER_COLOR:}")
    private String bannerColor;

    public HomeController(
            FrontendGrpcClient grpcClient,
            ShopProperties shopProperties,
            DeploymentDetailsService deploymentDetailsService,
            PlatformDetailsHolder platformDetailsHolder,
            AdChooser adChooser,
            ErrorRenderer errorRenderer) {
        this.grpcClient = grpcClient;
        this.shopProperties = shopProperties;
        this.deploymentDetailsService = deploymentDetailsService;
        this.platformDetailsHolder = platformDetailsHolder;
        this.adChooser = adChooser;
        this.errorRenderer = errorRenderer;
    }

    @GetMapping("/")
    public String home(HttpServletRequest request, HttpServletResponse response, Model model) {
        String currentCurrency = CurrencyUtil.currentCurrency(request, shopProperties);
        log.info("home (currency={})", currentCurrency);

        List<String> currencies;
        try {
            currencies = grpcClient.getCurrencies();
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve currencies", e, 500);
        }

        List<Hipstershop.Product> products;
        try {
            products = grpcClient.getProducts();
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve products", e, 500);
        }

        List<Hipstershop.CartItem> cart;
        try {
            cart = grpcClient.getCart(SessionContext.sessionId(request));
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve cart", e, 500);
        }

        List<ProductView> productViews = new ArrayList<>(products.size());
        for (Hipstershop.Product p : products) {
            Hipstershop.Money price;
            try {
                price = grpcClient.convertCurrency(p.getPriceUsd(), currentCurrency);
            } catch (Exception e) {
                return errorRenderer.render(
                        response, model, "failed to do currency conversion for product " + p.getId(), e, 500);
            }
            productViews.add(new ProductView(p, price));
        }

        String env = envPlatformOverride;
        if (env == null || env.isEmpty() || !ShopProperties.VALID_ENVS.contains(env)) {
            env = "local";
        }
        if (deploymentDetailsService.isRunningOnGcp()) {
            env = "gcp";
        }
        platformDetailsHolder.set(PlatformDetails.forEnv(env.toLowerCase()));

        model.addAttribute("show_currency", true);
        model.addAttribute("currencies", currencies);
        model.addAttribute("products", productViews);
        model.addAttribute("cart_size", CartUtil.cartSize(cart));
        model.addAttribute("banner_color", bannerColor);
        model.addAttribute("ad", adChooser.choose(List.of()));
        return "home";
    }
}
