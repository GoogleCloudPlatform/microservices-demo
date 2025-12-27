# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
images:
- name: gcr.io/google-samples/microservices-demo/adservice
  newTag: ONLINE_BOUTIQUE_VERSION-native-grpc-probes
- name: gcr.io/google-samples/microservices-demo/cartservice
  newTag: ONLINE_BOUTIQUE_VERSION-native-grpc-probes
- name: gcr.io/google-samples/microservices-demo/checkoutservice
  newTag: ONLINE_BOUTIQUE_VERSION-native-grpc-probes
- name: gcr.io/google-samples/microservices-demo/currencyservice
  newTag: ONLINE_BOUTIQUE_VERSION-native-grpc-probes
- name: gcr.io/google-samples/microservices-demo/emailservice
  newTag: ONLINE_BOUTIQUE_VERSION-native-grpc-probes
- name: gcr.io/google-samples/microservices-demo/paymentservice
  newTag: ONLINE_BOUTIQUE_VERSION-native-grpc-probes
- name: gcr.io/google-samples/microservices-demo/productcatalogservice
  newTag: ONLINE_BOUTIQUE_VERSION-native-grpc-probes
- name: gcr.io/google-samples/microservices-demo/recommendationservice
  newTag: ONLINE_BOUTIQUE_VERSION-native-grpc-probes
- name: gcr.io/google-samples/microservices-demo/shippingservice
  newTag: ONLINE_BOUTIQUE_VERSION-native-grpc-probes
patches:
# adservice - remove the exec and add the grpc for liveness and readiness probes
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: adservice
    spec:
      template:
        spec:
          containers:
            - name: server
              readinessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 9555
              livenessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 9555
# cartservice - remove the exec and add the grpc for liveness and readiness probes
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: cartservice
    spec:
      template:
        spec:
          containers:
            - name: server
              readinessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 7070
              livenessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 7070
# checkoutservice - remove the exec and add the grpc for liveness and readiness probes
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: checkoutservice
    spec:
      template:
        spec:
          containers:
            - name: server
              readinessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 5050
              livenessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 5050
# currencyservice - remove the exec and add the grpc for liveness and readiness probes
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: currencyservice
    spec:
      template:
        spec:
          containers:
            - name: server
              readinessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 7000
              livenessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 7000
# emailservice - remove the exec and add the grpc for liveness and readiness probes
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: emailservice
    spec:
      template:
        spec:
          containers:
            - name: server
              readinessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 8080
              livenessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 8080
# paymentservice - remove the exec and add the grpc for liveness and readiness probes
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: paymentservice
    spec:
      template:
        spec:
          containers:
            - name: server
              readinessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 50051
              livenessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 50051
# productcatalogservice - remove the exec and add the grpc for liveness and readiness probes
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: productcatalogservice
    spec:
      template:
        spec:
          containers:
            - name: server
              readinessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 3550
              livenessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 3550
# recommendationservice - remove the exec and add the grpc for liveness and readiness probes
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: recommendationservice
    spec:
      template:
        spec:
          containers:
            - name: server
              readinessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 8080
              livenessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 8080
# shippingservice - remove the exec and add the grpc for liveness and readiness probes
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: shippingservice
    spec:
      template:
        spec:
          containers:
            - name: server
              readinessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 50051
              livenessProbe:
                exec:
                  $patch: delete
                grpc:
                  port: 50051
