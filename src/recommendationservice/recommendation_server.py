#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import random
import time
from concurrent import futures

import grpc
import rook
from jaeger_client import Config
from grpc_opentracing import open_tracing_server_interceptor
from grpc_opentracing.grpcext import intercept_server

from utils import demo_pb2, demo_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from utils.logger import getJSONLogger
logger = getJSONLogger('recommendationservice-server')

class RecommendationService(demo_pb2_grpc.RecommendationServiceServicer):
    def ListRecommendations(self, request, context):
        max_responses = 5
        # fetch list of products from product catalog stub
        cat_response = product_catalog_stub.ListProducts(demo_pb2.Empty())
        product_ids = [x.id for x in cat_response.products]
        known_product_ids = list(set(request.product_ids))
        filtered_products = list(set(product_ids)-set(request.product_ids))
        num_products = len(filtered_products)
        num_return = min(max_responses, num_products)
        # sample list of indicies to return
        indices = random.sample(range(num_products), num_return)
        # fetch product ids from indices
        prod_list = [filtered_products[i] for i in indices]
        self.RecommendationLogging(request.user_id, known_product_ids, prod_list)
        # build and return response
        response = demo_pb2.ListRecommendationsResponse()
        response.product_ids.extend(prod_list)
        return response

    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)

    def Watch(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.UNIMPLEMENTED)

    def RecommendationLogging(self, user_id, known_products, recommended_products):
        logger.info("handling recommendations for user \"{}\"".format(user_id))
        logger.debug("products the user is interested in - {}".format(known_products))
        logger.debug("products recommended to the user - {}".format(recommended_products))
        logger.info("done calculating recommendations for user \"{}\"".format(user_id))


def init_tracer():
  config = Config(
    config={
      'sampler': {'type': 'const', 'param': 1},
      'local_agent': {
        'reporting_host': 'jaeger-agent',
        'reporting_port': 5775
      }
    },
    service_name='microservices-demo-recommendationservice')
  return config.initialize_tracer()


if __name__ == "__main__":
    logger.info("initializing recommendationservice")

    rook.start()

    port = os.environ.get('PORT', "8080")
    catalog_addr = os.environ.get('PRODUCT_CATALOG_SERVICE_ADDR', '')
    if catalog_addr == "":
        raise Exception('PRODUCT_CATALOG_SERVICE_ADDR environment variable not set')
    logger.info("product catalog address: " + catalog_addr)
    channel = grpc.insecure_channel(catalog_addr)
    product_catalog_stub = demo_pb2_grpc.ProductCatalogServiceStub(channel)

    # create gRPC server
    tracer = init_tracer()
    tracer_interceptor = open_tracing_server_interceptor(tracer)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server = intercept_server(server, tracer_interceptor)

    # add class to gRPC server
    service = RecommendationService()
    demo_pb2_grpc.add_RecommendationServiceServicer_to_server(service, server)
    health_pb2_grpc.add_HealthServicer_to_server(service, server)

    # start server
    logger.info("listening on port: " + port)
    server.add_insecure_port('[::]:'+port)
    server.start()

    # keep alive
    try:
         while True:
            time.sleep(10000)
    except KeyboardInterrupt:
            server.stop(0)
