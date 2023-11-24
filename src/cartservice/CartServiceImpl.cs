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
using System.Collections.Generic;
using System.Threading.Tasks;
using cartservice.interfaces;
using Grpc.Core;
using Hipstershop;
using static Hipstershop.CartService;
using System.Diagnostics;

namespace cartservice;

// Cart wrapper to deal with grpc communication
internal class CartServiceImpl : CartServiceBase
{
    private ICartStore cartStore;
    private static readonly Empty Empty = new();

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

    // Simplified implementation for B3multi propagator
    // It is needed as we do not have support for Grpc server in OpenTelemetry .NET Instrumentation
    public ActivityContext TraceContextFromGrpcContext(ServerCallContext context)
    {
        try
        {
            string traceId = null;
            string spanId = null;
            string sampled = null;
            foreach (var header in context.RequestHeaders)
            {
                if (header.IsBinary)
                {
                    continue;
                }

                switch (header.Key.ToLowerInvariant())
                {
                    case "x-b3-traceid":
                        traceId = header.Value;
                        if (traceId.Length == 16)
                        {
                            traceId = "0000000000000000" + traceId;
                        }
                        break;
                    case "x-b3-spanid":
                        spanId = header.Value;
                        break;
                    case "x-b3-sampled":
                        sampled = header.Value;
                        break;
                }
            }

            return !string.IsNullOrEmpty(traceId) && !string.IsNullOrEmpty(spanId) && !string.IsNullOrEmpty(sampled)
                ? new ActivityContext(ActivityTraceId.CreateFromString(traceId),
                    ActivitySpanId.CreateFromString(spanId),
                    sampled == "1" ? ActivityTraceFlags.Recorded : ActivityTraceFlags.None, isRemote: true)
                : new ActivityContext();
        }
        catch
        {
            return new ActivityContext();
        }
    }

    public override async Task<Empty> AddItem(AddItemRequest request, ServerCallContext context)
    {
        using var activity = ActivitySourceUtil.ActivitySource.StartActivity("AddItem", ActivityKind.Server, TraceContextFromGrpcContext(context));
        activity?.SetTag("component", "rpc");
        activity?.SetTag("grpc.method", "/hipstershop.CartService/AddItem");

        await cartStore.AddItemAsync(request.UserId, request.Item.ProductId, request.Item.Quantity);
        return Empty;
    }

    public override async Task<Empty> EmptyCart(EmptyCartRequest request, ServerCallContext context)
    {
        using var activity = ActivitySourceUtil.ActivitySource.StartActivity("EmptyCart", ActivityKind.Server, TraceContextFromGrpcContext(context));
        activity?.SetTag("component", "rpc");
        activity?.SetTag("grpc.method", "/hipstershop.CartService/EmptyCart");

        await cartStore.EmptyCartAsync(request.UserId);
        return Empty;
    }

    public override Task<Cart> GetCart(GetCartRequest request, ServerCallContext context)
    {
        using var activity = ActivitySourceUtil.ActivitySource.StartActivity("GetCart", ActivityKind.Server, TraceContextFromGrpcContext(context));
        {
            activity?.SetTag("component", "rpc");
            activity?.SetTag("grpc.method", "/hipstershop.CartService/GetCart");

            return cartStore.GetCartAsync(request.UserId);
        }
    }
}