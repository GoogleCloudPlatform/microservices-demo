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

// wishlistservice keeps one or more wish lists per shopper. It speaks gRPC,
// like the rest of the demo, and owns its own Redis instance.
package main

import (
	"context"
	"errors"
	"log/slog"
	"net"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"
	"google.golang.org/grpc/status"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/wishlistservice/genproto"
)

const (
	defaultPort = "8080"
	defaultTTL  = 48 * time.Hour

	maxNameLen      = 64
	maxUserIDLen    = 64
	maxProductIDLen = 32

	healthCheckMethod = "/grpc.health.v1.Health/Check"
)

type server struct {
	pb.UnimplementedWishlistServiceServer

	store *store
	log   *slog.Logger
}

func main() {
	log := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug}))

	port := defaultPort
	if v := os.Getenv("PORT"); v != "" {
		port = v
	}
	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		log.Error("environment variable REDIS_ADDR not set")
		os.Exit(1)
	}
	ttl := defaultTTL
	if v := os.Getenv("WISHLIST_TTL_SECONDS"); v != "" {
		secs, err := strconv.Atoi(v)
		if err != nil {
			log.Error("invalid WISHLIST_TTL_SECONDS", "value", v)
			os.Exit(1)
		}
		ttl = time.Duration(secs) * time.Second
	}

	svc := &server{store: newStore(newRedisClient(redisAddr), ttl), log: log}

	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Error("failed to listen", "error", err)
		os.Exit(1)
	}

	grpcSrv := grpc.NewServer(grpc.UnaryInterceptor(svc.logUnary))
	pb.RegisterWishlistServiceServer(grpcSrv, svc)
	healthpb.RegisterHealthServer(grpcSrv, svc)
	reflection.Register(grpcSrv)

	go func() {
		stop := make(chan os.Signal, 1)
		signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
		<-stop
		log.Info("shutting down")
		grpcSrv.GracefulStop()
	}()

	log.Info("starting wishlistservice", "port", port, "redis", redisAddr, "ttl", ttl.String())
	if err := grpcSrv.Serve(lis); err != nil {
		log.Error("server stopped", "error", err)
		os.Exit(1)
	}
	log.Info("wishlistservice stopped")
}

// ---------------------------------------------------------------- interceptor

func (s *server) logUnary(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
	start := time.Now()
	resp, err := handler(ctx, req)
	if info.FullMethod != healthCheckMethod { // las sondas ahogarían el registro
		s.log.Info("rpc",
			"method", info.FullMethod,
			"code", status.Code(err).String(),
			"duration_ms", time.Since(start).Milliseconds())
	}
	return resp, err
}

// --------------------------------------------------------------- health check
//
// Dos niveles, como antes tenían /healthz y /readyz:
//   - sin nombre de servicio (liveness): vivo es vivo.
//   - con nombre de servicio (readiness): además comprueba Redis.

func (s *server) Check(ctx context.Context, req *healthpb.HealthCheckRequest) (*healthpb.HealthCheckResponse, error) {
	if req.GetService() == "" {
		return &healthpb.HealthCheckResponse{Status: healthpb.HealthCheckResponse_SERVING}, nil
	}
	if err := s.store.ping(); err != nil {
		s.log.Warn("readiness check failed", "error", err)
		return &healthpb.HealthCheckResponse{Status: healthpb.HealthCheckResponse_NOT_SERVING}, nil
	}
	return &healthpb.HealthCheckResponse{Status: healthpb.HealthCheckResponse_SERVING}, nil
}

func (s *server) Watch(req *healthpb.HealthCheckRequest, ws healthpb.Health_WatchServer) error {
	return status.Errorf(codes.Unimplemented, "health check via Watch not implemented")
}

// ----------------------------------------------------------------------- RPCs

func (s *server) CreateWishlist(ctx context.Context, req *pb.CreateWishlistRequest) (*pb.Wishlist, error) {
	user, err := validUser(req.GetUserId())
	if err != nil {
		return nil, err
	}
	name := strings.TrimSpace(req.GetName())
	if name == "" {
		name = "My Wishlist"
	}
	if len(name) > maxNameLen {
		name = name[:maxNameLen]
	}
	wl, err := s.store.Create(user, name)
	if err != nil {
		return nil, s.fail(err)
	}
	return toPB(*wl), nil
}

func (s *server) ListWishlists(ctx context.Context, req *pb.ListWishlistsRequest) (*pb.ListWishlistsResponse, error) {
	user, err := validUser(req.GetUserId())
	if err != nil {
		return nil, err
	}
	lists, err := s.store.List(user)
	if err != nil {
		return nil, s.fail(err)
	}
	out := &pb.ListWishlistsResponse{Wishlists: make([]*pb.Wishlist, 0, len(lists))}
	for _, wl := range lists {
		out.Wishlists = append(out.Wishlists, toPB(wl))
	}
	return out, nil
}

func (s *server) GetWishlist(ctx context.Context, req *pb.GetWishlistRequest) (*pb.Wishlist, error) {
	user, err := validUser(req.GetUserId())
	if err != nil {
		return nil, err
	}
	id, err := validID(req.GetId())
	if err != nil {
		return nil, err
	}
	wl, err := s.store.Get(user, id)
	if err != nil {
		return nil, s.fail(err)
	}
	return toPB(*wl), nil
}

func (s *server) RenameWishlist(ctx context.Context, req *pb.RenameWishlistRequest) (*pb.Wishlist, error) {
	user, err := validUser(req.GetUserId())
	if err != nil {
		return nil, err
	}
	id, err := validID(req.GetId())
	if err != nil {
		return nil, err
	}
	name := strings.TrimSpace(req.GetName())
	if name == "" {
		return nil, status.Error(codes.InvalidArgument, "name is required")
	}
	if len(name) > maxNameLen {
		name = name[:maxNameLen]
	}
	wl, err := s.store.Rename(user, id, name)
	if err != nil {
		return nil, s.fail(err)
	}
	return toPB(*wl), nil
}

func (s *server) DeleteWishlist(ctx context.Context, req *pb.DeleteWishlistRequest) (*pb.WishlistEmpty, error) {
	user, err := validUser(req.GetUserId())
	if err != nil {
		return nil, err
	}
	id, err := validID(req.GetId())
	if err != nil {
		return nil, err
	}
	if err := s.store.Delete(user, id); err != nil {
		return nil, s.fail(err)
	}
	return &pb.WishlistEmpty{}, nil
}

func (s *server) AddWishlistItem(ctx context.Context, req *pb.AddWishlistItemRequest) (*pb.WishlistEmpty, error) {
	user, err := validUser(req.GetUserId())
	if err != nil {
		return nil, err
	}
	id, err := validID(req.GetId())
	if err != nil {
		return nil, err
	}
	productID, err := validProduct(req.GetProductId())
	if err != nil {
		return nil, err
	}
	if err := s.store.AddItem(user, id, productID); err != nil {
		return nil, s.fail(err)
	}
	return &pb.WishlistEmpty{}, nil
}

func (s *server) RemoveWishlistItem(ctx context.Context, req *pb.RemoveWishlistItemRequest) (*pb.WishlistEmpty, error) {
	user, err := validUser(req.GetUserId())
	if err != nil {
		return nil, err
	}
	id, err := validID(req.GetId())
	if err != nil {
		return nil, err
	}
	productID, err := validProduct(req.GetProductId())
	if err != nil {
		return nil, err
	}
	if err := s.store.RemoveItem(user, id, productID); err != nil {
		return nil, s.fail(err)
	}
	return &pb.WishlistEmpty{}, nil
}

func (s *server) GetWishlistSummary(ctx context.Context, req *pb.WishlistSummaryRequest) (*pb.WishlistSummaryResponse, error) {
	user, err := validUser(req.GetUserId())
	if err != nil {
		return nil, err
	}
	lists, items, err := s.store.Summary(user)
	if err != nil {
		return nil, s.fail(err)
	}
	return &pb.WishlistSummaryResponse{ListCount: int32(lists), ItemCount: int32(items)}, nil
}

// -------------------------------------------------------------------- helpers

func toPB(w Wishlist) *pb.Wishlist {
	out := &pb.Wishlist{
		Id:        w.ID,
		Name:      w.Name,
		CreatedAt: w.CreatedAt,
		ItemCount: int32(w.ItemCount),
	}
	for _, it := range w.Items {
		out.Items = append(out.Items, &pb.WishlistItem{
			ProductId: it.ProductID,
			AddedAt:   it.AddedAt,
		})
	}
	return out
}

func validUser(user string) (string, error) {
	user = strings.TrimSpace(user)
	if user == "" || len(user) > maxUserIDLen || strings.ContainsAny(user, " \t\r\n") {
		return "", status.Error(codes.InvalidArgument, "user_id is required")
	}
	return user, nil
}

func validID(id string) (string, error) {
	id = strings.TrimSpace(id)
	if id == "" || len(id) > maxUserIDLen {
		return "", status.Error(codes.InvalidArgument, "wishlist id is required")
	}
	return id, nil
}

func validProduct(productID string) (string, error) {
	productID = strings.TrimSpace(productID)
	if productID == "" || len(productID) > maxProductIDLen {
		return "", status.Error(codes.InvalidArgument, "product_id is required")
	}
	return productID, nil
}

// fail traduce los errores del almacenamiento a códigos de gRPC.
func (s *server) fail(err error) error {
	switch {
	case errors.Is(err, errNotFound):
		return status.Error(codes.NotFound, "wishlist not found")
	case errors.Is(err, errTooManyLists):
		return status.Error(codes.ResourceExhausted, "wishlist limit reached")
	case errors.Is(err, errTooManyItems):
		return status.Error(codes.ResourceExhausted, "this wishlist is full")
	default:
		s.log.Error("storage failure", "error", err)
		return status.Error(codes.Unavailable, "storage unavailable")
	}
}
