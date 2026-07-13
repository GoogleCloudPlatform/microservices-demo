package hipstershop.frontend.grpc;

import hipstershop.AdServiceGrpc;
import hipstershop.CartServiceGrpc;
import hipstershop.CheckoutServiceGrpc;
import hipstershop.CurrencyServiceGrpc;
import hipstershop.Demo;
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
        Demo.GetSupportedCurrenciesResponse resp =
                currencyStub.getSupportedCurrencies(Demo.Empty.getDefaultInstance());
        List<String> out = new ArrayList<>();
        for (String c : resp.getCurrencyCodesList()) {
            if (shopProperties.getWhitelistedCurrencies().contains(c)) {
                out.add(c);
            }
        }
        return out;
    }

    public List<Demo.Product> getProducts() {
        return productCatalogStub.listProducts(Demo.Empty.getDefaultInstance()).getProductsList();
    }

    public Demo.Product getProduct(String id) {
        return productCatalogStub.getProduct(Demo.GetProductRequest.newBuilder().setId(id).build());
    }

    public List<Demo.CartItem> getCart(String userId) {
        return cartStub.getCart(Demo.GetCartRequest.newBuilder().setUserId(userId).build()).getItemsList();
    }

    public void emptyCart(String userId) {
        cartStub.emptyCart(Demo.EmptyCartRequest.newBuilder().setUserId(userId).build());
    }

    public void insertCart(String userId, String productId, int quantity) {
        cartStub.addItem(Demo.AddItemRequest.newBuilder()
                .setUserId(userId)
                .setItem(Demo.CartItem.newBuilder().setProductId(productId).setQuantity(quantity).build())
                .build());
    }

    public Demo.Money convertCurrency(Demo.Money money, String currency) {
        return currencyStub.convert(Demo.CurrencyConversionRequest.newBuilder()
                .setFrom(money)
                .setToCode(currency)
                .build());
    }

    public Demo.Money getShippingQuote(List<Demo.CartItem> items, String currency) {
        Demo.GetQuoteResponse quote = shippingStub.getQuote(
                Demo.GetQuoteRequest.newBuilder().addAllItems(items).build());
        return convertCurrency(quote.getCostUsd(), currency);
    }

    public List<Demo.Product> getRecommendations(String userId, List<String> productIds) {
        Demo.ListRecommendationsRequest.Builder reqBuilder =
                Demo.ListRecommendationsRequest.newBuilder().setUserId(userId);
        if (productIds != null) {
            reqBuilder.addAllProductIds(productIds);
        }
        Demo.ListRecommendationsResponse resp = recommendationStub.listRecommendations(reqBuilder.build());
        List<Demo.Product> out = new ArrayList<>();
        for (String id : resp.getProductIdsList()) {
            out.add(getProduct(id));
        }
        if (out.size() > 4) {
            out = out.subList(0, 4); // take only first four to fit the UI
        }
        return out;
    }

    public Demo.PlaceOrderResponse placeOrder(Demo.PlaceOrderRequest request) {
        return checkoutStub.placeOrder(request);
    }

    public List<Demo.Ad> getAd(List<String> contextKeys) {
        AdServiceGrpc.AdServiceBlockingStub stubWithDeadline =
                adStub.withDeadline(Deadline.after(100, TimeUnit.MILLISECONDS));
        Demo.AdRequest.Builder reqBuilder = Demo.AdRequest.newBuilder();
        if (contextKeys != null) {
            reqBuilder.addAllContextKeys(contextKeys);
        }
        return stubWithDeadline.getAds(reqBuilder.build()).getAdsList();
    }
}
