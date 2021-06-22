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
from google.auth.exceptions import DefaultCredentialsError

from utils import demo_pb2_grpc, demo_pb2
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
import rook

from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
from opencensus.ext.grpc import server_interceptor
from opencensus.common.transports.async_ import AsyncTransport
from opencensus.trace import samplers

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
    shipping address:\n
    city: \"{}\"\n
    country: \"{}\"\n
    street_address_1: \"{}\"\n
    street_address_2: \"{}\"\n
    zip_code: \"{}\"
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

def start():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                       interceptors=(tracer_interceptor,))
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
  logger.info('starting the email service in dummy mode.')

  rook.start()

  try:
    if "DISABLE_TRACING" in os.environ:
      raise KeyError()
    else:
      logger.info("Tracing enabled.")
      sampler = samplers.AlwaysOnSampler()
      exporter = stackdriver_exporter.StackdriverExporter(
        project_id=os.environ.get('GCP_PROJECT_ID'),
        transport=AsyncTransport)
      tracer_interceptor = server_interceptor.OpenCensusServerInterceptor(sampler, exporter)
  except (KeyError, DefaultCredentialsError):
      logger.info("Tracing disabled.")
      tracer_interceptor = server_interceptor.OpenCensusServerInterceptor()

  start()
