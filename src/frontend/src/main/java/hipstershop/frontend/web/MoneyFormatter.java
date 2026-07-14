package hipstershop.frontend.web;

import hipstershop.Hipstershop;
import java.util.Map;
import org.springframework.stereotype.Component;

/** Ports {@code renderMoney}/{@code renderCurrencyLogo} template funcs from handlers.go. */
@Component("moneyFormatter")
public class MoneyFormatter {

    private static final Map<String, String> LOGOS = Map.of(
            "USD", "$",
            "CAD", "$",
            "JPY", "¥",
            "EUR", "€",
            "TRY", "₺",
            "GBP", "£");

    public String renderMoney(Hipstershop.Money money) {
        String logo = renderCurrencyLogo(money.getCurrencyCode());
        // Matches the Go implementation exactly: integer division of nanos by 1e7 (not rounded).
        return String.format("%s%d.%02d", logo, money.getUnits(), money.getNanos() / 10000000);
    }

    public String renderCurrencyLogo(String currencyCode) {
        return LOGOS.getOrDefault(currencyCode, "$");
    }
}
