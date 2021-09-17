// <copyright file="SemanticConventions.cs" company="OpenTelemetry Authors">
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

namespace OpenTelemetry.Internal
{
    /// <summary>
    /// Constants for semantic attribute names outlined by the OpenTelemetry specifications.
    /// <see href="https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/README.md"/>.
    /// </summary>
    internal static class SemanticConventions
    {
        // The set of constants matches the specification as of this commit.
        // https://github.com/open-telemetry/opentelemetry-specification/tree/main/specification/trace/semantic_conventions
        // https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/exceptions.md
#pragma warning disable CS1591 // Missing XML comment for publicly visible type or member
        public const string AttributeNetTransport = "net.transport";
        public const string AttributeNetPeerIp = "net.peer.ip";
        public const string AttributeNetPeerPort = "net.peer.port";
        public const string AttributeNetPeerName = "net.peer.name";
        public const string AttributeNetHostIp = "net.host.ip";
        public const string AttributeNetHostPort = "net.host.port";
        public const string AttributeNetHostName = "net.host.name";

        public const string AttributeEnduserId = "enduser.id";
        public const string AttributeEnduserRole = "enduser.role";
        public const string AttributeEnduserScope = "enduser.scope";

        public const string AttributePeerService = "peer.service";

        public const string AttributeHttpMethod = "http.method";
        public const string AttributeHttpUrl = "http.url";
        public const string AttributeHttpTarget = "http.target";
        public const string AttributeHttpHost = "http.host";
        public const string AttributeHttpScheme = "http.scheme";
        public const string AttributeHttpStatusCode = "http.status_code";
        public const string AttributeHttpStatusText = "http.status_text";
        public const string AttributeHttpFlavor = "http.flavor";
        public const string AttributeHttpServerName = "http.server_name";
        public const string AttributeHttpHostName = "host.name";
        public const string AttributeHttpHostPort = "host.port";
        public const string AttributeHttpRoute = "http.route";
        public const string AttributeHttpClientIP = "http.client_ip";
        public const string AttributeHttpUserAgent = "http.user_agent";
        public const string AttributeHttpRequestContentLength = "http.request_content_length";
        public const string AttributeHttpRequestContentLengthUncompressed = "http.request_content_length_uncompressed";
        public const string AttributeHttpResponseContentLength = "http.response_content_length";
        public const string AttributeHttpResponseContentLengthUncompressed = "http.response_content_length_uncompressed";

        public const string AttributeDbSystem = "db.system";
        public const string AttributeDbConnectionString = "db.connection_string";
        public const string AttributeDbUser = "db.user";
        public const string AttributeDbMsSqlInstanceName = "db.mssql.instance_name";
        public const string AttributeDbJdbcDriverClassName = "db.jdbc.driver_classname";
        public const string AttributeDbName = "db.name";
        public const string AttributeDbStatement = "db.statement";
        public const string AttributeDbOperation = "db.operation";
        public const string AttributeDbInstance = "db.instance";
        public const string AttributeDbUrl = "db.url";
        public const string AttributeDbCassandraKeyspace = "db.cassandra.keyspace";
        public const string AttributeDbHBaseNamespace = "db.hbase.namespace";
        public const string AttributeDbRedisDatabaseIndex = "db.redis.database_index";
        public const string AttributeDbMongoDbCollection = "db.mongodb.collection";

        public const string AttributeRpcSystem = "rpc.system";
        public const string AttributeRpcService = "rpc.service";
        public const string AttributeRpcMethod = "rpc.method";
        public const string AttributeRpcGrpcStatusCode = "rpc.grpc.status_code";

        public const string AttributeMessageType = "message.type";
        public const string AttributeMessageId = "message.id";
        public const string AttributeMessageCompressedSize = "message.compressed_size";
        public const string AttributeMessageUncompressedSize = "message.uncompressed_size";

        public const string AttributeFaasTrigger = "faas.trigger";
        public const string AttributeFaasExecution = "faas.execution";
        public const string AttributeFaasDocumentCollection = "faas.document.collection";
        public const string AttributeFaasDocumentOperation = "faas.document.operation";
        public const string AttributeFaasDocumentTime = "faas.document.time";
        public const string AttributeFaasDocumentName = "faas.document.name";
        public const string AttributeFaasTime = "faas.time";
        public const string AttributeFaasCron = "faas.cron";

        public const string AttributeMessagingSystem = "messaging.system";
        public const string AttributeMessagingDestination = "messaging.destination";
        public const string AttributeMessagingDestinationKind = "messaging.destination_kind";
        public const string AttributeMessagingTempDestination = "messaging.temp_destination";
        public const string AttributeMessagingProtocol = "messaging.protocol";
        public const string AttributeMessagingProtocolVersion = "messaging.protocol_version";
        public const string AttributeMessagingUrl = "messaging.url";
        public const string AttributeMessagingMessageId = "messaging.message_id";
        public const string AttributeMessagingConversationId = "messaging.conversation_id";
        public const string AttributeMessagingPayloadSize = "messaging.message_payload_size_bytes";
        public const string AttributeMessagingPayloadCompressedSize = "messaging.message_payload_compressed_size_bytes";
        public const string AttributeMessagingOperation = "messaging.operation";

        public const string AttributeExceptionEventName = "exception";
        public const string AttributeExceptionType = "exception.type";
        public const string AttributeExceptionMessage = "exception.message";
        public const string AttributeExceptionStacktrace = "exception.stacktrace";
#pragma warning restore CS1591 // Missing XML comment for publicly visible type or member
    }
}
