from thrift import Thrift
from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from thriftpy.demo import ProductCatalogService

def main():

    uri = "productcatalogservice:50000/ProductCatalogService"
    socket = THttpClient.THttpClient(f'http://{uri}')
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    transport.open()
    print("successfully connected to product-catalog-server")
    client = ProductCatalogService.Client(protocol)
    products = client.ListProducts()
    print(f"successfully retrieved products from product cataloge {products}")
    search = client.SearchProducts("accessories")
    print(f"successfully retrieved for products in assocries category {search}")
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx)
