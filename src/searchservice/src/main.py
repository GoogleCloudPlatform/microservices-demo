import grpc
from concurrent import futures

import search_pb2
import search_pb2_grpc
from product_cache import ProductCache


class SearchService(search_pb2_grpc.SearchServiceServicer):
    def __init__(self, product_cache):
        self.product_cache = product_cache

    def Search(self, request, context):
        query = request.query
        results = self.cache.search(query)

        return search_pb2.SearchResponse(results=results)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    product_cache = ProductCache("productcatalogservice:3550")
    search_service = SearchService(product_cache)

    search_pb2_grpc.add_SearchServiceServicer_to_server(search_service, server)

    server.add_insecure_port("[::]:8080")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()