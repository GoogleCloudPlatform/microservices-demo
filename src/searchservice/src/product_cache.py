import grpc
import time
from typing import List

from recommendationservice import demo_pb2
from recommendationservice import demo_pb2_grpc


class ProductCache:
    def __init__(self, catalog_addr: str):
        self.catalog_addr = catalog_addr
        self.products = []
        self.last_update = 0

        channel = grpc.insecure_channel(catalog_addr)
        self.stub = demo_pb2_grpc.ProductCatalogServiceStub(channel)

    def refresh(self):
        if time.time() - self.last_update < 120:
            return
        
        response = self.stub.ListProducts(demo_pb2.Empty())
        self.products = response.products
        self.last_update = time.time()

    def search(self, query: str):
        self.refresh_if_needed()

        q = query.lower()
        return [p for p in self.products
                    if q in p.name.lower()
        ]

