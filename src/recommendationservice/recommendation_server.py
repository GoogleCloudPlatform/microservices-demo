import grpc
import demo_pb2
import demo_pb2_grpc
from concurrent import futures
import time

class RecommendationService(demo_pb2_grpc.RecommendationServiceServicer):
    def ListRecommendations(self, request, context):
        response = demo_pb2.ListRecommendationsResponse()
        return response

if __name__ == "__main__":
    # create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # add class to gRPC server
    demo_pb2_grpc.add_RecommendationServiceServicer_to_server(RecommendationService(), server)

    # start server
    print("Listening on port 8080")
    server.add_insecure_port('[::]:8080')
    server.start()

    # keep alive
    try:
         while True:
            time.sleep(86400)
    except KeyboardInterrupt:
            server.stop(0)
