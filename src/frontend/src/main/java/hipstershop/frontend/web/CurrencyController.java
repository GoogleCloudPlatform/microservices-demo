package hipstershop.frontend.web;

import hipstershop.frontend.config.ShopProperties;
import hipstershop.frontend.validation.SetCurrencyPayload;
import hipstershop.frontend.validation.ValidationUtil;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Validator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

/** Ports {@code setCurrencyHandler} from handlers.go. */
@Controller
public class CurrencyController {

    private static final Logger log = LoggerFactory.getLogger(CurrencyController.class);

    private final ShopProperties shopProperties;
    private final Validator validator;
    private final ErrorRenderer errorRenderer;

    public CurrencyController(ShopProperties shopProperties, Validator validator, ErrorRenderer errorRenderer) {
        this.shopProperties = shopProperties;
        this.validator = validator;
        this.errorRenderer = errorRenderer;
    }

    @PostMapping("/setCurrency")
    public String setCurrency(
            @RequestParam(value = "currency_code", required = false, defaultValue = "") String currencyCode,
            HttpServletRequest request,
            HttpServletResponse response,
            Model model) {
        String referer = request.getHeader("referer");
        String redirectTarget = (referer == null || referer.isEmpty()) ? "/" : referer;

        if (shopProperties.isCurrencyLocked()) {
            log.debug("currency is locked via DEFAULT_CURRENCY env var; ignoring setCurrency request");
            return "redirect:" + redirectTarget;
        }

        SetCurrencyPayload payload = new SetCurrencyPayload(currencyCode);
        try {
            ValidationUtil.validate(validator, payload);
        } catch (ValidationUtil.ValidationException e) {
            return errorRenderer.render(response, model, e.getMessage(), null, 422);
        }
        log.debug("setting currency (new={})", payload.getCurrency());

        if (!payload.getCurrency().isEmpty()) {
            Cookie cookie = new Cookie(ShopProperties.COOKIE_CURRENCY, payload.getCurrency());
            cookie.setMaxAge(ShopProperties.COOKIE_MAX_AGE);
            cookie.setPath("/");
            response.addCookie(cookie);
        }
        return "redirect:" + redirectTarget;
    }
}
