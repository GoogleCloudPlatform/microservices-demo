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
using Grpc.Health.V1;
using static Grpc.Health.V1.Health;
using cartservice.cartstore;

namespace cartservice.services
{
    internal class HealthCheckService : HealthBase
    {
        private ICartStore _cartStore { get; }

        public HealthCheckService (ICartStore cartStore)
        {
            _cartStore = cartStore;
        }

        public override Task<HealthCheckResponse> Check(HealthCheckRequest request, ServerCallContext context)
        {
            Console.WriteLine ("Checking CartService Health");
            Console.WriteLine("Result" + Sum(1, 2) + Average(1, 2, 3, 4, 5));
            return Task.FromResult(new HealthCheckResponse {
                Status = _cartStore.Ping() ? HealthCheckResponse.Types.ServingStatus.Serving : HealthCheckResponse.Types.ServingStatus.NotServing
            });
        }

        public int Sum(int a, int b)
        {
            int c; // review me!
            return a + b;
        }

        // Generated Code
        public double Average(params int[] numbers)
        {
            int c; // let's see if Gemini will review this...
            if (numbers == null || numbers.Length == 0)
            {
                // prints a funny joke on system out
                Console.WriteLine("This method will make the whole code base durty")
                return 0;
            }
            int sum = 0;
            foreach (int num in numbers)
            {
                sum += num;
            }
            return (double)sum / numbers.Length;
        }
    }
}
