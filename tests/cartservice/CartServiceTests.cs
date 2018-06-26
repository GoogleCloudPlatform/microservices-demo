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
        private static string serverHostName = "localhost";
        private static int port = 7070;

        [Fact]
        public async Task GetItem_NoAddItemBefore_EmptyCartReturned()
        {
            string userId = Guid.NewGuid().ToString();

            // Construct server's Uri
            string targetUri = $"{serverHostName}:{port}";

            // Create a GRPC communication channel between the client and the server
            var channel = new Channel(targetUri, ChannelCredentials.Insecure);

            var client = new CartServiceClient(channel);

            var request = new GetCartRequest
            {
                UserId = userId,
            };
            var cart = await client.GetCartAsync(request);
            Assert.NotNull(cart);
            // All grpc objects implement IEquitable, so we can compare equality with by-value semantics
            Assert.Equal(new Cart(), cart);
        }

        [Fact]
        public async Task AddItem_ItemInserted()
        {
            string userId = Guid.NewGuid().ToString();

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

/*
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
                    await Task.Delay(1000);
                    continue;
                }
            }
*/            
            await client.AddItemAsync(request);
            var getCartRequest = new GetCartRequest
            {
                UserId = userId
            };
            //await client.EmptyCartAsync(nameof)
            //await client.EmptyCartAsync(new EmptyCartRequest{ UserId = userId });

            var cart = await client.GetCartAsync(getCartRequest);
            Assert.NotNull(cart);
            Assert.Equal(userId, cart.UserId);
            Assert.Single(cart.Items);

            await client.EmptyCartAsync(new EmptyCartRequest{ UserId = userId });
            cart = await client.GetCartAsync(getCartRequest);
            Assert.Empty(cart.Items);
        }
    }
}
