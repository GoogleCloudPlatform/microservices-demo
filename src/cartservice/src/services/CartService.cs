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
        public readonly static string SERVICENAME = "cartservice";

        // NOTE: logLevel must be a GELF valid severity value (WARN or ERROR), INFO if not specified
        public void emitLog(string messageEvent, string logLevel)
        {
            DateTime now = DateTime.UtcNow;
            string logMessage = "";

            switch (logLevel)
            {
                case "ERROR":
                    logMessage = now.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture) + " - ERROR - " + SERVICENAME + " - " + messageEvent;
                    Console.WriteLine(logMessage);
                    break;

                case "WARN":
                    logMessage = now.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture) + " - WARN - " + SERVICENAME + " - " + messageEvent;
                    Console.WriteLine(logMessage);
                    break;

                default:
                    logMessage = now.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture) + " - INFO - " + SERVICENAME + " - " + messageEvent;
                    Console.WriteLine(logMessage);
                    break;
            }
        }

        public CartService(ICartStore cartStore)
        {
            _cartStore = cartStore;
        }

        public async override Task<Empty> AddItem(AddItemRequest request, ServerCallContext context)
        {
            var RequestID = context.RequestHeaders.Get("requestid").Value;
            var ServiceName = context.RequestHeaders.Get("servicename").Value;

            if (RequestID == null && ServiceName == null) 
            {
                emitLog(ServiceName + ": An error occurred while retrieving the RequestID", "ERROR");
                return null;
            }

            string messageEvent = "Received request from " + ServiceName.ToString() + " (request_id: " + RequestID.ToString() + ")";
            emitLog(messageEvent, "INFO");

            await _cartStore.AddItemAsync(request.UserId, request.Item.ProductId, request.Item.Quantity);

            messageEvent = "Answered to request from " + ServiceName.ToString() + " (request_id: " + RequestID.ToString() + ")";
            emitLog(messageEvent, "INFO");

            return Empty;
        }

        public override Task<Cart> GetCart(GetCartRequest request, ServerCallContext context)
        {
            var RequestID = context.RequestHeaders.Get("requestid").Value;
            var ServiceName = context.RequestHeaders.Get("servicename").Value;

            if (RequestID == null && ServiceName == null) 
            {
                emitLog(ServiceName + ": An error occurred while retrieving the RequestID", "ERROR");
                return null;
            }

            string messageEvent = "Received request from " + ServiceName.ToString() + " (request_id: " + RequestID.ToString() + ")";
            emitLog(messageEvent, "INFO");
            messageEvent = "Answered to request from " + ServiceName.ToString() + " (request_id: " + RequestID.ToString() + ")";
            emitLog(messageEvent, "INFO");

            return _cartStore.GetCartAsync(request.UserId);
        }

        public async override Task<Empty> EmptyCart(EmptyCartRequest request, ServerCallContext context)
        {
            var RequestID = context.RequestHeaders.Get("requestid").Value;
            var ServiceName = context.RequestHeaders.Get("servicename").Value;

            if (RequestID == null && ServiceName == null) 
            {
                emitLog(ServiceName + ": An error occurred while retrieving the RequestID", "ERROR");
                return null;
            }

            string messageEvent = "Received request from " + ServiceName.ToString() + " (request_id: " + RequestID.ToString() + ")";
            emitLog(messageEvent, "INFO");

            await _cartStore.EmptyCartAsync(request.UserId);

            messageEvent = "Answered to request from " + ServiceName.ToString() + " (request_id: " + RequestID.ToString() + ")";
            emitLog(messageEvent, "INFO");
            
            return Empty;
        }
    }
}
