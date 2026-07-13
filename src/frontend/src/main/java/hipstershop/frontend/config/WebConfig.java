package hipstershop.frontend.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * The Go frontend served static files under the URL prefix "/static/" (see
 * main.go's {@code http.StripPrefix(baseUrl+"/static/", ...)}), and other
 * services (e.g. productcatalogservice's bundled product data) return
 * picture paths like "/static/img/products/sunglasses.jpg" that assume this
 * prefix. Spring Boot's default static handler instead serves
 * classpath:/static/ at the URL root, so this explicitly maps "/static/**"
 * back to that classpath folder to keep those paths working.
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/static/**").addResourceLocations("classpath:/static/");
    }
}
