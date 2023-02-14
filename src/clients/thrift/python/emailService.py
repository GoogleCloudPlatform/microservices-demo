from thrift import Thrift
from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from thriftpy.demo import EmailService
from thriftpy.demo.ttypes import Address, CartItem, OrderResult, OrderItem, Money

def main():
    uri = "emailservice:50000/EmailService"
    socket = THttpClient.THttpClient(f'http://{uri}')
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    transport.open()
    client = EmailService.Client(protocol)


    order_id="0a8e4c64-7fb3-4579-b05b-65cacdab69a1"
    shipping_tracking_id="7b16c3c4-41ab-11ed-b878-0242ac120002"
    shipping_cost=Money(currency_code="USD", units=150, nanos=99000000)
    shipping_address=Address(
        street_address="1600 Amp street",
        city="Mountain View",
        state="CA",
        country="USA",
        zip_code=94043)

    items=[]

    items.append(OrderItem(
        CartItem(product_id="OLJCESPC7Z", quantity=1),
        Money(currency_code="USD", units=15, nanos=99000000),
        ))

    items.append(OrderItem(
        CartItem(product_id="66VCHSJNUP", quantity=3),
        Money(currency_code="USD", units=75, nanos=99000000),
        ))
    items.append(OrderItem(
        CartItem(product_id="1YMWWN1N4O", quantity=2),
        Money(currency_code="USD", units=60, nanos=99000000),
        ))

    print("About to call EmailService.SendOrderConfirmation().")
    response = client.SendOrderConfirmation(
        "someone@example.com",
        OrderResult(
            order_id,
            shipping_tracking_id,
            shipping_cost,
            shipping_address,
            items)
        )
    print("Successfully called EmailService.SendOrderConfirmation().")
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx)
