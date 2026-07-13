package hipstershop.frontend.config;

import hipstershop.AdServiceGrpc;
import hipstershop.CartServiceGrpc;
import hipstershop.CheckoutServiceGrpc;
import hipstershop.CurrencyServiceGrpc;
import hipstershop.ProductCatalogServiceGrpc;
import hipstershop.RecommendationServiceGrpc;
import hipstershop.ShippingServiceGrpc;
import hipstershop.frontend.tracing.GrpcTracingClientInterceptor;
import io.grpc.ManagedChannel;
import io.grpc.netty.shaded.io.grpc.netty.NettyChannelBuilder;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Tracer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Establishes one gRPC channel per downstream service, mirroring {@code mustConnGRPC}
 * in the Go frontend's main.go. Env var names are unchanged so the existing
 * Kubernetes manifests / docker-compose files require no edits.
 */
@Configuration
public class GrpcChannelConfig {

    private static final Logger log = LoggerFactory.getLogger(GrpcChannelConfig.class);

    @Value("${PRODUCT_CATALOG_SERVICE_ADDR}")
    private String productCatalogSvcAddr;

    @Value("${CURRENCY_SERVICE_ADDR}")
    private String currencySvcAddr;

    @Value("${CART_SERVICE_ADDR}")
    private String cartSvcAddr;

    @Value("${RECOMMENDATION_SERVICE_ADDR}")
    private String recommendationSvcAddr;

    @Value("${SHIPPING_SERVICE_ADDR}")
    private String shippingSvcAddr;

    @Value("${CHECKOUT_SERVICE_ADDR}")
    private String checkoutSvcAddr;

    @Value("${AD_SERVICE_ADDR}")
    private String adSvcAddr;

    private ManagedChannel buildChannel(String addr, OpenTelemetry openTelemetry, Tracer tracer) {
        log.info("connecting to grpc target: {}", addr);
        return NettyChannelBuilder.forTarget(addr)
                .usePlaintext()
                .intercept(new GrpcTracingClientInterceptor(openTelemetry, tracer))
                .build();
    }

    @Bean(destroyMethod = "shutdown")
    public ManagedChannel productCatalogChannel(OpenTelemetry openTelemetry, Tracer tracer) {
        return buildChannel(productCatalogSvcAddr, openTelemetry, tracer);
    }

    @Bean(destroyMethod = "shutdown")
    public ManagedChannel currencyChannel(OpenTelemetry openTelemetry, Tracer tracer) {
        return buildChannel(currencySvcAddr, openTelemetry, tracer);
    }

    @Bean(destroyMethod = "shutdown")
    public ManagedChannel cartChannel(OpenTelemetry openTelemetry, Tracer tracer) {
        return buildChannel(cartSvcAddr, openTelemetry, tracer);
    }

    @Bean(destroyMethod = "shutdown")
    public ManagedChannel recommendationChannel(OpenTelemetry openTelemetry, Tracer tracer) {
        return buildChannel(recommendationSvcAddr, openTelemetry, tracer);
    }

    @Bean(destroyMethod = "shutdown")
    public ManagedChannel shippingChannel(OpenTelemetry openTelemetry, Tracer tracer) {
        return buildChannel(shippingSvcAddr, openTelemetry, tracer);
    }

    @Bean(destroyMethod = "shutdown")
    public ManagedChannel checkoutChannel(OpenTelemetry openTelemetry, Tracer tracer) {
        return buildChannel(checkoutSvcAddr, openTelemetry, tracer);
    }

    @Bean(destroyMethod = "shutdown")
    public ManagedChannel adChannel(OpenTelemetry openTelemetry, Tracer tracer) {
        return buildChannel(adSvcAddr, openTelemetry, tracer);
    }

    @Bean
    public ProductCatalogServiceGrpc.ProductCatalogServiceBlockingStub productCatalogStub(
            ManagedChannel productCatalogChannel) {
        return ProductCatalogServiceGrpc.newBlockingStub(productCatalogChannel);
    }

    @Bean
    public CurrencyServiceGrpc.CurrencyServiceBlockingStub currencyStub(ManagedChannel currencyChannel) {
        return CurrencyServiceGrpc.newBlockingStub(currencyChannel);
    }

    @Bean
    public CartServiceGrpc.CartServiceBlockingStub cartStub(ManagedChannel cartChannel) {
        return CartServiceGrpc.newBlockingStub(cartChannel);
    }

    @Bean
    public RecommendationServiceGrpc.RecommendationServiceBlockingStub recommendationStub(
            ManagedChannel recommendationChannel) {
        return RecommendationServiceGrpc.newBlockingStub(recommendationChannel);
    }

    @Bean
    public ShippingServiceGrpc.ShippingServiceBlockingStub shippingStub(ManagedChannel shippingChannel) {
        return ShippingServiceGrpc.newBlockingStub(shippingChannel);
    }

    @Bean
    public CheckoutServiceGrpc.CheckoutServiceBlockingStub checkoutStub(ManagedChannel checkoutChannel) {
        return CheckoutServiceGrpc.newBlockingStub(checkoutChannel);
    }

    @Bean
    public AdServiceGrpc.AdServiceBlockingStub adStub(ManagedChannel adChannel) {
        return AdServiceGrpc.newBlockingStub(adChannel);
    }
}
