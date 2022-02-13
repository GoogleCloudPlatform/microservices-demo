package hipstershop;

import java.io.IOException;

import cse.project.ratingservice.RatingServiceRate;
import io.opencensus.contrib.grpc.metrics.RpcViews;
import io.grpc.health.v1.HealthCheckResponse.ServingStatus;
import io.grpc.services.*;
import io.grpc.Server;
import io.grpc.ServerBuilder;

public class RatingService {
	public static void main(String[] args) throws IOException, InterruptedException {

		RpcViews.registerAllViews();
		Server server;
		HealthStatusManager healthMgr;
		healthMgr = new HealthStatusManager();
		server = ServerBuilder.forPort(9090).addService(new RatingServiceRate()).addService(healthMgr.getHealthService()).build();
		server.start();
		System.out.print("Service started at "+server.getPort());
		healthMgr.setStatus("", ServingStatus.SERVING);
		server.awaitTermination();
	}

}