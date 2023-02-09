from thrift import Thrift
from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from thriftpy.demo import RecommendationService

def main():

    uri = "recommendation-service-port50000.demo.skyramp.test/RecommendationService"
    socket = THttpClient.THttpClient(f'http://{uri}')
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    transport.open()
    print("successfully connected to recommendation-service")
    client = RecommendationService.Client(protocol)
    cart_item = [ "9SIQT8TOJO" ]
    recommendations = client.ListRecommendations(cart_item)
    print(f"successfully retrieved recommendations from recommendation service {recommendations}")
    transport.close()

if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx)
