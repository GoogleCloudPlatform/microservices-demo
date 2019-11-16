import ballerina/grpc;
import ballerina/log;
import ballerina/kubernetes;

// Product catalog client.
ProductCatalogServiceBlockingClient catalogClient = new ("http://productcatalogservice:3550");
final Empty req = {};

@kubernetes:Service {
    serviceType: "ClusterIP",
    name: "recommendationservice"
}
service RecommendationService on new grpc:Listener(8080) {

    resource function ListRecommendations(grpc:Caller caller, ListRecommendationsRequest value) {
        // Fetch list of products from product catalog stub
        var products = catalogClient->ListProducts(req);
        if (products is grpc:Error) {
            log:printError("Error when retrieving products", products);

            // Return a fixed set of recommendations on error.
            ListRecommendationsRequest response = {
                user_id: value.user_id,
                product_ids: ["9SIQT8TOJO", "6E92ZMYYFZ", "LS4PSXUNUM"]
            };
            
            var e = caller->send(response);
            if (e is error) {
                log:printError("Error when sending recommendations", e);
            }

            e = caller->complete();
            if (e is error) {
                log:printError("Error when sending recommendations", e);
            }
        } else {
            // Get the ListProductResponse from the union typed value.
            ListProductsResponse listProductResponse = products[0];
            Product[] productList = listProductResponse.products;
            
            // Extract product id from the product list.
            string[] productIds = [];
            foreach Product product in productList {
                productIds.push(product.id);
            }

            // Filter products which already available in the request.
            string[] filteredProducts = [];
            foreach string productId in productIds {
                boolean isExist = false;
                foreach string availableId in value.product_ids {
                    if (productId == availableId) {
                        isExist = true;
                    }
                }
                if (!isExist) {
                    filteredProducts.push(productId);
                }
            }

            // Send the list of recommentations
            ListRecommendationsRequest response = {
                user_id: value.user_id,
                product_ids: filteredProducts.reverse()
            };

            var e = caller->send(response);
            if (e is error) {
                log:printError("Error when sending recommendations", e);
            }

            e = caller->complete();
            if (e is error) {
                log:printError("Error when sending recommendations", e);
            }
        }
    }
}
