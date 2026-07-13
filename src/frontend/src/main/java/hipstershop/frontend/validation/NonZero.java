package hipstershop.frontend.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Mirrors go-playground/validator's "required" tag applied to a numeric field:
 * the value must be present and not equal to zero (unlike Bean Validation's
 * {@code @NotNull}, which only rejects null).
 */
@Target({ElementType.FIELD, ElementType.METHOD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = NonZeroValidator.class)
public @interface NonZero {
    String message() default "must be required";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};
}
