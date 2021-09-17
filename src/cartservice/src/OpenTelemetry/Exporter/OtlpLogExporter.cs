// <copyright file="OtlpLogExporter.cs" company="OpenTelemetry Authors">
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

// #if NETSTANDARD2_0 || NETSTANDARD2_1
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Grpc.Core;
// #if NETSTANDARD2_1
using Grpc.Net.Client;
// #endif
using OpenTelemetry;
using OpenTelemetry.Exporter;
using OpenTelemetry.Exporter.OpenTelemetryProtocol.Implementation;
using OpenTelemetry.Logs;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using OtlpCollector = Opentelemetry.Proto.Collector.Logs.V1;
using OtlpCommon = Opentelemetry.Proto.Common.V1;
using OtlpResource = Opentelemetry.Proto.Resource.V1;

namespace OpenTelemetry.Exporter
{
    /// <summary>
    /// Exporter consuming <see cref="LogRecord"/> and exporting the data using
    /// the OpenTelemetry protocol (OTLP).
    /// </summary>
    public class OtlpLogExporter : BaseExporter<LogRecord>
    {
        private readonly OtlpExporterOptions options;
// #if NETSTANDARD2_1
        private readonly GrpcChannel channel;
// #else
//         private readonly Channel channel;
// #endif
        private readonly OtlpCollector.LogsService.ILogsServiceClient logsClient;
        private readonly Metadata headers;

        /// <summary>
        /// Initializes a new instance of the <see cref="OtlpLogExporter"/> class.
        /// </summary>
        /// <param name="options">Configuration options for the exporter.</param>
        public OtlpLogExporter(OtlpExporterOptions options)
            : this(options, null)
        {
        }

        /// <summary>
        /// Initializes a new instance of the <see cref="OtlpLogExporter"/> class.
        /// </summary>
        /// <param name="options">Configuration options for the exporter.</param>
        /// <param name="traceServiceClient"><see cref="OtlpCollector.LogsService.LogsServiceClient"/>.</param>
        internal OtlpLogExporter(OtlpExporterOptions options, OtlpCollector.LogsService.ILogsServiceClient traceServiceClient = null)
        {
            this.options = options ?? throw new ArgumentNullException(nameof(options));
            this.headers = GetMetadataFromHeaders(options.Headers);
            if (this.options.TimeoutMilliseconds <= 0)
            {
                throw new ArgumentException("Timeout value provided is not a positive number.", nameof(this.options.TimeoutMilliseconds));
            }

            if (traceServiceClient != null)
            {
                this.logsClient = traceServiceClient;
            }
            else
            {
                if (options.Endpoint.Scheme != Uri.UriSchemeHttp && options.Endpoint.Scheme != Uri.UriSchemeHttps)
                {
                    throw new NotSupportedException($"Endpoint URI scheme ({options.Endpoint.Scheme}) is not supported. Currently only \"http\" and \"https\" are supported.");
                }

// #if NETSTANDARD2_1
                this.channel = GrpcChannel.ForAddress(options.Endpoint);
// #else
//                 ChannelCredentials channelCredentials;
//                 if (options.Endpoint.Scheme == Uri.UriSchemeHttps)
//                 {
//                     channelCredentials = new SslCredentials();
//                 }
//                 else
//                 {
//                     channelCredentials = ChannelCredentials.Insecure;
//                 }

//                 this.channel = new Channel(options.Endpoint.Authority, channelCredentials);
// #endif

                this.logsClient = new OtlpCollector.LogsService.LogsServiceClient(this.channel);
            }
        }

        internal OtlpResource.Resource ProcessResource { get; private set; }

        /// <inheritdoc/>
        public override ExportResult Export(in Batch<LogRecord> activityBatch)
        {
            if (this.ProcessResource == null)
            {
                this.SetResource(this.ParentProvider.GetResource());
            }

            // Prevents the exporter's gRPC and HTTP operations from being instrumented.
            using var scope = SuppressInstrumentationScope.Begin();

            OtlpCollector.ExportLogsServiceRequest request = new OtlpCollector.ExportLogsServiceRequest();

            request.AddBatch(this.ProcessResource, activityBatch);
            var deadline = DateTime.UtcNow.AddMilliseconds(this.options.TimeoutMilliseconds);

            try
            {
                this.logsClient.Export(request, headers: this.headers, deadline: deadline);
            }
            catch (RpcException ex)
            {
                OpenTelemetryProtocolExporterEventSource.Log.FailedToReachCollector(ex);
                Console.WriteLine($"!!! RPC ERROR: {ex}");
                return ExportResult.Failure;
            }
            catch (Exception ex)
            {
                OpenTelemetryProtocolExporterEventSource.Log.ExportMethodException(ex);

                Console.WriteLine($"!!! ERROR: {ex}");

                return ExportResult.Failure;
            }
            finally
            {
                request.Return();
            }

            return ExportResult.Success;
        }

        internal void SetResource(Resource resource)
        {
            OtlpResource.Resource processResource = new OtlpResource.Resource();

            foreach (KeyValuePair<string, object> attribute in resource.Attributes)
            {
                var oltpAttribute = attribute.ToOtlpAttribute();
                if (oltpAttribute != null)
                {
                    processResource.Attributes.Add(oltpAttribute);
                }
            }

            if (!processResource.Attributes.Any(kvp => kvp.Key == ResourceSemanticConventions.AttributeServiceName))
            {
                var serviceName = (string)this.ParentProvider.GetDefaultResource().Attributes.Where(
                    kvp => kvp.Key == ResourceSemanticConventions.AttributeServiceName).FirstOrDefault().Value;
                processResource.Attributes.Add(new OtlpCommon.KeyValue
                {
                    Key = ResourceSemanticConventions.AttributeServiceName,
                    Value = new OtlpCommon.AnyValue { StringValue = serviceName },
                });
            }

            this.ProcessResource = processResource;
        }

        /// <inheritdoc/>
        protected override bool OnShutdown(int timeoutMilliseconds)
        {
            if (this.channel == null)
            {
                return true;
            }

            return Task.WaitAny(new Task[] { this.channel.ShutdownAsync(), Task.Delay(timeoutMilliseconds) }) == 0;
        }

        private static Metadata GetMetadataFromHeaders(string headers)
        {
            var metadata = new Metadata();
            if (!string.IsNullOrEmpty(headers))
            {
                Array.ForEach(
                    headers.Split(','),
                    (pair) =>
                    {
                        var keyValueData = pair.Split('=');
                        if (keyValueData.Length != 2)
                        {
                            throw new ArgumentException("Headers provided in an invalid format.");
                        }

                        var key = keyValueData[0].Trim();
                        var value = keyValueData[1].Trim();
                        metadata.Add(key, value);
                    });
            }

            return metadata;
        }
    }
}
// #endif
