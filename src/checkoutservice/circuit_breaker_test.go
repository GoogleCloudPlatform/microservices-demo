package main

import (
	"context"
	"testing"
	"time"

	gobreaker "github.com/sony/gobreaker/v2"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func TestIsTransientGRPCError(t *testing.T) {
	tests := []struct {
		name string
		err  error
		want bool
	}{
		{"nil error", nil, false},
		{"unavailable", status.Error(codes.Unavailable, "down"), true},
		{"deadline exceeded", status.Error(codes.DeadlineExceeded, "timeout"), true},
		{"resource exhausted", status.Error(codes.ResourceExhausted, "quota"), true},
		{"aborted", status.Error(codes.Aborted, "aborted"), true},
		{"canceled", status.Error(codes.Canceled, "canceled"), true},
		{"invalid argument", status.Error(codes.InvalidArgument, "bad input"), false},
		{"not found", status.Error(codes.NotFound, "missing"), false},
		{"unauthenticated", status.Error(codes.Unauthenticated, "no auth"), false},
		{"permission denied", status.Error(codes.PermissionDenied, "forbidden"), false},
		{"internal", status.Error(codes.Internal, "bug"), false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := isTransientGRPCError(tt.err); got != tt.want {
				t.Errorf("isTransientGRPCError() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestCircuitBreakerTripsOnTransientErrors(t *testing.T) {
	cb := newCircuitBreaker("test-payment", 1, 10*time.Second, 5*time.Second, 0.6, 5)

	// Send 5 transient errors to meet the minRequests threshold (60% of 5 = 3 needed)
	for i := 0; i < 5; i++ {
		cb.Execute(func() (any, error) {
			return nil, status.Errorf(codes.Unavailable, "service down")
		})
	}

	// Circuit should now be open
	_, err := cb.Execute(func() (any, error) {
		t.Error("should not execute when circuit is open")
		return nil, nil
	})

	if err != gobreaker.ErrOpenState {
		t.Errorf("expected ErrOpenState, got %v", err)
	}
}

func TestCircuitBreakerDoesNotTripOnClientErrors(t *testing.T) {
	cb := newCircuitBreaker("test-catalog", 1, 10*time.Second, 5*time.Second, 0.6, 5)

	// Send 10 client errors — these should NOT trip the circuit
	for i := 0; i < 10; i++ {
		cb.Execute(func() (any, error) {
			return nil, status.Errorf(codes.InvalidArgument, "bad request")
		})
	}

	// Circuit should still be closed — function should execute
	called := false
	result, err := cb.Execute(func() (any, error) {
		called = true
		return "ok", nil
	})

	if !called {
		t.Error("function should have been called — circuit should still be closed")
	}
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if result != "ok" {
		t.Errorf("expected 'ok', got %v", result)
	}
}

func TestCircuitBreakerRecovery(t *testing.T) {
	// Use a very short timeout so the test doesn't take long
	cb := newCircuitBreaker("test-recovery", 1, 10*time.Second, 100*time.Millisecond, 0.6, 5)

	// Trip the circuit
	for i := 0; i < 5; i++ {
		cb.Execute(func() (any, error) {
			return nil, status.Errorf(codes.Unavailable, "down")
		})
	}

	// Verify it's open
	if cb.State() != gobreaker.StateOpen {
		t.Fatalf("expected StateOpen, got %v", cb.State())
	}

	// Wait for timeout to transition to half-open
	time.Sleep(150 * time.Millisecond)

	// Send a successful request — should transition to closed
	result, err := cb.Execute(func() (any, error) {
		return "recovered", nil
	})

	if err != nil {
		t.Errorf("expected successful execution in half-open, got error: %v", err)
	}
	if result != "recovered" {
		t.Errorf("expected 'recovered', got %v", result)
	}
	if cb.State() != gobreaker.StateClosed {
		t.Errorf("expected StateClosed after recovery, got %v", cb.State())
	}
}

func TestCbExecuteAddsSpanAttributes(t *testing.T) {
	cb := newCircuitBreaker("test-otel", 1, 10*time.Second, 5*time.Second, 0.6, 5)

	// cbExecute should not panic with a background context (no active span)
	result, err := cbExecute(context.Background(), cb, func() (any, error) {
		return "success", nil
	})

	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if result != "success" {
		t.Errorf("expected 'success', got %v", result)
	}
}

func TestCbExecuteReportsRejection(t *testing.T) {
	cb := newCircuitBreaker("test-reject", 1, 10*time.Second, 5*time.Second, 0.6, 5)

	// Trip the circuit
	for i := 0; i < 5; i++ {
		cb.Execute(func() (any, error) {
			return nil, status.Errorf(codes.Unavailable, "down")
		})
	}

	// cbExecute should handle open circuit without panic
	_, err := cbExecute(context.Background(), cb, func() (any, error) {
		t.Error("should not execute when circuit is open")
		return nil, nil
	})

	if err != gobreaker.ErrOpenState {
		t.Errorf("expected ErrOpenState, got %v", err)
	}
}

func TestNewCircuitBreakerSettings(t *testing.T) {
	cb := newCircuitBreaker("test-settings", 3, 10*time.Second, 30*time.Second, 0.7, 5)

	if cb.Name() != "test-settings" {
		t.Errorf("expected name 'test-settings', got %q", cb.Name())
	}
	if cb.State() != gobreaker.StateClosed {
		t.Errorf("expected initial state StateClosed, got %v", cb.State())
	}
}
