# Development Principles

> **Note:** This document outlines guidances behind some development decisions
> behind the Hipster Shop demo application.

### Minimal configuration

Running the demo locally or on GCP should require minimal to no
configuration unless absolutely necessary to run critical parts of the demo.

Configuration that takes multiple steps, especially such as creating service
accounts should be avoided.

### App must work well outside GCP

Demo application should work reasonably well when it is not deployed to GCP
services. The experience of running the application locally or on GCP should
be close.

For example:
- OpenCensus prints the traces to stdout when it cannot connect to GCP.
- Stackdriver Debugging tries connecting to GCP multiple times, eventually gives
  up.

### Running on GCP must not reduce functionality

Running the demo on the GCP must not reduce/lose any of the capabilities
developers have when running locally.

For example: Logs should still be printed to stdout/stderr even though logs are
uploaded to Stackdriver Logging when on GCP, so that developers can use "kubectl
logs" to diagnose each container.

### Microservice implementations should not be complex

Each service should provide a minimal implementation and try to avoid
unnecessary code and logic that's not executed.

Keep in mind that any service implementation is a decent example of “a GRPC
application that runs on Kubernetes”. Keeping the source code short and
navigable will serve this purpose.

It is okay to have intentional inefficiencies in the code as they help
illustrate the capabilities of profiling and diagnostics offerings.
