package hipstershop.frontend.web;

import hipstershop.Demo;
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

    public CheckoutController(
            FrontendGrpcClient grpcClient, ShopProperties shopProperties, Validator validator,
            ErrorRenderer errorRenderer) {
        this.grpcClient = grpcClient;
        this.shopProperties = shopProperties;
        this.validator = validator;
        this.errorRenderer = errorRenderer;
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

        if (!couponCode.isEmpty() && !ShopProperties.COUPON_DEFS.containsKey(couponCode)) {
            return "redirect:/cart?coupon_error=Invalid+coupon+code+%22" + couponCode
                    + "%22.+Please+try+again.&coupon_code=" + couponCode;
        }

        PlaceOrderPayload payload = new PlaceOrderPayload(
                email, streetAddress, zipCode, city, state, country, ccNumber, ccMonth, ccYear, ccCvv);
        try {
            ValidationUtil.validate(validator, payload);
        } catch (ValidationUtil.ValidationException e) {
            return errorRenderer.render(response, model, e.getMessage(), null, 422);
        }

        Demo.PlaceOrderRequest orderRequest = Demo.PlaceOrderRequest.newBuilder()
                .setEmail(payload.getEmail())
                .setCreditCard(Demo.CreditCardInfo.newBuilder()
                        .setCreditCardNumber(payload.getCcNumber())
                        .setCreditCardExpirationMonth((int) (long) payload.getCcMonth())
                        .setCreditCardExpirationYear((int) (long) payload.getCcYear())
                        .setCreditCardCvv((int) (long) payload.getCcCvv())
                        .build())
                .setUserId(SessionContext.sessionId(request))
                .setUserCurrency(CurrencyUtil.currentCurrency(request, shopProperties))
                .setAddress(Demo.Address.newBuilder()
                        .setStreetAddress(payload.getStreetAddress())
                        .setCity(payload.getCity())
                        .setState(payload.getState())
                        .setZipCode((int) (long) payload.getZipCode())
                        .setCountry(payload.getCountry())
                        .build())
                .setCouponCode(couponCode)
                .build();

        Demo.PlaceOrderResponse order;
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

        List<Demo.Product> recommendations;
        try {
            recommendations = grpcClient.getRecommendations(SessionContext.sessionId(request), null);
        } catch (Exception e) {
            recommendations = List.of();
        }

        Demo.Money totalPaid = order.getOrder().getShippingCost();
        List<LineItemView> orderItems = new ArrayList<>(order.getOrder().getItemsCount());
        for (Demo.OrderItem v : order.getOrder().getItemsList()) {
            Demo.Money multPrice = Money.multiplySlow(v.getCost(), v.getItem().getQuantity());
            totalPaid = Money.sum(totalPaid, multPrice);

            Demo.Product p;
            try {
                p = grpcClient.getProduct(v.getItem().getProductId());
            } catch (Exception e) {
                return errorRenderer.render(
                        response, model, "could not retrieve product #" + v.getItem().getProductId(), e, 500);
            }
            orderItems.add(new LineItemView(p, v.getItem().getQuantity(), multPrice));
        }

        Demo.Money discount = order.getOrder().hasDiscountAmount() ? order.getOrder().getDiscountAmount() : null;
        if (discount != null && discount.getUnits() > 0) {
            Demo.Money negativeDiscount = Demo.Money.newBuilder()
                    .setCurrencyCode(discount.getCurrencyCode())
                    .setUnits(-discount.getUnits())
                    .setNanos(-discount.getNanos())
                    .build();
            try {
                Demo.Money newTotal = Money.sum(totalPaid, negativeDiscount);
                if (newTotal.getUnits() >= 0) {
                    totalPaid = newTotal;
                } else {
                    totalPaid = Demo.Money.newBuilder().setCurrencyCode(discount.getCurrencyCode()).build();
                }
            } catch (Exception e) {
                totalPaid = Demo.Money.newBuilder().setCurrencyCode(discount.getCurrencyCode()).build();
            }
        }

        List<String> currencies;
        try {
            currencies = grpcClient.getCurrencies();
        } catch (Exception e) {
            return errorRenderer.render(response, model, "could not retrieve currencies", e, 500);
        }

        Demo.Money discountAmount = null;
        String couponCodeUsed = "";
        long couponDiscountDisplay = 0;
        if (!couponCode.isEmpty()) {
            discountAmount = order.getOrder().getDiscountAmount();
            couponCodeUsed = order.getOrder().getCouponCodeUsed();
            // Show the coupon's flat face value (e.g. "10") rather than the real
            // currency-converted amount actually deducted, matching the cart page's
            // coupon hint text and keeping the exact discount amount private.
            ShopProperties.CouponDef def = ShopProperties.COUPON_DEFS.get(couponCodeUsed);
            if (def != null) {
                couponDiscountDisplay = def.discountUsd();
            }
        }

        model.addAttribute("show_currency", false);
        model.addAttribute("currencies", currencies);
        model.addAttribute("order", order.getOrder());
        model.addAttribute("order_items", orderItems);
        model.addAttribute("total_paid", totalPaid);
        model.addAttribute("recommendations", recommendations);
        model.addAttribute("discount_amount", discountAmount);
        model.addAttribute("coupon_code_used", couponCodeUsed);
        model.addAttribute("coupon_discount_display", couponDiscountDisplay);
        return "order";
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
