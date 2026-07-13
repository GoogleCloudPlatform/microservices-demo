package hipstershop.frontend.web;

import hipstershop.Demo;

/** Product + localized price, used by the home and product pages. */
public class ProductView {
    private final Demo.Product item;
    private final Demo.Money price;

    public ProductView(Demo.Product item, Demo.Money price) {
        this.item = item;
        this.price = price;
    }

    public Demo.Product getItem() {
        return item;
    }

    public Demo.Money getPrice() {
        return price;
    }
}
