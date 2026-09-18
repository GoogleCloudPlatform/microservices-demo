// Package healthcheck provides structured health check endpoints that report
// per-dependency status with an overall service health roll-up.
//
// Each dependency checker runs with a timeout and contributes to the aggregate
// status:
//
//	healthy   — all dependencies are reachable
//	degraded  — at least one non-critical dependency is down
//	unhealthy — at least one critical dependency is down
package healthcheck

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/connectivity"
)

// Status represents the health state of a service or dependency.
type Status string

const (
	StatusHealthy   Status = "healthy"
	StatusDegraded  Status = "degraded"
	StatusUnhealthy Status = "unhealthy"
)

// DependencyCheck defines a single dependency health probe.
type DependencyCheck struct {
	// Name is a human-readable identifier (e.g. "product-catalog", "redis").
	Name string
	// Critical marks the dependency as required for the service to function.
	// If a critical dependency is unhealthy the overall status is unhealthy.
	Critical bool
	// Check performs the actual health probe. Return nil for healthy.
	Check func(ctx context.Context) error
}

// DependencyResult is the probe result for a single dependency.
type DependencyResult struct {
	Name     string `json:"name"`
	Status   Status `json:"status"`
	Critical bool   `json:"critical"`
	Latency  string `json:"latency"`
	Error    string `json:"error,omitempty"`
}

// HealthResponse is the JSON body returned by the health endpoint.
type HealthResponse struct {
	Status       Status             `json:"status"`
	Service      string             `json:"service"`
	Version      string             `json:"version"`
	Timestamp    string             `json:"timestamp"`
	Dependencies []DependencyResult `json:"dependencies"`
}

// Checker holds the configuration for the structured health check.
type Checker struct {
	ServiceName  string
	Version      string
	Dependencies []DependencyCheck
	Timeout      time.Duration // per-dependency timeout
}

// NewChecker creates a Checker with sensible defaults.
func NewChecker(serviceName, version string) *Checker {
	return &Checker{
		ServiceName: serviceName,
		Version:     version,
		Timeout:     3 * time.Second,
	}
}

// AddDependency registers a dependency health check.
func (c *Checker) AddDependency(dep DependencyCheck) {
	c.Dependencies = append(c.Dependencies, dep)
}

// AddGRPCDependency is a convenience helper that checks whether a gRPC
// client connection is in a READY or IDLE state.
func (c *Checker) AddGRPCDependency(name string, conn *grpc.ClientConn, critical bool) {
	c.AddDependency(DependencyCheck{
		Name:     name,
		Critical: critical,
		Check: func(ctx context.Context) error {
			if conn == nil {
				return fmt.Errorf("connection is nil")
			}
			state := conn.GetState()
			if state == connectivity.Ready || state == connectivity.Idle {
				return nil
			}
			return fmt.Errorf("connection state: %s", state.String())
		},
	})
}

// Run executes all dependency checks concurrently and returns the aggregate
// response.
func (c *Checker) Run(ctx context.Context) HealthResponse {
	results := make([]DependencyResult, len(c.Dependencies))
	var wg sync.WaitGroup

	for i, dep := range c.Dependencies {
		wg.Add(1)
		go func(idx int, d DependencyCheck) {
			defer wg.Done()

			checkCtx, cancel := context.WithTimeout(ctx, c.Timeout)
			defer cancel()

			start := time.Now()
			err := d.Check(checkCtx)
			latency := time.Since(start)

			result := DependencyResult{
				Name:     d.Name,
				Critical: d.Critical,
				Latency:  latency.Round(time.Millisecond).String(),
			}
			if err != nil {
				result.Status = StatusUnhealthy
				result.Error = err.Error()
			} else {
				result.Status = StatusHealthy
			}
			results[idx] = result
		}(i, dep)
	}

	wg.Wait()

	// Determine overall status
	overall := StatusHealthy
	for _, r := range results {
		if r.Status == StatusUnhealthy {
			if r.Critical {
				overall = StatusUnhealthy
				break // critical failure = unhealthy, no need to continue
			}
			if overall != StatusUnhealthy {
				overall = StatusDegraded
			}
		}
	}

	return HealthResponse{
		Status:       overall,
		Service:      c.ServiceName,
		Version:      c.Version,
		Timestamp:    time.Now().UTC().Format(time.RFC3339),
		Dependencies: results,
	}
}

// Handler returns an http.HandlerFunc that serves the structured health check.
func (c *Checker) Handler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		resp := c.Run(r.Context())

		w.Header().Set("Content-Type", "application/json")
		switch resp.Status {
		case StatusHealthy:
			w.WriteHeader(http.StatusOK)
		case StatusDegraded:
			w.WriteHeader(http.StatusOK) // still serving, but degraded
		case StatusUnhealthy:
			w.WriteHeader(http.StatusServiceUnavailable)
		}

		json.NewEncoder(w).Encode(resp)
	}
}

// LivenessHandler returns a simple liveness probe (always 200 if the process
// is running). Use this for Kubernetes livenessProbe.
func LivenessHandler(serviceName string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]string{
			"status":  "alive",
			"service": serviceName,
		})
	}
}
