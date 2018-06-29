using System.Threading.Tasks;

namespace cartservice.interfaces
{
    internal interface ICartStore
    {
        Task InitializeAsync();
        
        Task AddItemAsync(string userId, string productId, int quantity);
        Task EmptyCartAsync(string userId);

        Task<Hipstershop.Cart> GetCartAsync(string userId);
    }
}