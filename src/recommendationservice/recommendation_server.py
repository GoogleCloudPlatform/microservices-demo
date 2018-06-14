import grpc
import demo_pb2
import demo_pb2_grpc
from concurrent import futures
import time
import sys
import random

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
    # get port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = "8080"

    # create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # add class to gRPC server
    demo_pb2_grpc.add_RecommendationServiceServicer_to_server(RecommendationService(), server)

    # start server
    print("Listening on port " + port)
    server.add_insecure_port('[::]:'+port)
    server.start()

    # keep alive
    try:
         while True:
            time.sleep(10000)
    except KeyboardInterrupt:
            server.stop(0)
