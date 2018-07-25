import grpc

import demo_pb2
import demo_pb2_grpc

# from opencensus.trace.tracer import Tracer
# from opencensus.trace.exporters import stackdriver_exporter
# from opencensus.trace.ext.grpc import client_interceptor

# try:
#     exporter = stackdriver_exporter.StackdriverExporter()
#     tracer = Tracer(exporter=exporter)
#     tracer_interceptor = client_interceptor.OpenCensusClientInterceptor(tracer, host_port='0.0.0.0:8080')
# except:
#     tracer_interceptor = client_interceptor.OpenCensusClientInterceptor()

def send_confirmation_email(email, order):
  channel = grpc.insecure_channel('0.0.0.0:8080')
  # channel = grpc.intercept_channel(channel, tracer_interceptor)
  stub = demo_pb2_grpc.EmailServiceStub(channel)
  try:
    response = stub.SendOrderConfirmation(demo_pb2.SendOrderConfirmationRequest(
      email = email,
      order = order
    ))
    print('Request sent.')
  except grpc.RpcError as err:
    print(err.details())
    print('{}, {}'.format(err.code().name, err.code().value))

if __name__ == '__main__':
  print('Client for email service.')