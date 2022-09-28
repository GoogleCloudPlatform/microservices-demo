job "redis" {
  
  datacenters = ["london"]
  type = "service"

  constraint {
    attribute = "${node.class}"
    value     = "apps"
  }

  update {
    stagger      = "10s"
    max_parallel = 1
  }

  group "redis" {
    count = 1
    network {
      mode = "bridge"
      port "envoy_metrics" {
        to = 9102
      }
    }

    service {
      name = "redis"
      port = "6379"
      tags = ["prometheus=true"]
      meta {
        envoy_metrics_port = "${NOMAD_HOST_PORT_envoy_metrics}"
      }
      connect {
        sidecar_service {
          proxy {
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

    task "redis" {
      driver         = "docker"
      shutdown_delay = "10s"

      config {
        image = "redis:alpine"
      }

      env {
        PORT = "6379"
        JAEGER_SERVICE_ADDR = "tracing.service.consul:24268"
        JAEGER_HOST = "tracing.service.consul"
        JAEGER_PORT = "24268"
        DISABLE_PROFILER = 1
      }

      resources {
        cpu    = 100
        memory = 128
      }
    }
  }
}