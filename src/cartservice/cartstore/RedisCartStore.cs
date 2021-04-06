// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using cartservice.interfaces;
using Google.Protobuf;
using Grpc.Core;
using Hipstershop;
using StackExchange.Redis;
using OpenTelemetry.Trace;

namespace cartservice.cartstore
{
  public class RedisCartStore : ICartStore
  {

    private const string CART_FIELD_NAME = "cart";

    private volatile ConnectionMultiplexer redis;
    private readonly object locker = new object();
    private readonly byte[] emptyCartBytes;

    private static double EXTERNAL_DB_ACCESS_RATE = Convert.ToDouble(Environment.GetEnvironmentVariable("EXTERNAL_DB_ACCESS_RATE"));
    private static Int16 EXTERNAL_DB_MAX_DURATION_MILLIS = Convert.ToInt16(Environment.GetEnvironmentVariable("EXTERNAL_DB_MAX_DURATION_MILLIS"));
    private static double EXTERNAL_DB_ERROR_RATE = Convert.ToDouble(Environment.GetEnvironmentVariable("EXTERNAL_DB_ERROR_RATE"));

    public static string EXTERNAL_DB_NAME = Environment.GetEnvironmentVariable("EXTERNAL_DB_NAME") ?? "global.datastore";

    private readonly Tracer _tracer;
    private readonly Random _random;

    public RedisCartStore(ConnectionMultiplexer connection)
    {
      redis = connection;
      // Serialize empty cart into byte array.
      var cart = new Hipstershop.Cart();
      emptyCartBytes = cart.ToByteArray();

      _tracer = Program.tracerProvider.GetTracer("cartservice");
      _random = new Random();
    }

    public Task InitializeAsync()
    {
      return Task.CompletedTask;
    }

    public async Task AddItemAsync(string userId, string productId, int quantity)
    {
      Console.WriteLine($"AddItemAsync called with userId={userId}, productId={productId}, quantity={quantity}");

      try
      {
        var db = redis.GetDatabase();

        // Access the cart from the cache
        var value = await db.HashGetAsync(userId, CART_FIELD_NAME);

        Hipstershop.Cart cart;
        if (value.IsNull)
        {
          cart = new Hipstershop.Cart();
          cart.UserId = userId;
          cart.Items.Add(new Hipstershop.CartItem { ProductId = productId, Quantity = quantity });
        }
        else
        {
          cart = Hipstershop.Cart.Parser.ParseFrom(value);
          var existingItem = cart.Items.SingleOrDefault(i => i.ProductId == productId);
          if (existingItem == null)
          {
            cart.Items.Add(new Hipstershop.CartItem { ProductId = productId, Quantity = quantity });
          }
          else
          {
            existingItem.Quantity += quantity;
          }
        }

        await db.HashSetAsync(userId, new[] { new HashEntry(CART_FIELD_NAME, cart.ToByteArray()) });

        // Attempt to access "external database" some percentage of the time
        if (_random.NextDouble() < EXTERNAL_DB_ACCESS_RATE)
        {
          using (var span = _tracer.StartActiveSpan("Cart.DbQuery.UpdateCart", SpanKind.Client))
          {
            span
                .SetAttribute("db.system", "postgres")
                .SetAttribute("db.type", "postgres")
                .SetAttribute("peer.service", EXTERNAL_DB_NAME + ":98321");

            if (_random.NextDouble() < EXTERNAL_DB_ERROR_RATE)
            {
              span.SetAttribute("error", "true");
            }

            Thread.Sleep(TimeSpan.FromMilliseconds(_random.Next(0, EXTERNAL_DB_MAX_DURATION_MILLIS)));
            span.End();
          }
        }

      }
      catch (Exception ex)
      {
        throw new RpcException(new Grpc.Core.Status(StatusCode.FailedPrecondition, $"Can't access cart storage. {ex}"));
      }
    }

    public async Task EmptyCartAsync(string userId)
    {
      Console.WriteLine($"EmptyCartAsync called with userId={userId}");

      try
      {
        var db = redis.GetDatabase();

        // Update the cache with empty cart for given user
        await db.HashSetAsync(userId, new[] { new HashEntry(CART_FIELD_NAME, emptyCartBytes) });
      }
      catch (Exception ex)
      {
        throw new RpcException(new Grpc.Core.Status(StatusCode.FailedPrecondition, $"Can't access cart storage. {ex}"));
      }
    }

    public async Task<Hipstershop.Cart> GetCartAsync(string userId)
    {
      Console.WriteLine($"GetCartAsync called with userId={userId}");

      try
      {
        var db = redis.GetDatabase();

        // Access the cart from the cache
        var value = await db.HashGetAsync(userId, CART_FIELD_NAME);

        if (!value.IsNull)
        {
          // Attempt to access "external database" some percentage of the time. This happens after
          // our redis call to represent some kind fo "cache miss" or secondary call that is not
          // in the redis cache.
          if (_random.NextDouble() < EXTERNAL_DB_ACCESS_RATE)
          {
            using (var span = _tracer.StartActiveSpan("Cart.DbQuery.GetCart", SpanKind.Client))
            {
              span
                  .SetAttribute("db.system", "postgres")
                  .SetAttribute("db.type", "postgres")
                  .SetAttribute("peer.service", EXTERNAL_DB_NAME + ":98321");

              if (_random.NextDouble() < EXTERNAL_DB_ERROR_RATE)
              {
                span.SetAttribute("error", "true");
              }

              Thread.Sleep(TimeSpan.FromMilliseconds(_random.Next(0, EXTERNAL_DB_MAX_DURATION_MILLIS)));
              span.End();
            }
          }

          return Hipstershop.Cart.Parser.ParseFrom(value);
        }

        // We decided to return empty cart in cases when user wasn't in the cache before
        return new Hipstershop.Cart();
      }
      catch (Exception ex)
      {
        throw new RpcException(new Grpc.Core.Status(StatusCode.FailedPrecondition, $"Can't access cart storage. {ex}"));
      }
    }

    public bool Ping()
    {
      try
      {
        var cache = redis.GetDatabase();
        var res = cache.Ping();
        return res != TimeSpan.Zero;
      }
      catch (Exception)
      {
        return false;
      }
    }
  }
}
