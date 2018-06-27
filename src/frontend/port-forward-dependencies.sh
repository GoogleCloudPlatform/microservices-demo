#!/bin/bash
set -ex

kubectl port-forward $(kubectl get pods -l app=currencyservice -o=name) 7000:31337 &
kubectl port-forward $(kubectl get pods -l app=recommendationservice -o=name) 8081:8080 &
kubectl port-forward $(kubectl get pods -l app=cartservice -o=name) 7070:7070 &
kubectl port-forward $(kubectl get pods -l app=productcatalogservice -o=name) 3550:3550 &
kubectl port-forward $(kubectl get pods -l app=checkoutservice -o=name) 5050:5050 &

set +x
trap "exit" INT TERM ERR
trap "kill 0" EXIT
wait
