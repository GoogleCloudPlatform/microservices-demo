# other k8s artifacts
kubectl apply -f  ./kubernetes-manifests/emailservice.yaml
kubectl apply -f  ./kubernetes-manifests/frontend.yaml
kubectl apply -f  ./kubernetes-manifests/loadgenerator.yaml
kubectl apply -f  ./kubernetes-manifests/paymentservice.yaml
kubectl apply -f  ./kubernetes-manifests/recommendationservice.yaml
kubectl apply -f  ./kubernetes-manifests/redis.yaml
kubectl apply -f  ./kubernetes-manifests/shippingservice.yaml

# ballerina service k8s artifacts
kubectl apply -f  ./src/recommendationservice_ballerina/target/kubernetes/recommendationservice_ballerina

# challenges
kubectl apply -f  ./kubernetes-manifests/currencyservice.yaml
# kubectl apply -f  ./src/currencyservice_ballerina/target/kubernetes/currencyservice_ballerina

kubectl apply -f  ./kubernetes-manifests/productcatalogservice.yaml
# kubectl apply -f  ./src/productcatalogservice_ballerina/target/kubernetes/productcatalogservice_ballerina

kubectl apply -f  ./kubernetes-manifests/cartservice.yaml
# kubectl apply -f  ./src/cartservice_ballerina/target/kubernetes/cartservice_ballerina

kubectl apply -f  ./kubernetes-manifests/adservice.yaml
# kubectl apply -f  ./src/adservice_ballerina/target/kubernetes/adservice_ballerina

kubectl apply -f  ./kubernetes-manifests/checkoutservice.yaml
# kubectl apply -f  ./src/checkoutservice_ballerina/target/kubernetes/checkoutservice_ballerina
