using System;
using cartservice.cartstore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using OpenTelemetry;
using OpenTelemetry.Exporter;
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

                builder
                    .AddOtlpExporter(options => {
                        var opts = GetOptions();
                        options.Endpoint = opts.endpoint;
                        options.Headers = opts.headers;
                    });
            });
        }

        public static void ConfigureOpenTelemetry(this ILoggingBuilder builder)
        {
            builder
                .AddOpenTelemetry(options =>
                {
                    var opts = GetOptions();

                    var otlpExporterOptions = new OtlpExporterOptions
                    {
                        Endpoint = opts.endpoint,
                        Headers = opts.headers,
                    };

                    options
                        .SetResourceBuilder(ResourceBuilder)
                        .AddProcessor(new SpanEventLogProcessor())
                        .AddProcessor(new BatchLogRecordExportProcessor(new OtlpLogExporter(otlpExporterOptions)));
                });
        }

        private static (Uri endpoint, string headers) GetOptions()
        {
            var newRelicApiKey = Environment.GetEnvironmentVariable("NEW_RELIC_API_KEY");
            var otlpEndpoint = "https://" + Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT");
            return (new Uri(otlpEndpoint), $"api-key={newRelicApiKey}");
        }
    }
}
