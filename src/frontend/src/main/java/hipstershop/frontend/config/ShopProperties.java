package hipstershop.frontend.config;

import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Application-wide constants and env-derived settings, mirroring the
 * package-level state the Go frontend keeps in main.go/handlers.go.
 */
@Component
public class ShopProperties {

    public static final String DEFAULT_CURRENCY = "USD";
    public static final int COOKIE_MAX_AGE = 60 * 60 * 48;
    public static final String COOKIE_PREFIX = "shop_";
    public static final String COOKIE_SESSION_ID = COOKIE_PREFIX + "session-id";
    public static final String COOKIE_CURRENCY = COOKIE_PREFIX + "currency";

    public static final List<String> VALID_ENVS = List.of("local", "gcp", "azure", "aws", "onprem", "alibaba");

    public record CouponDef(long discountUsd, long minOrderUsd) {
    }

    public static final List<String> COUPON_ORDER = List.of("SAVE10", "SAVE50", "SAVE100");

    public static final Map<String, CouponDef> COUPON_DEFS = Map.of(
            "SAVE10", new CouponDef(10, 50),
            "SAVE50", new CouponDef(50, 200),
            "SAVE100", new CouponDef(100, 350));

    // CAD is deliberately excluded: it shares the "$" symbol with USD, which caused
    // confusing coupon/total displays that looked like they were in USD but weren't.
    private final Set<String> whitelistedCurrencies = new LinkedHashSet<>(
            Set.of("USD", "EUR", "JPY", "GBP", "TRY"));

    private String baseUrl;
    private String lockedCurrency;
    private String frontendMessage;
    private boolean cymbalBrand;
    private boolean assistantEnabled;
    private boolean singleSharedSession;

    public ShopProperties(
            @Value("${BASE_URL:}") String baseUrl,
            @Value("${DEFAULT_CURRENCY:}") String defaultCurrencyEnv,
            @Value("${FRONTEND_MESSAGE:}") String frontendMessage,
            @Value("${CYMBAL_BRANDING:}") String cymbalBranding,
            @Value("${ENABLE_ASSISTANT:}") String enableAssistant,
            @Value("${ENABLE_SINGLE_SHARED_SESSION:}") String enableSingleSharedSession) {
        this.baseUrl = baseUrl;
        if (defaultCurrencyEnv != null && !defaultCurrencyEnv.isEmpty()) {
            this.lockedCurrency = defaultCurrencyEnv;
            this.whitelistedCurrencies.add(defaultCurrencyEnv);
        } else {
            this.lockedCurrency = "";
        }
        this.frontendMessage = frontendMessage == null ? "" : frontendMessage.trim();
        this.cymbalBrand = "true".equalsIgnoreCase(cymbalBranding);
        this.assistantEnabled = "true".equalsIgnoreCase(enableAssistant);
        this.singleSharedSession = "true".equalsIgnoreCase(enableSingleSharedSession);
    }

    public Set<String> getWhitelistedCurrencies() {
        return whitelistedCurrencies;
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public String getLockedCurrency() {
        return lockedCurrency;
    }

    public boolean isCurrencyLocked() {
        return lockedCurrency != null && !lockedCurrency.isEmpty();
    }

    public String getFrontendMessage() {
        return frontendMessage;
    }

    public boolean isCymbalBrand() {
        return cymbalBrand;
    }

    public boolean isAssistantEnabled() {
        return assistantEnabled;
    }

    public boolean isSingleSharedSession() {
        return singleSharedSession;
    }
}
