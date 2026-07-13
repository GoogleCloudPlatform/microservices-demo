package hipstershop.frontend.validation;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import org.hibernate.validator.constraints.CreditCardNumber;

/** Mirrors the Go frontend's {@code validator.PlaceOrderPayload}. */
public class PlaceOrderPayload {

    // Hibernate Validator's default @Email accepts domains without a TLD (e.g. "a@b"),
    // unlike go-playground/validator's "email" tag; the extra pattern requires a dot
    // in the domain part so validation behavior matches the Go frontend.
    @NotBlank
    @Email
    @Pattern(regexp = "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")
    private String email;

    @NotBlank
    @Size(max = 512)
    private String streetAddress;

    @NotNull
    @NonZero
    private Long zipCode;

    @NotBlank
    @Size(max = 128)
    private String city;

    @NotBlank
    @Size(max = 128)
    private String state;

    @NotBlank
    @Size(max = 128)
    private String country;

    @NotBlank
    @CreditCardNumber
    private String ccNumber;

    @NotNull
    @Min(1)
    @Max(12)
    private Long ccMonth;

    @NotNull
    @NonZero
    private Long ccYear;

    @NotNull
    @NonZero
    private Long ccCvv;

    public PlaceOrderPayload(String email, String streetAddress, Long zipCode, String city, String state,
                              String country, String ccNumber, Long ccMonth, Long ccYear, Long ccCvv) {
        this.email = email;
        this.streetAddress = streetAddress;
        this.zipCode = zipCode;
        this.city = city;
        this.state = state;
        this.country = country;
        this.ccNumber = ccNumber;
        this.ccMonth = ccMonth;
        this.ccYear = ccYear;
        this.ccCvv = ccCvv;
    }

    public String getEmail() {
        return email;
    }

    public String getStreetAddress() {
        return streetAddress;
    }

    public Long getZipCode() {
        return zipCode;
    }

    public String getCity() {
        return city;
    }

    public String getState() {
        return state;
    }

    public String getCountry() {
        return country;
    }

    public String getCcNumber() {
        return ccNumber;
    }

    public Long getCcMonth() {
        return ccMonth;
    }

    public Long getCcYear() {
        return ccYear;
    }

    public Long getCcCvv() {
        return ccCvv;
    }
}
