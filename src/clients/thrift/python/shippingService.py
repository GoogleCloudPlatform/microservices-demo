from thrift import Thrift
from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from thriftpy.demo import ShippingService
from thriftpy.demo.ttypes import Address, CartItem

def main():
    uri = "shippingservice:50000/ShippingService"
    socket = THttpClient.THttpClient(f'http://{uri}')
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    transport.open()
    client = ShippingService.Client(protocol)

    items = []
    items.append( CartItem(product_id="OLJCESPC7Z", quantity=1))
    items.append( CartItem(product_id="66VCHSJNUP", quantity=3))
    items.append( CartItem(product_id="1YMWWN1N4O", quantity=2))

    address=Address(
        street_address="1600 Amp street",
        city="Mountain View",
        state="CA",
        country="USA",
        zip_code=94043)

    print("About to call ShippingService.GetQuote().")
    response = client.GetQuote(address=address, items=items)
    print("Successfully called ShippingService.GetQuote().")
    print(response)
    print("\nAbout to call ShippingService.ShipOrder().")
    response = client.ShipOrder(address=address, items=items)
    print("Successfully called ShippingService.ShipOrder().")
    print(response)
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx)
