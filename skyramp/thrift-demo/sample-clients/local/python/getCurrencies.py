from thrift import Thrift
from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from thriftpy.demo import CurrencyService
from thriftpy.demo.ttypes import Money

def main():
    uri = "checkout-service-port50000.demo.skyramp.test/CurrencyService"
    socket = THttpClient.THttpClient(f'http://{uri}')
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    transport.open()
    client = CurrencyService.Client(protocol)
    result = client.GetSupportedCurrencies()
    print("Successfully retrieved list of currencies {result}.\n")
    print(result)

    # Convert Currencies
    result = client.Convert(
        from_curr=Money(currency_code="USD", units= 100, nanos=99000000),
        to_curr="CAD"
        )
    print("Successfully converted currency USD to {result}.\n")
    print(result)
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx)
