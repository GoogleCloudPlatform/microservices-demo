package hipstershop.frontend.validation;

import jakarta.validation.constraints.NotBlank;

/** Mirrors the Go frontend's {@code validator.SetCurrencyPayload}. */
public class SetCurrencyPayload {

    @NotBlank
    @Iso4217
    private String currency;

    public SetCurrencyPayload(String currency) {
        this.currency = currency;
    }

    public String getCurrency() {
        return currency;
    }
}
