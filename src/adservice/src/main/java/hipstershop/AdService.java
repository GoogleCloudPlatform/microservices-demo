package hipstershop;

import com.google.common.collect.ImmutableListMultimap;
import com.google.common.collect.Iterables;
import hipstershop.Demo.Ad;
import hipstershop.Demo.AdRequest;
import hipstershop.Demo.AdResponse;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.StatusRuntimeException;
import io.grpc.health.v1.HealthCheckResponse.ServingStatus;
import io.grpc.services.*;
import io.grpc.stub.StreamObserver;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Random;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public final class AdService {

  private static final Logger l = LogManager.getLogger(AdService.class);
  private static int M = 2;
  private Server s;
  private HealthStatusManager h;
  private static final AdService a = new AdService();

  private void st() throws IOException {
    int p = Integer.parseInt(System.getenv().getOrDefault("PORT", "9555"));
    h = new HealthStatusManager();
    s =
        ServerBuilder.forPort(p)
            .addService(new AImpl())
            .addService(h.getHealthService())
            .build()
            .start();
    l.info("Ad Service started, listening on " + p);
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  System.err.println("*** shutting down gRPC ads server since JVM is shutting down");
                  AdService.this.sp();
                  System.err.println("*** server shut down");
                }));
    h.setStatus("", ServingStatus.SERVING);
  }

  private void sp() {
    if (s != null) {
      h.clearStatus("");
      s.shutdown();
    }
  }

  private static class AImpl extends hipstershop.AdServiceGrpc.AdServiceImplBase {
    @Override
    public void getAds(AdRequest r, StreamObserver<AdResponse> o) {
      AdService a = AdService.i();
      try {
        List<Ad> ads = new ArrayList<>();
        l.info("received ad request (context_words=" + r.getContextKeysList() + ")");
        if (r.getContextKeysCount() > 0) {
          for (int i = 0; i < r.getContextKeysCount(); i++) {
            Collection<Ad> c = a.gAC(r.getContextKeys(i));
            ads.addAll(c);
          }
        } else {
          ads = a.gRA();
        }
        if (ads.isEmpty()) {
          ads = a.gRA();
        }
        AdResponse rp = AdResponse.newBuilder().addAllAds(ads).build();
        o.onNext(rp);
        o.onCompleted();
      } catch (StatusRuntimeException e) {
        l.log(Level.WARN, "GetAds Failed with status {}", e.getStatus());
        o.onError(e);
      }
    }
  }

  private static final ImmutableListMultimap<String, Ad> am = cAM();

  private Collection<Ad> gAC(String c) {
    return am.get(c);
  }

  private static final Random r = new Random();

  private List<Ad> gRA() {
    List<Ad> ads = new ArrayList<>(M);
    Collection<Ad> allAds = am.values();
    for (int i = 0; i < M; i++) {
      ads.add(Iterables.get(allAds, r.nextInt(allAds.size())));
    }
    return ads;
  }

  private static AdService i() {
    return a;
  }

  private void bUS() throws InterruptedException {
    if (s != null) {
      s.awaitTermination();
    }
  }

  private static ImmutableListMultimap<String, Ad> cAM() {
    Ad h =
        Ad.newBuilder()
            .setRedirectUrl("/product/2ZYFJ3GM2N")
            .setText("Hairdryer for sale. 50% off.")
            .build();
    Ad t =
        Ad.newBuilder()
            .setRedirectUrl("/product/66VCHSJNUP")
            .setText("Tank top for sale. 20% off.")
            .build();
    Ad c =
        Ad.newBuilder()
            .setRedirectUrl("/product/0PUK6V6EV0")
            .setText("Candle holder for sale. 30% off.")
            .build();
    Ad b =
        Ad.newBuilder()
            .setRedirectUrl("/product/9SIQT8TOJO")
            .setText("Bamboo glass jar for sale. 10% off.")
            .build();
    Ad w =
        Ad.newBuilder()
            .setRedirectUrl("/product/1YMWWN1N4O")
            .setText("Watch for sale. Buy one, get second kit for free")
            .build();
    Ad m =
        Ad.newBuilder()
            .setRedirectUrl("/product/6E92ZMYYFZ")
            .setText("Mug for sale. Buy two, get third one for free")
            .build();
     Ad l =
        Ad.newBuilder()
            .setRedirectUrl("/product/L9ECAV7KIM")
            .setText("Loafers for sale. Buy one, get second one for free")
            .build();
    return ImmutableListMultimap.<String, Ad>builder()
        .putAll("clothing", t)
        .putAll("accessories", w)
        .putAll("footwear", l)
        .putAll("hair", h)
        .putAll("decor", c)
        .putAll("kitchen", b, m)
        .build();
  }

    private static void iS() {
    if (System.getenv("DISABLE_STATS") != null) {
      l.info("Stats disabled.");
      return;
    }
    l.info("Stats enabled, but temporarily unavailable");

    // TODO(arbrown) Implement OpenTelemetry stats
  }

  private static void iT() {
    if (System.getenv("DISABLE_TRACING") != null) {
      l.info("Tracing disabled.");
      return;
    }
    l.info("Tracing enabled but temporarily unavailable");
    l.info("See https://github.com/GoogleCloudPlatform/microservices-demo/issues/422 for more info.");
    // TODO(arbrown) Implement OpenTelemetry tracing
    l.info("Tracing enabled - Stackdriver exporter initialized.");
  }

  public static void main(String[] args) throws IOException, InterruptedException {
    new Thread(
            () -> {
              iS();
              iT();
            })
        .start();
    l.info("AdService starting.");
    final AdService a = AdService.i();
    a.st();
    a.bUS();
  }
}
