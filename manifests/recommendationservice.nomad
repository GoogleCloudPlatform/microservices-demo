job "recommendation" {
  
  datacenters = ["london"]
  type = "service"

  constraint {
    attribute = "${node.class}"
    value     = "apps"
  }

  update {
    max_parallel      = 1
    health_check      = "checks"
    min_healthy_time  = "10s"
    healthy_deadline  = "5m"
    progress_deadline = "10m"
    auto_revert       = true
    auto_promote      = false
    canary            = 1
    stagger           = "30s"
  }

  group "recommendation" {
    count = 1
    network {
      mode = "bridge"
      port "envoy_metrics" {
        to = 9102
      }
    }

    service {
      name = "recommendation"
      port = "5050"
      tags        = ["prometheus=true"]

canary_tags = ["prometheus=true", "canary"]
      meta {
        envoy_metrics_port = "${NOMAD_HOST_PORT_envoy_metrics}"
      }
      connect {
        sidecar_service {
          proxy {
            upstreams {
              destination_name = "product-catalog"
              local_bind_port  = 5051
            }
            config {
              envoy_prometheus_bind_addr = "0.0.0.0:9102"
            }
          }
        }
      }//
      //check {
      //  name     = "alive"
      //  type     = "grpc"
      //  interval = "20s"
      //  timeout  = "3s"
      //}
      //
    }

    restart {
      attempts = 2
      interval = "30m"
      delay = "15s"
      mode = "fail"
    }

    task "recommendation" {
      driver         = "docker"
      shutdown_delay = "10s"

      config {
        image = "raquio/demo-recommendationservice:v0.0.2"
      }

      env {
        PORT = "5050"
        JAEGER_SERVICE_ADDR = "tracing.service.consul:24268"
        JAEGER_HOST = "tracing.service.consul"
        JAEGER_PORT = "24268"
        DISABLE_PROFILER = 1
        PRODUCT_CATALOG_SERVICE_ADDR = "${NOMAD_UPSTREAM_ADDR_product-catalog}"
      }

      resources {
        cpu    = 100
        memory = 450
      }
    }
  }
}