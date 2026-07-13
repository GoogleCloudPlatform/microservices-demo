package hipstershop.frontend.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import java.util.Currency;

public class Iso4217Validator implements ConstraintValidator<Iso4217, String> {
    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null || value.isEmpty()) {
            return false;
        }
        try {
            Currency.getInstance(value);
            return true;
        } catch (IllegalArgumentException e) {
            return false;
        }
    }
}
