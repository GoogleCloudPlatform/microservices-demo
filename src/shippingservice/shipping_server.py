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
import traceback
from concurrent import futures

import googleclouddebugger
import googlecloudprofiler
from google.auth.exceptions import DefaultCredentialsError
import grpc
from opencensus.trace.exporters import print_exporter
from opencensus.trace.exporters import stackdriver_exporter
from opencensus.trace.ext.grpc import server_interceptor
from opencensus.common.transports.async_ import AsyncTransport
from opencensus.trace.samplers import always_on

import demo_pb2
import demo_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

import easypost

from logger import getJSONLogger
logger = getJSONLogger('shippingservice-server')

from ddtrace import patch_all
patch_all()

def initStackdriverProfiling():
  project_id = None
  try:
    project_id = os.environ["GCP_PROJECT_ID"]
  except KeyError:
    # Environment variable not set
    pass

  for retry in xrange(1,4):
    try:
      if project_id:
        googlecloudprofiler.start(service='shipping_server', service_version='1.0.0', verbose=0, project_id=project_id)
      else:
        googlecloudprofiler.start(service='shipping_server', service_version='1.0.0', verbose=0)
      logger.info("Successfully started Stackdriver Profiler.")
      return
    except (BaseException) as exc:
      logger.info("Unable to start Stackdriver Profiler Python agent. " + str(exc))
      if (retry < 4):
        logger.info("Sleeping %d seconds to retry Stackdriver Profiler agent initialization"%(retry*10))
        time.sleep (1)
      else:
        logger.warning("Could not initialize Stackdriver Profiler after retrying, giving up")
  return

class ShippingService():
    
    def __init__(self, from_address_pb, to_address_pb):
        easypost.api_key = os.environ("EASYPOST_API_KEY")
    
    def create_shipment(self, from_address_pb, to_address_pb):
        self.shipment = easypost.Shipment.create(
                               to_address=self.create_address(to_address_pb),
                               from_address=self.create_address(from_address_pb),
                               parcel=self.create_parcel()
        self.shipment.buy(rate=shipment.lowest_rate(carriers=['USPS'], 
                          services=['First']))
                               )

if __name__ == "__main__":
    logger.info("initializing xchangerateservice")

    port = os.environ.get('PORT', "8082")
    api_key = os.environ.get('EASYPOST_API_KEY', '')
    if api_key == "":
        raise Exception('EASYPOST_API_KEY environment variable not set')

    # create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                      interceptors=(tracer_interceptor,))

    # add class to gRPC server
    service = ShippingService()
    demo_pb2_grpc.add_ShippingServiceServicer_to_server(service, server)
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
