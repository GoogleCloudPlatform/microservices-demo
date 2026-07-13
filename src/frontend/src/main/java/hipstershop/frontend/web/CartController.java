package hipstershop.frontend.web;

import hipstershop.Demo;
import hipstershop.frontend.config.ShopProperties;
import hipstershop.frontend.grpc.FrontendGrpcClient;
import hipstershop.frontend.money.Money;
import hipstershop.frontend.session.SessionContext;
import hipstershop.frontend.validation.AddToCartPayload;
import hipstershop.frontend.validation.ValidationUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Validator;
import java.time.Year;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

/** Ports {@code viewCartHandler}/{@code addToCartHandler}/{@code emptyCartHandler} from handlers.go. */
@Controller
public class CartController {

    private static final Logger log = LoggerFactory.getLogger(CartController.class);

    private final FrontendGrpcClient grpcClient;
    private final ShopProperties shopProperties;
    private final Validator validator;
    private final ErrorRenderer errorRenderer;

    public CartController(
            FrontendGrpcClient grpcClient, ShopProperties shopProperties, Validator validator,
            ErrorRenderer errorRenderer) {
        this.grpcClient = grpcClient;
        this.shopProperties = shopProperties;
        this.validator = validator;
        this.errorRenderer = errorRenderer;
    }

    @GetMapping("/cart")
    public String viewCart(
            @RequestParam(value = "coupon_error", required = false, defaultValue = "") String couponError,
            @RequestParam(value = "coupon_code", required = false, defaultValue = "") String lastCoupon,
            HttpServletRequest request,
            HttpServletResponse response,
            Model model) {
        log.debug("view user cart");
        String currentCurrency = CurrencyUtil.currentCurrency(request, shopProperties);

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

        List<Demo.Product> recommendations;
        try {
            recommendations = grpcClient.getRecommendations(SessionContext.sessionId(request), CartUtil.cartIds(cart));
        } catch (Exception e) {
            log.warn("failed to get product recommendations", e);
            recommendations = List.of();
        }

        Demo.Money shippingCost;
        try {
            shippingCost = grpcClient.getShippingQuote(cart, currentCurrency);
        } catch (Exception e) {
            return errorRenderer.render(response, model, "failed to get shipping quote", e, 500);
        }

        List<LineItemView> items = new ArrayList<>(cart.size());
        Demo.Money totalPrice = Demo.Money.newBuilder().setCurrencyCode(currentCurrency).build();
        for (Demo.CartItem item : cart) {
            Demo.Product p;
            try {
                p = grpcClient.getProduct(item.getProductId());
            } catch (Exception e) {
                return errorRenderer.render(
                        response, model, "could not retrieve product #" + item.getProductId(), e, 500);
            }
            Demo.Money price;
            try {
                price = grpcClient.convertCurrency(p.getPriceUsd(), currentCurrency);
            } catch (Exception e) {
                return errorRenderer.render(
                        response, model, "could not convert currency for product #" + item.getProductId(), e, 500);
            }
            Demo.Money multPrice = Money.multiplySlow(price, item.getQuantity());
            items.add(new LineItemView(p, item.getQuantity(), multPrice));
            totalPrice = Money.sum(totalPrice, multPrice);
        }
        totalPrice = Money.sum(totalPrice, shippingCost);
        int year = Year.now().getValue();

        List<CouponOptionView> couponOptions = new ArrayList<>();
        for (String code : ShopProperties.COUPON_ORDER) {
            ShopProperties.CouponDef def = ShopProperties.COUPON_DEFS.get(code);
            couponOptions.add(new CouponOptionView(code, def.discountUsd(), def.minOrderUsd()));
        }

        model.addAttribute("currencies", currencies);
        model.addAttribute("recommendations", recommendations);
        model.addAttribute("cart_size", CartUtil.cartSize(cart));
        model.addAttribute("shipping_cost", shippingCost);
        model.addAttribute("show_currency", true);
        model.addAttribute("total_cost", totalPrice);
        model.addAttribute("items", items);
        model.addAttribute("expiration_years", List.of(year, year + 1, year + 2, year + 3, year + 4));
        model.addAttribute("coupon_error", couponError);
        model.addAttribute("last_coupon", lastCoupon);
        model.addAttribute("coupon_options", couponOptions);
        return "cart";
    }

    @PostMapping("/cart")
    public String addToCart(
            @RequestParam(value = "quantity", required = false, defaultValue = "") String quantityRaw,
            @RequestParam(value = "product_id", required = false, defaultValue = "") String productId,
            HttpServletRequest request,
            HttpServletResponse response,
            Model model) {
        long quantity = parseUnsignedLongOrZero(quantityRaw);
        AddToCartPayload payload = new AddToCartPayload(quantity, productId);
        try {
            ValidationUtil.validate(validator, payload);
        } catch (ValidationUtil.ValidationException e) {
            return errorRenderer.render(response, model, e.getMessage(), null, 422);
        }
        log.debug("adding to cart (product={}, quantity={})", payload.getProductId(), payload.getQuantity());

        Demo.Product p;
        try {
            p = grpcClient.getProduct(payload.getProductId());
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve product", e, 500);
        }

        try {
            grpcClient.insertCart(
                    SessionContext.sessionId(request), p.getId(), (int) (long) payload.getQuantity());
        } catch (Exception e) {
            return errorRenderer.render(response, model, "failed to add to cart", e, 500);
        }
        return "redirect:/cart";
    }

    @PostMapping("/cart/empty")
    public String emptyCart(HttpServletRequest request, HttpServletResponse response, Model model) {
        log.debug("emptying cart");
        try {
            grpcClient.emptyCart(SessionContext.sessionId(request));
        } catch (Exception e) {
            return errorRenderer.render(response, model, "failed to empty cart", e, 500);
        }
        return "redirect:/";
    }

    private long parseUnsignedLongOrZero(String raw) {
        try {
            long v = Long.parseLong(raw);
            return v < 0 ? 0 : v;
        } catch (Exception e) {
            return 0;
        }
    }

    public static class CouponOptionView {
        private final String code;
        private final long discountUsd;
        private final long minOrderUsd;

        public CouponOptionView(String code, long discountUsd, long minOrderUsd) {
            this.code = code;
            this.discountUsd = discountUsd;
            this.minOrderUsd = minOrderUsd;
        }

        public String getCode() {
            return code;
        }

        public long getDiscountUsd() {
            return discountUsd;
        }

        public long getMinOrderUsd() {
            return minOrderUsd;
        }
    }
}
