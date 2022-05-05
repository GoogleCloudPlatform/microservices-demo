// Copyright 2020 Google LLC
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
using System.Diagnostics;
using System.Threading.Tasks;
using Grpc.Core;
using Microsoft.Extensions.Logging;
using cartservice.cartstore;
using Hipstershop;
using OpenTelemetry.Trace;

namespace cartservice.services
{
    public class CartService : Hipstershop.CartService.CartServiceBase
    {
        private static readonly Random _random = new Random();
        private readonly static Empty Empty = new Empty();
        private ICartStore _cartStore;
        private readonly ILogger<CartService> _logger;

        public CartService(ILogger<CartService> logger, ICartStore cartStore)
        {
            _logger = logger;
            _cartStore = cartStore;
        }

        public async override Task<Empty> AddItem(AddItemRequest request, ServerCallContext context)
        {
            await _cartStore.AddItemAsync(request.UserId, request.Item.ProductId, request.Item.Quantity);
            _logger.LogInformation("CartService.AddItem UserId={UserId}, ProductId={ProductId}, Quantity={Quantity}",
                request.UserId,
                request.Item.ProductId,
                request.Item.Quantity);
            return Empty;
        }

        public override Task<Cart> GetCart(GetCartRequest request, ServerCallContext context)
        {
            _logger.LogInformation("CartService.GetCart UserId={UserId}", request.UserId);
            return _cartStore.GetCartAsync(request.UserId);
        }

        public async override Task<Empty> EmptyCart(EmptyCartRequest request, ServerCallContext context)
        {
            this._cartStore = _random.Next() % 5 != 0 
                ? this._cartStore
                : new RedisCartStore("badhost:4567");

            try
            {
                await _cartStore.EmptyCartAsync(request.UserId);
            }
            catch (Exception e)
            {
                // Recording the original exception to preserve the stack trace on the activity event
                Activity.Current?.RecordException(e);

                // Throw a new exception and use its message for the status description
                var ex = new Exception("Can't access cart storage.");
                Activity.Current?.SetStatus(ActivityStatusCode.Error, ex.Message);
                throw ex;
            }
            
            _logger.LogInformation("CartService.EmptyCart UserId={UserId}", request.UserId);
            return Empty;
        }
    }
}