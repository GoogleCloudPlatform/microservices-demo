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
using cartservice.interfaces;
using Hipstershop;
using OpenCensus.Trace;
using OpenCensus.Trace.Sampler;

namespace cartservice.cartstore
{
    /// <summary>
    /// Wrapper for Cart Store - instrumented with OpenCensus tracing
    /// </summary>
    internal class InstrumentedCartStore : ICartStore
    {
        private readonly ICartStore cartStore;
        private static ITracer tracer = Tracing.Tracer;
        private ISpanBuilder initializeSpanBuilder, addItemSpanBuilder, emptySpanBuilder, getItemSpanBuilder, pingSpanBuilder; 

        public InstrumentedCartStore(ICartStore cartStore)
        {
            this.cartStore = cartStore;

            // Create Span Builders for tracing
            initializeSpanBuilder = CreateSpanBuilder("Initialize Cart Store");
            addItemSpanBuilder = CreateSpanBuilder("Add Item");
            emptySpanBuilder = CreateSpanBuilder("Empty Cart");
            getItemSpanBuilder = CreateSpanBuilder("Get Cart");
            pingSpanBuilder = CreateSpanBuilder("Ping");
        }
        public Task AddItemAsync(string userId, string productId, int quantity)
        {
            using (var span = addItemSpanBuilder.StartScopedSpan())
            {
                return cartStore.AddItemAsync(userId, productId, quantity);
            }
        }

        public Task EmptyCartAsync(string userId)
        {
            using (var span = emptySpanBuilder.StartScopedSpan())
            {
                return cartStore.EmptyCartAsync(userId);
            }
        }

        public Task<Cart> GetCartAsync(string userId)
        {
            using (var span = getItemSpanBuilder.StartScopedSpan())
            {
                return cartStore.GetCartAsync(userId);
            }
        }

        public Task InitializeAsync()
        {
            using (var span = initializeSpanBuilder.StartScopedSpan())
            {
                return cartStore.InitializeAsync();
            }
        }

        public bool Ping()
        {
            using (var span = pingSpanBuilder.StartScopedSpan())
            {
                return cartStore.Ping();
            }
        }

        public static ICartStore Create(string redis)
        {
            ICartStore cartStore;

            // Redis was specified
            if (!string.IsNullOrEmpty(redis))
            {
                // If you want to start cart store using local cache in process, you can replace the following line with this:
                // cartStore = new LocalCartStore();
                cartStore = new RedisCartStore(redis);
            }
            else
            {
                Console.WriteLine("Redis cache host(hostname+port) was not specified. Starting a cart service using local store");
                Console.WriteLine("If you wanted to use Redis Cache as a backup store, you should provide its address via command line or REDIS_ADDRESS environment variable.");
                cartStore = new LocalCartStore();
            }

            // We create the cart store wrapped with instrumentation
            return new InstrumentedCartStore(cartStore);
        }

        private static ISpanBuilder CreateSpanBuilder(string spanName)
        {
            var spanBuilder = tracer
                .SpanBuilder(spanName)
                .SetRecordEvents(true)
                .SetSampler(Samplers.AlwaysSample);

            return spanBuilder;
        }
    }
}