using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;
using cartservice.interfaces;
using Hipstershop;

namespace cartservice.cartstore
{
    internal class LocalCartStore : ICartStore
    {
        // Maps between user and their cart
        private ConcurrentDictionary<string, Hipstershop.Cart> userCartItems = new ConcurrentDictionary<string, Hipstershop.Cart>();

        public Task AddItemAsync(string userId, string productId, int quantity)
        {
            Console.WriteLine($"AddItemAsync called with userId={userId}, productId={productId}, quantity={quantity}");
            var newCart = new Hipstershop.Cart
                {
                    UserId = userId,
                    Items = { new Hipstershop.CartItem { ProductId = productId, Quantity = quantity } }
                };
            userCartItems.AddOrUpdate(userId, newCart,
            (k, exVal) =>
            {
                // Currently we assume that we only add to the cart
                exVal.Items.Add(new Hipstershop.CartItem { ProductId = productId, Quantity = quantity });
                return exVal;
            });

            return Task.CompletedTask;
        }

        public Task EmptyCartAsync(string userId)
        {
            Console.WriteLine($"EmptyCartAsync called with userId={userId}");
            userCartItems[userId] = new Hipstershop.Cart();

            return Task.CompletedTask;
        }

        public Task<Hipstershop.Cart> GetCartAsync(string userId)
        {
            Console.WriteLine($"GetCartAsync called with userId={userId}");
            Hipstershop.Cart cart = null;
            if (!userCartItems.TryGetValue(userId, out cart))
            {
                Console.WriteLine($"No carts for user {userId}");
            }
            return Task.FromResult(cart);
        }
    }
}