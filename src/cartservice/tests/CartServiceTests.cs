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
using System.Threading.Tasks;
using Grpc.Core;
using Hipstershop;
using Xunit;
using static Hipstershop.CartService;

namespace cartservice
{
    public class E2ETests
    {
        private static string serverHostName = "localhost";
        private static int port = 7070;

        [Fact]
        public async Task GetItem_NoAddItemBefore_EmptyCartReturned()
        {
            string userId = Guid.NewGuid().ToString();

            // Construct server's Uri
            string targetUri = $"{serverHostName}:{port}";

            // Create a GRPC communication channel between the client and the server
            var channel = new Channel(targetUri, ChannelCredentials.Insecure);

            var client = new CartServiceClient(channel);

            var request = new GetCartRequest
            {
                UserId = userId,
            };

            var cart = await client.GetCartAsync(request);
            Assert.NotNull(cart);

            // All grpc objects implement IEquitable, so we can compare equality with by-value semantics
            Assert.Equal(new Cart(), cart);
        }

        [Fact]
        public async Task AddItem_ItemExists_Updated()
        {
            string userId = Guid.NewGuid().ToString();

            // Construct server's Uri
            string targetUri = $"{serverHostName}:{port}";

            // Create a GRPC communication channel between the client and the server
            var channel = new Channel(targetUri, ChannelCredentials.Insecure);
            
            var client = new CartServiceClient(channel);
            var request = new AddItemRequest
            {
                UserId = userId,
                Item = new CartItem
                {
                    ProductId = "1",
                    Quantity = 1
                }
            };

            // First add - nothing should fail
            await client.AddItemAsync(request);

            // Second add of existing product - quantity should be updated
            await client.AddItemAsync(request);
            
            var getCartRequest = new GetCartRequest
            {
                UserId = userId
            };
            var cart = await client.GetCartAsync(getCartRequest);
            Assert.NotNull(cart);
            Assert.Equal(userId, cart.UserId);
            Assert.Single(cart.Items);
            Assert.Equal(2, cart.Items[0].Quantity);

            // Cleanup
            await client.EmptyCartAsync(new EmptyCartRequest{ UserId = userId });
        }

        [Fact]
        public async Task AddItem_New_Inserted()
        {
            string userId = Guid.NewGuid().ToString();

            // Construct server's Uri
            string targetUri = $"{serverHostName}:{port}";

            // Create a GRPC communication channel between the client and the server
            var channel = new Channel(targetUri, ChannelCredentials.Insecure);
            
            // Create a proxy object to work with the server
            var client = new CartServiceClient(channel);

            var request = new AddItemRequest
            {
                UserId = userId,
                Item = new CartItem
                {
                    ProductId = "1",
                    Quantity = 1
                }
            };

            await client.AddItemAsync(request);

            var getCartRequest = new GetCartRequest
            {
                UserId = userId
            };
            var cart = await client.GetCartAsync(getCartRequest);
            Assert.NotNull(cart);
            Assert.Equal(userId, cart.UserId);
            Assert.Single(cart.Items);

            await client.EmptyCartAsync(new EmptyCartRequest{ UserId = userId });
            cart = await client.GetCartAsync(getCartRequest);
            Assert.Empty(cart.Items);
        }
    }
}
