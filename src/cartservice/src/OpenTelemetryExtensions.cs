using cartservice.cartstore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using OpenTelemetry.Logs;
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

        public static void AddOpenTelemetry(this IServiceCollection services, ICartStore cartStore)
        {
            services.AddOpenTelemetryTracing(builder => {
                builder.SetResourceBuilder(ResourceBuilder);
                
                builder.AddAspNetCoreInstrumentation();

                if (cartStore is RedisCartStore redisCartStore)
                {
                    builder.AddRedisInstrumentation(redisCartStore.ConnectionMultiplexer);
                }

                builder.AddOtlpExporter();
            });

            services.AddOpenTelemetryMetrics(builder => {
                builder
                    .SetResourceBuilder(ResourceBuilder)
                    .AddAspNetCoreInstrumentation()
                    .AddOtlpExporter((exporterOptions, metricReaderOptions) =>
                    {
                        metricReaderOptions.TemporalityPreference = MetricReaderTemporalityPreference.Delta;
                    });
            });
        }

        public static void ConfigureOpenTelemetry(this ILoggingBuilder builder)
        {
            builder
                .AddOpenTelemetry(options =>
                {
                    options.IncludeFormattedMessage = true;

                    options
                        .SetResourceBuilder(ResourceBuilder)
                        .AddProcessor(new SpanEventLogProcessor())
                        .AddOtlpExporter();
                });
        }
    }
}
