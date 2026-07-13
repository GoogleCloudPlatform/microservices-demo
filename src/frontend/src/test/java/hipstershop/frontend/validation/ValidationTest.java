package hipstershop.frontend.validation;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/** Ports the key cases from the Go frontend's validator/validator_test.go. */
class ValidationTest {

    private static ValidatorFactory factory;
    private static Validator validator;

    @BeforeAll
    static void setUp() {
        factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @AfterAll
    static void tearDown() {
        factory.close();
    }

    private boolean isValid(Object payload) {
        return validator.validate(payload).isEmpty();
    }

    @Test
    void placeOrderPasses() {
        PlaceOrderPayload payload = new PlaceOrderPayload(
                "test@example.com", "12345 example street", 10004L, "New York", "New York",
                "United States", "5272940000751666", 4L, 2024L, 584L);
        assertTrue(isValid(payload));
    }

    @Test
    void placeOrderFailsInvalidEmail() {
        PlaceOrderPayload payload = new PlaceOrderPayload(
                "test@example", "12345 example street", 10004L, "New York", "New York",
                "United States", "5272940000751666", 4L, 2024L, 584L);
        assertFalse(isValid(payload));
    }

    @Test
    void placeOrderFailsAddressTooLong() {
        PlaceOrderPayload payload = new PlaceOrderPayload(
                "test@example.com", "12345 example street".repeat(513), 10004L, "New York", "New York",
                "United States", "5272940000751666", 4L, 2024L, 584L);
        assertFalse(isValid(payload));
    }

    @Test
    void placeOrderFailsZeroZipCode() {
        PlaceOrderPayload payload = new PlaceOrderPayload(
                "test@example.com", "12345 example street", 0L, "New York", "New York",
                "United States", "5272940000751666", 4L, 2024L, 584L);
        assertFalse(isValid(payload));
    }

    @Test
    void placeOrderFailsInvalidCcMonth() {
        PlaceOrderPayload payload = new PlaceOrderPayload(
                "test@example.com", "12345 example street", 10004L, "New York", "New York",
                "United States", "5272940000751666", 13L, 2024L, 584L);
        assertFalse(isValid(payload));
    }

    @Test
    void placeOrderFailsMissingCcYear() {
        PlaceOrderPayload payload = new PlaceOrderPayload(
                "test@example.com", "12345 example street", 10004L, "New York", "New York",
                "United States", "5272940000751666", 12L, 0L, 584L);
        assertFalse(isValid(payload));
    }

    @Test
    void addToCartPassesAtBounds() {
        assertTrue(isValid(new AddToCartPayload(1L, "OLJCESPC7Z")));
        assertTrue(isValid(new AddToCartPayload(10L, "OLJCESPC7Z")));
    }

    @Test
    void addToCartFailsOutOfBounds() {
        assertFalse(isValid(new AddToCartPayload(0L, "OLJCESPC7Z")));
        assertFalse(isValid(new AddToCartPayload(11L, "OLJCESPC7Z")));
        assertFalse(isValid(new AddToCartPayload(1L, "")));
    }

    @Test
    void setCurrencyPassesKnownCodes() {
        for (String code : new String[] {"EUR", "USD", "JPY", "GBP", "TRY", "CAD"}) {
            assertTrue(isValid(new SetCurrencyPayload(code)), code + " should be valid");
        }
    }

    @Test
    void setCurrencyFailsUnknownCodes() {
        assertFalse(isValid(new SetCurrencyPayload("ABC")));
        assertFalse(isValid(new SetCurrencyPayload("$")));
        assertFalse(isValid(new SetCurrencyPayload("")));
    }
}
