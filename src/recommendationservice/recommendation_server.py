import grpc
import demo_pb2
import demo_pb2_grpc
from concurrent import futures
import time

class RecommendationService(demo_pb2_grpc.RecommendationServiceServicer):
    def ListRecommendations(self, request, context):
        print("handling request")
        response = demo_pb2.ListRecommendationsResponse()
        prod_list = []
        for i in range(3):
            this_price = demo_pb2.MoneyAmount(decimal=i,
                                              fractional=i)
            this_prod = demo_pb2.Product(id=i,
                                         name="test-"+str(i),
                                         description="test product",
                                         picture="test image",
                                         price_usd=this_price)
            prod_list.append(this_prod)
        response.products.extend(prod_list)
        return response

if __name__ == "__main__":
    # create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # add class to gRPC server
    demo_pb2_grpc.add_RecommendationServiceServicer_to_server(RecommendationService(), server)

    # start server
    print("Listening on port 8081")
    server.add_insecure_port('[::]:8081')
    server.start()

    # keep alive
    try:
         while True:
            time.sleep(10000)
    except KeyboardInterrupt:
            server.stop(0)
