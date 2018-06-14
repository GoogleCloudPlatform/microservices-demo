import grpc
import demo_pb2
import demo_pb2_grpc
import sys

if __name__ == "__main__":
    # get port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = "8080"

    # set up server stub
    channel = grpc.insecure_channel('localhost:'+port)
    stub = demo_pb2_grpc.RecommendationServiceStub(channel)

    # form request
    request = demo_pb2.ListRecommendationsRequest(user_id="test", product_ids=["test"])

    # make call to server
    response = stub.ListRecommendations(request)
    print(response)
