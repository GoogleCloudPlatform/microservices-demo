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
using System.Globalization;
using Grpc.Core;
using Microsoft.Extensions.Logging;
using cartservice.cartstore;
using Hipstershop;

namespace cartservice.services
{
    public class CartService : Hipstershop.CartService.CartServiceBase
    {
        private readonly static Empty Empty = new Empty();
        private readonly ICartStore _cartStore;
        public readonly static string CARTSERVICE = "cartservice";

        // NOTE: logLevel must be a GELF valid severity value (WARN or ERROR), INFO if not specified
        public void emitLog(string messageEvent, string logLevel)
        {
            DateTime now = DateTime.UtcNow;
            string timestamp = now.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture);
            string logMessage = "";

            switch (logLevel)
            {
                case "ERROR":
                    logMessage = timestamp + " - " + logLevel + " - " + CARTSERVICE + " - " + messageEvent;
                    Console.WriteLine(logMessage);
                    break;

                case "WARN":
                    logMessage = timestamp + " - " + logLevel + " - " + CARTSERVICE + " - " + messageEvent;
                    Console.WriteLine(logMessage);
                    break;

                default:
                    logMessage = timestamp + " - " + logLevel + " - " + CARTSERVICE + " - " + messageEvent;
                    Console.WriteLine(logMessage);
                    break;
            }
        }

        // Reads gRPC metadata and logs the received requests
        public Tuple<string, string> initMetadata(ServerCallContext context) {
            var RequestID = context.RequestHeaders.Get("requestid").Value;
            var ServiceName = context.RequestHeaders.Get("servicename").Value;
            Tuple<string, string> header = new Tuple<string, string>(RequestID.ToString(), ServiceName.ToString());

            if (RequestID == null && ServiceName == null) {
                emitLog(CARTSERVICE + ": An error occurred while retrieving the RequestID", "ERROR");
                return null;
            }
            emitLog("Received request from " + ServiceName.ToString() + " (request_id: " + RequestID.ToString() + ")", "INFO");
            
            return header;
        }

        public CartService(ICartStore cartStore)
        {
            _cartStore = cartStore;
        }

        public async override Task<Empty> AddItem(AddItemRequest request, ServerCallContext context)
        {
            Tuple<string, string> header = initMetadata(context);

            await _cartStore.AddItemAsync(request.UserId, request.Item.ProductId, request.Item.Quantity);

            emitLog("Answered request from " + header.Item1 + " (request_id: " + header.Item2 + ")", "INFO");

            return Empty;
        }

        public override Task<Cart> GetCart(GetCartRequest request, ServerCallContext context)
        {
            Tuple<string, string> header = initMetadata(context);

            emitLog("Answered request from " + header.Item1 + " (request_id: " + header.Item2 + ")", "INFO");

            return _cartStore.GetCartAsync(request.UserId);
        }

        public async override Task<Empty> EmptyCart(EmptyCartRequest request, ServerCallContext context)
        {
            Tuple<string, string> header = initMetadata(context);

            await _cartStore.EmptyCartAsync(request.UserId);

            emitLog("Answered request from " + header.Item1 + " (request_id: " + header.Item2 + ")", "INFO");
            
            return Empty;
        }
    }
}
