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
