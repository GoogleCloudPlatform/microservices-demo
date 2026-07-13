package hipstershop.frontend.web;

import hipstershop.frontend.config.ShopProperties;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;

/** Ports {@code currentCurrency} from handlers.go. */
public final class CurrencyUtil {

    private CurrencyUtil() {
    }

    public static String currentCurrency(HttpServletRequest request, ShopProperties shopProperties) {
        if (shopProperties.isCurrencyLocked()) {
            return shopProperties.getLockedCurrency();
        }
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (Cookie c : cookies) {
                if (ShopProperties.COOKIE_CURRENCY.equals(c.getName())) {
                    return c.getValue();
                }
            }
        }
        return ShopProperties.DEFAULT_CURRENCY;
    }
}
