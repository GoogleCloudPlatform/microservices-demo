*** Settings ***
Library           RequestsLibrary
Library           Collections
Suite Setup       Set Suite Variable    ${BASE_URL}    %{machine_dns}
#Suite Teardown    Close All Sessions
*** Variables ***
@{products}    0PUK6V6EV0    1YMWWN1N4O    2ZYFJ3GM2N    66VCHSJNUP    6E92ZMYYFZ    9SIQT8TOJO    L9ECAV7KIM    LS4PSXUNUM    OLJCESPC7Z
${load}    1
*** Test Cases ***
Load Test
    FOR    ${i}    IN RANGE    ${load}
        Test Session
    END
#Bad Requests Test
#    Create Session    frontend    ${BASE_URL}
#    ${response}=    GET On Session    frontend    /product/89
#    Should Be Equal As Integers    ${response.status_code}    500
#    ${data}=    Create Dictionary    currency_code=not a currency
#    POST On Session    frontend    /setCurrency    data=${data}
#    Should Be Equal As Integers    ${response.status_code}    500
Index Test
    Test Index
Set Currency Test
    Test Set Currency
Browse Product Test
    Test Browse Product
View Cart Test
    Test View Cart
Add To Cart Test
    Test Add To Cart
Icon Test
    Test Icon
Checkout Test
    Test Checkout
*** Keywords ***
Test Session
    Test Index
    Test Set Currency
    Test Browse Product
    Test Add To Cart
    Test View Cart
    Test Add To Cart
    Test Checkout
Test Index
    Create Session    frontend    ${BASE_URL}
    ${response}=    GET On Session    frontend    /
    Should Be Equal As Integers    ${response.status_code}    200
Test Set Currency
    ${currencies}=    Create List    EUR    USD    JPY    CAD
    FOR    ${currency}    IN    @{currencies}
        ${data}=    Create Dictionary    currency_code=${currency}
        ${response}=    POST On Session    frontend    /setCurrency    data=${data}
        Should Be Equal As Integers    ${response.status_code}    200
    END
Test Browse Product
    FOR    ${product_id}    IN    @{products}
        ${response}=    GET On Session    frontend    /product/${product_id}
        Should Be Equal As Integers    ${response.status_code}    200
    END
Test View Cart
    ${response}=    GET On Session    frontend    /cart
    Should Be Equal As Integers    ${response.status_code}    200
    ${response}=    POST On Session    frontend    /cart/empty
    Should Be Equal As Integers    ${response.status_code}    200
Test Add To Cart
    FOR    ${product_id}    IN    @{products}
        ${response}=    GET On Session    frontend    /product/${product_id}
        Should Be Equal As Integers    ${response.status_code}    200
        ${quantity}=    Evaluate    random.choice([1, 2, 3, 4, 5, 10])
        ${data}=    Create Dictionary    product_id=${product_id}    quantity=${quantity}
        ${response}=    POST On Session    frontend    /cart    data=${data}
        Should Be Equal As Integers    ${response.status_code}    200
    END
Test Icon
    ${response}=    GET On Session    frontend    /static/favicon.ico
    Should Be Equal As Integers    ${response.status_code}    200
    ${response}=    GET On Session    frontend    /static/img/products/hairdryer.jpg
    Should Be Equal As Integers    ${response.status_code}    200
Test Checkout
    FOR    ${product_id}    IN    @{products}
        ${quantity}=    Evaluate    random.choice([1, 2, 3, 4, 5, 10])
        ${data}=    Create Dictionary    product_id=${product_id}
        ...    quantity=${quantity}
        ...    email=someone@example.com
        ...    street_address=1600 Amphitheatre Parkway
        ...    zip_code=94043
        ...    city=Mountain View
        ...    state=CA
        ...    country=United States
        ...    credit_card_number=4432-8015-6152-0454
        ...    credit_card_expiration_month=1
        ...    credit_card_expiration_year=2039
        ...    credit_card_cvv=672
        ${response}=    POST On Session    frontend    /cart/checkout    data=${data}
        Should Be Equal As Integers    ${response.status_code}    200
    END
