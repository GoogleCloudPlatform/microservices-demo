import os
import ssl
import sys
sys.path.append('thriftpy')

from thrift import Thrift
from thrift.transport import TSSLSocket
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from demo import EmailService

def main():
    socket = TSSLSocket.TSSLSocket('email-service', 50000, cert_reqs=ssl.CERT_NONE)
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    transport.open()
    print("successfully connected to email-service", flush=True)
    client = EmailService.Client(protocol)
    order = Thrift.TType.LIST
    order['order_']
        "order_id": "100",
        "shipping_tracking_id": "abcde",
        "shiping_cost": {"currency_code": "USD", "units": 100, "nanos": 20}
    }
    client.SendOrderConfirmation("user@mail.com", order)
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx.message)