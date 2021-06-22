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

from concurrent import futures
import os
import time
import grpc
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jaeger_client import Config
from grpc_opentracing import open_tracing_server_interceptor
from grpc_opentracing.grpcext import intercept_server
import rook

from utils import demo_pb2_grpc, demo_pb2
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from utils.logger import getJSONLogger
logger = getJSONLogger('emailservice-server')

# Loads confirmation email template from file
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('confirmation.html')

class EmailService(demo_pb2_grpc.EmailServiceServicer):
  def SendOrderConfirmation(self, request, context):
    self.SendOrderLogging(request, context)
    return demo_pb2.Empty()

  def Check(self, request, context):
    return health_pb2.HealthCheckResponse(
      status=health_pb2.HealthCheckResponse.SERVING)

  def Watch(self, request, context):
    return health_pb2.HealthCheckResponse(
      status=health_pb2.HealthCheckResponse.UNIMPLEMENTED)

  def SendOrderLogging(self, request, context):
    logger.info("starting to handle order confirmation email for order_id \"{}\"".format(request.order.order_id))

    logger.debug('''
    shipping address:
    city: \"{}\";
    country: \"{}\";
    street_address_1: \"{}\";
    street_address_2: \"{}\";
    zip_code: \"{}\";
    '''.format(request.order.shipping_address.city,
               request.order.shipping_address.country,
               request.order.shipping_address.street_address_1,
               request.order.shipping_address.street_address_2,
               request.order.shipping_address.zip_code))

    logger.debug("validating order details - \"{}\"".format(request.order.order_id))
    logger.debug("order details are valid - \"{}\"".format(request.order.order_id))

    email = request.email + "%20"
    logger.debug("validating email address - \"{}\"".format(email))
    logger.debug("email address is valid - \"{}\"".format(email))
    logger.debug("email-service failed to send email to address \"{}\"".format(email))
    logger.error("failed to send confirmation email for order_id \"{}\"".format(request.order.order_id))

def init_tracer():
  config = Config(
    config={
      'sampler': {'type': 'const', 'param': 1},
      'local_agent': {
        'reporting_host': 'jaeger-agent',
        'reporting_port': 5775
      }
    },
    service_name='microservices-demo-emailservice')
  return config.initialize_tracer()

def start():
  tracer = init_tracer()
  tracer_interceptor = open_tracing_server_interceptor(tracer)
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  server = intercept_server(server, tracer_interceptor)

  service = EmailService()

  demo_pb2_grpc.add_EmailServiceServicer_to_server(service, server)
  health_pb2_grpc.add_HealthServicer_to_server(service, server)

  port = os.environ.get('PORT', "8080")
  logger.info("listening on port: "+port)
  server.add_insecure_port('[::]:'+port)
  server.start()
  try:
    while True:
      time.sleep(3600)
  except KeyboardInterrupt:
    server.stop(0)


if __name__ == '__main__':
  logger.info('starting the emailservice.')
  rook.start()
  start()
