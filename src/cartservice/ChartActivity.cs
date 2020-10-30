using System;
using System.Diagnostics;

namespace cartservice
{

    internal static class CartActivity
    {
        public const string ActivitySourceName = "CartService";
        public static readonly ActivitySource ActivitySource = new ActivitySource(ActivitySourceName);
    }
    
}
