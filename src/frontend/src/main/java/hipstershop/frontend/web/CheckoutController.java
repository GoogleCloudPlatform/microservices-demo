package hipstershop.frontend.web;

import hipstershop.Hipstershop;
import hipstershop.frontend.config.ShopProperties;
import hipstershop.frontend.grpc.FrontendGrpcClient;
import hipstershop.frontend.money.Money;
import hipstershop.frontend.session.SessionContext;
import hipstershop.frontend.validation.PlaceOrderPayload;
import hipstershop.frontend.validation.ValidationUtil;
import io.grpc.Status;
import io.grpc.StatusRuntimeException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Validator;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

/** Ports {@code placeOrderHandler} from handlers.go. */
@Controller
public class CheckoutController {

    private static final Logger log = LoggerFactory.getLogger(CheckoutController.class);

    private final FrontendGrpcClient grpcClient;
    private final ShopProperties shopProperties;
    private final Validator validator;
    private final ErrorRenderer errorRenderer;
    private final MoneyFormatter moneyFormatter;

    public CheckoutController(
            FrontendGrpcClient grpcClient, ShopProperties shopProperties, Validator validator,
            ErrorRenderer errorRenderer, MoneyFormatter moneyFormatter) {
        this.grpcClient = grpcClient;
        this.shopProperties = shopProperties;
        this.validator = validator;
        this.errorRenderer = errorRenderer;
        this.moneyFormatter = moneyFormatter;
    }

    @PostMapping("/cart/checkout")
    public String placeOrder(
            @RequestParam(value = "email", required = false, defaultValue = "") String email,
            @RequestParam(value = "street_address", required = false, defaultValue = "") String streetAddress,
            @RequestParam(value = "zip_code", required = false, defaultValue = "") String zipCodeRaw,
            @RequestParam(value = "city", required = false, defaultValue = "") String city,
            @RequestParam(value = "state", required = false, defaultValue = "") String state,
            @RequestParam(value = "country", required = false, defaultValue = "") String country,
            @RequestParam(value = "credit_card_number", required = false, defaultValue = "") String ccNumber,
            @RequestParam(value = "credit_card_expiration_month", required = false, defaultValue = "") String ccMonthRaw,
            @RequestParam(value = "credit_card_expiration_year", required = false, defaultValue = "") String ccYearRaw,
            @RequestParam(value = "credit_card_cvv", required = false, defaultValue = "") String ccCvvRaw,
            @RequestParam(value = "coupon_code", required = false, defaultValue = "") String couponCodeRaw,
            HttpServletRequest request,
            HttpServletResponse response,
            Model model) {
        log.debug("placing order");

        long zipCode = parseLongOrZero(zipCodeRaw);
        long ccMonth = parseLongOrZero(ccMonthRaw);
        long ccYear = parseLongOrZero(ccYearRaw);
        long ccCvv = parseLongOrZero(ccCvvRaw);
        String couponCode = couponCodeRaw.trim().toUpperCase();

        if (!couponCode.isEmpty()) {
            ShopProperties.CouponDef couponDef = ShopProperties.COUPON_DEFS.get(couponCode);
            if (couponDef == null) {
                return "redirect:/cart?coupon_error=Invalid+coupon+code+%22" + couponCode
                        + "%22.+Please+try+again.&coupon_code=" + couponCode;
            }
            String currentCurrency = CurrencyUtil.currentCurrency(request, shopProperties);
            long orderSubtotal;
            try {
                orderSubtotal = getOrderSubtotal(request, currentCurrency);
            } catch (Exception e) {
                return errorRenderer.render(response, model, "could not verify coupon eligibility", e, 500);
            }
            // minOrderUsd is compared as a flat number directly against the shopper's real,
            // currency-converted cart total (what's actually displayed on the page) — no
            // conversion of the threshold itself, matching the cart page's
            // "Save X off orders above Y" hint text.
            if (orderSubtotal < couponDef.minOrderUsd()) {
                String currencyLogo = moneyFormatter.renderCurrencyLogo(currentCurrency);
                return "redirect:/cart?coupon_error=Coupon+code+%22" + couponCode + "%22+requires+an+order+of+at+least+"
                        + urlEncode(currencyLogo) + couponDef.minOrderUsd() + ".+Please+try+again.&coupon_code=" + couponCode;
            }
        }

        PlaceOrderPayload payload = new PlaceOrderPayload(
                email, streetAddress, zipCode, city, state, country, ccNumber, ccMonth, ccYear, ccCvv);
        try {
            ValidationUtil.validate(validator, payload);
        } catch (ValidationUtil.ValidationException e) {
            return errorRenderer.render(response, model, e.getMessage(), null, 422);
        }

        Hipstershop.PlaceOrderRequest orderRequest = Hipstershop.PlaceOrderRequest.newBuilder()
                .setEmail(payload.getEmail())
                .setCreditCard(Hipstershop.CreditCardInfo.newBuilder()
                        .setCreditCardNumber(payload.getCcNumber())
                        .setCreditCardExpirationMonth((int) (long) payload.getCcMonth())
                        .setCreditCardExpirationYear((int) (long) payload.getCcYear())
                        .setCreditCardCvv((int) (long) payload.getCcCvv())
                        .build())
                .setUserId(SessionContext.sessionId(request))
                .setUserCurrency(CurrencyUtil.currentCurrency(request, shopProperties))
                .setAddress(Hipstershop.Address.newBuilder()
                        .setStreetAddress(payload.getStreetAddress())
                        .setCity(payload.getCity())
                        .setState(payload.getState())
                        .setZipCode((int) (long) payload.getZipCode())
                        .setCountry(payload.getCountry())
                        .build())
                .setCouponCode(couponCode)
                .build();

        Hipstershop.PlaceOrderResponse order;
        try {
            order = grpcClient.placeOrder(orderRequest);
        } catch (StatusRuntimeException e) {
            if (!couponCode.isEmpty()) {
                Status status = e.getStatus();
                if (status.getCode() == Status.Code.FAILED_PRECONDITION || status.getCode() == Status.Code.INVALID_ARGUMENT) {
                    return "redirect:/cart?coupon_error="
                            + urlEncode(status.getDescription()) + "&coupon_code=" + urlEncode(couponCode);
                }
            }
            return errorRenderer.render(response, model, "failed to complete the order", e, 500);
        } catch (Exception e) {
            return errorRenderer.render(response, model, "failed to complete the order", e, 500);
        }
        log.info("order placed (order_id={})", order.getOrder().getOrderId());

        List<Hipstershop.Product> recommendations;
        try {
            recommendations = grpcClient.getRecommendations(SessionContext.sessionId(request), null);
        } catch (Exception e) {
            recommendations = List.of();
        }

        Hipstershop.Money totalPaid = order.getOrder().getShippingCost();
        List<LineItemView> orderItems = new ArrayList<>(order.getOrder().getItemsCount());
        for (Hipstershop.OrderItem v : order.getOrder().getItemsList()) {
            Hipstershop.Money multPrice = Money.multiplySlow(v.getCost(), v.getItem().getQuantity());
            totalPaid = Money.sum(totalPaid, multPrice);

            Hipstershop.Product p;
            try {
                p = grpcClient.getProduct(v.getItem().getProductId());
            } catch (Exception e) {
                return errorRenderer.render(
                        response, model, "could not retrieve product #" + v.getItem().getProductId(), e, 500);
            }
            orderItems.add(new LineItemView(p, v.getItem().getQuantity(), multPrice));
        }

        Hipstershop.Money discount = order.getOrder().hasDiscountAmount() ? order.getOrder().getDiscountAmount() : null;
        if (discount != null && discount.getUnits() > 0) {
            Hipstershop.Money negativeDiscount = Hipstershop.Money.newBuilder()
                    .setCurrencyCode(discount.getCurrencyCode())
                    .setUnits(-discount.getUnits())
                    .setNanos(-discount.getNanos())
                    .build();
            try {
                Hipstershop.Money newTotal = Money.sum(totalPaid, negativeDiscount);
                if (newTotal.getUnits() >= 0) {
                    totalPaid = newTotal;
                } else {
                    totalPaid = Hipstershop.Money.newBuilder().setCurrencyCode(discount.getCurrencyCode()).build();
                }
            } catch (Exception e) {
                totalPaid = Hipstershop.Money.newBuilder().setCurrencyCode(discount.getCurrencyCode()).build();
            }
        }

        List<String> currencies;
        try {
            currencies = grpcClient.getCurrencies();
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve currencies", e, 500);
        }

        // Only surface the "Coupon Discount" row when the shopper actually typed a code —
        // a silently-defaulted coupon still reduces total_paid above, but stays invisible
        // in the UI since the shopper never asked for it.
        Hipstershop.Money discountAmount = null;
        String couponCodeUsed = "";
        if (!couponCode.isEmpty()) {
            discountAmount = order.getOrder().getDiscountAmount();
            couponCodeUsed = order.getOrder().getCouponCodeUsed();
        }

        model.addAttribute("show_currency", false);
        model.addAttribute("currencies", currencies);
        model.addAttribute("order", order.getOrder());
        model.addAttribute("order_items", orderItems);
        model.addAttribute("total_paid", totalPaid);
        model.addAttribute("recommendations", recommendations);
        model.addAttribute("discount_amount", discountAmount);
        model.addAttribute("coupon_code_used", couponCodeUsed);
        return "order";
    }

    /** Cart items' price plus shipping cost, converted into the shopper's current currency. */
    private long getOrderSubtotal(HttpServletRequest request, String currency) {
        List<Hipstershop.CartItem> cart = grpcClient.getCart(SessionContext.sessionId(request));
        Hipstershop.Money subtotal = Hipstershop.Money.newBuilder().setCurrencyCode(currency).build();
        for (Hipstershop.CartItem item : cart) {
            Hipstershop.Product p = grpcClient.getProduct(item.getProductId());
            Hipstershop.Money price = grpcClient.convertCurrency(p.getPriceUsd(), currency);
            subtotal = Money.sum(subtotal, Money.multiplySlow(price, item.getQuantity()));
        }
        subtotal = Money.sum(subtotal, grpcClient.getShippingQuote(cart, currency));
        return subtotal.getUnits();
    }

    private long parseLongOrZero(String raw) {
        try {
            return Long.parseLong(raw);
        } catch (Exception e) {
            return 0;
        }
    }

    private String urlEncode(String s) {
        return s == null ? "" : URLEncoder.encode(s, StandardCharsets.UTF_8);
    }
}
