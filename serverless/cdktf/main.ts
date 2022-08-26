import { Construct } from "constructs";
import { App, TerraformOutput, TerraformStack } from "cdktf";
import { loadAll } from "js-yaml";
import { readFileSync } from "fs";
import {
  GoogleProvider,
  ProjectService,
  DataGoogleIamPolicy,
  ComputeNetwork,
  DnsManagedZone,
  ComputeSubnetwork,
  VpcAccessConnector,
  RedisInstance,
  DnsRecordSet,
  ComputeRegionNetworkEndpointGroup,
  ComputeRegionBackendService,
  ComputeForwardingRule,
  ComputeAddress,
  ComputeRegionTargetHttpProxy,
  ComputeRegionUrlMap,
  CloudRunServiceIamPolicy,
  CloudRunService,
  ComputeRegionUrlMapPathMatcherPathRule,
} from "@cdktf/provider-google";
import { DockerProvider, Image, RegistryImage } from "@cdktf/provider-docker";


class MyStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    const project_id = process.env.PROJECT_ID;
    const location = "us-central1";
    const domain_name = "example.com";
    const svc_host_port = `microservice.${domain_name}:80`;
    const lb_subnet_cidr = "10.0.1.0/24";
    const proxy_subnet_cidr = "10.0.0.0/24";
    const serverless_connector_subnet_cidr = "10.128.0.0/28";
    const image_tag = "v1.0.0";
    const noauthIAMPolicy = new DataGoogleIamPolicy(this, "allusers", {
      binding: [{
        role: "roles/run.invoker",
        members: ["allUsers"],
      }],
    });

    // Should we build container images from source?
    const build_image_from_src = (this.node.tryGetContext("buildImageFromSrc") == "true");

    new DockerProvider(this, "docker", {
      registryAuth: [{
        address: "gcr.io",
      }]
    });
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

    new GoogleProvider(this, "google-provider",
      {
        region: location,
        project: project_id,
      });

    // Enable services
    new ProjectService(this, "EnableGCE", {
      service: "compute.googleapis.com",
      disableOnDestroy: false,
    });

    new ProjectService(this, "EnableGCR", {
      service: "containerregistry.googleapis.com",
      disableOnDestroy: false,
    });

    new ProjectService(this, "EnableCloudRun", {
      service: "run.googleapis.com",
      disableOnDestroy: false,
    });

    new ProjectService(this, "EnableCloudDNS", {
      service: "dns.googleapis.com",
      disableOnDestroy: false,
    });

    new ProjectService(this, "EnableServerlessVPCAccess", {
      service: "vpcaccess.googleapis.com",
      disableOnDestroy: false,
    });

    new ProjectService(this, "EnableRedis", {
      service: "redis.googleapis.com",
      disableOnDestroy: false,
    });

    // Create a VPC
    const microservice_vpc = new ComputeNetwork(this, "microservice-vpc", {
      name: "microservice-vpc",
      autoCreateSubnetworks: false,
    });

    // Create a managed DNS private zone
    const private_zone = new DnsManagedZone(this, "private-zone", {
      name: "private-zone",
      dnsName: `${domain_name}.`,
      description: "Example private DNS zone",
      visibility: "private",
      privateVisibilityConfig: {
        networks: [
          {
            networkUrl: microservice_vpc.id,
          }
        ]
      },
    });

    // Create a subnet for internal LBs
    // Individual internal LB will have a reserved static private IP
    // from this subnet
    const lb_subnet = new ComputeSubnetwork(this, "lb-subnet", {
      name: "lb-subnet",
      ipCidrRange: lb_subnet_cidr,
      region: location,
      network: microservice_vpc.id,
    });

    // Create a proxy-only subnet
    // https://cloud.google.com/load-balancing/docs/l7-internal#proxy-only_subnet
    const proxy_subnet = new ComputeSubnetwork(this, "proxy-subnet", {
      name: "proxy-subnet",
      ipCidrRange: proxy_subnet_cidr,
      region: location,
      purpose: "REGIONAL_MANAGED_PROXY",
      role: "ACTIVE",
      network: microservice_vpc.id,
    });

    // Create a serverless connector and its subnet
    const connector = new VpcAccessConnector(this, "connector", {
      name: "vpc-connector",
      ipCidrRange: serverless_connector_subnet_cidr,
      network: microservice_vpc.id,
      region: location,
    });

    // Create a Redis cache instance & add it to the private DNS zone
    const cache = new RedisInstance(this, "cache", {
      name: "redis-cache",
      memorySizeGb: 1,
      region: location,
      authorizedNetwork: microservice_vpc.id,
    });

    new DnsRecordSet(this, "redis-record-set", {
      name: `redis.${domain_name}.`,
      type: "A",
      ttl: 300,
      managedZone: private_zone.name,
      rrdatas: [cache.host],
    });

    // List for the path rules of the microservices
    // Path rule example: /hipstershop.ProductCatalogService/*
    let path_rules: ComputeRegionUrlMapPathMatcherPathRule[] = [];

    // Build and deploy the internal services
    for (let svc of internal_services) {
      // let container_image_name = ""; // pulumi.Output<string> = pulumi.interpolate``;
      let container_image;
      if (build_image_from_src) {
        // Build the container image
        container_image = new RegistryImage(this, `${svc.name}-image`, {
          name: `gcr.io/${project_id}/${svc.name}:${image_tag}`,
          buildAttribute:
          {
            context: `${__dirname}/${svc.src_location}`,
          },
        });
        // container_image_name = container_image.name
      } else {
        container_image = new Image(this, `${svc.name}-image`, {
          name: `${svc_image.get(svc.name)}`,
        })
      }
      // Deploy the Cloud Run service
      const clourd_run_svc = new CloudRunService(this, svc.name, {
        name: svc.name,
        location: location,
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
                image: container_image.name,
                env: svc.envs,
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
        dependsOn: [container_image, connector]
      });

      // Create a serverless NEG for each service
      // URL mask doesn't work for gRPC services
      const neg = new ComputeRegionNetworkEndpointGroup(this, `${svc.name}-neg`, {
        name: `${svc.name}-neg`,
        region: location,
        networkEndpointType: "SERVERLESS",
        cloudRun: {
          service: clourd_run_svc.name,
        }
      });

      // Create a backend service
      const backend_svc = new ComputeRegionBackendService(this, `${svc.name}-backend-svc`, {
        name: `${svc.name}-backend-svc`,
        region: location,
        protocol: "HTTP2",
        loadBalancingScheme: "INTERNAL_MANAGED",
        backend: [{
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
      new CloudRunServiceIamPolicy(this, `${svc.name}NoauthIamPolicy`, {
        location: clourd_run_svc.location,
        project: clourd_run_svc.project,
        service: clourd_run_svc.name,
        policyData: noauthIAMPolicy.policyData,
      });
    }

    // Build the public facing frontend service
    let frontend_image;
    if (build_image_from_src) {
      frontend_image = new RegistryImage(this, "frontend-image", {
        name: `gcr.io/${project_id}/frontend:${image_tag}`,
        buildAttribute:
        {
          context: `${__dirname}/../../src/frontend`,
        },
      });
    } else {
      frontend_image = new Image(this, "frontend-image", {
        name: `${svc_image.get("frontend")}`,
      })
    }
    const frontend_svc = new CloudRunService(this, "frontend", {
      name: "frontend",
      location: location,
      template: {
        spec: {
          containers: [
            {
              image: frontend_image.name,
              env: [
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
      },
      dependsOn: [frontend_image, connector]
    });

    // Allow unauthenticated invocations
    new CloudRunServiceIamPolicy(this, "frontend-NoauthIamPolicy", {
      location: frontend_svc.location,
      project: frontend_svc.project,
      service: frontend_svc.name,
      policyData: noauthIAMPolicy.policyData,
    });

    // Display the frontend URL in the output
    const frontend_url = frontend_svc.status.get(0).url;
    new TerraformOutput(this, "frontend_url", {
      value: frontend_url,
    });

    // Create a URL map for the internal load balancer
    const url_map = new ComputeRegionUrlMap(this, "microservice-url-map", {
      name: "microservice-url-map",
      // It's required to have either defalutUrlRedirect or defalutService
      // Use defaultUrlRedirect here to make GCP happy
      defaultUrlRedirect: { stripQuery: false, pathRedirect: "/" },
      region: location,
      // Both host name and port(80) are required
      hostRule: [{ hosts: [`microservice.${domain_name}:80`], pathMatcher: "microservice-allpaths" }],
      pathMatcher: [{
        name: "microservice-allpaths",
        // Required but not really useful here
        defaultUrlRedirect: { stripQuery: false, pathRedirect: "/" },
        // The path rules collected from the earlier Cloud Run deployments
        pathRule: path_rules,
      }],
    });

    // Create a target proxy
    const target_proxy = new ComputeRegionTargetHttpProxy(this, "microservice-target-proxy", {
      name: "microservice-target-proxy",
      urlMap: url_map.id,
      region: location,
    });

    // Reserve an internal IP for the LB
    const internal_ip = new ComputeAddress(this, "microservice-internal-lb-ip", {
      name: "microservice-internal-lb-ip",
      subnetwork: lb_subnet.id,
      addressType: "INTERNAL",
      region: location,
    });

    // Create a forwarding rule
    new ComputeForwardingRule(this, "microservice-foward-rule", {
      name: "microservice-foward-rule",
      region: location,
      ipProtocol: "TCP",
      portRange: "80",
      loadBalancingScheme: "INTERNAL_MANAGED",
      network: microservice_vpc.name,
      subnetwork: lb_subnet.id,
      target: target_proxy.id,
      ipAddress: internal_ip.address,
      dependsOn: [proxy_subnet],
    });

    // Register the DNS record
    new DnsRecordSet(this, "microservice-record", {
      name: `microservice.${domain_name}.`,
      type: "A",
      ttl: 300,
      managedZone: private_zone.name,
      rrdatas: [internal_ip.address],
    });

  }
}

const app = new App();
new MyStack(app, "cdktf");
app.synth();
