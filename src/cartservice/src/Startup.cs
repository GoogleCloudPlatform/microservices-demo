using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging; // Keep this using statement as other classes might use ILogger
using cartservice.cartstore;
using cartservice.services;
using Microsoft.Extensions.Caching.StackExchangeRedis;

namespace cartservice
{
    public class Startup
    {
        // private readonly ILogger<Startup> _logger; // This line should be removed or commented out

        public IConfiguration Configuration { get; }

        public Startup(IConfiguration configuration) // Constructor without ILogger
        {
            Configuration = configuration;
            // _logger = logger; // This line should be removed or commented out
        }

        // This method gets called by the runtime. Use this method to add services to the container.
        // For more information on how to configure your application, visit https://go.microsoft.com/fwlink/?LinkID=398940
        public void ConfigureServices(IServiceCollection services)
        {
            // Configure CartStore based on environment variable or appsettings.json
            string cartStoreType = Configuration["CartStore"];
            // _logger.LogInformation($"CartStore type configured: {cartStoreType}"); // COMMENTED OUT THIS LINE

            if (string.Equals(cartStoreType, "AzureMySQL", StringComparison.OrdinalIgnoreCase))
            {
                string connectionString = Configuration["AZURE_MYSQL_CONNECTION_STRING"];
                if (string.IsNullOrEmpty(connectionString))
                {
                    // _logger.LogError("AZURE_MYSQL_CONNECTION_STRING is not configured. Please set it via environment variable or appsettings.json."); // COMMENTED OUT THIS LINE
                    throw new ApplicationException("AZURE_MYSQL_CONNECTION_STRING is missing.");
                }
                services.AddSingleton<ICartStore>(serviceProvider =>
                {
                    // This logger is for AzureMySQLCartStore, which is still injected correctly
                    var loggerForStore = serviceProvider.GetRequiredService<ILogger<AzureMySQLCartStore>>();
                    return new AzureMySQLCartStore(connectionString, loggerForStore);
                });
                // _logger.LogInformation("Using AzureMySQLCartStore."); // COMMENTED OUT THIS LINE
            }
            else if (string.Equals(cartStoreType, "Redis", StringComparison.OrdinalIgnoreCase))
            {
                string redisAddress = Configuration["REDIS_ADDR"];
                services.AddStackExchangeRedisCache(options =>
                {
                    options.Configuration = redisAddress ?? "redis-cart:6379";
                    options.InstanceName = "RedisCartStore";
                });
                services.AddSingleton<ICartStore, RedisCartStore>();
                // _logger.LogInformation("Using RedisCartStore."); // COMMENTED OUT THIS LINE
            }
            // Temporarily commented out AlloyDB section. Uncomment and adjust if needed later.
            /*
            else if (string.Equals(cartStoreType, "AlloyDB", StringComparison.OrdinalIgnoreCase))
            {
                // _logger.LogInformation("Creating AlloyDB cart store"); // COMMENTED OUT THIS LINE
                services.AddSingleton<ICartStore>(
                    new cartstore.AlloyDBCartStore(
                        Configuration["ALLOYDB_CONNECTION_STRING"],
                        Configuration["ALLOYDB_SECRET_NAME"],
                        Configuration["GCP_PROJECT_ID"],
                        Configuration["ALLOYDB_REGION"]));
                // _logger.LogInformation("Using AlloyDBCartStore."); // COMMENTED OUT THIS LINE
            }
            */
            else // Default to the original in-memory cache setup using RedisCartStore if no specific store is configured
            {
                // _logger.LogWarning("No specific cart store was configured or recognized (e.g., AzureMySQL, Redis, AlloyDB). Falling back to in-memory store (using RedisCartStore with DistributedMemoryCache)."); // COMMENTED OUT THIS LINE
                services.AddDistributedMemoryCache(); // This sets up an in-memory IDistributedCache
                services.AddSingleton<ICartStore, RedisCartStore>(); // This uses the in-memory cache as its backend
            }

            services.AddGrpc();
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseRouting();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapGrpcService<CartService>();
                endpoints.MapGrpcService<cartservice.services.HealthCheckService>();

                endpoints.MapGet("/", async context =>
                {
                    await context.Response.WriteAsync("Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");
                });
            });
        }
    }
}