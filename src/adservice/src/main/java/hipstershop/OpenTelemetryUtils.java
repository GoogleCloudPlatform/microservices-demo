package hipstershop;

import static java.util.Collections.singleton;

import com.newrelic.telemetry.opentelemetry.export.NewRelicMetricExporter;
import io.opentelemetry.exporters.logging.LoggingMetricExporter;
import io.opentelemetry.metrics.MeterProvider;
import io.opentelemetry.sdk.metrics.MeterSdkProvider;
import io.opentelemetry.sdk.metrics.export.IntervalMetricReader;
import io.opentelemetry.sdk.metrics.export.MetricExporter;
import java.net.URI;

public class OpenTelemetryUtils {
  // seems like docker/k8s/skaffold/something passes in this value when the env var is missing.
  public static final String NO_VALUE_ENV_VAR = "<no value>";
  private static IntervalMetricReader intervalMetricReader;

  //todo: once the auto-agent supports metrics exporter config, then this can go away.
  public static MeterProvider initializeForNewRelic() {
    String newRelicApiKey = System.getenv("NEW_RELIC_API_KEY");

    MetricExporter metricExporter;
    if (apiKeyIsMissing(newRelicApiKey)) {
      System.out
          .println("NEW_RELIC_API_KEY not present. Falling back to the logging metrics exporter.");
      metricExporter = new LoggingMetricExporter();
    } else {
      NewRelicMetricExporter.Builder builder = NewRelicMetricExporter.newBuilder()
          .apiKey(newRelicApiKey)
          .enableAuditLogging();
      String metricEndpoint = System.getenv("NEW_RELIC_METRIC_URL");
      if (metricEndpoint != null && !NO_VALUE_ENV_VAR.equals(metricEndpoint)) {
        builder.uriOverride(URI.create(metricEndpoint));
      }
      metricExporter = builder.build();
    }

    MeterSdkProvider meterSdkProvider = MeterSdkProvider.builder().build();
    intervalMetricReader = IntervalMetricReader.builder()
        .setMetricProducers(singleton(meterSdkProvider.getMetricProducer()))
        .setExportIntervalMillis(5000)
        .setMetricExporter(metricExporter)
        .build();
    return meterSdkProvider;
  }

  private static boolean apiKeyIsMissing(String newRelicApiKey) {
    return newRelicApiKey == null
        || newRelicApiKey.isEmpty()
        || NO_VALUE_ENV_VAR.equals(newRelicApiKey);
  }

  public static void shutdownSdk() {
    intervalMetricReader.shutdown();
  }

}
