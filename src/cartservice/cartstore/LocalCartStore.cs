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
using System.Collections.Concurrent;
using System.Threading.Tasks;
using System.Linq;
using cartservice.interfaces;
using Hipstershop;

namespace cartservice.cartstore
{
    internal class LocalCartStore : ICartStore
    {
        // Maps between user and their cart
        private ConcurrentDictionary<string, Hipstershop.Cart> userCartItems = new ConcurrentDictionary<string, Hipstershop.Cart>();
        private readonly Hipstershop.Cart emptyCart = new Hipstershop.Cart();

        public Task InitializeAsync()
        {
            Console.WriteLine("Local Cart Store was initialized");

            return Task.CompletedTask;
        }

        public Task AddItemAsync(string userId, string productId, int quantity)
        {
            Console.WriteLine($"AddItemAsync called with userId={userId}, productId={productId}, quantity={quantity}");
            var newCart = new Hipstershop.Cart
                {
                    UserId = userId,
                    Items = { new Hipstershop.CartItem { ProductId = productId, Quantity = quantity } }
                };
            userCartItems.AddOrUpdate(userId, newCart,
            (k, exVal) =>
            {
                // If the item exists, we update its quantity
                var existingItem = exVal.Items.SingleOrDefault(item => item.ProductId == productId);
                if (existingItem != null)
                {
                    existingItem.Quantity += quantity;
                }
                else
                {
                    exVal.Items.Add(new Hipstershop.CartItem { ProductId = productId, Quantity = quantity });
                }

                return exVal;
            });

            return Task.CompletedTask;
        }

        public Task EmptyCartAsync(string userId)
        {
            Console.WriteLine($"EmptyCartAsync called with userId={userId}");
            userCartItems[userId] = emptyCart;

            return Task.CompletedTask;
        }

        public Task<Hipstershop.Cart> GetCartAsync(string userId)
        {
            Console.WriteLine($"GetCartAsync called with userId={userId}");
            Hipstershop.Cart cart = null;
            if (!userCartItems.TryGetValue(userId, out cart))
            {
                Console.WriteLine($"No carts for user {userId}");
                return Task.FromResult(emptyCart);
            }

            return Task.FromResult(cart);
        }

        public bool Ping()
        {
            return true;
        }
    }
}