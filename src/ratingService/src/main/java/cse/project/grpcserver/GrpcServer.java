package cse.project.grpcserver;

import java.io.IOException;

import cse.project.ratingservice.RatingService;
import io.grpc.health.v1.HealthCheckResponse.ServingStatus;
import io.grpc.services.*;
import io.grpc.Server;
import io.grpc.ServerBuilder;

public class GrpcServer {
	public static void main(String[] args) throws IOException, InterruptedException {

		Server server;
		HealthStatusManager healthMgr;
		healthMgr = new HealthStatusManager();
		server = ServerBuilder.forPort(9090).addService(new RatingService()).addService(healthMgr.getHealthService()).build();
		server.start();
		System.out.print("Service started at "+server.getPort());
		healthMgr.setStatus("", ServingStatus.SERVING);
		server.awaitTermination();
	}

}