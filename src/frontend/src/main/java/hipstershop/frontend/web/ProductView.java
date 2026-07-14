package hipstershop.frontend.web;

import hipstershop.Hipstershop;

/** Product + localized price, used by the home and product pages. */
public class ProductView {
    private final Hipstershop.Product item;
    private final Hipstershop.Money price;

    public ProductView(Hipstershop.Product item, Hipstershop.Money price) {
        this.item = item;
        this.price = price;
    }

    public Hipstershop.Product getItem() {
        return item;
    }

    public Hipstershop.Money getPrice() {
        return price;
    }
}
