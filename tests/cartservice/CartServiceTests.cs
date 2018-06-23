using System;
using System.Threading.Tasks;
using Grpc.Core;
using Hipstershop;
using Xunit;
using static Hipstershop.CartService;

namespace cartservice
{
    public class E2ETests
    {
        private static string serverHostName = "172.17.0.2";
        private static int port = 7070;

        [Fact]
        public async Task AddItem_ItemInserted()
        {
            string userId = "user1";

            // Construct server's Uri
            string targetUri = $"{serverHostName}:{port}";

            // Create a GRPC communication channel between the client and the server
            var channel = new Channel(targetUri, ChannelCredentials.Insecure);
            //ar interceptorObject = new ObjecT();
            //var channel.Intercept(interceptorObject);
            // Create a proxy object to work with the server
            var client = new CartServiceClient(channel);

            var request = new AddItemRequest
            {
                UserId = userId,
                Item = new CartItem
                {
                    ProductId = "1",
                    Quantity = 1
                }
            };

            for (int i = 0; i < 3; i++)
            {
                try
                {
                    Console.WriteLine("Try " + i+1);
                    await client.AddItemAsync(request);
                    break;
                }
                catch (Exception)
                {
                    continue;
                }
            }
            
            var getCardRequest = new GetCartRequest
            {
                UserId = userId
            };
            var cart = await client.GetCartAsync(getCardRequest);

            Assert.Equal(userId, cart.UserId);
            Assert.Single(cart.Items);
        }
    }
}
