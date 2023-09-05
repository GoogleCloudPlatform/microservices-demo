*** Settings ***
Library           Collections
Library           RequestsLibrary
Library           OperatingSystem

*** Variables ***
@{products}       0PUK6V6EV0  1YMWWN1N4O  2ZYFJ3GM2N  66VCHSJNUP  6E92ZMYYFZ  9SIQT8TOJO  L9ECAV7KIM  LS4PSXUNUM  OLJCESPC7Z
${load}           10
${mdns}           Get Environment Variable    machine_dns
${BASE_URL}       http://${mdns}:8081

*** Test Cases ***
Load Test
    ${threads}=    Create List
    : FOR    ${i}    IN RANGE    ${load}
    \    ${thread}=    Run Keyword    Test Session
    \    Append To List    ${threads}    ${thread}
    : END
    FOR    ${thread}    IN    @{threads}
        Wait Until Keyword Succeeds    2s    10ms    Test Session
    END

*** Keywords ***
Set Base URL
    [Arguments]    ${env}
    ${machine_dns}=    Get Environment Variable    ${env}
    ${base_url}=    Set Variable    http://${machine_dns}:8081
    Set Suite Variable    ${BASE_URL}    ${base_url}

Test Session
    ${order}=    Create List    Test Index    Test Set Currency    Test Browse Product    Test Add To Cart    Test View Cart    Test Add To Cart    Test Checkout
    ${session}=    Create Session    ${BASE_URL}
    : FOR    ${o}    IN    ${order}
    \    Run Keyword    ${o}    ${session}
    : END

Test Bad Requests
    [Arguments]    ${r}
    ${response}=    Get Request    ${BASE_URL}/product/89
    Should Be Equal As Strings    ${response.status_code}    500
    ${data}=    Create Dictionary    currency_code    not a currency
    ${response}=    Post Request    ${BASE_URL}/setCurrency    data=${data}
    Should Be Equal As Strings    ${response.status_code}    500

Test Index
    [Arguments]    ${r}
    ${response}=    Get Request    ${BASE_URL}/
    Should Be Equal As Strings    ${response.status_code}    200

Test Set Currency
    [Arguments]    ${r}
    ${currencies}=    Create List    EUR    USD    JPY    CAD
    : FOR    ${currency}    IN    @{currencies}
    \    ${data}=    Create Dictionary    currency_code    ${currency}
    \    ${response}=    Post Request    ${BASE_URL}/setCurrency    data=${data}
    \    Should Be Equal As Strings    ${response.status_code}    200
    ${data}=    Create Dictionary    currency_code    ${random.choice(['EUR', 'USD', 'JPY', 'CAD'])}
    ${response}=    Post Request    ${BASE_URL}/setCurrency    data=${data}

Test Browse Product
    [Arguments]    ${r}
    : FOR    ${product_id}    IN    @{products}
    \    ${response}=    Get Request    ${BASE_URL}/product/${product_id}
    \    Should Be Equal As Strings    ${response.status_code}    200

Test View Cart
    [Arguments]    ${r}
    ${response}=    Get Request    ${BASE_URL}/cart
    Should Be Equal As Strings    ${response.status_code}    200
    ${response}=    Post Request    ${BASE_URL}/cart/empty
    Should Be Equal As Strings    ${response.status_code}    200

Test Add To Cart
    [Arguments]    ${r}
    : FOR    ${product_id}    IN    @{products}
    \    ${response}=    Get Request    ${BASE_URL}/product/${product_id}
    \    Should Be Equal As Strings    ${response.status_code}    200
    \    ${data}=    Create Dictionary    product_id    ${product_id}    quantity    ${random.choice([1, 2, 3, 4, 5, 10])}
    \    ${response}=    Post Request    ${BASE_URL}/cart    data=${data}
    \    Should Be Equal As Strings    ${response.status_code}    200

Test Checkout
    [Arguments]    ${r}
    ${data}=    Create Dictionary    email    someone@example.com    street_address    1600 Amphitheatre Parkway    zip_code    94043    city    Mountain View    state    CA    country    United States    credit_card_number    4432-8015-6152-0454    credit_card_expiration_month    1    credit_card_expiration_year    2039    credit_card_cvv    672
    : FOR    ${product_id}    IN    @{products}
    \    ${response}=    Post Request    ${BASE_URL}/cart/checkout    data=${data}
    \    Should Be Equal As Strings    ${response.status_code}    200 
