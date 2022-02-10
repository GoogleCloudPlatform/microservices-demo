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
using OpenTracing;
using OpenTracing.Propagation;
using OpenTracing.Util;
using System.Collections;

namespace cartservice
{

    // Cart wrapper to deal with grpc communication
    internal class CartServiceImpl : CartServiceBase
    {
        private ITracer tracer;
        private ICartStore cartStore;
        private readonly static Empty Empty = new Empty();

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
            this.tracer = GlobalTracer.Instance;
        }

        public ISpanContext TraceContextFromGrpcContext(Grpc.Core.ServerCallContext context)
        {
            var carrier = new MetadataCarrier(context.RequestHeaders);
            return this.tracer.Extract(BuiltinFormats.HttpHeaders, carrier);
        }

        public async override Task<Empty> AddItem(AddItemRequest request, Grpc.Core.ServerCallContext context)
        {
            using (IScope scope = this.tracer.BuildSpan("AddItem").AsChildOf(this.TraceContextFromGrpcContext(context)).StartActive())
            {
                ISpan span = scope.Span;
                span.SetTag("span.kind", "server");
                span.SetTag("component", "rpc");
                span.SetTag("grpc.method", "/hipstershop.CartService/AddItem");

                await cartStore.AddItemAsync(request.UserId, request.Item.ProductId, request.Item.Quantity);
                return Empty;
            }
        }

        public async override Task<Empty> EmptyCart(EmptyCartRequest request, ServerCallContext context)
        {
            using (IScope scope = this.tracer.BuildSpan("EmptyCart").AsChildOf(this.TraceContextFromGrpcContext(context)).StartActive())
            {
                ISpan span = scope.Span;
                span.SetTag("span.kind", "server");
                span.SetTag("component", "rpc");
                span.SetTag("grpc.method", "/hipstershop.CartService/EmptyCart");

                await cartStore.EmptyCartAsync(request.UserId);
                return Empty;
            }
        }

        public override Task<Hipstershop.Cart> GetCart(GetCartRequest request, ServerCallContext context)
        {
            using (IScope scope = this.tracer.BuildSpan("GetCart").AsChildOf(this.TraceContextFromGrpcContext(context)).StartActive())
            {
                ISpan span = scope.Span;
                span.SetTag("span.kind", "server");
                span.SetTag("component", "rpc");
                span.SetTag("grpc.method", "/hipstershop.CartService/GetCart");

                return cartStore.GetCartAsync(request.UserId);
            }
        }
    }

    internal class MetadataCarrier : ITextMap
    {
        private readonly Metadata _metadata;

        public MetadataCarrier(Metadata metadata)
        {
            _metadata = metadata;
        }

        public void Set(string key, string value)
        {
            _metadata.Add(key, value);
        }

        public IEnumerator<KeyValuePair<string, string>> GetEnumerator()
        {
            foreach (var entry in _metadata)
            {
                if (entry.IsBinary)
                    continue;

                yield return new KeyValuePair<string, string>(entry.Key, entry.Value);
            }
        }

        IEnumerator IEnumerable.GetEnumerator()
        {
            return GetEnumerator();
        }
    }
}