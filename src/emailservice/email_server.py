from concurrent import futures
import argparse
import os
import sys
import time

from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateError
from google.api_core.exceptions import GoogleAPICallError
import grpc

import demo_pb2
import demo_pb2_grpc

# from opencensus.trace.ext.grpc import server_interceptor
# from opencensus.trace.samplers import always_on
# from opencensus.trace.exporters import stackdriver_exporter
# from opencensus.trace.exporters import print_exporter

# import googleclouddebugger

# try:
#     sampler = always_on.AlwaysOnSampler()
#     exporter = stackdriver_exporter.StackdriverExporter()
#     tracer_interceptor = server_interceptor.OpenCensusServerInterceptor(sampler, exporter)
# except:
#     tracer_interceptor = server_interceptor.OpenCensusServerInterceptor()

# try:
#     googleclouddebugger.enable(
#         module='emailserver',
#         version='1.0.0'
#     )
# except:
#     pass

# Loads confirmation email template from file
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('confirmation.html')

class EmailService(demo_pb2_grpc.EmailServiceServicer):
  def __init__(self):
    raise Exception('cloud mail client not implemented')
    super().__init__()

  @staticmethod
  def send_email(client, email_address, content):
    response = client.send_message(
      sender = client.sender_path(project_id, region, sender_id),
      envelope_from_authority = '',
      header_from_authority = '',
      envelope_from_address = from_address,
      simple_message = {
        "from": {
          "address_spec": from_address,
        },
        "to": [{ 
          "address_spec": email_address 
        }],
        "subject": "Your Confirmation Email",
        "html_body": content
      }
    )
    
    print("Message sent: {}".format(response.rfc822_message_id))

  def SendOrderConfirmation(self, request, context):
    email = request.email
    order = request.order

    try:
      confirmation = template.render(order = order)
    except TemplateError as err:
      context.set_details("An error occurred when preparing the confirmation mail.")
      print(err.message)
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

class DummyEmailService(demo_pb2_grpc.EmailServiceServicer):
  def SendOrderConfirmation(self, request, context):
    print('A request to send order confirmation email to {} has been received.'.format(request.email))
    return demo_pb2.Empty()

def start(dummy_mode):
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))#, interceptors=(tracer_interceptor,))
  if dummy_mode:
    demo_pb2_grpc.add_EmailServiceServicer_to_server(DummyEmailService(), server)
  else:
    raise Exception('non-dummy mode not implemented')
  server.add_insecure_port('[::]:8080')
  server.start()
  try:
    while True:
      time.sleep(3600)
  except KeyboardInterrupt:
    server.stop(0)


if __name__ == '__main__':
  print('Starting the email service in dummy mode.')
  start(dummy_mode = True)
