using System;

namespace cartservice.cartstore
{
    public class MyCartItem
    {
        public Guid Id { get; set; }
        public string UserId { get; set; }
        public string ProductId { get; set; }
        public int Quantity { get; set; }
    }
}