/*
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package hipstershop;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.health.v1.HealthCheckResponse.ServingStatus;
import io.grpc.protobuf.services.HealthStatusManager;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Entry point for the checkout service.
 *
 * <p>Like the Go implementation this service plays two gRPC roles at once: it is a <b>server</b>
 * exposing {@code CheckoutService.PlaceOrder}, and a <b>client</b> to six downstream services
 * (cart, product catalog, currency, shipping, payment, email). Downstream addresses are read from
 * environment variables so the deployment (Kubernetes) controls service discovery — nothing is
 * hardcoded.
 */
public final class CheckoutService {

  private static final Logger logger = LogManager.getLogger(CheckoutService.class);

  private static final String DEFAULT_PORT = "5050";

  private Server server;
  private HealthStatusManager healthMgr;
  private CheckoutServiceImpl impl;

  private void start() throws IOException {
    int port = Integer.parseInt(System.getenv().getOrDefault("PORT", DEFAULT_PORT));

    // Resolve the six downstream service addresses. Missing any of these is a
    // configuration error and we fail fast, matching the Go mustMapEnv behaviour.
    String cartAddr = mustGetEnv("CART_SERVICE_ADDR");
    String catalogAddr = mustGetEnv("PRODUCT_CATALOG_SERVICE_ADDR");
    String currencyAddr = mustGetEnv("CURRENCY_SERVICE_ADDR");
    String shippingAddr = mustGetEnv("SHIPPING_SERVICE_ADDR");
    String paymentAddr = mustGetEnv("PAYMENT_SERVICE_ADDR");
    String emailAddr = mustGetEnv("EMAIL_SERVICE_ADDR");

    // One long-lived channel per downstream, opened once and reused for every
    // request (gRPC multiplexes calls over a single HTTP/2 connection).
    // usePlaintext() mirrors the Go insecure credentials: security is expected
    // from the mesh / cluster network, not from app-level TLS.
    ManagedChannel cartChannel = channel(cartAddr);
    ManagedChannel catalogChannel = channel(catalogAddr);
    ManagedChannel currencyChannel = channel(currencyAddr);
    ManagedChannel shippingChannel = channel(shippingAddr);
    ManagedChannel paymentChannel = channel(paymentAddr);
    ManagedChannel emailChannel = channel(emailAddr);

    impl =
        new CheckoutServiceImpl(
            cartChannel,
            catalogChannel,
            currencyChannel,
            shippingChannel,
            paymentChannel,
            emailChannel);

    healthMgr = new HealthStatusManager();

    server =
        ServerBuilder.forPort(port)
            .addService(impl)
            // Standard gRPC health service that Kubernetes liveness/readiness
            // probes call (grpc.health.v1.Health).
            .addService(healthMgr.getHealthService())
            .build()
            .start();

    logger.info("CheckoutService started, listening on {}", port);

    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  System.err.println("*** shutting down gRPC checkout server (JVM shutdown)");
                  CheckoutService.this.stop();
                  System.err.println("*** server shut down");
                }));

    healthMgr.setStatus("", ServingStatus.SERVING);
  }

  private void stop() {
    if (healthMgr != null) {
      healthMgr.clearStatus("");
    }
    if (impl != null) {
      impl.shutdownChannels();
    }
    if (server != null) {
      try {
        server.shutdown().awaitTermination(10, TimeUnit.SECONDS);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
      }
    }
  }

  private void blockUntilShutdown() throws InterruptedException {
    if (server != null) {
      server.awaitTermination();
    }
  }

  private static ManagedChannel channel(String target) {
    return ManagedChannelBuilder.forTarget(target).usePlaintext().build();
  }

  private static String mustGetEnv(String key) {
    String value = System.getenv(key);
    if (value == null || value.isBlank()) {
      throw new IllegalStateException("environment variable \"" + key + "\" not set");
    }
    return value;
  }

  public static void main(String[] args) throws Exception {
    final CheckoutService service = new CheckoutService();
    service.start();
    service.blockUntilShutdown();
  }
}
