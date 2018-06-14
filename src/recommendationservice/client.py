import grpc
import demo_pb2
import demo_pb2_grpc

channel = grpc.insecure_channel('localhost:8081')
stub = demo_pb2_grpc.RecommendationServiceStub(channel)

request = demo_pb2.ListRecommendationsRequest(user_id="test", product_ids=["test"])

response = stub.ListRecommendations(request)

print(response)
