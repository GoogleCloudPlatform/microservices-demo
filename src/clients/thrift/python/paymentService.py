from thrift import Thrift
from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from thriftpy.demo import PaymentService
from thriftpy.demo.ttypes import Money, CreditCardInfo

def main():
    uri = "paymentservice:50000/PaymentService"
    socket = THttpClient.THttpClient(f'http://{uri}')
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    transport.open()
    client = PaymentService.Client(protocol)
    reply = client.Charge(
            amount=Money(
                currency_code="USD",
                units=100,
                nanos=9900000
            ),
            credit_card=CreditCardInfo(
                credit_card_number="4432-8015-6152-0454",
                credit_card_cvv=672,
                credit_card_expiration_year=2024,
                credit_card_expiration_month=1))
    print("Successfully charged for order.\n")
    print(reply)
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx)
