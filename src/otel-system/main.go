package main

import (
	"context"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/google/uuid"
	"github.com/newrelic/newrelic-telemetry-sdk-go/telemetry"
	"github.com/newrelic/opentelemetry-exporter-go/newrelic"
	"github.com/sirupsen/logrus"
	"go.opentelemetry.io/contrib/detectors/gcp"
	"go.opentelemetry.io/contrib/instrumentation/host"
	"go.opentelemetry.io/contrib/instrumentation/runtime"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp"
	"go.opentelemetry.io/otel/exporters/stdout"
	"go.opentelemetry.io/otel/label"
	"go.opentelemetry.io/otel/sdk/export/metric"
	"go.opentelemetry.io/otel/sdk/metric/controller/push"
	"go.opentelemetry.io/otel/sdk/metric/processor/basic"
	"go.opentelemetry.io/otel/sdk/metric/selector/simple"
	"go.opentelemetry.io/otel/sdk/resource"
	"go.opentelemetry.io/otel/semconv"
)

const (
	nrAPIKeyEnv     = "NEW_RELIC_API_KEY"
	nrEndpointEnv   = "NEW_RELIC_METRIC_URL"
	otlpEndpointEnv = "OTLP_EXPORTER_ENDPOINT"

	serviceName = "otel-system"
)

var log *logrus.Logger

func init() {
	log = logrus.New()
	log.Level = logrus.DebugLevel
	log.Formatter = &logrus.JSONFormatter{
		FieldMap: logrus.FieldMap{
			logrus.FieldKeyTime:  "timestamp",
			logrus.FieldKeyLevel: "severity",
			logrus.FieldKeyMsg:   "message",
		},
		TimestampFormat: time.RFC3339Nano,
	}
	log.Out = os.Stdout
}

func nrExporter(ctx context.Context, key string) (metric.Exporter, error) {
	var opts []func(*telemetry.Config)
	if u, ok := os.LookupEnv(nrEndpointEnv); ok {
		opts = append(opts, func(cfg *telemetry.Config) {
			cfg.MetricsURLOverride = u
		})
		logrus.Infof("exporting to New Relic: %s", u)
	} else {
		logrus.Info("exporting to New Relic")
	}

	opts = append(opts, func(cfg *telemetry.Config) {
		cfg.DebugLogger = func(m map[string]interface{}) {
			log.Info(m)
		}
		cfg.ErrorLogger = func(m map[string]interface{}) {
			log.Error(m)
		}
	})

	return newrelic.NewExporter(serviceName, key, opts...)
}

func otlpExporter(ctx context.Context, endpoint string) (metric.Exporter, error) {
	logrus.Infof("exporting with OTLP exporter: %s", endpoint)
	return otlp.NewExporter(
		ctx,
		otlp.WithInsecure(),
		otlp.WithAddress(endpoint),
	)
}

func exporter(ctx context.Context) (metric.Exporter, error) {
	if key, ok := os.LookupEnv(nrAPIKeyEnv); ok {
		return nrExporter(ctx, key)
	}

	if ep, ok := os.LookupEnv(otlpEndpointEnv); ok {
		return otlpExporter(ctx, ep)
	}

	logrus.Info("defaulting to stdout exporter")
	return stdout.NewExporter(stdout.WithPrettyPrint())
}

func detectedResource(ctx context.Context) (*resource.Resource, error) {
	srv := semconv.ServiceNameKey.String(serviceName)

	var instID label.KeyValue
	if host, ok := os.LookupEnv("HOSTNAME"); ok && host != "" {
		instID = semconv.ServiceInstanceIDKey.String(host)
	} else {
		instID = semconv.ServiceInstanceIDKey.String(uuid.New().String())
	}

	return resource.New(
		ctx,
		resource.WithAttributes(srv, instID),
		resource.WithDetectors(new(gcp.GCE)),
	)
}

func main() {
	ctx := context.Background()

	exp, err := exporter(ctx)
	if err != nil {
		logrus.WithError(err).Fatal("failed to setup exporter")
	}

	res, err := detectedResource(ctx)
	if err != nil {
		logrus.WithError(err).Fatal("failed to detect resource")
	}

	pusher := push.New(
		basic.New(simple.NewWithInexpensiveDistribution(), exp),
		exp,
		push.WithPeriod(time.Second),
		push.WithResource(res),
	)
	pusher.Start()
	otel.SetMeterProvider(pusher.MeterProvider())
	defer pusher.Stop()

	// Include runtime metric instrumentation.
	if err := runtime.Start(runtime.WithMinimumReadMemStatsInterval(time.Second)); err != nil {
		logrus.WithError(err).Fatal("failed to setup runtime instrumentation")
	}

	// Include host system metric instrumentation.
	if err := host.Start(); err != nil {
		logrus.WithError(err).Fatal("failed to setup host system instrumentation")
	}

	stopChan := make(chan os.Signal, 1)
	signal.Notify(stopChan, syscall.SIGTERM, syscall.SIGINT)
	<-stopChan
}
