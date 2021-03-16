// <copyright file="TraceService.cs" company="OpenTelemetry Authors">
// Copyright The OpenTelemetry Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// </copyright>

using System;
using System.Threading;
using Grpc.Core;

namespace Opentelemetry.Proto.Collector.Logs.V1
{
    /// <summary>
    /// TraceService extensions.
    /// </summary>
    internal static partial class LogsService
    {
        /// <summary>Interface for TraceService.</summary>
        public interface ILogsServiceClient
        {
            /// <summary>
            /// For performance reasons, it is recommended to keep this RPC
            /// alive for the entire life of the application.
            /// </summary>
            /// <param name="request">The request to send to the server.</param>
            /// <param name="headers">The initial metadata to send with the call. This parameter is optional.</param>
            /// <param name="deadline">An optional deadline for the call. The call will be cancelled if deadline is hit.</param>
            /// <param name="cancellationToken">An optional token for canceling the call.</param>
            /// <returns>The response received from the server.</returns>
            ExportLogsServiceResponse Export(ExportLogsServiceRequest request, Metadata headers = null, DateTime? deadline = null, CancellationToken cancellationToken = default);
        }

        /// <summary>
        /// LogsServiceClient extensions.
        /// </summary>
        public partial class LogsServiceClient : ILogsServiceClient
        {
        }
    }
}
