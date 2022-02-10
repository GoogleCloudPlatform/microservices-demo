package cse.project.grpcserver;

import java.io.IOException;

import cse.project.ratingservice.RatingService;
import io.grpc.Server;
import io.grpc.ServerBuilder;

public class GrpcServer {

	public static void main(String[] args) throws IOException, InterruptedException {
		
		Server server = ServerBuilder.forPort(9090).addService(new RatingService()).build();
		server.start();
		System.out.print("Service started at "+server.getPort());
		server.awaitTermination();
	}

}
