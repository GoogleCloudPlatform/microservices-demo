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
import argparse
import os
import sys
import time
import grpc
import urllib.parse
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateError

import demo_pb2
import demo_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from opentelemetry import trace
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient

from logger import getJSONLogger
logger = getJSONLogger('emailservice-server')

zipkin_exporter = ZipkinExporter(endpoint=os.environ['SIGNALFX_ENDPOINT_URL'])
span_processor = BatchSpanProcessor(zipkin_exporter)

set_global_textmap(B3MultiFormat)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(span_processor)
tracer = trace.get_tracer(__name__)

instrumentor = GrpcInstrumentorClient()
instrumentor.instrument()
grpc_server_instrumentor = GrpcInstrumentorServer()
grpc_server_instrumentor.instrument()


# Loads confirmation email template from file
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('confirmation.html')

class BaseEmailService(demo_pb2_grpc.EmailServiceServicer):
  def Check(self, request, context):
    return health_pb2.HealthCheckResponse(
      status=health_pb2.HealthCheckResponse.SERVING)

  def Watch(self, request, context, send_response_callback=None):
      context.write(health_pb2.HealthCheckResponse(status=health_pb2.HealthCheckResponse.SERVING))


class DummyEmailService(BaseEmailService):
  def SendOrderConfirmation(self, request, context):
    logger.info('A request to send order confirmation email to {} has been received.'.format(request.email))
    return demo_pb2.Empty()


class HealthCheck():
  def Check(self, request, context):
    return health_pb2.HealthCheckResponse(
      status=health_pb2.HealthCheckResponse.SERVING)

  def Watch(self, request, context, send_response_callback=None):
      context.write(health_pb2.HealthCheckResponse(status=health_pb2.HealthCheckResponse.SERVING))

def start():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  service = None
  service = DummyEmailService()

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

  start()
