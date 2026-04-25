package healthcheck

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestAllHealthy(t *testing.T) {
	c := NewChecker("test-svc", "0.1.0")
	c.AddDependency(DependencyCheck{
		Name:     "db",
		Critical: true,
		Check:    func(ctx context.Context) error { return nil },
	})
	c.AddDependency(DependencyCheck{
		Name:     "cache",
		Critical: false,
		Check:    func(ctx context.Context) error { return nil },
	})

	resp := c.Run(context.Background())
	if resp.Status != StatusHealthy {
		t.Errorf("expected healthy, got %s", resp.Status)
	}
	if len(resp.Dependencies) != 2 {
		t.Errorf("expected 2 dependencies, got %d", len(resp.Dependencies))
	}
}

func TestCriticalUnhealthy(t *testing.T) {
	c := NewChecker("test-svc", "0.1.0")
	c.AddDependency(DependencyCheck{
		Name:     "db",
		Critical: true,
		Check:    func(ctx context.Context) error { return fmt.Errorf("connection refused") },
	})
	c.AddDependency(DependencyCheck{
		Name:     "cache",
		Critical: false,
		Check:    func(ctx context.Context) error { return nil },
	})

	resp := c.Run(context.Background())
	if resp.Status != StatusUnhealthy {
		t.Errorf("expected unhealthy, got %s", resp.Status)
	}
}

func TestNonCriticalUnhealthy(t *testing.T) {
	c := NewChecker("test-svc", "0.1.0")
	c.AddDependency(DependencyCheck{
		Name:     "db",
		Critical: true,
		Check:    func(ctx context.Context) error { return nil },
	})
	c.AddDependency(DependencyCheck{
		Name:     "cache",
		Critical: false,
		Check:    func(ctx context.Context) error { return fmt.Errorf("timeout") },
	})

	resp := c.Run(context.Background())
	if resp.Status != StatusDegraded {
		t.Errorf("expected degraded, got %s", resp.Status)
	}
}

func TestHandlerReturns503WhenUnhealthy(t *testing.T) {
	c := NewChecker("test-svc", "0.1.0")
	c.AddDependency(DependencyCheck{
		Name:     "db",
		Critical: true,
		Check:    func(ctx context.Context) error { return fmt.Errorf("down") },
	})

	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()
	c.Handler()(w, req)

	if w.Code != http.StatusServiceUnavailable {
		t.Errorf("expected 503, got %d", w.Code)
	}
}

func TestHandlerReturns200WhenHealthy(t *testing.T) {
	c := NewChecker("test-svc", "0.1.0")
	c.AddDependency(DependencyCheck{
		Name:     "db",
		Critical: true,
		Check:    func(ctx context.Context) error { return nil },
	})

	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()
	c.Handler()(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("expected 200, got %d", w.Code)
	}
}

func TestTimeoutRespected(t *testing.T) {
	c := NewChecker("test-svc", "0.1.0")
	c.Timeout = 50 * time.Millisecond
	c.AddDependency(DependencyCheck{
		Name:     "slow",
		Critical: true,
		Check: func(ctx context.Context) error {
			select {
			case <-ctx.Done():
				return ctx.Err()
			case <-time.After(5 * time.Second):
				return nil
			}
		},
	})

	resp := c.Run(context.Background())
	if resp.Status != StatusUnhealthy {
		t.Errorf("expected unhealthy due to timeout, got %s", resp.Status)
	}
}
