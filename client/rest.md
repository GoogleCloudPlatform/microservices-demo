




# Cart Service

```
Curl:

CART_SERVER=127.0.0.1:60000

get cart
curl http://$CART_SERVER/get-cart?user_id='12345'

empty cart
curl http://$CART_SERVER/get-cart?user_id='12345'

add cart
curl http://$CART_SERVER/add-cart?user_id='12345'&product_id="HAT"&quantity=3

curl http://dev:60000/get-cart\?user_id\=12345   
curl http://dev:60000/add-cart\?user_id\=12345\&product_id\=123\&quantity\=4




Phyton:

if http:
    transport = THttpClient.THttpClient(host, port, uri)
else:
    if ssl:
        socket = TSSLSocket.TSSLSocket(host, port, validate=validate, ca_certs=ca_certs, keyfile=keyfile, certfile=certfile)
    else:
        socket = TSocket.TSocket(host, port)
    if framed:
        transport = TTransport.TFramedTransport(socket)
    else:
        transport = TTransport.TBufferedTransport(socket)


import os
import sys
sys.path.append('thriftpy')

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from demo import CartService
transport = THttpClient.THttpClient(host, port, uri)
protocol = TBinaryProtocol(transport)
client = CartService.Client(protocol)
transport.open()
res = client


```

