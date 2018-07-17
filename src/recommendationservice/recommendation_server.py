import grpc
import demo_pb2
import demo_pb2_grpc
from concurrent import futures
import time
import random
import os

from opencensus.trace.ext.grpc import server_interceptor
from opencensus.trace.samplers import always_on
from opencensus.trace.exporters import stackdriver_exporter
from opencensus.trace.exporters import print_exporter

import googleclouddebugger

class RecommendationService(demo_pb2_grpc.RecommendationServiceServicer):
    def ListRecommendations(self, request, context):
        max_responses = 5
        # fetch list of products from product catalog stub
        cat_response = stub.ListProducts(demo_pb2.Empty())
        product_ids = [x.id for x in cat_response.products]
        filtered_products = list(set(product_ids)-set(request.product_ids))
        num_products = len(filtered_products)
        num_return = min(max_responses, num_products)
        # sample list of indicies to return
        indices = random.sample(range(num_products), num_return)
        # fetch product ids from indices
        prod_list = [filtered_products[i] for i in indices]
        print("handling request: {}".format(prod_list))
        # build and return response
        response = demo_pb2.ListRecommendationsResponse()
        response.product_ids.extend(prod_list)
        return response

if __name__ == "__main__":
    print("starting recommendationservice")
    try:
        sampler = always_on.AlwaysOnSampler()
        exporter = stackdriver_exporter.StackdriverExporter()
        tracer_interceptor = server_interceptor.OpenCensusServerInterceptor(sampler, exporter)
    except:
        tracer_interceptor = server_interceptor.OpenCensusServerInterceptor()

    try:
        googleclouddebugger.enable(
            module='recommendationserver',
            version='1.0.0'
        )
    except:
        pass

    # get port from $PORT envar
    port = os.environ.get('PORT', "8080")
    # get product catalog service address from $PRODUCT_CATALOG_SERVICE_ADDR envar
    catalog_addr = os.environ.get('PRODUCT_CATALOG_SERVICE_ADDR', '')
    if catalog_addr == "":
        raise Exception('PRODUCT_CATALOG_SERVICE_ADDR environment not set')
    print("product catalog address: " + catalog_addr)
    print("listening on port: " + port)
    # stub for product catalog service
    channel = grpc.insecure_channel(catalog_addr)
    stub = demo_pb2_grpc.ProductCatalogServiceStub(channel)
    # create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),interceptors=(tracer_interceptor,))
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
