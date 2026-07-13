package hipstershop.frontend.web;

import hipstershop.Demo;
import java.util.List;

/** Ports {@code cartSize}/{@code cartIDs} from handlers.go. */
public final class CartUtil {

    private CartUtil() {
    }

    public static int cartSize(List<Demo.CartItem> items) {
        int total = 0;
        for (Demo.CartItem item : items) {
            total += item.getQuantity();
        }
        return total;
    }

    public static List<String> cartIds(List<Demo.CartItem> items) {
        return items.stream().map(Demo.CartItem::getProductId).toList();
    }
}
