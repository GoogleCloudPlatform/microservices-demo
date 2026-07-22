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

import hipstershop.Hipstershop.Address;
import hipstershop.Hipstershop.Cart;
import hipstershop.Hipstershop.CartItem;
import hipstershop.Hipstershop.ChargeRequest;
import hipstershop.Hipstershop.ChargeResponse;
import hipstershop.Hipstershop.CreditCardInfo;
import hipstershop.Hipstershop.CurrencyConversionRequest;
import hipstershop.Hipstershop.Empty;
import hipstershop.Hipstershop.EmptyCartRequest;
import hipstershop.Hipstershop.GetCartRequest;
import hipstershop.Hipstershop.GetProductRequest;
import hipstershop.Hipstershop.GetQuoteRequest;
import hipstershop.Hipstershop.GetQuoteResponse;
import hipstershop.Hipstershop.Money;
import hipstershop.Hipstershop.OrderItem;
import hipstershop.Hipstershop.OrderResult;
import hipstershop.Hipstershop.PlaceOrderRequest;
import hipstershop.Hipstershop.PlaceOrderResponse;
import hipstershop.Hipstershop.Product;
import hipstershop.Hipstershop.SendOrderConfirmationRequest;
import hipstershop.Hipstershop.ShipOrderRequest;
import hipstershop.Hipstershop.ShipOrderResponse;
import io.grpc.ManagedChannel;
import io.grpc.Status;
import io.grpc.StatusRuntimeException;
import io.grpc.stub.StreamObserver;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Implements {@code CheckoutService.PlaceOrder}. This is a stateless orchestrator: it owns no data
 * and fulfils an order by calling the other services in sequence. The flow mirrors the original Go
 * checkoutservice one-for-one, including the coupon discount feature.
 */
final class CheckoutServiceImpl extends CheckoutServiceGrpc.CheckoutServiceImplBase {

  private static final Logger logger = LogManager.getLogger(CheckoutServiceImpl.class);

  /**
   * Coupon codes and their whole-unit discount. The numeric coupon value must match what the
   * shopper sees in the selected currency, so SAVE10 means 10 units of the checkout currency.
   */
  private static final Map<String, Long> COUPONS =
      Map.of(
          "SAVE10", 10L,
          "SAVE50", 50L,
          "SAVE100", 100L);

  private final List<ManagedChannel> channels = new ArrayList<>();

  private final CartServiceGrpc.CartServiceBlockingStub cartStub;
  private final ProductCatalogServiceGrpc.ProductCatalogServiceBlockingStub catalogStub;
  private final CurrencyServiceGrpc.CurrencyServiceBlockingStub currencyStub;
  private final ShippingServiceGrpc.ShippingServiceBlockingStub shippingStub;
  private final PaymentServiceGrpc.PaymentServiceBlockingStub paymentStub;
  private final EmailServiceGrpc.EmailServiceBlockingStub emailStub;

  CheckoutServiceImpl(
      ManagedChannel cartChannel,
      ManagedChannel catalogChannel,
      ManagedChannel currencyChannel,
      ManagedChannel shippingChannel,
      ManagedChannel paymentChannel,
      ManagedChannel emailChannel) {
    channels.add(cartChannel);
    channels.add(catalogChannel);
    channels.add(currencyChannel);
    channels.add(shippingChannel);
    channels.add(paymentChannel);
    channels.add(emailChannel);

    this.cartStub = CartServiceGrpc.newBlockingStub(cartChannel);
    this.catalogStub = ProductCatalogServiceGrpc.newBlockingStub(catalogChannel);
    this.currencyStub = CurrencyServiceGrpc.newBlockingStub(currencyChannel);
    this.shippingStub = ShippingServiceGrpc.newBlockingStub(shippingChannel);
    this.paymentStub = PaymentServiceGrpc.newBlockingStub(paymentChannel);
    this.emailStub = EmailServiceGrpc.newBlockingStub(emailChannel);
  }

  @Override
  public void placeOrder(
      PlaceOrderRequest req, StreamObserver<PlaceOrderResponse> responseObserver) {
    logger.info(
        "[PlaceOrder] user_id=\"{}\" user_currency=\"{}\"",
        req.getUserId(),
        req.getUserCurrency());

    try {
      String orderId = UUID.randomUUID().toString();

      OrderPrep prep =
          prepareOrderItemsAndShippingQuoteFromCart(
              req.getUserId(), req.getUserCurrency(), req.getAddress());

      // Running total = shipping + sum(item cost * quantity), in the user's currency.
      Money total = MoneyUtil.zero(req.getUserCurrency());
      total = MoneyUtil.sum(total, prep.shippingCostLocalized);
      for (OrderItem item : prep.orderItems) {
        Money multPrice = MoneyUtil.multiplySlow(item.getCost(), item.getItem().getQuantity());
        total = MoneyUtil.sum(total, multPrice);
      }

      // ---------------------------------------------------------------
      // Coupon validation and discount application.
      //
      // discountAmount / couponCodeUsed stay zero/empty unless a valid
      // coupon is applied, so the order proceeds at full price otherwise.
      // ---------------------------------------------------------------
      Money discountAmount = MoneyUtil.zero(req.getUserCurrency());
      String couponCodeUsed = "";

      // Start from the default coupon; only override it if the client actually sent one.
      String couponCode = "SAVE10";
      String requestCouponCode = req.getCouponCode();
      if (requestCouponCode != null && !requestCouponCode.isEmpty()) {
        couponCode = requestCouponCode;
      }

      Long couponValue = COUPONS.get(couponCode);
      if (couponValue != null) {
        discountAmount =
            Money.newBuilder()
                .setCurrencyCode(req.getUserCurrency())
                .setUnits(couponValue)
                .setNanos(0)
                .build();
        couponCodeUsed = couponCode;

        // Apply the discount, but never let the charged total go negative —
        // paymentservice must not receive a negative amount.
        Money newTotal = MoneyUtil.sum(total, MoneyUtil.negate(discountAmount));
        if (!MoneyUtil.isNegative(newTotal)) {
          total = newTotal;
        } else {
          // Discount exceeds the total: the order is free.
          total = MoneyUtil.zero(req.getUserCurrency());
        }
      } else {
        logger.info("coupon code \"{}\" not found, skipping discount", couponCode);
      }

      String txId = chargeCard(total, req.getCreditCard());
      logger.info("payment went through (transaction_id: {})", txId);

      String shippingTrackingId = shipOrder(req.getAddress(), prep.cartItems);

      emptyUserCart(req.getUserId());

      OrderResult orderResult =
          OrderResult.newBuilder()
              .setOrderId(orderId)
              .setShippingTrackingId(shippingTrackingId)
              .setShippingCost(prep.shippingCostLocalized)
              .setShippingAddress(req.getAddress())
              .addAllItems(prep.orderItems)
              .setDiscountAmount(discountAmount)
              .setCouponCodeUsed(couponCodeUsed)
              .build();

      // A failed confirmation email is non-fatal — the order still succeeds.
      try {
        sendOrderConfirmation(req.getEmail(), orderResult);
        logger.info("order confirmation email sent to \"{}\"", req.getEmail());
      } catch (StatusRuntimeException e) {
        logger.warn(
            "failed to send order confirmation to \"{}\": {}", req.getEmail(), e.getStatus());
      }

      PlaceOrderResponse response =
          PlaceOrderResponse.newBuilder().setOrder(orderResult).build();
      responseObserver.onNext(response);
      responseObserver.onCompleted();

    } catch (StatusRuntimeException e) {
      // Propagate a downstream gRPC status upstream unchanged.
      logger.error("[PlaceOrder] failed: {}", e.getStatus());
      responseObserver.onError(e);
    } catch (RuntimeException e) {
      logger.error("[PlaceOrder] internal error", e);
      responseObserver.onError(
          Status.INTERNAL.withDescription(e.getMessage()).withCause(e).asRuntimeException());
    }
  }

  // ------------------------------------------------------------------
  // Order preparation
  // ------------------------------------------------------------------

  /** Holds the intermediate order data assembled before charging the card. */
  private static final class OrderPrep {
    List<OrderItem> orderItems;
    List<CartItem> cartItems;
    Money shippingCostLocalized;
  }

  private OrderPrep prepareOrderItemsAndShippingQuoteFromCart(
      String userId, String userCurrency, Address address) {
    OrderPrep out = new OrderPrep();

    List<CartItem> cartItems = getUserCart(userId);
    out.cartItems = cartItems;
    out.orderItems = prepOrderItems(cartItems, userCurrency);

    Money shippingUsd = quoteShipping(address, cartItems);
    out.shippingCostLocalized = convertCurrency(shippingUsd, userCurrency);

    return out;
  }

  private List<CartItem> getUserCart(String userId) {
    Cart cart = cartStub.getCart(GetCartRequest.newBuilder().setUserId(userId).build());
    return cart.getItemsList();
  }

  private void emptyUserCart(String userId) {
    // Error is intentionally swallowed (as in the Go code): a failure to empty
    // the cart should not fail an already-charged order.
    try {
      cartStub.emptyCart(EmptyCartRequest.newBuilder().setUserId(userId).build());
    } catch (StatusRuntimeException e) {
      logger.warn("failed to empty user cart during checkout: {}", e.getStatus());
    }
  }

  private List<OrderItem> prepOrderItems(List<CartItem> items, String userCurrency) {
    List<OrderItem> out = new ArrayList<>(items.size());
    for (CartItem item : items) {
      Product product =
          catalogStub.getProduct(
              GetProductRequest.newBuilder().setId(item.getProductId()).build());
      Money price = convertCurrency(product.getPriceUsd(), userCurrency);
      out.add(OrderItem.newBuilder().setItem(item).setCost(price).build());
    }
    return out;
  }

  private Money quoteShipping(Address address, List<CartItem> items) {
    GetQuoteResponse quote =
        shippingStub.getQuote(
            GetQuoteRequest.newBuilder().setAddress(address).addAllItems(items).build());
    return quote.getCostUsd();
  }

  private Money convertCurrency(Money from, String toCurrency) {
    return currencyStub.convert(
        CurrencyConversionRequest.newBuilder().setFrom(from).setToCode(toCurrency).build());
  }

  private String chargeCard(Money amount, CreditCardInfo paymentInfo) {
    ChargeResponse resp =
        paymentStub.charge(
            ChargeRequest.newBuilder().setAmount(amount).setCreditCard(paymentInfo).build());
    return resp.getTransactionId();
  }

  private String shipOrder(Address address, List<CartItem> items) {
    ShipOrderResponse resp =
        shippingStub.shipOrder(
            ShipOrderRequest.newBuilder().setAddress(address).addAllItems(items).build());
    return resp.getTrackingId();
  }

  private void sendOrderConfirmation(String email, OrderResult order) {
    Empty ignored =
        emailStub.sendOrderConfirmation(
            SendOrderConfirmationRequest.newBuilder().setEmail(email).setOrder(order).build());
  }

  /** Closes all downstream channels. Called from the server shutdown hook. */
  void shutdownChannels() {
    for (ManagedChannel channel : channels) {
      try {
        channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
      }
    }
  }
}
