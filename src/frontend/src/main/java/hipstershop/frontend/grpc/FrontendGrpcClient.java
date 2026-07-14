package hipstershop.frontend.grpc;

import hipstershop.AdServiceGrpc;
import hipstershop.CartServiceGrpc;
import hipstershop.CheckoutServiceGrpc;
import hipstershop.CurrencyServiceGrpc;
import hipstershop.Hipstershop;
import hipstershop.ProductCatalogServiceGrpc;
import hipstershop.RecommendationServiceGrpc;
import hipstershop.ShippingServiceGrpc;
import hipstershop.frontend.config.ShopProperties;
import hipstershop.frontend.money.Money;
import io.grpc.Deadline;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.springframework.stereotype.Service;

/**
 * Thin gRPC client wrappers for every downstream service the frontend talks
 * to, a direct port of the Go frontend's rpc.go.
 */
@Service
public class FrontendGrpcClient {

    private final ProductCatalogServiceGrpc.ProductCatalogServiceBlockingStub productCatalogStub;
    private final CurrencyServiceGrpc.CurrencyServiceBlockingStub currencyStub;
    private final CartServiceGrpc.CartServiceBlockingStub cartStub;
    private final RecommendationServiceGrpc.RecommendationServiceBlockingStub recommendationStub;
    private final ShippingServiceGrpc.ShippingServiceBlockingStub shippingStub;
    private final CheckoutServiceGrpc.CheckoutServiceBlockingStub checkoutStub;
    private final AdServiceGrpc.AdServiceBlockingStub adStub;
    private final ShopProperties shopProperties;

    public FrontendGrpcClient(
            ProductCatalogServiceGrpc.ProductCatalogServiceBlockingStub productCatalogStub,
            CurrencyServiceGrpc.CurrencyServiceBlockingStub currencyStub,
            CartServiceGrpc.CartServiceBlockingStub cartStub,
            RecommendationServiceGrpc.RecommendationServiceBlockingStub recommendationStub,
            ShippingServiceGrpc.ShippingServiceBlockingStub shippingStub,
            CheckoutServiceGrpc.CheckoutServiceBlockingStub checkoutStub,
            AdServiceGrpc.AdServiceBlockingStub adStub,
            ShopProperties shopProperties) {
        this.productCatalogStub = productCatalogStub;
        this.currencyStub = currencyStub;
        this.cartStub = cartStub;
        this.recommendationStub = recommendationStub;
        this.shippingStub = shippingStub;
        this.checkoutStub = checkoutStub;
        this.adStub = adStub;
        this.shopProperties = shopProperties;
    }

    public List<String> getCurrencies() {
        Hipstershop.GetSupportedCurrenciesResponse resp =
                currencyStub.getSupportedCurrencies(Hipstershop.Empty.getDefaultInstance());
        List<String> out = new ArrayList<>();
        for (String c : resp.getCurrencyCodesList()) {
            if (shopProperties.getWhitelistedCurrencies().contains(c)) {
                out.add(c);
            }
        }
        return out;
    }

    public List<Hipstershop.Product> getProducts() {
        return productCatalogStub.listProducts(Hipstershop.Empty.getDefaultInstance()).getProductsList();
    }

    public Hipstershop.Product getProduct(String id) {
        return productCatalogStub.getProduct(Hipstershop.GetProductRequest.newBuilder().setId(id).build());
    }

    public List<Hipstershop.CartItem> getCart(String userId) {
        return cartStub.getCart(Hipstershop.GetCartRequest.newBuilder().setUserId(userId).build()).getItemsList();
    }

    public void emptyCart(String userId) {
        cartStub.emptyCart(Hipstershop.EmptyCartRequest.newBuilder().setUserId(userId).build());
    }

    public void insertCart(String userId, String productId, int quantity) {
        cartStub.addItem(Hipstershop.AddItemRequest.newBuilder()
                .setUserId(userId)
                .setItem(Hipstershop.CartItem.newBuilder().setProductId(productId).setQuantity(quantity).build())
                .build());
    }

    public Hipstershop.Money convertCurrency(Hipstershop.Money money, String currency) {
        return currencyStub.convert(Hipstershop.CurrencyConversionRequest.newBuilder()
                .setFrom(money)
                .setToCode(currency)
                .build());
    }

    public Hipstershop.Money getShippingQuote(List<Hipstershop.CartItem> items, String currency) {
        Hipstershop.GetQuoteResponse quote = shippingStub.getQuote(
                Hipstershop.GetQuoteRequest.newBuilder().addAllItems(items).build());
        return convertCurrency(quote.getCostUsd(), currency);
    }

    public List<Hipstershop.Product> getRecommendations(String userId, List<String> productIds) {
        Hipstershop.ListRecommendationsRequest.Builder reqBuilder =
                Hipstershop.ListRecommendationsRequest.newBuilder().setUserId(userId);
        if (productIds != null) {
            reqBuilder.addAllProductIds(productIds);
        }
        Hipstershop.ListRecommendationsResponse resp = recommendationStub.listRecommendations(reqBuilder.build());
        List<Hipstershop.Product> out = new ArrayList<>();
        for (String id : resp.getProductIdsList()) {
            out.add(getProduct(id));
        }
        if (out.size() > 4) {
            out = out.subList(0, 4); // take only first four to fit the UI
        }
        return out;
    }

    public Hipstershop.PlaceOrderResponse placeOrder(Hipstershop.PlaceOrderRequest request) {
        return checkoutStub.placeOrder(request);
    }

    public List<Hipstershop.Ad> getAd(List<String> contextKeys) {
        AdServiceGrpc.AdServiceBlockingStub stubWithDeadline =
                adStub.withDeadline(Deadline.after(100, TimeUnit.MILLISECONDS));
        Hipstershop.AdRequest.Builder reqBuilder = Hipstershop.AdRequest.newBuilder();
        if (contextKeys != null) {
            reqBuilder.addAllContextKeys(contextKeys);
        }
        return stubWithDeadline.getAds(reqBuilder.build()).getAdsList();
    }
}
