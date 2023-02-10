# Protocol Documentation
<a name="top"></a>

## Table of Contents

- [demo.proto](#demo-proto)
    - [Ad](#hipstershop-Ad)
    - [AdRequest](#hipstershop-AdRequest)
    - [AdResponse](#hipstershop-AdResponse)
    - [AddItemRequest](#hipstershop-AddItemRequest)
    - [Address](#hipstershop-Address)
    - [Cart](#hipstershop-Cart)
    - [CartItem](#hipstershop-CartItem)
    - [ChargeRequest](#hipstershop-ChargeRequest)
    - [ChargeResponse](#hipstershop-ChargeResponse)
    - [CreditCardInfo](#hipstershop-CreditCardInfo)
    - [CurrencyConversionRequest](#hipstershop-CurrencyConversionRequest)
    - [Empty](#hipstershop-Empty)
    - [EmptyCartRequest](#hipstershop-EmptyCartRequest)
    - [GetCartRequest](#hipstershop-GetCartRequest)
    - [GetProductRequest](#hipstershop-GetProductRequest)
    - [GetQuoteRequest](#hipstershop-GetQuoteRequest)
    - [GetQuoteResponse](#hipstershop-GetQuoteResponse)
    - [GetSupportedCurrenciesResponse](#hipstershop-GetSupportedCurrenciesResponse)
    - [ListProductsResponse](#hipstershop-ListProductsResponse)
    - [ListRecommendationsRequest](#hipstershop-ListRecommendationsRequest)
    - [ListRecommendationsResponse](#hipstershop-ListRecommendationsResponse)
    - [Money](#hipstershop-Money)
    - [OrderItem](#hipstershop-OrderItem)
    - [OrderResult](#hipstershop-OrderResult)
    - [PlaceOrderRequest](#hipstershop-PlaceOrderRequest)
    - [PlaceOrderResponse](#hipstershop-PlaceOrderResponse)
    - [Product](#hipstershop-Product)
    - [SearchProductsRequest](#hipstershop-SearchProductsRequest)
    - [SearchProductsResponse](#hipstershop-SearchProductsResponse)
    - [SendOrderConfirmationRequest](#hipstershop-SendOrderConfirmationRequest)
    - [ShipOrderRequest](#hipstershop-ShipOrderRequest)
    - [ShipOrderResponse](#hipstershop-ShipOrderResponse)
  
    - [AdService](#hipstershop-AdService)
    - [CartService](#hipstershop-CartService)
    - [CheckoutService](#hipstershop-CheckoutService)
    - [CurrencyService](#hipstershop-CurrencyService)
    - [EmailService](#hipstershop-EmailService)
    - [PaymentService](#hipstershop-PaymentService)
    - [ProductCatalogService](#hipstershop-ProductCatalogService)
    - [RecommendationService](#hipstershop-RecommendationService)
    - [ShippingService](#hipstershop-ShippingService)
  
- [Scalar Value Types](#scalar-value-types)



<a name="demo-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## demo.proto



<a name="hipstershop-Ad"></a>

### Ad



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| redirect_url | [string](#string) |  | url to redirect to when an ad is clicked. |
| text | [string](#string) |  | short advertisement text to display. |






<a name="hipstershop-AdRequest"></a>

### AdRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| context_keys | [string](#string) | repeated | List of important key words from the current page describing the context. |






<a name="hipstershop-AdResponse"></a>

### AdResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| ads | [Ad](#hipstershop-Ad) | repeated |  |






<a name="hipstershop-AddItemRequest"></a>

### AddItemRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| user_id | [string](#string) |  |  |
| item | [CartItem](#hipstershop-CartItem) |  |  |






<a name="hipstershop-Address"></a>

### Address



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| street_address | [string](#string) |  |  |
| city | [string](#string) |  |  |
| state | [string](#string) |  |  |
| country | [string](#string) |  |  |
| zip_code | [int32](#int32) |  |  |






<a name="hipstershop-Cart"></a>

### Cart



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| user_id | [string](#string) |  |  |
| items | [CartItem](#hipstershop-CartItem) | repeated |  |






<a name="hipstershop-CartItem"></a>

### CartItem



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| product_id | [string](#string) |  |  |
| quantity | [int32](#int32) |  |  |






<a name="hipstershop-ChargeRequest"></a>

### ChargeRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| amount | [Money](#hipstershop-Money) |  |  |
| credit_card | [CreditCardInfo](#hipstershop-CreditCardInfo) |  |  |






<a name="hipstershop-ChargeResponse"></a>

### ChargeResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| transaction_id | [string](#string) |  |  |






<a name="hipstershop-CreditCardInfo"></a>

### CreditCardInfo



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| credit_card_number | [string](#string) |  |  |
| credit_card_cvv | [int32](#int32) |  |  |
| credit_card_expiration_year | [int32](#int32) |  |  |
| credit_card_expiration_month | [int32](#int32) |  |  |






<a name="hipstershop-CurrencyConversionRequest"></a>

### CurrencyConversionRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| from | [Money](#hipstershop-Money) |  |  |
| to_code | [string](#string) |  | The 3-letter currency code defined in ISO 4217. |






<a name="hipstershop-Empty"></a>

### Empty







<a name="hipstershop-EmptyCartRequest"></a>

### EmptyCartRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| user_id | [string](#string) |  |  |






<a name="hipstershop-GetCartRequest"></a>

### GetCartRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| user_id | [string](#string) |  |  |






<a name="hipstershop-GetProductRequest"></a>

### GetProductRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |






<a name="hipstershop-GetQuoteRequest"></a>

### GetQuoteRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| address | [Address](#hipstershop-Address) |  |  |
| items | [CartItem](#hipstershop-CartItem) | repeated |  |






<a name="hipstershop-GetQuoteResponse"></a>

### GetQuoteResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| cost_usd | [Money](#hipstershop-Money) |  |  |






<a name="hipstershop-GetSupportedCurrenciesResponse"></a>

### GetSupportedCurrenciesResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| currency_codes | [string](#string) | repeated | The 3-letter currency code defined in ISO 4217. |






<a name="hipstershop-ListProductsResponse"></a>

### ListProductsResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| products | [Product](#hipstershop-Product) | repeated |  |






<a name="hipstershop-ListRecommendationsRequest"></a>

### ListRecommendationsRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| user_id | [string](#string) |  |  |
| product_ids | [string](#string) | repeated |  |






<a name="hipstershop-ListRecommendationsResponse"></a>

### ListRecommendationsResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| product_ids | [string](#string) | repeated |  |






<a name="hipstershop-Money"></a>

### Money
Represents an amount of money with its currency type.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| currency_code | [string](#string) |  | The 3-letter currency code defined in ISO 4217. |
| units | [int64](#int64) |  | The whole units of the amount. For example if `currencyCode` is `&#34;USD&#34;`, then 1 unit is one US dollar. |
| nanos | [int32](#int32) |  | Number of nano (10^-9) units of the amount. The value must be between -999,999,999 and &#43;999,999,999 inclusive. If `units` is positive, `nanos` must be positive or zero. If `units` is zero, `nanos` can be positive, zero, or negative. If `units` is negative, `nanos` must be negative or zero. For example $-1.75 is represented as `units`=-1 and `nanos`=-750,000,000. |






<a name="hipstershop-OrderItem"></a>

### OrderItem



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| item | [CartItem](#hipstershop-CartItem) |  |  |
| cost | [Money](#hipstershop-Money) |  |  |






<a name="hipstershop-OrderResult"></a>

### OrderResult



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| order_id | [string](#string) |  |  |
| shipping_tracking_id | [string](#string) |  |  |
| shipping_cost | [Money](#hipstershop-Money) |  |  |
| shipping_address | [Address](#hipstershop-Address) |  |  |
| items | [OrderItem](#hipstershop-OrderItem) | repeated |  |






<a name="hipstershop-PlaceOrderRequest"></a>

### PlaceOrderRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| user_id | [string](#string) |  |  |
| user_currency | [string](#string) |  |  |
| address | [Address](#hipstershop-Address) |  |  |
| email | [string](#string) |  |  |
| credit_card | [CreditCardInfo](#hipstershop-CreditCardInfo) |  |  |






<a name="hipstershop-PlaceOrderResponse"></a>

### PlaceOrderResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| order | [OrderResult](#hipstershop-OrderResult) |  |  |






<a name="hipstershop-Product"></a>

### Product



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| picture | [string](#string) |  |  |
| price_usd | [Money](#hipstershop-Money) |  |  |
| categories | [string](#string) | repeated | Categories such as &#34;clothing&#34; or &#34;kitchen&#34; that can be used to look up other related products. |






<a name="hipstershop-SearchProductsRequest"></a>

### SearchProductsRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| query | [string](#string) |  |  |






<a name="hipstershop-SearchProductsResponse"></a>

### SearchProductsResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| results | [Product](#hipstershop-Product) | repeated |  |






<a name="hipstershop-SendOrderConfirmationRequest"></a>

### SendOrderConfirmationRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| email | [string](#string) |  |  |
| order | [OrderResult](#hipstershop-OrderResult) |  |  |






<a name="hipstershop-ShipOrderRequest"></a>

### ShipOrderRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| address | [Address](#hipstershop-Address) |  |  |
| items | [CartItem](#hipstershop-CartItem) | repeated |  |






<a name="hipstershop-ShipOrderResponse"></a>

### ShipOrderResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tracking_id | [string](#string) |  |  |





 

 

 


<a name="hipstershop-AdService"></a>

### AdService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| GetAds | [AdRequest](#hipstershop-AdRequest) | [AdResponse](#hipstershop-AdResponse) |  |


<a name="hipstershop-CartService"></a>

### CartService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| AddItem | [AddItemRequest](#hipstershop-AddItemRequest) | [Empty](#hipstershop-Empty) |  |
| GetCart | [GetCartRequest](#hipstershop-GetCartRequest) | [Cart](#hipstershop-Cart) |  |
| EmptyCart | [EmptyCartRequest](#hipstershop-EmptyCartRequest) | [Empty](#hipstershop-Empty) |  |


<a name="hipstershop-CheckoutService"></a>

### CheckoutService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| PlaceOrder | [PlaceOrderRequest](#hipstershop-PlaceOrderRequest) | [PlaceOrderResponse](#hipstershop-PlaceOrderResponse) |  |


<a name="hipstershop-CurrencyService"></a>

### CurrencyService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| GetSupportedCurrencies | [Empty](#hipstershop-Empty) | [GetSupportedCurrenciesResponse](#hipstershop-GetSupportedCurrenciesResponse) |  |
| Convert | [CurrencyConversionRequest](#hipstershop-CurrencyConversionRequest) | [Money](#hipstershop-Money) |  |


<a name="hipstershop-EmailService"></a>

### EmailService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| SendOrderConfirmation | [SendOrderConfirmationRequest](#hipstershop-SendOrderConfirmationRequest) | [Empty](#hipstershop-Empty) |  |


<a name="hipstershop-PaymentService"></a>

### PaymentService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| Charge | [ChargeRequest](#hipstershop-ChargeRequest) | [ChargeResponse](#hipstershop-ChargeResponse) |  |


<a name="hipstershop-ProductCatalogService"></a>

### ProductCatalogService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| ListProducts | [Empty](#hipstershop-Empty) | [ListProductsResponse](#hipstershop-ListProductsResponse) |  |
| GetProduct | [GetProductRequest](#hipstershop-GetProductRequest) | [Product](#hipstershop-Product) |  |
| SearchProducts | [SearchProductsRequest](#hipstershop-SearchProductsRequest) | [SearchProductsResponse](#hipstershop-SearchProductsResponse) |  |


<a name="hipstershop-RecommendationService"></a>

### RecommendationService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| ListRecommendations | [ListRecommendationsRequest](#hipstershop-ListRecommendationsRequest) | [ListRecommendationsResponse](#hipstershop-ListRecommendationsResponse) |  |


<a name="hipstershop-ShippingService"></a>

### ShippingService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| GetQuote | [GetQuoteRequest](#hipstershop-GetQuoteRequest) | [GetQuoteResponse](#hipstershop-GetQuoteResponse) |  |
| ShipOrder | [ShipOrderRequest](#hipstershop-ShipOrderRequest) | [ShipOrderResponse](#hipstershop-ShipOrderResponse) |  |

 



## Scalar Value Types

| .proto Type | Notes | C++ | Java | Python | Go | C# | PHP | Ruby |
| ----------- | ----- | --- | ---- | ------ | -- | -- | --- | ---- |
| <a name="double" /> double |  | double | double | float | float64 | double | float | Float |
| <a name="float" /> float |  | float | float | float | float32 | float | float | Float |
| <a name="int32" /> int32 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="int64" /> int64 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="uint32" /> uint32 | Uses variable-length encoding. | uint32 | int | int/long | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="uint64" /> uint64 | Uses variable-length encoding. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum or Fixnum (as required) |
| <a name="sint32" /> sint32 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sint64" /> sint64 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="fixed32" /> fixed32 | Always four bytes. More efficient than uint32 if values are often greater than 2^28. | uint32 | int | int | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="fixed64" /> fixed64 | Always eight bytes. More efficient than uint64 if values are often greater than 2^56. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum |
| <a name="sfixed32" /> sfixed32 | Always four bytes. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sfixed64" /> sfixed64 | Always eight bytes. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="bool" /> bool |  | bool | boolean | boolean | bool | bool | boolean | TrueClass/FalseClass |
| <a name="string" /> string | A string must always contain UTF-8 encoded or 7-bit ASCII text. | string | String | str/unicode | string | string | string | String (UTF-8) |
| <a name="bytes" /> bytes | May contain any arbitrary sequence of bytes. | string | ByteString | str | []byte | ByteString | string | String (ASCII-8BIT) |

