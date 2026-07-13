package hipstershop.frontend.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/** Mirrors go-playground/validator's "iso4217" tag: value must be a known ISO 4217 currency code. */
@Target({ElementType.FIELD, ElementType.METHOD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = Iso4217Validator.class)
public @interface Iso4217 {
    String message() default "must be a valid ISO 4217 currency code";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};
}
