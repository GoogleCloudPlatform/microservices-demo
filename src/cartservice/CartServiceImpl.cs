using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Grpc.Core;
using Hipstershop;
using static Hipstershop.CartService;

namespace cartservice
{
    // Cart wrapper to deal with grpc communication
    internal class CartServiceImpl : CartServiceBase
    {
        private CartStore cartStore;

        public CartServiceImpl(CartStore cartStore)
        {
            this.cartStore = cartStore;
        }

        public override Task<Empty> AddItem(AddItemRequest request, Grpc.Core.ServerCallContext context)
        {
            cartStore.AddItem(request.UserId, request.Item.ProductId, request.Item.Quantity);
            return Task.FromResult(new Empty());
        }

        public override Task<Empty> EmptyCart(EmptyCartRequest request, ServerCallContext context)
        {
            cartStore.EmptyCart(request.UserId);
            return Task.FromResult(new Empty());
        }

        public override Task<Hipstershop.Cart> GetCart(GetCartRequest request, ServerCallContext context)
        {
            var cart = cartStore.GetCart(request.UserId);
            return Task.FromResult(cart.ToHipsterCart());
        }
    }

    internal class CartStore
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

    internal static class CartUtils
    {
        public static Hipstershop.Cart ToHipsterCart(this Cart cart)
        {
            var hipsterCart = new Hipstershop.Cart
            {
                UserId = cart.UserId,
                Items = { cart.Items.Select(i => new CartItem { ProductId = i.Key, Quantity = i.Value }) }
            };
            return hipsterCart;
        }
    }

    // Actual implementation of the cart
    internal class Cart
    {
        // Maps between productId and its quantity
        private Dictionary<string, int> cart = new Dictionary<string, int>();

        public Cart(string userId)
        {
            UserId = userId;
        }

        public string UserId { get; set; }

        public void AddItem(string productId, int quantity)
        {
            cart.Add(productId, quantity);
        }

        public void EmptyCart()
        {
            cart.Clear();
        }

        public IReadOnlyDictionary<string, int> Items
        {
            get
            {
                return cart;
            }
        }
    }
}