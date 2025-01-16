package hipstershop;



import hipstershop.Demo.Ad;
import hipstershop.Demo.AdRequest;
import hipstershop.Demo.AdResponse;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusRuntimeException;
import java.util.concurrent.TimeUnit;
import javax.annotation.Nullable;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class AdServiceClient {

  private static final Logger logger = LogManager.getLogger(AdServiceClient.class);

  private final ManagedChannel channel;
  private final hipstershop.AdServiceGrpc.AdServiceBlockingStub blockingStub;
  private AdServiceClient(String host, int port) {
    this(
        ManagedChannelBuilder.forAddress(host, port)
            // Channels are secure by default (via SSL/TLS). For the example we disable TLS to avoid
            // needing certificates.
            .usePlaintext()
            .build());
  }

  private AdServiceCl(ManagedChannel channel) {
    this.channel = channel;
    blockingStub = hipstershop.AdServiceGrpc.newBlockingStub(channel);
  }

  private void shutdown() throws InterruptedException {
    channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
  }

  public void getAds(String contextKey) {
    logger.info("Get Ads with context " + contextKey + " ...");
    AdRequest request = AdRequest.newBuilder().addContextKeys(contextKey).build();
    AdResponse response;

    try {
      response = blockingStub.getAds(request);
    } catch (StatusRuntimeException e) {
      logger.log(Level.WARN, "RPC failed: " + e.getStatus());
      return;
    } 
    for (Ad ads : response.getAdsList()) {
      logger.info("Ads: " + ads.getText());
    }
  }

  private static int getPortOrDefaultFromArgs(String[] args) {
    int portNumber = 9555;
    if (2 < args.length) {
      try {
        portNumber = Integer.parseInt(args[2]);
      } catch (NumberFormatException e) {
        logger.warn(String.format("Port %s is invalid, use default port %d.", args[2], 9555));
      }
    }
    return portNumber;
  }

  private static String getStringOrDefaultFromArgs(
      String[] args, int index, @Nullable String defaultString) {
    String s = defaultString;
    if (index < args.length) {
      s = args[index];
    }
    return s;
  }

  public static void main(String[] args) throws InterruptedException {
    final String contextKeys = getStringOrDefaultFromArgs(args, 0, "camera");
    final String host = getStringOrDefaultFromArgs(args, 1, "localhost");
    final int serverPort = getPortOrDefaultFromArgs(args);

    AdServiceClient client = new AdServiceClient(host, serverPort);
    try {
      client.getAds(contextKeys);
    } finally {
      client.shutdown();
    }

    logger.info("Exiting AdServiceClient...");
  }
}
