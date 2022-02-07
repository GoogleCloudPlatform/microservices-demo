package cse.project.ratingservice;

import cse.project.grpc.ApiResponse;
import cse.project.grpc.Empty;
import cse.project.grpc.ProductRatingRequest;
import cse.project.grpc.ProductRatingResponse;
import cse.project.grpc.ProductRequest;

import cse.project.grpc.RatingServiceGrpc.RatingServiceImplBase;
import cse.project.grpc.ShopRatingResponse;
import cse.project.grpc.ShopRequest;
import cse.project.persistence.PersistenceService;
import io.grpc.stub.StreamObserver;
import static java.lang.Math.toIntExact;

public class RatingService extends RatingServiceImplBase{
	
	private PersistenceService persistenceService = new PersistenceService();
	
	@Override
	public void rateProduct(ProductRequest request, StreamObserver<ApiResponse> responseObserver) {
		
		persistenceService.saveProductRating(request.getProductId(), toIntExact(request.getRating()));
		ApiResponse.Builder response = ApiResponse.newBuilder();
		
		response.setResponseMessage("SUCCESS: product rating saved");
		responseObserver.onNext(response.build());
		responseObserver.onCompleted();
	}

	@Override
	public void getProductRating(ProductRatingRequest request, StreamObserver<ProductRatingResponse> responseObserver) {
		
		ProductRatingResponse.Builder response = ProductRatingResponse.newBuilder();
		
		response.setRating(persistenceService.getProductRating(request.getProductId()));
		response.setRatingCount(Long.valueOf(persistenceService.getNumberOfProductRatings(request.getProductId())));
		response.setResponseMessage("SUCESS: rating send");
		responseObserver.onNext(response.build());
		responseObserver.onCompleted();
	}

	@Override
	public void rateShop(ShopRequest request, StreamObserver<ApiResponse> responseObserver) {
		
		persistenceService.saveShopRating(toIntExact(request.getRating()));
		ApiResponse.Builder response = ApiResponse.newBuilder();
		
		response.setResponseMessage("SUCCESS: shop rating saved");
		responseObserver.onNext(response.build());
		responseObserver.onCompleted();
	}

	@Override
	public void getShopRating(Empty request, StreamObserver<ShopRatingResponse> responseObserver) {
		
		ShopRatingResponse.Builder response = ShopRatingResponse.newBuilder();
		
		response.setRating(persistenceService.getShopRating());
		response.setRatingCount(Long.valueOf(persistenceService.getNumberOfShopRatings()));
		response.setResponseMessage("SUCESS: rating send");
		responseObserver.onNext(response.build());
		responseObserver.onCompleted();
	}
	
}
