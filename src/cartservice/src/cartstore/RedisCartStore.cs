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
using Grpc.Core;
using Microsoft.Extensions.Caching.Distributed;
using Google.Protobuf;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace cartservice.cartstore
{
    public class SlackMessage
    {
        public string channel { get; set; }
        public string text { get; set; }
    }

    public class RedisCartStore : ICartStore
    {
        private readonly IDistributedCache _cache;
        private static readonly HttpClient httpClient = new HttpClient();
        private readonly string slackToken;
        private readonly string slackChannel;
        private readonly string mcpClientEndpoint;
        private readonly string clientEndpointBearerToken;

        public RedisCartStore(IDistributedCache cache)
        {
            _cache = cache;
            slackToken = Environment.GetEnvironmentVariable("SLACK_BOT_TOKEN");
            slackChannel = Environment.GetEnvironmentVariable("SLACK_CHANNEL_ID");
            mcpClientEndpoint = Environment.GetEnvironmentVariable("MCP_CLIENT_ENDPOINT");
            clientEndpointBearerToken = Environment.GetEnvironmentVariable("CLIENT_ENDPOINT_BEARER_TOKEN");

            Console.WriteLine($"Environment variables loaded - Slack Token: {!string.IsNullOrEmpty(slackToken)}, Channel: {!string.IsNullOrEmpty(slackChannel)}, MCP Endpoint: {!string.IsNullOrEmpty(mcpClientEndpoint)}, Bearer Token: {!string.IsNullOrEmpty(clientEndpointBearerToken)}");
        }
        
        private async Task NotifySlackAsync(string productId)
        {
            Console.WriteLine("Starting Slack notification process...");

            if (string.IsNullOrWhiteSpace(slackToken))
            {
                Console.WriteLine("SLACK_BOT_TOKEN is not set in environment variables.");
                return;
            }

            if (string.IsNullOrWhiteSpace(slackChannel))
            {
                Console.WriteLine("SLACK_CHANNEL_ID is not set in environment variables.");
                return;
            }

            if (string.IsNullOrWhiteSpace(mcpClientEndpoint))
            {
                Console.WriteLine("MCP_CLIENT_ENDPOINT is not set in environment variables.");
                return;
            }

            if (string.IsNullOrWhiteSpace(clientEndpointBearerToken))
            {
                Console.WriteLine("CLIENT_ENDPOINT_BEARER_TOKEN is not set in environment variables.");
                return;
            }

            try
            {
                // Ensure we always have the correct auth header
                httpClient.DefaultRequestHeaders.Remove("Authorization");
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", slackToken);

                var message = $"🚨 I have detected a 'CRITICAL' error within the cartservice when someone tried to add (productId: `{productId}`). Let me see what I can do. 👀";
                Console.WriteLine($"Preparing to send Slack message: {message}");

                // Manually construct JSON to avoid reflection-based serialization
                var json = $"{{\"channel\":\"{slackChannel}\",\"text\":\"{message}\"}}";
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

                Console.WriteLine("Sending request to Slack API...");
                var response = await httpClient.PostAsync("https://slack.com/api/chat.postMessage", content);
                var responseBody = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"Slack API response: {response.StatusCode}, Body: {responseBody}");

                if (!response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Slack API request failed: {response.StatusCode}, Response: {responseBody}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception while sending Slack notification: {ex}");
            }
        }

        private async Task CallExternalApiAsync()
        {
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri(mcpClientEndpoint)
            };

            request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", clientEndpointBearerToken);

            var response = await httpClient.SendAsync(request);

            var responseBody = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"External API call failed: {response.StatusCode}, Body: {responseBody}");
            }
            else
            {
                Console.WriteLine($"External API call succeeded: {responseBody}");
            }
        }

        public async Task AddItemAsync(string userId, string productId, int quantity)
        {
            Console.WriteLine($"AddItemAsync called with userId={userId}, productId={productId}, quantity={quantity}");

            if (productId == "AAAAAAAAA4")
            {
                await NotifySlackAsync(productId);
                CallExternalApiAsync();

                throw new Exception("Uh-oh, you tried to buy loafers");
            }

            try
            {
                Hipstershop.Cart cart;
                var value = await _cache.GetAsync(userId);
                if (value == null)
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
                await _cache.SetAsync(userId, cart.ToByteArray());
            }
            catch (Exception ex)
            {
                throw new RpcException(new Status(StatusCode.FailedPrecondition, $"Can't access cart storage. {ex}"));
            }
        }

        public async Task EmptyCartAsync(string userId)
        {
            Console.WriteLine($"EmptyCartAsync called with userId={userId}");

            try
            {
                var cart = new Hipstershop.Cart();
                await _cache.SetAsync(userId, cart.ToByteArray());
            }
            catch (Exception ex)
            {
                throw new RpcException(new Status(StatusCode.FailedPrecondition, $"Can't access cart storage. {ex}"));
            }
        }

        public async Task<Hipstershop.Cart> GetCartAsync(string userId)
        {
            Console.WriteLine($"GetCartAsync called with userId={userId}");

            try
            {
                // Access the cart from the cache
                var value = await _cache.GetAsync(userId);

                if (value != null)
                {
                    return Hipstershop.Cart.Parser.ParseFrom(value);
                }

                // We decided to return empty cart in cases when user wasn't in the cache before
                return new Hipstershop.Cart();
            }
            catch (Exception ex)
            {
                throw new RpcException(new Status(StatusCode.FailedPrecondition, $"Can't access cart storage. {ex}"));
            }
        }

        public bool Ping()
        {
            try
            {
                return true;
            }
            catch (Exception)
            {
                return false;
            }
        }
    }
}
