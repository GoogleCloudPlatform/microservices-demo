package hipstershop.frontend.web;

import hipstershop.Hipstershop;

/** Product + quantity + localized line price, used by the cart and order pages. */
public class LineItemView {
    private final Hipstershop.Product item;
    private final int quantity;
    private final Hipstershop.Money price;

    public LineItemView(Hipstershop.Product item, int quantity, Hipstershop.Money price) {
        this.item = item;
        this.quantity = quantity;
        this.price = price;
    }

    public Hipstershop.Product getItem() {
        return item;
    }

    public int getQuantity() {
        return quantity;
    }

    public Hipstershop.Money getPrice() {
        return price;
    }
}
