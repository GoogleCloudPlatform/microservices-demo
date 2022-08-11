import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import * as docker from "@pulumi/docker";
import { loadAll } from "js-yaml";
import { readFileSync } from "fs";

const location = "us-central1";
const domain_name = "example.com";
const svc_host_port = `microservice.${domain_name}:80`;
const lb_subnet_cidr = "10.0.1.0/24";
const proxy_subnet_cidr = "10.0.0.0/24";
const serverless_connector_subnet_cidr = "10.128.0.0/28";
const image_tag = "v1.0.0";
const noauthIAMPolicy = gcp.organizations.getIAMPolicy({
    bindings: [{
        role: "roles/run.invoker",
        members: ["allUsers"],
    }],
});

// Should we build container images from source?
let config = new pulumi.Config();
let build_image_from_src = config.getBoolean("build_image_from_src") || false;

// Read the k8s manifest and get all the images if not building from source
let svc_image = new Map<string, string>();
if (!build_image_from_src) {
    const microsvc_k8s_manifest =
        loadAll(readFileSync("../../release/kubernetes-manifests.yaml", 'utf8')) as [any];
    for (let item of microsvc_k8s_manifest) {
        if (item.kind == "Deployment") {
            let app_name = item.metadata.name as string;
            let image_name = item.spec.template.spec.containers[0].image as string;
            svc_image.set(app_name, image_name);
        }
    }
}

// The services communicate within the same VPC
// Internal services are private. They cannot be reached from the internet
const internal_services = [
    {
        "name": "cartservice",
        "path": "hipstershop.CartService",
        "port": 7070,
        "src_location": "../../src/cartservice/src",
        "envs": [{ name: "REDIS_ADDR", value: `redis.${domain_name}:6379` }],
    },
    {
        "name": "currencyservice",
        "path": "hipstershop.CurrencyService",
        "port": 7000,
        "src_location": "../../src/currencyservice",
        "envs": [
            { name: "DISABLE_TRACING", value: "1" },
            { name: "DISABLE_PROFILER", value: "1" },
            { name: "DISABLE_DEBUGGER", value: "1" },
        ],
    },
    {
        "name": "productcatalogservice",
        "path": "hipstershop.ProductCatalogService",
        "port": 7070,
        "src_location": "../../src/productcatalogservice",
        "envs": [
            { name: "DISABLE_TRACING", value: "1" },
            { name: "DISABLE_PROFILER", value: "1" },
            { name: "DISABLE_STATS", value: "1" },
        ],
    },
    {
        "name": "recommendationservice",
        "path": "hipstershop.RecommendationService",
        "port": 8080,
        "src_location": "../../src/recommendationservice",
        "envs": [
            { name: "DISABLE_TRACING", value: "1" },
            { name: "DISABLE_PROFILER", value: "1" },
            { name: "DISABLE_DEBUGGER", value: "1" },
            { name: "PRODUCT_CATALOG_SERVICE_ADDR", value: svc_host_port }
        ],
    },
    {
        "name": "shippingservice",
        "path": "hipstershop.ShippingService",
        "port": 50051,
        "src_location": "../../src/shippingservice",
        "envs": [
            { name: "DISABLE_TRACING", value: "1" },
            { name: "DISABLE_PROFILER", value: "1" },
            { name: "DISABLE_DEBUGGER", value: "1" },
        ],
    },
    {
        "name": "checkoutservice",
        "path": "hipstershop.CheckoutService",
        "port": 5050,
        "src_location": "../../src/checkoutservice",
        "envs": [
            { name: "PRODUCT_CATALOG_SERVICE_ADDR", value: svc_host_port },
            { name: "SHIPPING_SERVICE_ADDR", value: svc_host_port },
            { name: "PAYMENT_SERVICE_ADDR", value: svc_host_port },
            { name: "EMAIL_SERVICE_ADDR", value: svc_host_port },
            { name: "CURRENCY_SERVICE_ADDR", value: svc_host_port },
            { name: "CART_SERVICE_ADDR", value: svc_host_port },
            { name: "DISABLE_TRACING", value: "1" },
            { name: "DISABLE_PROFILER", value: "1" },
            { name: "DISABLE_STATS", value: "1" },
        ],
    },
    {
        "name": "adservice",
        "path": "hipstershop.AdService",
        "port": 9555,
        "src_location": "../../src/adservice",
        "envs": [
            { name: "DISABLE_TRACING", value: "1" },
            { name: "DISABLE_STATS", value: "1" },
        ],
    },
    {
        "name": "emailservice",
        "path": "hipstershop.EmailService",
        "port": 8080,
        "src_location": "../../src/emailservice",
        "envs": [
            { name: "DISABLE_TRACING", value: "1" },
            { name: "DISABLE_PROFILER", value: "1" },
        ],
    },
    {
        "name": "paymentservice",
        "path": "hipstershop.PaymentService",
        "port": 50051,
        "src_location": "../../src/paymentservice",
        "envs": [
            { name: "DISABLE_TRACING", value: "1" },
            { name: "DISABLE_PROFILER", value: "1" },
            { name: "DISABLE_DEBUGGER", value: "1" },
        ],
    },
];

// Enable services
const enable_gce = new gcp.projects.Service("EnableGCE", {
    service: "compute.googleapis.com",
}, { retainOnDelete: true });

const enable_gcr = new gcp.projects.Service("EnableGCR", {
    service: "containerregistry.googleapis.com",
}, { retainOnDelete: true });

const enable_cloud_run = new gcp.projects.Service("EnableCloudRun", {
    service: "run.googleapis.com",
}, { retainOnDelete: true });

const enable_dns = new gcp.projects.Service("EnableCloudDNS", {
    service: "dns.googleapis.com"
}, { retainOnDelete: true });

const enable_vpcaccess = new gcp.projects.Service("EnableServerlessVPCAccess", {
    service: "vpcaccess.googleapis.com"
}, { retainOnDelete: true });

const enable_redis = new gcp.projects.Service("EnableRedis", {
    service: "redis.googleapis.com"
}, { retainOnDelete: true });

// Create a VPC
const microservice_vpc = new gcp.compute.Network("microservice-vpc", {
    autoCreateSubnetworks: false,
}, { dependsOn: enable_gce });

// Create a managed DNS private zone
const private_zone = new gcp.dns.ManagedZone("private-zone", {
    dnsName: `${domain_name}.`,
    description: "Example private DNS zone",
    visibility: "private",
    privateVisibilityConfig: {
        networks: [
            {
                networkUrl: microservice_vpc.id,
            },
        ],
    },
}, { dependsOn: enable_dns });

// Create a subnet for internal LBs
// Individual internal LB will have a reserved static private IP
// from this subnet
const lb_subnet = new gcp.compute.Subnetwork("lb-subnet", {
    ipCidrRange: lb_subnet_cidr,
    region: location,
    network: microservice_vpc.id,
});

// Create a proxy-only subnet
// https://cloud.google.com/load-balancing/docs/l7-internal#proxy-only_subnet
new gcp.compute.Subnetwork("proxy-subnet", {
    ipCidrRange: proxy_subnet_cidr,
    region: location,
    purpose: "REGIONAL_MANAGED_PROXY",
    role: "ACTIVE",
    network: microservice_vpc.id,
});

// Create a serverless connector and its subnet
const connector = new gcp.vpcaccess.Connector("connector", {
    ipCidrRange: serverless_connector_subnet_cidr,
    network: microservice_vpc.id,
    region: location,
}, { dependsOn: enable_vpcaccess });

// Create a Redis cache instance & add it to the private DNS zone
const cache = new gcp.redis.Instance("cache", {
    memorySizeGb: 1,
    region: location,
    authorizedNetwork: microservice_vpc.id,
}, { dependsOn: enable_redis });

export const cache_ip = cache.host

new gcp.dns.RecordSet("redis-record-set", {
    name: `redis.${domain_name}.`,
    type: "A",
    ttl: 300,
    managedZone: private_zone.name,
    rrdatas: [cache_ip],
});

// List for the path rules of the microservices
// Path rule example: /hipstershop.ProductCatalogService/*
let path_rules: gcp.types.input.compute.RegionUrlMapPathMatcherPathRule[] = [];

// Build and deploy the internal services
for (let svc of internal_services) {
    let container_image_name: pulumi.Output<string> = pulumi.interpolate``;
    if (build_image_from_src) {
        // Build the container image
        let container_image = new docker.Image(`${svc.name}-image`, {
            imageName: pulumi.interpolate`gcr.io/${gcp.config.project}/${svc.name}:${image_tag}`,
            build: {
                context: svc.src_location,
            },
        }, { dependsOn: enable_gcr });
        container_image_name = container_image.imageName;
    }
    // Deploy the Cloud Run service
    const clourd_run_svc = new gcp.cloudrun.Service(svc.name, {
        location,
        metadata: {
            annotations: {
                // For valid annotation values and descriptions, see
                // https://cloud.google.com/sdk/gcloud/reference/run/deploy#--ingress
                "run.googleapis.com/ingress": "internal",
            },
        },
        template: {
            spec: {
                containers: [
                    {
                        image: svc_image.get(svc.name) || container_image_name,
                        envs: svc.envs,
                        // Use h2c to enable end-to-end HTTP/2
                        ports: [{ name: "h2c", containerPort: svc.port }],
                    },
                ],
            },
            metadata: {
                annotations: {
                    // Use the VPC connector for internal traffic
                    "run.googleapis.com/vpc-access-connector": connector.name,
                    // Route all traffic through the VPC connector
                    "run.googleapis.com/vpc-access-egress": "all-traffic",
                },
            },
        },
    }, { dependsOn: [enable_gcr, enable_cloud_run, connector] });

    // Create a serverless NEG for each service
    // URL mask doesn't work for gRPC services
    const neg = new gcp.compute.RegionNetworkEndpointGroup(`${svc.name}-neg`, {
        region: location,
        networkEndpointType: "SERVERLESS",
        cloudRun: {
            service: clourd_run_svc.name,
        }
    });

    // Create a backend service
    const backend_svc = new gcp.compute.RegionBackendService(`${svc.name}-backend-svc`, {
        region: location,
        protocol: "HTTP2",
        loadBalancingScheme: "INTERNAL_MANAGED",
        backends: [{
            group: neg.id,
            balancingMode: "UTILIZATION",
            capacityScaler: 1.0,
        }],
    });

    path_rules.push(
        {
            paths: [`/${svc.path}/*`],
            service: backend_svc.id,
        }
    )

    // Allow unauthenticated invocations for internal services
    new gcp.cloudrun.IamPolicy(`${svc.name}NoauthIamPolicy`, {
        location: clourd_run_svc.location,
        project: clourd_run_svc.project,
        service: clourd_run_svc.name,
        policyData: noauthIAMPolicy.then(noauthIAMPolicy => noauthIAMPolicy.policyData),
    });
}

// Build the public facing frontend service
let frontend_image_name: pulumi.Output<string> = pulumi.interpolate``;
if (build_image_from_src) {
    const frontend_image = new docker.Image("frontend-image", {
        imageName: pulumi.interpolate`gcr.io/${gcp.config.project}/frontend:${image_tag}`,
        build: {
            context: "../../src/frontend",
        },
    }, { dependsOn: enable_gcr });
    frontend_image_name = frontend_image.imageName;
}
const frontend_svc = new gcp.cloudrun.Service("frontend", {
    location,
    template: {
        spec: {
            containers: [
                {
                    image: svc_image.get("frontend") || frontend_image_name,
                    envs: [
                        { name: "PRODUCT_CATALOG_SERVICE_ADDR", value: svc_host_port },
                        { name: "CURRENCY_SERVICE_ADDR", value: svc_host_port },
                        { name: "CART_SERVICE_ADDR", value: svc_host_port },
                        { name: "RECOMMENDATION_SERVICE_ADDR", value: svc_host_port },
                        { name: "SHIPPING_SERVICE_ADDR", value: svc_host_port },
                        { name: "CHECKOUT_SERVICE_ADDR", value: svc_host_port },
                        { name: "AD_SERVICE_ADDR", value: svc_host_port },
                        { name: "DISABLE_TRACING", value: "1" },
                        { name: "DISABLE_PROFILER", value: "1" },
                        { name: "DISABLE_DEBUGGER", value: "1" },
                    ],
                    ports: [{ containerPort: 8080 }]
                },
            ],
        },
        metadata: {
            annotations: {
                "run.googleapis.com/vpc-access-connector": connector.name,
            },
        },
    }
}, { dependsOn: [enable_cloud_run, connector] });

// Allow unauthenticated invocations
new gcp.cloudrun.IamPolicy("frontend-NoauthIamPolicy", {
    location: frontend_svc.location,
    project: frontend_svc.project,
    service: frontend_svc.name,
    policyData: noauthIAMPolicy.then(noauthIAMPolicy => noauthIAMPolicy.policyData),
});

// Display the frontend URL in the output
export const frontend_url = pulumi.interpolate`${frontend_svc.statuses[0].url}`

// Create a URL map for the internal load balancer
const url_map = new gcp.compute.RegionUrlMap("microservice-url-map", {
    // It's required to have either defalutUrlRedirect or defalutService
    // Use defaultUrlRedirect here to make GCP happy
    defaultUrlRedirect: { stripQuery: false, pathRedirect: "/" },
    region: location,
    // Both host name and port(80) are required
    hostRules: [{ hosts: [`microservice.${domain_name}:80`], pathMatcher: "microservice-allpaths" }],
    pathMatchers: [{
        name: "microservice-allpaths",
        // Required but not really useful here
        defaultUrlRedirect: { stripQuery: false, pathRedirect: "/" },
        // The path rules collected from the earlier Cloud Run deployments
        pathRules: path_rules,
    }],
});

// Create a target proxy
const target_proxy = new gcp.compute.RegionTargetHttpProxy("microservice-target-proxy", {
    urlMap: url_map.id,
    region: location,
});

// Reserve an internal IP for the LB
const internal_ip = new gcp.compute.Address("microservice-internal-lb-ip", {
    subnetwork: lb_subnet.id,
    addressType: "INTERNAL",
    region: location,
});

// Create a forwarding rule
new gcp.compute.ForwardingRule("microservice-foward-rule", {
    region: location,
    ipProtocol: "TCP",
    portRange: "80",
    loadBalancingScheme: "INTERNAL_MANAGED",
    network: microservice_vpc.name,
    subnetwork: lb_subnet.id,
    target: target_proxy.id,
    ipAddress: internal_ip.address,
});

// Register the DNS record
new gcp.dns.RecordSet("microservice-record", {
    name: `microservice.${domain_name}.`,
    type: "A",
    ttl: 300,
    managedZone: private_zone.name,
    rrdatas: [internal_ip.address],
});
