// <copyright file="ResourceSemanticConventions.cs" company="OpenTelemetry Authors">
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

namespace OpenTelemetry.Resources
{
    internal static class ResourceSemanticConventions
    {
        public const string AttributeServiceName = "service.name";
        public const string AttributeServiceNamespace = "service.namespace";
        public const string AttributeServiceInstance = "service.instance.id";
        public const string AttributeServiceVersion = "service.version";

        public const string AttributeTelemetrySdkName = "telemetry.sdk.name";
        public const string AttributeTelemetrySdkLanguage = "telemetry.sdk.language";
        public const string AttributeTelemetrySdkVersion = "telemetry.sdk.version";

        public const string AttributeContainerName = "container.name";
        public const string AttributeContainerImage = "container.image.name";
        public const string AttributeContainerTag = "container.image.tag";

        public const string AttributeFaasName = "faas.name";
        public const string AttributeFaasId = "faas.id";
        public const string AttributeFaasVersion = "faas.version";
        public const string AttributeFaasInstance = "faas.instance";

        public const string AttributeK8sCluster = "k8s.cluster.name";
        public const string AttributeK8sNamespace = "k8s.namespace.name";
        public const string AttributeK8sPod = "k8s.pod.name";
        public const string AttributeK8sDeployment = "k8s.deployment.name";

        public const string AttributeHostHostname = "host.hostname";
        public const string AttributeHostId = "host.id";
        public const string AttributeHostName = "host.name";
        public const string AttributeHostType = "host.type";
        public const string AttributeHostImageName = "host.image.name";
        public const string AttributeHostImageId = "host.image.id";
        public const string AttributeHostImageVersion = "host.image.version";

        public const string AttributeProcessId = "process.id";
        public const string AttributeProcessExecutableName = "process.executable.name";
        public const string AttributeProcessExecutablePath = "process.executable.path";
        public const string AttributeProcessCommand = "process.command";
        public const string AttributeProcessCommandLine = "process.command_line";
        public const string AttributeProcessUsername = "process.username";

        public const string AttributeCloudProvider = "cloud.provider";
        public const string AttributeCloudAccount = "cloud.account.id";
        public const string AttributeCloudRegion = "cloud.region";
        public const string AttributeCloudZone = "cloud.zone";
        public const string AttributeComponent = "component";
    }
}
