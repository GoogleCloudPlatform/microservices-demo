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
import ssl
import random

from thrift.transport import TSocket
from thrift.transport import TSSLSocket
from thrift.transport import THttpClient
from thrift.server import TServer
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from thriftpy.demo import RecommendationService, ProductCatalogService

class ListRecommendationHandler(RecommendationService.Iface):
    def ListRecommendations(self, in_product_ids):

        # transport = THttpClient.THttpClient(f'https://{self.productCatalogServerHost}:{self.productCatalogServerPort}')
        transport = TSSLSocket.TSSLSocket(self.productCatalogServerHost, self.productCatalogServerPort, cert_reqs=ssl.CERT_NONE)
        # For http
        # transport = TSocket.TSocket(self.productCatalogServerHost, self.productCatalogServerPort)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        transport.open()
        print("successfully connected to product-catalog-server", flush=True)
        client = ProductCatalogService.Client(protocol)
        products = client.ListProducts()
        print(f"successfully retrieved products from product cataloge {products}", flush=True)
        product_ids =[]
        for product in products:
            print(product.id)
            product_ids.append(product.id)

        max_responses = 5
        filtered_products = list(set(product_ids)-set(in_product_ids))

        num_products = len(filtered_products)
        num_return = min(max_responses, num_products)
        # sample list of indicies to return
        indices = random.sample(range(num_products), num_return)
        # fetch product ids from indices
        prod_list = [filtered_products[i] for i in indices]
        print(f"filtered and returns 5 random id's {prod_list}", flush=True)
        return prod_list

    def __init__(self, productCatalogServerHost, productCatalogServerPort):
        self.productCatalogServerHost = productCatalogServerHost
        self.productCatalogServerPort = productCatalogServerPort


def startServer(port):
    socket = TSocket.TServerSocket(port=port)


def startThrift(thriftPort, productCatalogServerHost, productCatalogServerPort):
    print("starting thrift server on port {}".format(thriftPort), flush=True)
    trans_svr = TSocket.TServerSocket(port=thriftPort)
    proc = RecommendationService.Processor(ListRecommendationHandler(productCatalogServerHost, productCatalogServerPort))
    server = TServer.TSimpleServer(proc, trans_svr)
    server.serve()
