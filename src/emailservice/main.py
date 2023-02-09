# Copyright 2022 Skyramp, Inc.
#
#	Licensed under the Apache License, Version 2.0 (the "License");
#	you may not use this file except in compliance with the License.
#	You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	Unless required by applicable law or agreed to in writing, software
#	distributed under the License is distributed on an "AS IS" BASIS,
#	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#	See the License for the specific language governing permissions and
#	limitations under the License.
import os
from time import sleep
from threading import Thread
import email_server as grpc
import email_thrift_server as thrift
import email_rest_server as rest


class Option:
    def __init__(self, port, http=False, tls=False, buffered=False):
        self.port = port
        self.http = http
        self.tls = tls
        self.buffered = buffered

thriftOpt = Option(port="50000")

if "THRIFT_PORT" in os.environ:
    thriftOpt.port = os.environ['THRIFT_PORT']

if "THRIFT_HTTP" in os.environ:
    thriftOpt.http = True

if "THRIFT_TLS" in os.environ:
    thriftOpt.tls = True

if "THRIFT_BUFFERED" in os.environ:
    thriftOpt.buffered = True

restOpt = Option(port="60000")
if "REST_PORT" in os.environ:
    restOpt.port = os.environ['REST_PORT']

if "REST_TLS" in os.environ:
    restOpt.tls = True

def runGrpc():
    print("starting email-service grpc endpoint")
    grpc.startGrpc()

def runRest():
    print("starting email-service rest endpoint")
    rest.startRest(restOpt)

def runThrift():
    print("starting email-service thrift endpoint")
    thrift.startThrift(thriftOpt)

if __name__ == "__main__":
    grpcThread = Thread(target=runGrpc)
    restThread = Thread(target=runRest)
    thriftThread = Thread(target=runThrift)
    grpcThread.start()
    restThread.start()
    thriftThread.start()
    grpcThread.join()
    restThread.join()
    thriftThread.join()
