package hipstershop.frontend.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import hipstershop.Demo;
import hipstershop.frontend.config.ShopProperties;
import hipstershop.frontend.grpc.FrontendGrpcClient;
import hipstershop.frontend.packaging.PackagingClient;
import hipstershop.frontend.packaging.PackagingInfo;
import hipstershop.frontend.session.SessionContext;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.ResponseBody;

/** Ports {@code productHandler} and {@code getProductByID} from handlers.go. */
@Controller
public class ProductController {

    private static final Logger log = LoggerFactory.getLogger(ProductController.class);

    private final FrontendGrpcClient grpcClient;
    private final ShopProperties shopProperties;
    private final AdChooser adChooser;
    private final PackagingClient packagingClient;
    private final ErrorRenderer errorRenderer;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public ProductController(
            FrontendGrpcClient grpcClient,
            ShopProperties shopProperties,
            AdChooser adChooser,
            PackagingClient packagingClient,
            ErrorRenderer errorRenderer) {
        this.grpcClient = grpcClient;
        this.shopProperties = shopProperties;
        this.adChooser = adChooser;
        this.packagingClient = packagingClient;
        this.errorRenderer = errorRenderer;
    }

    @GetMapping("/product/{id}")
    public String product(
            @PathVariable("id") String id, HttpServletRequest request, HttpServletResponse response, Model model) {
        if (id == null || id.isEmpty()) {
            return errorRenderer.render(response, model, "product id not specified", null, 400);
        }
        String currentCurrency = CurrencyUtil.currentCurrency(request, shopProperties);
        log.debug("serving product page (id={}, currency={})", id, currentCurrency);

        Demo.Product p;
        try {
            p = grpcClient.getProduct(id);
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve product", e, 500);
        }

        List<String> currencies;
        try {
            currencies = grpcClient.getCurrencies();
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve currencies", e, 500);
        }

        List<Demo.CartItem> cart;
        try {
            cart = grpcClient.getCart(SessionContext.sessionId(request));
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve cart", e, 500);
        }

        Demo.Money price;
        try {
            price = grpcClient.convertCurrency(p.getPriceUsd(), currentCurrency);
        } catch (Exception e) {
            return errorRenderer.render(response, model, "failed to convert currency", e, 500);
        }

        List<Demo.Product> recommendations;
        try {
            recommendations = grpcClient.getRecommendations(SessionContext.sessionId(request), List.of(id));
        } catch (Exception e) {
            log.warn("failed to get product recommendations", e);
            recommendations = List.of();
        }

        PackagingInfo packagingInfo = null;
        if (packagingClient.isConfigured()) {
            packagingInfo = packagingClient.getPackagingInfo(id);
        }

        model.addAttribute("ad", adChooser.choose(p.getCategoriesList()));
        model.addAttribute("show_currency", true);
        model.addAttribute("currencies", currencies);
        model.addAttribute("product", new ProductView(p, price));
        model.addAttribute("recommendations", recommendations);
        model.addAttribute("cart_size", CartUtil.cartSize(cart));
        model.addAttribute("packagingInfo", packagingInfo);
        return "product";
    }

    @GetMapping("/product-meta/{ids}")
    @ResponseBody
    public ResponseEntity<byte[]> getProductByID(@PathVariable("ids") String id) {
        if (id == null || id.isEmpty()) {
            return ResponseEntity.ok().build();
        }
        Demo.Product p;
        try {
            p = grpcClient.getProduct(id);
        } catch (Exception e) {
            return ResponseEntity.ok().build();
        }
        try {
            byte[] json = objectMapper.writeValueAsBytes(toJsonMap(p));
            return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(json);
        } catch (Exception e) {
            return ResponseEntity.ok().build();
        }
    }

    private Map<String, Object> toJsonMap(Demo.Product p) {
        Map<String, Object> json = new LinkedHashMap<>();
        if (!p.getId().isEmpty()) {
            json.put("id", p.getId());
        }
        if (!p.getName().isEmpty()) {
            json.put("name", p.getName());
        }
        if (!p.getDescription().isEmpty()) {
            json.put("description", p.getDescription());
        }
        if (!p.getPicture().isEmpty()) {
            json.put("picture", p.getPicture());
        }
        if (p.hasPriceUsd()) {
            Map<String, Object> price = new LinkedHashMap<>();
            Demo.Money m = p.getPriceUsd();
            if (!m.getCurrencyCode().isEmpty()) {
                price.put("currency_code", m.getCurrencyCode());
            }
            if (m.getUnits() != 0) {
                price.put("units", m.getUnits());
            }
            if (m.getNanos() != 0) {
                price.put("nanos", m.getNanos());
            }
            json.put("price_usd", price);
        }
        if (p.getCategoriesCount() > 0) {
            json.put("categories", p.getCategoriesList());
        }
        return json;
    }
}
