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
        private readonly ICartStore _cartStore;
        private readonly ILogger<CartService> _logger;

        public CartService(ILogger<CartService> logger, ICartStore cartStore)
        {
            _logger = logger;
            _cartStore = cartStore;
        }

        public async override Task<Empty> AddItem(AddItemRequest request, ServerCallContext context)
        {
            try
            {
                MaybeThrowError();
            }
            catch (RpcException ex)
            {
                var activity = System.Diagnostics.Activity.Current;
                activity?.SetStatus(global::OpenTelemetry.Trace.Status.Error.WithDescription(ex.Message));
                activity?.RecordException(ex);
                throw;
            }

            await _cartStore.AddItemAsync(request.UserId, request.Item.ProductId, request.Item.Quantity);
            _logger.LogInformation("CartService.AddItem UserId={UserId}, ProductId={ProductId}, Quantity={Quantity}",
                request.UserId,
                request.Item.ProductId,
                request.Item.Quantity);
            return Empty;
        }

        public override Task<Cart> GetCart(GetCartRequest request, ServerCallContext context)
        {
            try
            {
                MaybeThrowError();
            }
            catch (RpcException ex)
            {
                var activity = System.Diagnostics.Activity.Current;
                activity?.SetStatus(global::OpenTelemetry.Trace.Status.Error.WithDescription(ex.Message));
                activity?.RecordException(ex);
                throw;
            }

            _logger.LogInformation("CartService.GetCart UserId={UserId}", request.UserId);
            return _cartStore.GetCartAsync(request.UserId);
        }

        public async override Task<Empty> EmptyCart(EmptyCartRequest request, ServerCallContext context)
        {
            try
            {
                MaybeThrowError();
            }
            catch (RpcException ex)
            {
                var activity = System.Diagnostics.Activity.Current;
                activity?.SetStatus(global::OpenTelemetry.Trace.Status.Error.WithDescription(ex.Message));
                activity?.RecordException(ex);
                throw;
            }
            
            await _cartStore.EmptyCartAsync(request.UserId);
            _logger.LogInformation("CartService.EmptyCart UserId={UserId}", request.UserId);
            return Empty;
        }

        private void MaybeThrowError()
        {
            if (_random.Next() % 10 == 0)
            {
                var ex = new RpcException(new Grpc.Core.Status(Grpc.Core.StatusCode.Unknown, "I'm a random error"));
                _logger.LogError(ex, "I'm a random error");
                throw ex;
            }
        }
    }
}