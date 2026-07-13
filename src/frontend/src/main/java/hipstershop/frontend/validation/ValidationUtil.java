package hipstershop.frontend.validation;

import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validator;
import java.util.Set;

/**
 * Validates a payload and, on failure, builds an error message in the same
 * shape as the Go frontend's {@code validator.ValidationErrorResponse}
 * ("Field '&lt;field&gt;' is invalid: &lt;rule&gt;" per violation).
 */
public final class ValidationUtil {

    private ValidationUtil() {
    }

    public static <T> void validate(Validator validator, T payload) {
        Set<ConstraintViolation<T>> violations = validator.validate(payload);
        if (violations.isEmpty()) {
            return;
        }
        StringBuilder sb = new StringBuilder();
        for (ConstraintViolation<T> violation : violations) {
            sb.append("Field '")
                    .append(violation.getPropertyPath())
                    .append("' is invalid: ")
                    .append(violation.getMessage())
                    .append('\n');
        }
        throw new ValidationException(sb.toString());
    }

    public static class ValidationException extends RuntimeException {
        public ValidationException(String message) {
            super(message);
        }
    }
}
