package hipstershop.frontend.web;

import hipstershop.frontend.config.ShopProperties;
import hipstershop.frontend.deployment.DeploymentDetailsService;
import hipstershop.frontend.session.SessionContext;
import jakarta.servlet.http.HttpServletRequest;
import java.time.Year;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

/** Ports {@code injectCommonTemplateData} from handlers.go. */
@ControllerAdvice(basePackages = "hipstershop.frontend.web")
public class GlobalModelAttributes {

    private final ShopProperties shopProperties;
    private final DeploymentDetailsService deploymentDetailsService;
    private final PlatformDetailsHolder platformDetailsHolder;
    private final MoneyFormatter moneyFormatter;

    public GlobalModelAttributes(
            ShopProperties shopProperties,
            DeploymentDetailsService deploymentDetailsService,
            PlatformDetailsHolder platformDetailsHolder,
            MoneyFormatter moneyFormatter) {
        this.shopProperties = shopProperties;
        this.deploymentDetailsService = deploymentDetailsService;
        this.platformDetailsHolder = platformDetailsHolder;
        this.moneyFormatter = moneyFormatter;
    }

    @ModelAttribute
    public void addCommonAttributes(Model model, HttpServletRequest request) {
        PlatformDetails plat = platformDetailsHolder.get();
        model.addAttribute("session_id", SessionContext.sessionId(request));
        model.addAttribute("request_id", SessionContext.requestId(request));
        model.addAttribute("user_currency", CurrencyUtil.currentCurrency(request, shopProperties));
        model.addAttribute("currency_locked", shopProperties.isCurrencyLocked());
        model.addAttribute("platform_css", plat.css());
        model.addAttribute("platform_name", plat.provider());
        model.addAttribute("is_cymbal_brand", shopProperties.isCymbalBrand());
        model.addAttribute("assistant_enabled", shopProperties.isAssistantEnabled());
        model.addAttribute("deploymentDetails", deploymentDetailsService.getDeploymentDetails());
        model.addAttribute("frontendMessage", shopProperties.getFrontendMessage());
        model.addAttribute("currentYear", Year.now().getValue());
        model.addAttribute("baseUrl", shopProperties.getBaseUrl());
        model.addAttribute("moneyFormatter", moneyFormatter);
    }
}
