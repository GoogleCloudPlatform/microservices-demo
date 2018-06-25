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

        public override Task<Hipstershop.Cart> GetCart(GetCartRequest request, ServerCallContext context)
        {
            return cartStore.GetCartAsync(request.UserId);
        }
    }
}