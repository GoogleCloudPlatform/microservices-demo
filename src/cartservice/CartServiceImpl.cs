using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using cartservice.interfaces;
using Grpc.Core;
using Hipstershop;
using static Hipstershop.CartService;

namespace cartservice
{
    // Cart wrapper to deal with grpc communication
    internal class CartServiceImpl : CartServiceBase
    {
        private ICartStore cartStore;
        private readonly static Empty Empty = new Empty();

        public CartServiceImpl(ICartStore cartStore)
        {
            this.cartStore = cartStore;
        }

        public async override Task<Empty> AddItem(AddItemRequest request, Grpc.Core.ServerCallContext context)
        {
            await cartStore.AddItemAsync(request.UserId, request.Item.ProductId, request.Item.Quantity);
            return Empty;
        }

        public async override Task<Empty> EmptyCart(EmptyCartRequest request, ServerCallContext context)
        {
            await cartStore.EmptyCartAsync(request.UserId);
            return Empty;
        }

        public async override Task<Hipstershop.Cart> GetCart(GetCartRequest request, ServerCallContext context)
        {
            return await cartStore.GetCartAsync(request.UserId);
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