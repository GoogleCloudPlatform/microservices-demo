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
using System.Collections.Generic;
using System.Linq;
using System.Diagnostics;
using System.Threading.Tasks;
using cartservice.interfaces;
using Grpc.Core;
using Hipstershop;
using OpenTelemetry;
using OpenTelemetry.Trace;
using OpenTelemetry.Context.Propagation;
using static Hipstershop.CartService;

namespace cartservice
{

    // Cart wrapper to deal with grpc communication
    internal class CartServiceImpl : CartServiceBase
    {
        private ICartStore cartStore;
        private readonly static Empty Empty = new Empty();

        private static readonly ActivitySource TraceActivitySource = new ActivitySource(
            "opentelemetry.dotnet");

        private static readonly B3Propagator b3propagator = new B3Propagator();

        private static readonly Func<Grpc.Core.Metadata, string, IEnumerable<string>> Getter =
            (md, key) =>
            {
                List<string> result = new List<string>();
                foreach (var item in md.GetAll(key.ToLower()))
                {
                    result.Add(item.Value);
                }
                return result;
            };

        public CartServiceImpl(ICartStore cartStore)
        {
            this.cartStore = cartStore;
        }
        public ActivityContext traceContextFromGrpcContext(Grpc.Core.ServerCallContext context)
        {
            var spanCtx = new PropagationContext();
            return b3propagator.Extract(spanCtx, context.RequestHeaders, Getter).ActivityContext;
        }

        public async override Task<Empty> AddItem(AddItemRequest request, Grpc.Core.ServerCallContext context)
        {
            using (var activity = TraceActivitySource.StartActivity("AddItem", ActivityKind.Server, this.traceContextFromGrpcContext(context)))
            {
                activity?.SetTag("component", "rpc");
                activity?.SetTag("grpc.method", "/hipstershop.CartService/AddItem");
                await cartStore.AddItemAsync(request.UserId, request.Item.ProductId, request.Item.Quantity);
                return Empty;
            }
        }

        public async override Task<Empty> EmptyCart(EmptyCartRequest request, ServerCallContext context)
        {
            using (var activity = TraceActivitySource.StartActivity("EmptyCart", ActivityKind.Server, this.traceContextFromGrpcContext(context)))
            {
                activity?.SetTag("component", "rpc");
                activity?.SetTag("grpc.method", "/hipstershop.CartService/EmptyCart");
                await cartStore.EmptyCartAsync(request.UserId);
                return Empty;
            }
        }

        public override Task<Hipstershop.Cart> GetCart(GetCartRequest request, ServerCallContext context)
        {
            using (var activity = TraceActivitySource.StartActivity("GetCart", ActivityKind.Server, this.traceContextFromGrpcContext(context)))
            {
                activity?.SetTag("component", "rpc");
                activity?.SetTag("grpc.method", "/hipstershop.CartService/GetCart");
                return cartStore.GetCartAsync(request.UserId);
            }
        }
    }
}