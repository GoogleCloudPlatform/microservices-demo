#other k8s artifacts
kubectl delete -f  ./kubernetes-manifests/emailservice.yaml
kubectl delete -f  ./kubernetes-manifests/frontend.yaml
kubectl delete -f  ./kubernetes-manifests/loadgenerator.yaml
kubectl delete -f  ./kubernetes-manifests/paymentservice.yaml
kubectl delete -f  ./kubernetes-manifests/recommendationservice.yaml
kubectl delete -f  ./kubernetes-manifests/redis.yaml
kubectl delete -f  ./kubernetes-manifests/shippingservice.yaml

#ballerina service k8s artifacts
kubectl delete -f  ./src/recommendationservice_ballerina/target/kubernetes/recommendationservice_ballerina

#challenges
kubectl delete -f  ./kubernetes-manifests/currencyservice.yaml
# kubectl delete -f  ./src/currencyservice_ballerina/target/kubernetes/currencyservice_ballerina

kubectl delete -f  ./kubernetes-manifests/productcatalogservice.yaml
#kubectl delete -f  ./src/productcatalogservice_ballerina/target/kubernetes/productcatalogservice_ballerina

kubectl delete -f  ./kubernetes-manifests/cartservice.yaml
# kubectl delete -f  ./src/cartservice_ballerina/target/kubernetes/cartservice_ballerina

kubectl delete -f  ./kubernetes-manifests/adservice.yaml
# kubectl delete -f  ./src/adservice_ballerina/target/kubernetes/adservice_ballerina

kubectl delete -f  ./kubernetes-manifests/checkoutservice.yaml
# kubectl delete -f  ./src/checkoutservice_ballerina/target/kubernetes/checkoutservice_ballerina
