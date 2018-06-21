using System.Collections.Concurrent;
using cartservice.interfaces;

namespace cartservice.cartstore
{
    internal class LocalCartStore 
    {
        // Maps between user and their cart
        private ConcurrentDictionary<string, Cart> userCartItems = new ConcurrentDictionary<string, Cart>();

        public void AddItem(string userId, string productId, int quantity)
        {
            Cart cart;
            if (!userCartItems.TryGetValue(userId, out cart))
            {
                cart = new Cart(userId);
            }
            else
            {
                cart = userCartItems[userId];
            }
            cart.AddItem(productId, quantity);
        }

        public void EmptyCart(string userId)
        {
            Cart cart;
            if (userCartItems.TryGetValue(userId, out cart))
            {
                cart.EmptyCart();
            }
        }

        public Cart GetCart(string userId)
        {
            Cart cart = null;
            userCartItems.TryGetValue(userId, out cart);
            return cart;
        }
    }
}