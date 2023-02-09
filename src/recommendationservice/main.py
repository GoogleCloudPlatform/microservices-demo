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
import recommendation_server as grpc
import recommendation_thrift_server as thrift
import uvicorn

os.environ["DISABLE_TRACING"] = "1"
os.environ["DISABLE_PROFILER"] = "1"

# keep environment variables PRODUCT_CATALOG_SERVICE_ADDR for upstream grpc service
productCatalogService = os.environ.get('PRODUCT_CATALOG_SERVICE_ADDR', "product-catalog-service:8080")
os.environ["PRODUCT_CATALOG_SERVICE_ADDR"] = productCatalogService

productCatalogServiceHost = productCatalogService.split(":")[0]
os.environ["PRODUCT_CATALOG_SERVICE_HOST"] = productCatalogServiceHost
os.environ["REST_PORT"] = "60000"

thriftPort = 50000
restPort = 60000
productCatalogServiceThriftPort = 50000

def runGrpc():
    print("starting recommendation-service grpc endpoint")
    grpc.startGrpc()

def runRest():
    print("starting recommendation-service rest endpoint")
    uvicorn.run(
    "recommendation_rest_server:app",
    host="0.0.0.0",
    port=int(restPort))

def runThrift():
    print("starting recommendation-service thrift endpoint")
    thrift.startThrift(thriftPort, productCatalogServiceHost, productCatalogServiceThriftPort)

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
