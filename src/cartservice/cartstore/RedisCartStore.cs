using System;
using System.IO;
using System.Threading.Tasks;
using cartservice.interfaces;
using Google.Protobuf;
using Hipstershop;
using StackExchange.Redis;

namespace cartservice.cartstore
{
    public class RedisCartStore : ICartStore
    {
        private const string CART_FIELD_NAME = "cart";

        private readonly ConnectionMultiplexer redis;

        private readonly byte[] emptyCartBytes;

        public RedisCartStore(string redisAddress)
        {
            // Serialize empty cart into byte array.
            var cart = new Hipstershop.Cart();
            emptyCartBytes = cart.ToByteArray();

            string connectionString = $"{redisAddress},ssl=false,allowAdmin=true";
            Console.WriteLine("Connecting to Redis: " + connectionString);
            redis = ConnectionMultiplexer.Connect(connectionString);
        }

        public async Task AddItemAsync(string userId, string productId, int quantity)
        {
            var db = redis.GetDatabase();
            
            // Access the cart from the cache
            var value = await db.HashGetAsync(userId, CART_FIELD_NAME);

            Hipstershop.Cart cart;
            if (value.IsNull)
            {
                cart = new Hipstershop.Cart();
            }
            else
            {
                cart = Hipstershop.Cart.Parser.ParseFrom(value);
            }

            cart.Items.Add(new Hipstershop.CartItem { ProductId = productId, Quantity = quantity });
        }

        public async Task EmptyCartAsync(string userId)
        {
            var db = redis.GetDatabase();

            // Update the cache with empty cart for given user
            await db.HashSetAsync(userId, new[] { new HashEntry(CART_FIELD_NAME, emptyCartBytes) });
        }

        public async Task<Hipstershop.Cart> GetCartAsync(string userId)
        {
            var db = redis.GetDatabase();

            // Access the cart from the cache
            var value = await db.HashGetAsync(userId, CART_FIELD_NAME);

            Hipstershop.Cart cart = null;
            if (!value.IsNull)
            {
                cart = Hipstershop.Cart.Parser.ParseFrom(value);
            }

            return cart;
        }
    }
}