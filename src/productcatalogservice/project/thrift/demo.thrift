
// -----------------Cart service-----------------
service CartService {
    void AddItem(1: string user_id, 2: CartItem item)
    Cart GetCart(1: string user_id)
    void EmptyCart(1: string user_id)
}

struct CartItem {
    1: string product_id,
    2: i32  quantity,
}

struct Cart {
    1: string user_id,
    2: list<CartItem> items,
}


//---------------Recommendation service----------
service RecommendationService {
    list<string> ListRecommendations(1: list<string> selected_ids)
}

//---------------ProductCatalog Service ----------------
service ProductCatalogService {
    list<Product> ListProducts()
    Product GetProduct(1: string product_id)
    list<Product> SearchProducts(1: string query)
}

struct Product {
    1: string id,
    2: string name,
    3: string description,
    4: string picture,
    5: Money price_usd,
    6: list<string> categories,
}

// ---------------Shipping Service----------
service ShippingService {
    Money GetQuote(1: Address address, 2: list<CartItem> items)
    string ShipOrder(1: Address address, 2: list<CartItem> items)
}

struct Address {
    1: string street_address,
    2: string city,
    3: string state,
    4: string country,
    5: i32 zip_code,
}


//-----------------Currency service-----------------
service CurrencyService {
    list<string> GetSupportedCurrencies(),
    Money Convert(1: Money from_curr, 2: string to_curr)
}

// Represents an amount of money with its currency type.
struct Money {
    1: string currency_code,
    2: i64 units,
    3: i32 nanos,
}

// -------------Payment service-----------------
service PaymentService {
    string Charge(1: Money amount, 2: CreditCardInfo credit_card)
}

struct CreditCardInfo {
    1: string credit_card_number,
    2: i32 credit_card_cvv,
    3: i32 credit_card_expiration_year,
    4: i32 credit_card_expiration_month,
}


// -------------Email service-----------------
service EmailService {
    void SendOrderConfirmation(1: string email, 2: OrderResult order)
}

struct OrderItem {
    1: CartItem item,
    2: Money cost,
}

struct OrderResult {
    1: string order_id,
    2: string shipping_tracking_id,
    3: Money shipping_cost,
    4: Address shipping_address,
    5: list<OrderItem> items,
}

// -------------Checkout service-----------------
service CheckoutService {
    OrderResult PlaceOrder(1: string user_id, 2: string user_currency, 3: Address address 4: string email, 5: CreditCardInfo credit_card)
}

// ------------Ad service------------------
service AdService {
    list<Ad> GetAds(1: list<string> context_keys)
}

struct Ad {
    1: string redirect_url,
    2: string text,
}
