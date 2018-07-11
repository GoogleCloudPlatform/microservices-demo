package internal

import "google.golang.org/grpc"
import "go.opencensus.io/plugin/ocgrpc"

func DefaultDialOptions() []grpc.DialOption {
	return []grpc.DialOption{
		grpc.WithInsecure(),
		grpc.WithStatsHandler(&ocgrpc.ClientHandler{}),
	}
}

func DefaultServerOptions() []grpc.ServerOption {
	return []grpc.ServerOption{
		grpc.StatsHandler(&ocgrpc.ServerHandler{}),
	}
}
