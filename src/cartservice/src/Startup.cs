using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Hosting;
using cartservice.cartstore;
using cartservice.services;

var builder = WebApplication.CreateBuilder(args);

string redisAddress = builder.Configuration["REDIS_ADDR"];
ICartStore cartStore = null;
if (!string.IsNullOrEmpty(redisAddress))
{
    cartStore = new RedisCartStore(redisAddress);
}
else
{
    Console.WriteLine("Redis cache host(hostname+port) was not specified. Starting a cart service using local store");
    Console.WriteLine("If you wanted to use Redis Cache as a backup store, you should provide its address via command line or REDIS_ADDR environment variable.");
    cartStore = new LocalCartStore();
}
cartStore.InitializeAsync().GetAwaiter().GetResult();
Console.WriteLine("Initialization completed");
builder.Services.AddSingleton<ICartStore>(cartStore);
builder.Services.AddGrpc();

var app = builder.Build();
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
app.UseRouting();
app.UseEndpoints(endpoints =>
{
    endpoints.MapGrpcService<CartService>();
    endpoints.MapGrpcService<cartservice.services.HealthCheckService>();
});
app.MapGet("/", async context =>
{
    await context.Response.WriteAsync("Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");
});
app.Run();