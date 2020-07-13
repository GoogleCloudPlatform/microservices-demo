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
using cartservice.interfaces;
using Grpc.Core;
using Grpc.Health.V1;
using StackExchange.Redis;
using static Grpc.Health.V1.Health;

namespace cartservice {
    internal class HealthImpl : HealthBase {
        private ICartStore dependency { get; }
        public HealthImpl (ICartStore dependency) {
            this.dependency = dependency;
        }

        public override Task<HealthCheckResponse> Check(HealthCheckRequest request, ServerCallContext context){
            Console.WriteLine ("Checking CartService Health");
            return Task.FromResult(new HealthCheckResponse {
                Status = dependency.Ping() ? HealthCheckResponse.Types.ServingStatus.Serving : HealthCheckResponse.Types.ServingStatus.NotServing
            });
        }
    }
}
