using System;
using System.Threading.Tasks;
using Hipstershop;

namespace cartservice.cartstore
{
    public class MySqlCartStore : ICartStore
    {
        private readonly MySQLCartRepository _repository;
        private readonly Cart emptyCart = new Cart();

        public MySqlCartStore(MySQLCartRepository mySqlCartRepository)
        {
            _repository = mySqlCartRepository;
        }

        public Task InitializeAsync()
        {
            Console.WriteLine("MySQL Cart Store was initialized");

            return Task.CompletedTask;
        }

        public Task AddItemAsync(string userId, string productId, int quantity)
        {
            Console.WriteLine($"AddItemAsync called with userId={userId}, productId={productId}, quantity={quantity}");
            var newCart = new Cart
            {
                UserId = userId,
                Items = { new CartItem { ProductId = productId, Quantity = quantity } }
            };
            _ = _repository.SaveCart(newCart).Result;

            return Task.CompletedTask;
        }

        public Task EmptyCartAsync(string userId)
        {
            Console.WriteLine($"EmptyCartAsync called with userId={userId}");
            Cart newCart = new();
            newCart.UserId = userId;
            _ = _repository.SaveCart(newCart).Result;

            return Task.CompletedTask;
        }

        public Task<Cart> GetCartAsync(string userId)
        {
            Console.WriteLine($"GetCartAsync called with userId={userId}");
            Cart cart = _repository.GetCartByUserId(userId);
            if (cart == default)
            {
                Console.WriteLine($"No carts for user {userId}");
                return Task.FromResult(emptyCart);
            }

            return Task.FromResult(cart);
        }

        public bool Ping()
        {
            return true;
        }
    }
}
