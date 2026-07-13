package hipstershop.frontend.web;

import hipstershop.Demo;

/** Product + quantity + localized line price, used by the cart and order pages. */
public class LineItemView {
    private final Demo.Product item;
    private final int quantity;
    private final Demo.Money price;

    public LineItemView(Demo.Product item, int quantity, Demo.Money price) {
        this.item = item;
        this.quantity = quantity;
        this.price = price;
    }

    public Demo.Product getItem() {
        return item;
    }

    public int getQuantity() {
        return quantity;
    }

    public Demo.Money getPrice() {
        return price;
    }
}
