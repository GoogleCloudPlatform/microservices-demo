package hipstershop.frontend.web;

import hipstershop.Hipstershop;
import java.util.List;

/** Ports {@code cartSize}/{@code cartIDs} from handlers.go. */
public final class CartUtil {

    private CartUtil() {
    }

    public static int cartSize(List<Hipstershop.CartItem> items) {
        int total = 0;
        for (Hipstershop.CartItem item : items) {
            total += item.getQuantity();
        }
        return total;
    }

    public static List<String> cartIds(List<Hipstershop.CartItem> items) {
        return items.stream().map(Hipstershop.CartItem::getProductId).toList();
    }
}
