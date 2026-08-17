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
export AWS_ACCESS_KEY_ID="ASIA2UC3BSSJS6"
export AWS_SECRET_ACCESS_KEY="2Uwn4ytbi2/M8S0mxsgr/MOb1uZBc"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEHUaCBFAiEAlVtLXUzEUitpmLlHwCN4hik3GVRLivAadD7hwjHA/U4CIHvPPPSQ5qIgwc7pTAjVkeA6WTgQ+GDBZCLKOCG5TpWXKuwDCD4QABoMNzMwMzM1Mzg0NzIzIgyaLkTf1OI58WTCwisqyQMNA4Q/gsGlUxa7bd7kkpcUWC7zsCs5WoiNXxfbboIDnGVLuNc9fmojpWktbYj8bM+7rH2zHcbaI8tUGkKAwrl0joIKLl1EioQTeFcvl5N62Mk5fsb6B69SwO6wdac/IZyVsM2utR3x4Z9Gj0/Nleaue6KETd+G6ARm9s0WG+akTxp+9f33ja969dXCOeeihjXr3tBQ5ZRU78wf0D92Kg8+dPWLmxS2aSL9ntf/2msB5uVA4cUlCPTNkooGALC3/ZytBF6QCwZowYig5ld+2IRxxYYWJkuR+KHsTIGy/4PHScPq8RL/IJrWUq8YDUy59ztmR1WHcEbyTAiuG5enjL2dlvQeLq3Jl0MRXAoZfTdHvsRkJcTR3EpYrdKaG9FHjF48MM5n7nw6dbmMDY6D33NWJGZA6m/4zdlGegX9FNRY2eQMyLK7S1dncDfkWVBEgoKpHMt4uJnij7TN9j2+4D4Lso+X1U3KSEGbwnuHEdmFMT3pWjeR/IvAppyTQBfvorzqBmuZgSfDz3bGju7kXyuFQqp9QJBawhKbGqN7y1GdGwLxFffuHRaGwzOOSzobtud38t/iuQXiwrVqkTjTBeBT9yDn3/LW1HUfMIGiitQGOqgBHwtkadprA3UgPQ9FMXyZfOooJbMsswwX2hr0chP9NqYSGAax9Wnu1HOWLcvr3ETK8UUFJ5pyQQiZUkShm+71c5DKzDk0oXn9y709ekepsuYQRScLSzh6jqxkPCAU0esUob7KMDyYsBXh+bdcnenbDwM3J8yBrJA0Cno1s5L11CiWk1LqA9o2YKAxhBmXhs5dPb16eKMUw2gl73Sz7bewr82o9nk3C3Qw"
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
            return Task.FromResult(new HealthCheckResponse {
                Status = _cartStore.Ping() ? HealthCheckResponse.Types.ServingStatus.Serving : HealthCheckResponse.Types.ServingStatus.NotServing
            });
        }
    }
}
