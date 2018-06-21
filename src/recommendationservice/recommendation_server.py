import grpc
import demo_pb2
import demo_pb2_grpc
from concurrent import futures
import time
import random
import os

class RecommendationService(demo_pb2_grpc.RecommendationServiceServicer):
    def ListRecommendations(self, request, context):
        print("handling request")
        response = demo_pb2.ListRecommendationsResponse()
        prod_list = []
        for i in range(5):
            prod_list.append(str(random.randint(1,100)))
        response.product_ids.extend(prod_list)
        return response

if __name__ == "__main__":
    # get port from $PORT envar
    port = os.environ.get('PORT', "8080")
    # get product catalog service address from $PRODUCT_CATALOG_SERVICE_ADDR envar
    catalog_addr = os.environ.get('PRODUCT_CATALOG_SERVICE_ADDR', "localhost:8081")

    print("product catalog address: " + catalog_addr)
    print("listening on port: " + port)

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
