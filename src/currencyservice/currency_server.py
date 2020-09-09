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

from logger import getJSONLogger
logger = getJSONLogger('xchangerateservice-server')

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
        googlecloudprofiler.start(service='xchangerate_server', service_version='1.0.0', verbose=0, project_id=project_id)
      else:
        googlecloudprofiler.start(service='xchangerate_server', service_version='1.0.0', verbose=0)
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

class xChangeRateiService():
    
    def __init__(self):
        API_KEY = '6a565ada48da0541918ea2a9'        # os.environ("EXCHANGERATE_API_KEY")
        url = 'https://v6.exchangerate-api.com/v6/'+ API_KEY + '/latest/USD'
        response = requests.get(url)
        data = response.json()
        self.rates = data['conversion_rates']
    
    def convert (self, amt, from_curr, to_curr):
        try:
            return amt * self.rates[to_curr] / self.rates[from_curr]
        except:
            raise

if __name__ == "__main__":
    logger.info("initializing xchangerateservice")

    port = os.environ.get('PORT', "8081")
    api_key = os.environ.get('EXCHANGERATE_API_KEY', '')
    if api_key == "":
        raise Exception('EXCHANGERATE_API_KEY environment variable not set')

    # create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                      interceptors=(tracer_interceptor,))

    # add class to gRPC server
    service = xChangeRateiService()
    demo_pb2_grpc.add_xChangeRateiServiceServicer_to_server(service, server)
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
