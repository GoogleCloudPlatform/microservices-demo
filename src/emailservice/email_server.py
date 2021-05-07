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

import argparse
import os
import sys
import time
from concurrent import futures

import grpc
from google.api_core.exceptions import GoogleAPICallError
from grpc_health.v1 import health_pb2, health_pb2_grpc
from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

import demo_pb2
import demo_pb2_grpc
from logger import getJSONLogger

logger = getJSONLogger("emailservice-server")

grpc_server_instrumentor = GrpcInstrumentorServer()
grpc_server_instrumentor.instrument()
otlp_exporter = OTLPSpanExporter()

# Loads confirmation email template from file
env = Environment(
    loader=FileSystemLoader("templates"), autoescape=select_autoescape(["html", "xml"])
)
template = env.get_template("confirmation.html")


class BaseEmailService(demo_pb2_grpc.EmailServiceServicer):
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING
        )

    def Watch(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.UNIMPLEMENTED
        )


class EmailService(BaseEmailService):
    def __init__(self):
        raise Exception("cloud mail client not implemented")
        super().__init__()

    @staticmethod
    def send_email(client, email_address, content):
        response = client.send_message(
            sender=client.sender_path(project_id, region, sender_id),
            envelope_from_authority="",
            header_from_authority="",
            envelope_from_address=from_address,
            simple_message={
                "from": {
                    "address_spec": from_address,
                },
                "to": [{"address_spec": email_address}],
                "subject": "Your Confirmation Email",
                "html_body": content,
            },
        )
        logger.info("Message sent: {}".format(response.rfc822_message_id))

    def SendOrderConfirmation(self, request, context):
        email = request.email
        order = request.order

        try:
            confirmation = template.render(order=order)
        except TemplateError as err:
            context.set_details(
                "An error occurred when preparing the confirmation mail."
            )
            logger.error(err.message)
            context.set_code(grpc.StatusCode.INTERNAL)
            return demo_pb2.Empty()

        try:
            EmailService.send_email(self.client, email, confirmation)
        except GoogleAPICallError as err:
            context.set_details("An error occurred when sending the email.")
            print(err.message)
            context.set_code(grpc.StatusCode.INTERNAL)
            return demo_pb2.Empty()

        return demo_pb2.Empty()


class DummyEmailService(BaseEmailService):
    def SendOrderConfirmation(self, request, context):
        logger.info(
            "A request to send order confirmation email to {} has been received.".format(
                request.email
            )
        )
        return demo_pb2.Empty()


class HealthCheck:
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING
        )


def start(dummy_mode):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = None
    if dummy_mode:
        service = DummyEmailService()
    else:
        raise Exception("non-dummy mode not implemented yet")

    demo_pb2_grpc.add_EmailServiceServicer_to_server(service, server)
    health_pb2_grpc.add_HealthServicer_to_server(service, server)

    port = os.environ.get("PORT", "8080")
    logger.info("listening on port: " + port)
    server.add_insecure_port("[::]:" + port)
    server.start()
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    logger.info("starting the email service in dummy mode.")
    resource = Resource(attributes={"service.name": "emailservice"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))
    start(dummy_mode=True)
