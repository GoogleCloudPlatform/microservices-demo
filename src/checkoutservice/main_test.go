// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"context"
	"net"
	"testing"
	"time"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice/genproto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
	"google.golang.org/grpc/test/bufconn"
)

type deadlineCheckingEmailService struct {
	pb.UnimplementedEmailServiceServer
}

func (deadlineCheckingEmailService) SendOrderConfirmation(ctx context.Context, _ *pb.SendOrderConfirmationRequest) (*pb.Empty, error) {
	deadline, ok := ctx.Deadline()
	if !ok {
		return nil, status.Error(codes.InvalidArgument, "email request context has no deadline")
	}
	if remaining := time.Until(deadline); remaining <= 0 || remaining > time.Second {
		return nil, status.Errorf(codes.InvalidArgument, "email request timeout = %v, want at most %v", remaining, time.Second)
	}
	return &pb.Empty{}, nil
}

func TestSendOrderConfirmationHasBoundedTimeout(t *testing.T) {
	listener := bufconn.Listen(1024 * 1024)
	server := grpc.NewServer()
	pb.RegisterEmailServiceServer(server, deadlineCheckingEmailService{})
	go func() {
		_ = server.Serve(listener)
	}()
	t.Cleanup(server.Stop)

	conn, err := grpc.NewClient(
		"passthrough:///email",
		grpc.WithContextDialer(func(context.Context, string) (net.Conn, error) {
			return listener.Dial()
		}),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		t.Fatalf("grpc.NewClient() error = %v", err)
	}
	t.Cleanup(func() { _ = conn.Close() })

	cs := &checkoutService{emailSvcConn: conn}
	if err := cs.sendOrderConfirmation(context.Background(), "test@example.com", &pb.OrderResult{}); err != nil {
		t.Fatalf("sendOrderConfirmation() error = %v", err)
	}
}
