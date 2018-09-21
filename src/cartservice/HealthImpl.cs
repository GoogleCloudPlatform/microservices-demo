using System;
using cartservice.interfaces;
using Grpc.Health.V1;
using StackExchange.Redis;
using static Grpc.Health.V1.Health;

namespace cartservice {
    internal class HealthImpl : HealthBase {
        private ICartStore dependency { get; }
        public HealthImpl (ICartStore dependency) {
            this.dependency = dependency;
        }

        public HealthCheckResponse Check (HealthCheckRequest request) {
            Console.WriteLine ("Checking CartService Health");

            return new HealthCheckResponse {
                Status = dependency.Ping() ? HealthCheckResponse.Types.ServingStatus.Serving : HealthCheckResponse.Types.ServingStatus.NotServing
            };
        }
    }
}