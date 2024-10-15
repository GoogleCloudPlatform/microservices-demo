# src/adservice
docker build -t adservice .

# src/productcatalogservice
docker build -t productcatalogservice .

# src/cartservice/src
docker build -t cartservice .

# src/shippingservice
docker build -t shippingservice .

# src/currencyservice
docker build -t currencyservice .

# src/paymentservice
docker build -t paymentservice .

# src/emailservice
docker build -t emailservice .

# For dependencies services
# src/recommendationservice
docker build -t recommendationservice .

# src/frontend
docker build -t frontend .

# src/checkoutservice
docker build -t checkoutservice .

# src/loadgenerator
docker build -t loadgenerator .
