using System;
using System.Threading.Tasks;
using static System.Diagnostics.Stopwatch;
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
            var watch = StartNew();
            var result = Task.FromResult(new HealthCheckResponse {
                Status = dependency.Ping() ? HealthCheckResponse.Types.ServingStatus.Serving : HealthCheckResponse.Types.ServingStatus.NotServing
            });
            watch.Stop();
            var elapsedMs = watch.ElapsedMilliseconds;
            Console.WriteLine ("✅ Health Check took " + elapsedMs + "ms");
            return result;
        }
    }
}
