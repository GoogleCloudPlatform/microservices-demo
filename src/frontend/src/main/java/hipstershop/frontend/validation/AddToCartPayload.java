package hipstershop.frontend.validation;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

/** Mirrors the Go frontend's {@code validator.AddToCartPayload}. */
public class AddToCartPayload {

    @NotNull
    @Min(1)
    @Max(10)
    private Long quantity;

    @NotBlank
    private String productId;

    public AddToCartPayload(Long quantity, String productId) {
        this.quantity = quantity;
        this.productId = productId;
    }

    public Long getQuantity() {
        return quantity;
    }

    public String getProductId() {
        return productId;
    }
}
