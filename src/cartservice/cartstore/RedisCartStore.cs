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
using System.Linq;
using System.Threading.Tasks;
using cartservice.interfaces;
using Google.Protobuf;
using Grpc.Core;
using OpenTracing;
using OpenTracing.Util;
using StackExchange.Redis;

namespace cartservice.cartstore
{
  public class RedisCartStore : ICartStore
  {
    private const string CART_FIELD_NAME = "cart";

    private readonly byte[] emptyCartBytes;

    private static double EXTERNAL_DB_ACCESS_RATE = Convert.ToDouble(Environment.GetEnvironmentVariable("EXTERNAL_DB_ACCESS_RATE"));
    private static Int16 EXTERNAL_DB_MAX_DURATION_MILLIS = Convert.ToInt16(Environment.GetEnvironmentVariable("EXTERNAL_DB_MAX_DURATION_MILLIS"));
    private static double EXTERNAL_DB_ERROR_RATE = Convert.ToDouble(Environment.GetEnvironmentVariable("EXTERNAL_DB_ERROR_RATE"));
    private static string EXTERNAL_DB_NAME = Environment.GetEnvironmentVariable("EXTERNAL_DB_NAME") ?? "global.datastore";


    private readonly ITracer _tracer;
    private readonly Random _random;
    private readonly DatabaseCache _dbCache;

    public RedisCartStore(ConnectionMultiplexer connection)
    {
      // Serialize empty cart into byte array.
      var cart = new Hipstershop.Cart();
      emptyCartBytes = cart.ToByteArray();

      _tracer = GlobalTracer.Instance;
      _random = Random.Shared;
      _dbCache = new DatabaseCache(connection);
    }

    public Task InitializeAsync()
    {
      return Task.CompletedTask;
    }

    public async Task AddItemAsync(string userId, string productId, int quantity)
    {
      Console.WriteLine($"AddItemAsync called with userId={userId}, productId={productId}, quantity={quantity}");
      if (!UserId.IsValid(userId))
      {
        throw new ArgumentException(nameof(userId));
      }

      try
      {
        var db = _dbCache.Get();

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
        await ConditionallyMockExternalResourceAccess("Cart.DbQuery.GetCart");
      }
      catch (Exception ex)
      {
        throw new RpcException(new Grpc.Core.Status(StatusCode.FailedPrecondition, $"Can't access cart storage. {ex}"));
      }
    }

    public async Task EmptyCartAsync(string userId)
    {
      Console.WriteLine($"EmptyCartAsync called with userId={userId}");
      if (!UserId.IsValid(userId))
      {
        throw new ArgumentException(nameof(userId));
      }

      try
      {
        var db = _dbCache.Get();

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
      if (!UserId.IsValid(userId))
      {
        throw new ArgumentException(nameof(userId));
      }

      try
      {
        var db = _dbCache.Get();

        // Access the cart from the cache
        var value = await db.HashGetAsync(userId, CART_FIELD_NAME);

        if (!value.IsNull)
        {
          // Attempt to access "external database" some percentage of the time. This happens after
          // our redis call to represent some kind fo "cache miss" or secondary call that is not
          // in the redis cache.
          await ConditionallyMockExternalResourceAccess("Cart.DbQuery.GetCart");

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
        var db = _dbCache.ByPassBlocking();
        var res = db.Ping();
        return res != TimeSpan.Zero;
      }
      catch (Exception)
      {
        return false;
      }
    }

    private async Task<bool> ConditionallyMockExternalResourceAccess(string operation)
    {
      if (_random.NextDouble() >= EXTERNAL_DB_ACCESS_RATE)
      {
        return false;
      }

      using (IScope scope = _tracer.BuildSpan(operation).WithTag("span.kind", "client").StartActive())
      {
        ISpan span = scope.Span;
        span.SetTag("db.system", "postgres");
        span.SetTag("db.type", "postgres");
        span.SetTag("peer.service", EXTERNAL_DB_NAME + ":98321");

        if (_random.NextDouble() < EXTERNAL_DB_ERROR_RATE)
        {
          span.SetTag("error", "true");
        }

        await Task.Delay(_random.Next(0, EXTERNAL_DB_MAX_DURATION_MILLIS));

        return true;
      }
    }
  }
}
