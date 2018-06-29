using System;
using System.IO;
using System.Linq;
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

        private static ConnectionMultiplexer redis;

        private readonly byte[] emptyCartBytes;
<<<<<<< HEAD
        private readonly string connectionString;
        private readonly string redisAddr;
||||||| merged common ancestors
=======
        private readonly string connectionString;
>>>>>>> origin

        public RedisCartStore(string redisAddress)
        {
            // Serialize empty cart into byte array.
            var cart = new Hipstershop.Cart();
            emptyCartBytes = cart.ToByteArray();
            this.redisAddr = redisAddress;
            connectionString = $"{redisAddress},ssl=false,allowAdmin=true,connectRetry=5";
            Console.WriteLine($"Going to use Redis cache at this address: {connectionString}");
        }

<<<<<<< HEAD
        public Task InitializeAsync()
        {
||||||| merged common ancestors
            string connectionString = $"{redisAddress},ssl=false,allowAdmin=true";
=======
            connectionString = $"{redisAddress},ssl=false,allowAdmin=true";
            Console.WriteLine($"Going to use Redis cache at this address: {connectionString}");
        }

        public async Task InitializeAsync()
        {
>>>>>>> origin
            Console.WriteLine("Connecting to Redis: " + connectionString);
<<<<<<< HEAD

            redis = ConnectionMultiplexer.Connect(connectionString);
            Console.WriteLine("Connected successfully to Redis");

            return Task.CompletedTask;
||||||| merged common ancestors
            redis = ConnectionMultiplexer.Connect(connectionString);
=======
            redis = await ConnectionMultiplexer.ConnectAsync(connectionString, Console.Out);
            Console.WriteLine("Connected successfully to Redis");
>>>>>>> origin
        }

        public async Task AddItemAsync(string userId, string productId, int quantity)
        {
            Console.WriteLine($"AddItemAsync called with userId={userId}, productId={productId}, quantity={quantity}");

            var db = redis.GetDatabase();
            
            // Access the cart from the cache
            var value = await db.HashGetAsync(userId, CART_FIELD_NAME);

            Hipstershop.Cart cart;
            if (value.IsNull)
            {
                cart = new Hipstershop.Cart();
                cart.UserId = userId;
                cart.Items.Add(new Hipstershop.CartItem { ProductId = productId, Quantity = quantity });
            }
            else
            {
                cart = Hipstershop.Cart.Parser.ParseFrom(value);
                var existingItem = cart.Items.SingleOrDefault(i => i.ProductId == productId);
                if (existingItem == null)
                {
                    cart.Items.Add(new Hipstershop.CartItem { ProductId = productId, Quantity = quantity });
                }
                else
                {
                    existingItem.Quantity += quantity;
                }
            }

            await db.HashSetAsync(userId, new[]{ new HashEntry(CART_FIELD_NAME, cart.ToByteArray()) });
        }

        public async Task EmptyCartAsync(string userId)
        {
            Console.WriteLine($"EmptyCartAsync called with userId={userId}");

            var db = redis.GetDatabase();

            // Update the cache with empty cart for given user
            await db.HashSetAsync(userId, new[] { new HashEntry(CART_FIELD_NAME, emptyCartBytes) });
        }

        public async Task<Hipstershop.Cart> GetCartAsync(string userId)
        {
            Console.WriteLine($"GetCartAsync called with userId={userId}");
<<<<<<< HEAD
            try
            {
                var db = redis.GetDatabase();
                // Access the cart from the cache
||||||| merged common ancestors
            var db = redis.GetDatabase();
=======
            try
            {
                var db = redis.GetDatabase();
>>>>>>> origin

<<<<<<< HEAD
                var value = await db.HashGetAsync(userId, CART_FIELD_NAME);
||||||| merged common ancestors
            // Access the cart from the cache
            var value = await db.HashGetAsync(userId, CART_FIELD_NAME);
=======
                // Access the cart from the cache
                var value = await db.HashGetAsync(userId, CART_FIELD_NAME);
>>>>>>> origin

                if (!value.IsNull)
                {
                    return Hipstershop.Cart.Parser.ParseFrom(value);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
            }

            // We decided to return empty cart in cases when user wasn't in the cache before
            return new Hipstershop.Cart();
        }
    }
}
