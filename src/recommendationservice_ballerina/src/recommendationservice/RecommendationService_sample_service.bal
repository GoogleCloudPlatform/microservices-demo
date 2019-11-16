import ballerina/grpc;
import ballerina/io;
import ballerina/kubernetes;

// Product catalog client.
ProductCatalogServiceBlockingClient productCat = new ("http://productcatalogservice:3550");

@kubernetes:Service {
    serviceType: "ClusterIP",
    name: "recommendationservice"
}
service RecommendationService on new grpc:Listener(8080) {

    resource function ListRecommendations(grpc:Caller caller, ListRecommendationsRequest value) {
        Empty req = {};
        // Fetch list of products from product catalog stub
        var products = productCat->ListProducts(req);
        if (products is grpc:Error) {
            io:println("Error from Connector: " + products.reason() + " - "
            + <string>products.detail()["message"]);

            // You should return a ListRecommendationsResponse
            ListRecommendationsRequest resp = {
                user_id: value.user_id,
                product_ids: ["9SIQT8TOJO", "6E92ZMYYFZ", "LS4PSXUNUM"]
            };
            io:println(resp);
            var e = caller->send(resp);
            e = caller->complete();
        } else {
            ListProductsResponse listProductResponse;
            grpc:Headers headers;
            [listProductResponse, headers] = products;
            Product[] productList = listProductResponse.products;
            
            // Extract product id from the product list.
            string[] productIds = [];
            int i = 0;
            foreach Product v in productList {
                productIds[i] = v.id;
                i += 1;
            }

            // Filter products which already available in the request.
            string[] filtered_products = [];
            int j = 0;
            foreach string item in productIds {
                boolean isExist = false;
                foreach string v in value.product_ids {
                    if (item == v) {
                        isExist = true;
                    }
                }
                if (!isExist) {
                    filtered_products[j] = item;
                    j += 1;
                }
            }

            // Send the list of recommentations
            ListRecommendationsRequest resp = {
                user_id: value.user_id,
                product_ids: filtered_products.reverse()
            };
            io:println(resp);
            var e = caller->send(resp);
            e = caller->complete();
        }
    }
}
