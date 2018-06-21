import grpc
import demo_pb2
import demo_pb2_grpc
from concurrent import futures
import time
import random
import os

class RecommendationService(demo_pb2_grpc.RecommendationServiceServicer):
    def ListRecommendations(self, request, context):
        max_responses = 5

        # get list of products
        cat_response = stub.ListProducts(demo_pb2.Empty())
        num_prodcuts = len(cat_response.products)

        indices = random.sample(range(num_prodcuts), min(max_responses, num_prodcuts))
        prod_list = [cat_response.products[i].id for i in indices]
        print("handling request: {}".format(prod_list))

        response = demo_pb2.ListRecommendationsResponse()
        response.product_ids.extend(prod_list)
        return response

if __name__ == "__main__":
    # get port from $PORT envar
    port = os.environ.get('PORT', "8080")
    # get product catalog service address from $PRODUCT_CATALOG_SERVICE_ADDR envar
    catalog_addr = os.environ.get('PRODUCT_CATALOG_SERVICE_ADDR', "localhost:8081")

    print("product catalog address: " + catalog_addr)
    print("listening on port: " + port)

    # stub for product catalog service
    channel = grpc.insecure_channel(catalog_addr)
    stub = demo_pb2_grpc.ProductCatalogServiceStub(channel)

    # create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # add class to gRPC server
    demo_pb2_grpc.add_RecommendationServiceServicer_to_server(RecommendationService(), server)

    # start server
    server.add_insecure_port('[::]:'+port)
    server.start()

    # keep alive
    try:
         while True:
            time.sleep(10000)
    except KeyboardInterrupt:
            server.stop(0)
