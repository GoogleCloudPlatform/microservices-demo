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

import sys
import grpc
import demo_pb2
import demo_pb2_grpc

from opencensus.trace.tracer import Tracer
from opencensus.trace.exporters import stackdriver_exporter
from opencensus.trace.ext.grpc import client_interceptor

from logger import getJSONLogger
logger = getJSONLogger('recommendationservice-server')

if __name__ == "__main__":
    # get port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = "8080"

    try:
        exporter = stackdriver_exporter.StackdriverExporter()
        tracer = Tracer(exporter=exporter)
        tracer_interceptor = client_interceptor.OpenCensusClientInterceptor(tracer, host_port='localhost:'+port)
    except:
        tracer_interceptor = client_interceptor.OpenCensusClientInterceptor()

    # set up server stub
    channel = grpc.insecure_channel('localhost:'+port)
    channel = grpc.intercept_channel(channel, tracer_interceptor)
    stub = demo_pb2_grpc.RecommendationServiceStub(channel)
    # form request
    request = demo_pb2.ListRecommendationsRequest(user_id="test", product_ids=["test"])
    # make call to server
    response = stub.ListRecommendations(request)
    logger.info(response)
