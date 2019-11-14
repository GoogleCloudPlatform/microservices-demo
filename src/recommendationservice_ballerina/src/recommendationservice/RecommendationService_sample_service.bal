import ballerina/grpc;

listener grpc:Listener ep = new (9090);

service RecommendationService on ep {

    resource function ListRecommendations(grpc:Caller caller, ListRecommendationsRequest value) {
        // Implementation goes here.

        // You should return a ListRecommendationsResponse
    }
}

