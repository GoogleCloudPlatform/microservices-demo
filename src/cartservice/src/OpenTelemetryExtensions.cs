using System;
using cartservice.cartstore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using OpenTelemetry;
using OpenTelemetry.Exporter;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

namespace cartservice.OpenTelemetry
{
    public static class OpenTelemetryExtensions
    {
        private static ResourceBuilder ResourceBuilder =
            ResourceBuilder
                .CreateDefault()
                .AddService("CartService")
                .AddTelemetrySdk();

        private static MeterProvider MeterProvider;

        public static void AddOpenTelemetry(this IServiceCollection services, ICartStore cartStore)
        {
            services.AddOpenTelemetryTracing(builder => {
                builder.SetResourceBuilder(ResourceBuilder);
                
                builder.AddAspNetCoreInstrumentation();

                if (cartStore is RedisCartStore redisCartStore)
                {
                    builder.AddRedisInstrumentation(redisCartStore.ConnectionMultiplexer);
                }

                builder
                    .AddOtlpExporter(ConfigureOtlpExporter);
            });

            MeterProvider = Sdk.CreateMeterProviderBuilder()
                .SetResourceBuilder(ResourceBuilder)
                .AddAspNetCoreInstrumentation()
                .AddOtlpExporter(ConfigureOtlpExporter)
                .Build();
        }

        public static void ConfigureOpenTelemetry(this ILoggingBuilder builder)
        {
            builder
                .AddOpenTelemetry(options =>
                {
                    var otlpExporterOptions = new OtlpExporterOptions
                    {
                        Endpoint = new Uri(Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT"))
                    };

                    options
                        .SetResourceBuilder(ResourceBuilder)
                        .AddProcessor(new SpanEventLogProcessor())
                        .AddProcessor(new BatchLogRecordExportProcessor(new OtlpLogExporter(otlpExporterOptions)));
                });
        }

        private static void ConfigureOtlpExporter(OtlpExporterOptions options)
        {
            options.Endpoint = new Uri(Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT"));
            options.AggregationTemporality = AggregationTemporality.Delta;
        }
    }
}
