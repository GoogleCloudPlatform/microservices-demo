kubectl apply -f  HipsterShop/target/kubernetes/paymentservice
kubectl apply -f  HipsterShop/target/kubernetes/shippingservice
kubectl apply -f  HipsterShop/target/kubernetes/emailservice
kubectl apply -f k8s_manifests/frontend/frontend-kubernetes-manifests.yaml

ballerina build --sourceroot src/recommendationservice_ballerina --all --skip-tests
kubectl apply -f  src/recommendationservice/target/kubernetes/recommendationservice

# Cart service
kubectl apply -f  HipsterShop/target/kubernetes/adservice
# Replace above command with following command when you implemented the ad service in Ballerina.

# ballerina build --sourceroot src/adservice_ballerina --all --skip-tests
# kubectl apply -f  src/adservice_ballerina/target/kubernetes/adservice

kubectl apply -f  HipsterShop/target/kubernetes/currencyservice
# Replace above command with following command when you implemented the currency service in Ballerina.

# ballerina build --sourceroot src/currencyservice_ballerina --all --skip-tests
# kubectl apply -f  src/currencyservice_ballerina/target/kubernetes/currencyservice

# Cart service
kubectl apply -f  HipsterShop/target/kubernetes/cartservice
# Replace above command with following command when you implemented the cart service in Ballerina.

# ballerina build --sourceroot src/cartservice_ballerina --all --skip-tests
# kubectl apply -f  src/cartservice_ballerina/target/kubernetes/cartservice

# Product Catalog Service
kubectl apply -f  HipsterShop/target/kubernetes/productcatalogservice

# Replace above with following command when you implemented the product catalog service in Ballerina.

# ballerina build --sourceroot src/productcatalogservice_ballerina --all --skip-tests
# kubectl apply -f  src/productcatalogservice_ballerina/target/kubernetes/productcatalogservice

# Checkout service
kubectl apply -f  HipsterShop/target/kubernetes/checkoutservice
# Replace above with following command when you implemented the checkout service in Ballerina.

# ballerina build --sourceroot src/checkoutservice_ballerina --all --skip-tests
# kubectl apply -f  src/checkoutservice_ballerina/target/kubernetes/checkoutservice

kubectl get services
