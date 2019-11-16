import ballerina/grpc;

public type CartServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function AddItem(AddItemRequest req, grpc:Headers? headers = ()) returns ([Empty, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.CartService/AddItem", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<Empty>.constructFrom(result);
        if (value is Empty) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

    public remote function GetCart(GetCartRequest req, grpc:Headers? headers = ()) returns ([Cart, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.CartService/GetCart", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<Cart>.constructFrom(result);
        if (value is Cart) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

    public remote function EmptyCart(EmptyCartRequest req, grpc:Headers? headers = ()) returns ([Empty, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.CartService/EmptyCart", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<Empty>.constructFrom(result);
        if (value is Empty) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type CartServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function AddItem(AddItemRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.CartService/AddItem", req, msgListener, headers);
    }

    public remote function GetCart(GetCartRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.CartService/GetCart", req, msgListener, headers);
    }

    public remote function EmptyCart(EmptyCartRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.CartService/EmptyCart", req, msgListener, headers);
    }

};

public type RecommendationServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function ListRecommendations(ListRecommendationsRequest req, grpc:Headers? headers = ()) returns ([ListRecommendationsResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.RecommendationService/ListRecommendations", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<ListRecommendationsResponse>.constructFrom(result);
        if (value is ListRecommendationsResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type RecommendationServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function ListRecommendations(ListRecommendationsRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.RecommendationService/ListRecommendations", req, msgListener, headers);
    }

};

public type ProductCatalogServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function ListProducts(Empty req, grpc:Headers? headers = ()) returns ([ListProductsResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.ProductCatalogService/ListProducts", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<ListProductsResponse>.constructFrom(result);
        if (value is ListProductsResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

    public remote function GetProduct(GetProductRequest req, grpc:Headers? headers = ()) returns ([Product, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.ProductCatalogService/GetProduct", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<Product>.constructFrom(result);
        if (value is Product) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

    public remote function SearchProducts(SearchProductsRequest req, grpc:Headers? headers = ()) returns ([SearchProductsResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.ProductCatalogService/SearchProducts", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<SearchProductsResponse>.constructFrom(result);
        if (value is SearchProductsResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type ProductCatalogServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function ListProducts(Empty req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.ProductCatalogService/ListProducts", req, msgListener, headers);
    }

    public remote function GetProduct(GetProductRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.ProductCatalogService/GetProduct", req, msgListener, headers);
    }

    public remote function SearchProducts(SearchProductsRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.ProductCatalogService/SearchProducts", req, msgListener, headers);
    }

};

public type ShippingServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function GetQuote(GetQuoteRequest req, grpc:Headers? headers = ()) returns ([GetQuoteResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.ShippingService/GetQuote", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<GetQuoteResponse>.constructFrom(result);
        if (value is GetQuoteResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

    public remote function ShipOrder(ShipOrderRequest req, grpc:Headers? headers = ()) returns ([ShipOrderResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.ShippingService/ShipOrder", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<ShipOrderResponse>.constructFrom(result);
        if (value is ShipOrderResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type ShippingServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function GetQuote(GetQuoteRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.ShippingService/GetQuote", req, msgListener, headers);
    }

    public remote function ShipOrder(ShipOrderRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.ShippingService/ShipOrder", req, msgListener, headers);
    }

};

public type CurrencyServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function GetSupportedCurrencies(Empty req, grpc:Headers? headers = ()) returns ([GetSupportedCurrenciesResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.CurrencyService/GetSupportedCurrencies", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<GetSupportedCurrenciesResponse>.constructFrom(result);
        if (value is GetSupportedCurrenciesResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

    public remote function Convert(CurrencyConversionRequest req, grpc:Headers? headers = ()) returns ([Money, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.CurrencyService/Convert", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<Money>.constructFrom(result);
        if (value is Money) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type CurrencyServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function GetSupportedCurrencies(Empty req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.CurrencyService/GetSupportedCurrencies", req, msgListener, headers);
    }

    public remote function Convert(CurrencyConversionRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.CurrencyService/Convert", req, msgListener, headers);
    }

};

public type PaymentServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function Charge(ChargeRequest req, grpc:Headers? headers = ()) returns ([ChargeResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.PaymentService/Charge", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<ChargeResponse>.constructFrom(result);
        if (value is ChargeResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type PaymentServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function Charge(ChargeRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.PaymentService/Charge", req, msgListener, headers);
    }

};

public type EmailServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function SendOrderConfirmation(SendOrderConfirmationRequest req, grpc:Headers? headers = ()) returns ([Empty, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.EmailService/SendOrderConfirmation", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<Empty>.constructFrom(result);
        if (value is Empty) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type EmailServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function SendOrderConfirmation(SendOrderConfirmationRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.EmailService/SendOrderConfirmation", req, msgListener, headers);
    }

};

public type CheckoutServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function PlaceOrder(PlaceOrderRequest req, grpc:Headers? headers = ()) returns ([PlaceOrderResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.CheckoutService/PlaceOrder", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<PlaceOrderResponse>.constructFrom(result);
        if (value is PlaceOrderResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type CheckoutServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function PlaceOrder(PlaceOrderRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.CheckoutService/PlaceOrder", req, msgListener, headers);
    }

};

public type AdServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function GetAds(AdRequest req, grpc:Headers? headers = ()) returns ([AdResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.AdService/GetAds", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<AdResponse>.constructFrom(result);
        if (value is AdResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type AdServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function GetAds(AdRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.AdService/GetAds", req, msgListener, headers);
    }

};

public type CartItem record {|
    string product_id;
    int quantity;
    
|};


public type AddItemRequest record {|
    string user_id;
    CartItem item;
    
|};


public type EmptyCartRequest record {|
    string user_id;
    
|};


public type GetCartRequest record {|
    string user_id;
    
|};


public type Cart record {|
    string user_id;
    CartItem[] items;
    
|};


public type Empty record {|
    
|};


public type ListRecommendationsRequest record {|
    string user_id;
    string[] product_ids;
    
|};


public type ListRecommendationsResponse record {|
    string[] product_ids;
    
|};


public type Product record {|
    string id;
    string name;
    string description;
    string picture;
    Money price_usd;
    string[] categories;
    
|};


public type ListProductsResponse record {|
    Product[] products;
    
|};


public type GetProductRequest record {|
    string id;
    
|};


public type SearchProductsRequest record {|
    string query;
    
|};


public type SearchProductsResponse record {|
    Product[] results;
    
|};


public type GetQuoteRequest record {|
    Address address;
    CartItem[] items;
    
|};


public type GetQuoteResponse record {|
    Money cost_usd;
    
|};


public type ShipOrderRequest record {|
    Address address;
    CartItem[] items;
    
|};


public type ShipOrderResponse record {|
    string tracking_id;
    
|};


public type Address record {|
    string street_address;
    string city;
    string state;
    string country;
    int zip_code;
    
|};


public type Money record {|
    string currency_code;
    int units;
    int nanos;
    
|};


public type GetSupportedCurrenciesResponse record {|
    string[] currency_codes;
    
|};


public type CurrencyConversionRequest record {|
    Money 'from;
    string to_code;
    
|};


public type CreditCardInfo record {|
    string credit_card_number;
    int credit_card_cvv;
    int credit_card_expiration_year;
    int credit_card_expiration_month;
    
|};


public type ChargeRequest record {|
    Money amount;
    CreditCardInfo credit_card;
    
|};


public type ChargeResponse record {|
    string transaction_id;
    
|};


public type OrderItem record {|
    CartItem item;
    Money cost;
    
|};


public type OrderResult record {|
    string order_id;
    string shipping_tracking_id;
    Money shipping_cost;
    Address shipping_address;
    OrderItem[] items;
    
|};


public type SendOrderConfirmationRequest record {|
    string email;
    OrderResult 'order;
    
|};


public type PlaceOrderRequest record {|
    string user_id;
    string user_currency;
    Address address;
    string email;
    CreditCardInfo credit_card;
    
|};


public type PlaceOrderResponse record {|
    OrderResult 'order;
    
|};


public type AdRequest record {|
    string[] context_keys;
    
|};


public type AdResponse record {|
    Ad[] ads;
    
|};


public type Ad record {|
    string redirect_url;
    string text;
    
|};



const string ROOT_DESCRIPTOR = "0A0A64656D6F2E70726F746F120B6869707374657273686F7022450A08436172744974656D121D0A0A70726F647563745F6964180120012809520970726F647563744964121A0A087175616E7469747918022001280552087175616E7469747922540A0E4164644974656D5265717565737412170A07757365725F6964180120012809520675736572496412290A046974656D18022001280B32152E6869707374657273686F702E436172744974656D52046974656D222B0A10456D707479436172745265717565737412170A07757365725F6964180120012809520675736572496422290A0E476574436172745265717565737412170A07757365725F69641801200128095206757365724964224C0A044361727412170A07757365725F69641801200128095206757365724964122B0A056974656D7318022003280B32152E6869707374657273686F702E436172744974656D52056974656D7322070A05456D70747922560A1A4C6973745265636F6D6D656E646174696F6E735265717565737412170A07757365725F69641801200128095206757365724964121F0A0B70726F647563745F696473180220032809520A70726F64756374496473223E0A1B4C6973745265636F6D6D656E646174696F6E73526573706F6E7365121F0A0B70726F647563745F696473180120032809520A70726F6475637449647322BA010A0750726F64756374120E0A0269641801200128095202696412120A046E616D6518022001280952046E616D6512200A0B6465736372697074696F6E180320012809520B6465736372697074696F6E12180A0770696374757265180420012809520770696374757265122F0A0970726963655F75736418052001280B32122E6869707374657273686F702E4D6F6E657952087072696365557364121E0A0A63617465676F72696573180620032809520A63617465676F7269657322480A144C69737450726F6475637473526573706F6E736512300A0870726F647563747318012003280B32142E6869707374657273686F702E50726F64756374520870726F647563747322230A1147657450726F6475637452657175657374120E0A02696418012001280952026964222D0A1553656172636850726F64756374735265717565737412140A0571756572791801200128095205717565727922480A1653656172636850726F6475637473526573706F6E7365122E0A07726573756C747318012003280B32142E6869707374657273686F702E50726F647563745207726573756C7473226E0A0F47657451756F746552657175657374122E0A076164647265737318012001280B32142E6869707374657273686F702E41646472657373520761646472657373122B0A056974656D7318022003280B32152E6869707374657273686F702E436172744974656D52056974656D7322410A1047657451756F7465526573706F6E7365122D0A08636F73745F75736418012001280B32122E6869707374657273686F702E4D6F6E65795207636F7374557364226F0A10536869704F7264657252657175657374122E0A076164647265737318012001280B32142E6869707374657273686F702E41646472657373520761646472657373122B0A056974656D7318022003280B32152E6869707374657273686F702E436172744974656D52056974656D7322340A11536869704F72646572526573706F6E7365121F0A0B747261636B696E675F6964180120012809520A747261636B696E674964228F010A074164647265737312250A0E7374726565745F61646472657373180120012809520D7374726565744164647265737312120A046369747918022001280952046369747912140A0573746174651803200128095205737461746512180A07636F756E7472791804200128095207636F756E74727912190A087A69705F636F646518052001280552077A6970436F646522580A054D6F6E657912230A0D63757272656E63795F636F6465180120012809520C63757272656E6379436F646512140A05756E6974731802200128035205756E69747312140A056E616E6F7318032001280552056E616E6F7322470A1E476574537570706F7274656443757272656E63696573526573706F6E736512250A0E63757272656E63795F636F646573180120032809520D63757272656E6379436F646573225C0A1943757272656E6379436F6E76657273696F6E5265717565737412260A0466726F6D18012001280B32122E6869707374657273686F702E4D6F6E6579520466726F6D12170A07746F5F636F64651802200128095206746F436F646522E6010A0E43726564697443617264496E666F122C0A126372656469745F636172645F6E756D6265721801200128095210637265646974436172644E756D62657212260A0F6372656469745F636172645F637676180220012805520D63726564697443617264437676123D0A1B6372656469745F636172645F65787069726174696F6E5F7965617218032001280552186372656469744361726445787069726174696F6E59656172123F0A1C6372656469745F636172645F65787069726174696F6E5F6D6F6E746818042001280552196372656469744361726445787069726174696F6E4D6F6E746822790A0D43686172676552657175657374122A0A06616D6F756E7418012001280B32122E6869707374657273686F702E4D6F6E65795206616D6F756E74123C0A0B6372656469745F6361726418022001280B321B2E6869707374657273686F702E43726564697443617264496E666F520A6372656469744361726422370A0E436861726765526573706F6E736512250A0E7472616E73616374696F6E5F6964180120012809520D7472616E73616374696F6E4964225E0A094F726465724974656D12290A046974656D18012001280B32152E6869707374657273686F702E436172744974656D52046974656D12260A04636F737418022001280B32122E6869707374657273686F702E4D6F6E65795204636F73742282020A0B4F72646572526573756C7412190A086F726465725F696418012001280952076F72646572496412300A147368697070696E675F747261636B696E675F696418022001280952127368697070696E67547261636B696E67496412370A0D7368697070696E675F636F737418032001280B32122E6869707374657273686F702E4D6F6E6579520C7368697070696E67436F7374123F0A107368697070696E675F6164647265737318042001280B32142E6869707374657273686F702E41646472657373520F7368697070696E6741646472657373122C0A056974656D7318052003280B32162E6869707374657273686F702E4F726465724974656D52056974656D7322640A1C53656E644F72646572436F6E6669726D6174696F6E5265717565737412140A05656D61696C1801200128095205656D61696C122E0A056F7264657218022001280B32182E6869707374657273686F702E4F72646572526573756C7452056F7264657222D5010A11506C6163654F726465725265717565737412170A07757365725F6964180120012809520675736572496412230A0D757365725F63757272656E6379180220012809520C7573657243757272656E6379122E0A076164647265737318032001280B32142E6869707374657273686F702E4164647265737352076164647265737312140A05656D61696C1805200128095205656D61696C123C0A0B6372656469745F6361726418062001280B321B2E6869707374657273686F702E43726564697443617264496E666F520A6372656469744361726422440A12506C6163654F72646572526573706F6E7365122E0A056F7264657218012001280B32182E6869707374657273686F702E4F72646572526573756C7452056F72646572222E0A0941645265717565737412210A0C636F6E746578745F6B657973180120032809520B636F6E746578744B657973222F0A0A4164526573706F6E736512210A0361647318012003280B320F2E6869707374657273686F702E41645203616473223B0A02416412210A0C72656469726563745F75726C180120012809520B726564697265637455726C12120A047465787418022001280952047465787432CA010A0B4361727453657276696365123C0A074164644974656D121B2E6869707374657273686F702E4164644974656D526571756573741A122E6869707374657273686F702E456D7074792200123B0A0747657443617274121B2E6869707374657273686F702E47657443617274526571756573741A112E6869707374657273686F702E43617274220012400A09456D70747943617274121D2E6869707374657273686F702E456D70747943617274526571756573741A122E6869707374657273686F702E456D70747922003283010A155265636F6D6D656E646174696F6E53657276696365126A0A134C6973745265636F6D6D656E646174696F6E7312272E6869707374657273686F702E4C6973745265636F6D6D656E646174696F6E73526571756573741A282E6869707374657273686F702E4C6973745265636F6D6D656E646174696F6E73526573706F6E736522003283020A1550726F64756374436174616C6F675365727669636512470A0C4C69737450726F647563747312122E6869707374657273686F702E456D7074791A212E6869707374657273686F702E4C69737450726F6475637473526573706F6E7365220012440A0A47657450726F64756374121E2E6869707374657273686F702E47657450726F64756374526571756573741A142E6869707374657273686F702E50726F647563742200125B0A0E53656172636850726F647563747312222E6869707374657273686F702E53656172636850726F6475637473526571756573741A232E6869707374657273686F702E53656172636850726F6475637473526573706F6E7365220032AA010A0F5368697070696E675365727669636512490A0847657451756F7465121C2E6869707374657273686F702E47657451756F7465526571756573741A1D2E6869707374657273686F702E47657451756F7465526573706F6E73652200124C0A09536869704F72646572121D2E6869707374657273686F702E536869704F72646572526571756573741A1E2E6869707374657273686F702E536869704F72646572526573706F6E7365220032B7010A0F43757272656E637953657276696365125B0A16476574537570706F7274656443757272656E6369657312122E6869707374657273686F702E456D7074791A2B2E6869707374657273686F702E476574537570706F7274656443757272656E63696573526573706F6E7365220012470A07436F6E7665727412262E6869707374657273686F702E43757272656E6379436F6E76657273696F6E526571756573741A122E6869707374657273686F702E4D6F6E6579220032550A0E5061796D656E745365727669636512430A06436861726765121A2E6869707374657273686F702E436861726765526571756573741A1B2E6869707374657273686F702E436861726765526573706F6E7365220032680A0C456D61696C5365727669636512580A1553656E644F72646572436F6E6669726D6174696F6E12292E6869707374657273686F702E53656E644F72646572436F6E6669726D6174696F6E526571756573741A122E6869707374657273686F702E456D707479220032620A0F436865636B6F757453657276696365124F0A0A506C6163654F72646572121E2E6869707374657273686F702E506C6163654F72646572526571756573741A1F2E6869707374657273686F702E506C6163654F72646572526573706F6E7365220032480A09416453657276696365123B0A0647657441647312162E6869707374657273686F702E4164526571756573741A172E6869707374657273686F702E4164526573706F6E73652200620670726F746F33";
function getDescriptorMap() returns map<string> {
    return {
        "demo.proto":"0A0A64656D6F2E70726F746F120B6869707374657273686F7022450A08436172744974656D121D0A0A70726F647563745F6964180120012809520970726F647563744964121A0A087175616E7469747918022001280552087175616E7469747922540A0E4164644974656D5265717565737412170A07757365725F6964180120012809520675736572496412290A046974656D18022001280B32152E6869707374657273686F702E436172744974656D52046974656D222B0A10456D707479436172745265717565737412170A07757365725F6964180120012809520675736572496422290A0E476574436172745265717565737412170A07757365725F69641801200128095206757365724964224C0A044361727412170A07757365725F69641801200128095206757365724964122B0A056974656D7318022003280B32152E6869707374657273686F702E436172744974656D52056974656D7322070A05456D70747922560A1A4C6973745265636F6D6D656E646174696F6E735265717565737412170A07757365725F69641801200128095206757365724964121F0A0B70726F647563745F696473180220032809520A70726F64756374496473223E0A1B4C6973745265636F6D6D656E646174696F6E73526573706F6E7365121F0A0B70726F647563745F696473180120032809520A70726F6475637449647322BA010A0750726F64756374120E0A0269641801200128095202696412120A046E616D6518022001280952046E616D6512200A0B6465736372697074696F6E180320012809520B6465736372697074696F6E12180A0770696374757265180420012809520770696374757265122F0A0970726963655F75736418052001280B32122E6869707374657273686F702E4D6F6E657952087072696365557364121E0A0A63617465676F72696573180620032809520A63617465676F7269657322480A144C69737450726F6475637473526573706F6E736512300A0870726F647563747318012003280B32142E6869707374657273686F702E50726F64756374520870726F647563747322230A1147657450726F6475637452657175657374120E0A02696418012001280952026964222D0A1553656172636850726F64756374735265717565737412140A0571756572791801200128095205717565727922480A1653656172636850726F6475637473526573706F6E7365122E0A07726573756C747318012003280B32142E6869707374657273686F702E50726F647563745207726573756C7473226E0A0F47657451756F746552657175657374122E0A076164647265737318012001280B32142E6869707374657273686F702E41646472657373520761646472657373122B0A056974656D7318022003280B32152E6869707374657273686F702E436172744974656D52056974656D7322410A1047657451756F7465526573706F6E7365122D0A08636F73745F75736418012001280B32122E6869707374657273686F702E4D6F6E65795207636F7374557364226F0A10536869704F7264657252657175657374122E0A076164647265737318012001280B32142E6869707374657273686F702E41646472657373520761646472657373122B0A056974656D7318022003280B32152E6869707374657273686F702E436172744974656D52056974656D7322340A11536869704F72646572526573706F6E7365121F0A0B747261636B696E675F6964180120012809520A747261636B696E674964228F010A074164647265737312250A0E7374726565745F61646472657373180120012809520D7374726565744164647265737312120A046369747918022001280952046369747912140A0573746174651803200128095205737461746512180A07636F756E7472791804200128095207636F756E74727912190A087A69705F636F646518052001280552077A6970436F646522580A054D6F6E657912230A0D63757272656E63795F636F6465180120012809520C63757272656E6379436F646512140A05756E6974731802200128035205756E69747312140A056E616E6F7318032001280552056E616E6F7322470A1E476574537570706F7274656443757272656E63696573526573706F6E736512250A0E63757272656E63795F636F646573180120032809520D63757272656E6379436F646573225C0A1943757272656E6379436F6E76657273696F6E5265717565737412260A0466726F6D18012001280B32122E6869707374657273686F702E4D6F6E6579520466726F6D12170A07746F5F636F64651802200128095206746F436F646522E6010A0E43726564697443617264496E666F122C0A126372656469745F636172645F6E756D6265721801200128095210637265646974436172644E756D62657212260A0F6372656469745F636172645F637676180220012805520D63726564697443617264437676123D0A1B6372656469745F636172645F65787069726174696F6E5F7965617218032001280552186372656469744361726445787069726174696F6E59656172123F0A1C6372656469745F636172645F65787069726174696F6E5F6D6F6E746818042001280552196372656469744361726445787069726174696F6E4D6F6E746822790A0D43686172676552657175657374122A0A06616D6F756E7418012001280B32122E6869707374657273686F702E4D6F6E65795206616D6F756E74123C0A0B6372656469745F6361726418022001280B321B2E6869707374657273686F702E43726564697443617264496E666F520A6372656469744361726422370A0E436861726765526573706F6E736512250A0E7472616E73616374696F6E5F6964180120012809520D7472616E73616374696F6E4964225E0A094F726465724974656D12290A046974656D18012001280B32152E6869707374657273686F702E436172744974656D52046974656D12260A04636F737418022001280B32122E6869707374657273686F702E4D6F6E65795204636F73742282020A0B4F72646572526573756C7412190A086F726465725F696418012001280952076F72646572496412300A147368697070696E675F747261636B696E675F696418022001280952127368697070696E67547261636B696E67496412370A0D7368697070696E675F636F737418032001280B32122E6869707374657273686F702E4D6F6E6579520C7368697070696E67436F7374123F0A107368697070696E675F6164647265737318042001280B32142E6869707374657273686F702E41646472657373520F7368697070696E6741646472657373122C0A056974656D7318052003280B32162E6869707374657273686F702E4F726465724974656D52056974656D7322640A1C53656E644F72646572436F6E6669726D6174696F6E5265717565737412140A05656D61696C1801200128095205656D61696C122E0A056F7264657218022001280B32182E6869707374657273686F702E4F72646572526573756C7452056F7264657222D5010A11506C6163654F726465725265717565737412170A07757365725F6964180120012809520675736572496412230A0D757365725F63757272656E6379180220012809520C7573657243757272656E6379122E0A076164647265737318032001280B32142E6869707374657273686F702E4164647265737352076164647265737312140A05656D61696C1805200128095205656D61696C123C0A0B6372656469745F6361726418062001280B321B2E6869707374657273686F702E43726564697443617264496E666F520A6372656469744361726422440A12506C6163654F72646572526573706F6E7365122E0A056F7264657218012001280B32182E6869707374657273686F702E4F72646572526573756C7452056F72646572222E0A0941645265717565737412210A0C636F6E746578745F6B657973180120032809520B636F6E746578744B657973222F0A0A4164526573706F6E736512210A0361647318012003280B320F2E6869707374657273686F702E41645203616473223B0A02416412210A0C72656469726563745F75726C180120012809520B726564697265637455726C12120A047465787418022001280952047465787432CA010A0B4361727453657276696365123C0A074164644974656D121B2E6869707374657273686F702E4164644974656D526571756573741A122E6869707374657273686F702E456D7074792200123B0A0747657443617274121B2E6869707374657273686F702E47657443617274526571756573741A112E6869707374657273686F702E43617274220012400A09456D70747943617274121D2E6869707374657273686F702E456D70747943617274526571756573741A122E6869707374657273686F702E456D70747922003283010A155265636F6D6D656E646174696F6E53657276696365126A0A134C6973745265636F6D6D656E646174696F6E7312272E6869707374657273686F702E4C6973745265636F6D6D656E646174696F6E73526571756573741A282E6869707374657273686F702E4C6973745265636F6D6D656E646174696F6E73526573706F6E736522003283020A1550726F64756374436174616C6F675365727669636512470A0C4C69737450726F647563747312122E6869707374657273686F702E456D7074791A212E6869707374657273686F702E4C69737450726F6475637473526573706F6E7365220012440A0A47657450726F64756374121E2E6869707374657273686F702E47657450726F64756374526571756573741A142E6869707374657273686F702E50726F647563742200125B0A0E53656172636850726F647563747312222E6869707374657273686F702E53656172636850726F6475637473526571756573741A232E6869707374657273686F702E53656172636850726F6475637473526573706F6E7365220032AA010A0F5368697070696E675365727669636512490A0847657451756F7465121C2E6869707374657273686F702E47657451756F7465526571756573741A1D2E6869707374657273686F702E47657451756F7465526573706F6E73652200124C0A09536869704F72646572121D2E6869707374657273686F702E536869704F72646572526571756573741A1E2E6869707374657273686F702E536869704F72646572526573706F6E7365220032B7010A0F43757272656E637953657276696365125B0A16476574537570706F7274656443757272656E6369657312122E6869707374657273686F702E456D7074791A2B2E6869707374657273686F702E476574537570706F7274656443757272656E63696573526573706F6E7365220012470A07436F6E7665727412262E6869707374657273686F702E43757272656E6379436F6E76657273696F6E526571756573741A122E6869707374657273686F702E4D6F6E6579220032550A0E5061796D656E745365727669636512430A06436861726765121A2E6869707374657273686F702E436861726765526571756573741A1B2E6869707374657273686F702E436861726765526573706F6E7365220032680A0C456D61696C5365727669636512580A1553656E644F72646572436F6E6669726D6174696F6E12292E6869707374657273686F702E53656E644F72646572436F6E6669726D6174696F6E526571756573741A122E6869707374657273686F702E456D707479220032620A0F436865636B6F757453657276696365124F0A0A506C6163654F72646572121E2E6869707374657273686F702E506C6163654F72646572526571756573741A1F2E6869707374657273686F702E506C6163654F72646572526573706F6E7365220032480A09416453657276696365123B0A0647657441647312162E6869707374657273686F702E4164526571756573741A172E6869707374657273686F702E4164526573706F6E73652200620670726F746F33"
        
    };
}

