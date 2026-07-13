package hipstershop.frontend.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import org.springframework.context.annotation.Configuration;

/** Mirrors the @title/@version/@description/@BasePath godoc annotations in the Go frontend's main.go. */
@Configuration
@OpenAPIDefinition(info = @Info(
        title = "Hipster Shop Frontend API",
        version = "1.0",
        description = "Frontend service for Google Microservices Demo."))
public class OpenApiConfig {
}
