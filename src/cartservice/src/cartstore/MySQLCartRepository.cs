using System;
using System.Linq;
using System.Threading.Tasks;
using Hipstershop;

namespace cartservice.cartstore
{
    public class MySQLCartRepository
    {
        private readonly MyCartItemsContext _context;

        public MySQLCartRepository(MyCartItemsContext mySqlContext)
        {
            _context = mySqlContext;
        }

        public Cart GetCartByUserId(string id)
        {
            var cartItems = _context.CartItems
                .AsQueryable()
                .Where(p => p.UserId == id)
                .ToList();
            var newCart = new Cart();

            foreach (var cart in cartItems)
            {
                newCart.UserId = cart.UserId;
                CartItem cartItem = new()
                {
                    Quantity = cart.Quantity,
                    ProductId = cart.ProductId
                };
                newCart.Items.Add(cartItem);
            }

            return newCart;
        }

        public async Task<string> SaveCart(Cart cart)
        {

            foreach (var item in cart.Items)
            {
                var itemFromDb = _context.CartItems
                .AsQueryable()
                .Where(i => i.UserId == cart.UserId && i.ProductId == item.ProductId)
                .FirstOrDefault();

                if (itemFromDb == default)
                {
                    MyCartItem myCartItem = new()
                    {
                        Id = new Guid(),
                        UserId = cart.UserId,
                        ProductId = item.ProductId,
                        Quantity = item.Quantity
                    };
                    await _context.AddAsync(myCartItem);
                    await _context.SaveChangesAsync();
                }
                else
                {
                    itemFromDb.Quantity = item.Quantity + itemFromDb.Quantity;
                    await _context.SaveChangesAsync();
                }
            }

            return cart.UserId;
        }

        public async Task<int> DeleteCartByUserId(string id)
        {
            var listMyCartItems = _context.CartItems
                .AsQueryable()
                .Where(p => p.UserId == id)
                .ToList();

            int count = listMyCartItems.Count;
            _context.CartItems.RemoveRange(listMyCartItems);
            await _context.SaveChangesAsync();

            return count;
        }
    }
}
