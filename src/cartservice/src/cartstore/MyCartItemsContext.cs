using Microsoft.EntityFrameworkCore;

namespace cartservice.cartstore
{
    public class MyCartItemsContext : DbContext
    {
        public MyCartItemsContext(DbContextOptions<MyCartItemsContext> options) : base(options)
        {
        }

        public DbSet<MyCartItem> CartItems { get; set; }

    }
}