from thrift import Thrift
from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from thriftpy.demo import CheckoutService
from thriftpy.demo.ttypes import Address, CreditCardInfo

def main():
    uri = "checkout-service-port50000.demo.skyramp.test/CheckoutService"
    socket = THttpClient.THttpClient(f'http://{uri}')
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    transport.open()
    client = CheckoutService.Client(protocol)
    reply = client.PlaceOrder(
            user_id="abcde",
            user_currency="USD",
            address=Address(
                street_address="1600 Amp street",
                city="Mountain View",
                state="CA",
                country="USA",
                zip_code=94043),
            email="someone@example.com",
            credit_card=CreditCardInfo(
                credit_card_number="4432-8015-6152-0454",
                credit_card_cvv=672,
                credit_card_expiration_year=2024,
                credit_card_expiration_month=1))
    print("Successfully placed order.\n")
    print(reply)
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx)
