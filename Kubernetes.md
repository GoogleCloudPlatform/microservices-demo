# Guia profunda de Kubernetes para este proyecto

Esta guia explica que es Kubernetes, como funciona, que papel cumple en este
repositorio, como levantar Online Boutique en Docker Desktop y que ventajas te
da en desarrollo local y en despliegues reales.

El objetivo no es solo copiar comandos. La idea es que puedas leer los YAML del
proyecto y entender por que existen, que hace cada parte y como diagnosticar
problemas cuando algo no levanta.

## Indice

1. [Resumen mental](#resumen-mental)
2. [Que es Kubernetes](#que-es-kubernetes)
3. [Docker vs Kubernetes vs Docker Compose](#docker-vs-kubernetes-vs-docker-compose)
4. [Como funciona Kubernetes por dentro](#como-funciona-kubernetes-por-dentro)
5. [Conceptos y definiciones clave](#conceptos-y-definiciones-clave)
6. [Que hace Kubernetes en este proyecto](#que-hace-kubernetes-en-este-proyecto)
7. [Tree del repositorio relacionado con Kubernetes](#tree-del-repositorio-relacionado-con-kubernetes)
8. [Arquitectura de Online Boutique](#arquitectura-de-online-boutique)
9. [Como leer los manifiestos YAML](#como-leer-los-manifiestos-yaml)
10. [Release vs kubernetes-manifests vs Skaffold vs Kustomize vs Helm](#release-vs-kubernetes-manifests-vs-skaffold-vs-kustomize-vs-helm)
11. [Levantar Kubernetes en Docker Desktop](#levantar-kubernetes-en-docker-desktop)
12. [Opcion A: levantar rapido con imagenes publicas](#opcion-a-levantar-rapido-con-imagenes-publicas)
13. [Opcion B: levantar en modo desarrollo con Skaffold](#opcion-b-levantar-en-modo-desarrollo-con-skaffold)
14. [Comandos de inspeccion y debugging](#comandos-de-inspeccion-y-debugging)
15. [Problemas comunes](#problemas-comunes)
16. [Ventajas que ofrece Kubernetes](#ventajas-que-ofrece-kubernetes)
17. [Limitaciones y costos mentales](#limitaciones-y-costos-mentales)
18. [Cheat sheet](#cheat-sheet)
19. [Referencias](#referencias)

## Resumen mental

Docker responde principalmente a esta pregunta:

> Como empaqueto y ejecuto una aplicacion en un contenedor?

Kubernetes responde una pregunta mas amplia:

> Como ejecuto muchos contenedores como un sistema completo, manteniendolos
> vivos, conectados, configurados, observables y reemplazables?

En este proyecto eso importa porque Online Boutique no es una sola aplicacion.
Es un conjunto de microservicios:

- Un frontend web.
- Servicios internos para carrito, pagos, envios, catalogo, moneda,
  recomendaciones, anuncios y correo.
- Redis como almacenamiento del carrito.
- Un generador de carga opcional para simular usuarios.

Kubernetes se encarga de que todo eso corra como un sistema.

```text
Usuario
  |
  v
frontend-external  Service tipo LoadBalancer
  |
  v
frontend  Deployment + Pods
  |
  +--> productcatalogservice
  +--> currencyservice
  +--> cartservice ------> redis-cart
  +--> recommendationservice
  +--> adservice
  +--> checkoutservice
          |
          +--> paymentservice
          +--> shippingservice
          +--> emailservice
          +--> cartservice
```

La version corta:

- Docker crea y corre contenedores.
- Kubernetes orquesta contenedores.
- `kubectl` es la CLI para hablar con Kubernetes.
- Un `Deployment` declara como correr una aplicacion.
- Un `Service` da una direccion estable para llegar a Pods dinamicos.
- Docker Desktop puede crear un cluster local para practicar y desarrollar.
- Este repo trae manifiestos Kubernetes listos para desplegar Online Boutique.

## Que es Kubernetes

Kubernetes, tambien llamado K8s, es una plataforma open source para administrar
workloads y servicios containerizados usando configuracion declarativa y
automatizacion.

La palabra clave es declarativa.

Tu no ejecutas manualmente cada contenedor uno por uno. Le dices al cluster:

```text
Quiero este estado:

- 1 frontend corriendo.
- 1 cartservice corriendo.
- 1 redis-cart corriendo.
- Un Service interno para cada microservicio.
- Un Service externo para entrar al frontend.
- Health checks para detectar fallos.
- Limites de CPU y memoria.
```

Kubernetes intenta constantemente que el estado real coincida con ese estado
deseado.

Si un contenedor muere, Kubernetes puede reiniciarlo.
Si un Pod desaparece, el Deployment crea otro.
Si un Pod cambia de IP, el Service sigue ofreciendo un nombre estable.
Si cambias una imagen, Kubernetes hace rollout.
Si necesitas mas capacidad, puedes escalar replicas.

## Docker vs Kubernetes vs Docker Compose

No son enemigos. Resuelven niveles distintos del problema.

| Herramienta | Pregunta que responde | Ejemplo |
| --- | --- | --- |
| Dockerfile | Como construyo una imagen? | `src/frontend/Dockerfile` |
| Docker | Como ejecuto un contenedor? | `docker run frontend` |
| Docker Compose | Como ejecuto varios contenedores en una maquina? | `docker compose up` |
| Kubernetes | Como opero aplicaciones containerizadas con networking, salud, escalado, rollouts y declaracion de estado? | `kubectl apply -f release/kubernetes-manifests.yaml` |
| Skaffold | Como construyo imagenes y las despliego a Kubernetes durante desarrollo? | `skaffold run` o `skaffold dev` |
| Kustomize | Como personalizo YAML de Kubernetes sin duplicarlo? | `kubectl apply -k kustomize/` |
| Helm | Como empaqueto una app Kubernetes como chart configurable? | `helm install ...` |

Una analogia practica:

```text
Dockerfile      = receta para construir una caja.
Docker image    = la caja ya construida.
Container       = una caja encendida.
Kubernetes YAML = plano de como deben vivir muchas cajas juntas.
Kubernetes      = sistema que mantiene esas cajas funcionando.
```

## Como funciona Kubernetes por dentro

Un cluster de Kubernetes tiene dos grandes partes:

```text
Cluster Kubernetes
|
+-- Control Plane
|   |
|   +-- kube-apiserver
|   +-- etcd
|   +-- kube-scheduler
|   +-- kube-controller-manager
|
+-- Worker Nodes
    |
    +-- kubelet
    +-- kube-proxy
    +-- container runtime
    +-- Pods
```

### Control Plane

Es el cerebro del cluster.

- **kube-apiserver**: entrada principal. `kubectl` habla con este API.
- **etcd**: base de datos clave-valor donde se guarda el estado del cluster.
- **kube-scheduler**: decide en que nodo debe correr un Pod.
- **kube-controller-manager**: ejecuta controladores que comparan estado deseado
  vs estado real.

### Worker Node

Es donde corren los Pods.

- **kubelet**: agente del nodo. Recibe instrucciones y mantiene Pods corriendo.
- **kube-proxy**: ayuda a implementar networking de Services.
- **container runtime**: componente que ejecuta contenedores.
- **Pods**: unidades donde viven tus contenedores.

En Docker Desktop, todo esto corre localmente dentro de la maquina virtual y/o
contenedores gestionados por Docker Desktop.

### Ciclo cuando aplicas un YAML

```text
1. Escribes un manifiesto YAML.
2. Ejecutas kubectl apply.
3. kubectl envia el manifiesto al kube-apiserver.
4. Kubernetes guarda el estado deseado.
5. Los controladores detectan que faltan recursos.
6. El scheduler asigna Pods a nodos.
7. El kubelet crea los contenedores.
8. Los Services exponen endpoints estables.
9. Las probes revisan salud.
10. Kubernetes corrige desviaciones.
```

Ejemplo:

```powershell
kubectl apply -f .\release\kubernetes-manifests.yaml
```

Ese comando no "corre un script" tradicional. Declara objetos Kubernetes. Luego
el cluster se encarga de materializarlos.

## Conceptos y definiciones clave

### Cluster

Conjunto de maquinas, reales o virtuales, administradas por Kubernetes.

En produccion podria ser GKE, EKS, AKS o un cluster propio. En local puede ser
Docker Desktop, Minikube o Kind.

### Node

Maquina dentro del cluster donde pueden correr Pods.

En Docker Desktop con `kubeadm` normalmente tienes un nodo local llamado
`docker-desktop`. Con `kind`, Docker Desktop puede crear un cluster multi-nodo.

### Namespace

Separacion logica dentro del cluster.

Sirve para agrupar recursos:

```powershell
kubectl create namespace online-boutique
kubectl get pods -n online-boutique
```

Si no indicas namespace, Kubernetes usa `default`.

### Pod

Unidad minima deployable en Kubernetes. Normalmente contiene un contenedor.

Kubernetes no administra contenedores sueltos directamente: administra Pods.

```text
Deployment frontend
  |
  v
ReplicaSet
  |
  v
Pod frontend-xxxxx
  |
  v
Container server
```

### Deployment

Objeto que declara como correr una aplicacion.

Controla:

- Imagen del contenedor.
- Numero de replicas.
- Variables de entorno.
- Puertos.
- Probes.
- Requests y limits.
- Estrategia de actualizacion.

En este proyecto, casi cada microservicio tiene su propio `Deployment`.

### ReplicaSet

Objeto que asegura que exista cierto numero de Pods.

Normalmente no lo editas directamente. Lo crea y maneja el Deployment.

### Service

Objeto que da una direccion estable para llegar a Pods.

Los Pods son efimeros: pueden morir y volver con otra IP. Un Service resuelve
ese problema.

Ejemplo conceptual:

```text
Service cartservice
  DNS: cartservice
  Port: 7070
  Selector: app=cartservice
    |
    +--> Pod cartservice-a
    +--> Pod cartservice-b
```

Aunque los Pods cambien, otros servicios siguen llamando a:

```text
cartservice:7070
```

### ClusterIP

Tipo de Service interno. Solo se accede desde dentro del cluster.

En este proyecto casi todos los servicios son `ClusterIP`:

- `cartservice`
- `redis-cart`
- `checkoutservice`
- `productcatalogservice`
- `currencyservice`
- `paymentservice`
- `shippingservice`
- `emailservice`
- `recommendationservice`
- `adservice`

Eso es correcto: no quieres exponer pagos, carrito o Redis directamente al
mundo.

### LoadBalancer

Tipo de Service externo. En cloud crea un balanceador real. En Docker Desktop,
Docker implementa una forma local de exponerlo.

En este proyecto se usa para:

```text
frontend-external
```

Ese Service apunta al Deployment `frontend`.

### ConfigMap y Secret

No son protagonistas en el despliegue base de este repo, pero son importantes:

- `ConfigMap`: configuracion no sensible.
- `Secret`: credenciales o datos sensibles codificados y gestionados por
  Kubernetes.

En aplicaciones reales, usarias estos objetos para evitar quemar configuracion
directamente en el YAML.

### Liveness Probe

Health check que responde:

> Esta vivo el contenedor?

Si falla repetidamente, Kubernetes reinicia el contenedor.

### Readiness Probe

Health check que responde:

> Esta listo para recibir trafico?

Si falla, el Pod puede seguir vivo, pero el Service no deberia enviarle trafico.

### Requests y Limits

Definen recursos.

- `requests`: lo que el contenedor pide como base para planificacion.
- `limits`: lo maximo que puede consumir.

Ejemplo conceptual:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 64Mi
  limits:
    cpu: 200m
    memory: 128Mi
```

`100m` significa 100 millicores, o 0.1 CPU.

### ServiceAccount

Identidad que usa un Pod dentro del cluster.

Aunque en este proyecto base no se explota mucho para permisos avanzados, es una
buena practica declarar ServiceAccounts por servicio.

### Label y Selector

Kubernetes conecta objetos por etiquetas.

Ejemplo:

```yaml
metadata:
  labels:
    app: frontend
```

Y luego un Service selecciona Pods con:

```yaml
selector:
  app: frontend
```

Eso significa:

```text
Service frontend -> manda trafico a Pods con label app=frontend
```

## Que hace Kubernetes en este proyecto

Este repositorio es Online Boutique, una aplicacion demo de microservicios. El
README del proyecto indica que esta compuesta por 11 microservicios escritos en
distintos lenguajes y comunicados por gRPC.

Kubernetes hace de plataforma donde todos esos servicios viven.

### Lo que Kubernetes crea

Para cada microservicio principal, Kubernetes crea normalmente:

```text
Deployment
Service
ServiceAccount
```

Para Redis crea:

```text
Deployment redis-cart
Service redis-cart
Volume emptyDir
```

Para el frontend crea ademas:

```text
Service frontend-external tipo LoadBalancer
```

### Por que el proyecto necesita esto

Porque son muchos procesos independientes:

```text
frontend
cartservice
checkoutservice
currencyservice
emailservice
paymentservice
productcatalogservice
recommendationservice
shippingservice
adservice
redis-cart
loadgenerator
```

Cada uno tiene:

- Imagen distinta.
- Lenguaje distinto.
- Puerto distinto.
- Health checks distintos.
- Dependencias distintas.
- Variables de entorno distintas.

Kubernetes permite describir todo eso como infraestructura versionada.

## Tree del repositorio relacionado con Kubernetes

Vista resumida de lo importante:

```text
microservices-demo/
|
+-- README.md
+-- skaffold.yaml
+-- release/
|   +-- kubernetes-manifests.yaml
|   +-- istio-manifests.yaml
|
+-- kubernetes-manifests/
|   +-- README.md
|   +-- kustomization.yaml
|   +-- frontend.yaml
|   +-- cartservice.yaml
|   +-- checkoutservice.yaml
|   +-- productcatalogservice.yaml
|   +-- currencyservice.yaml
|   +-- paymentservice.yaml
|   +-- shippingservice.yaml
|   +-- emailservice.yaml
|   +-- recommendationservice.yaml
|   +-- adservice.yaml
|   +-- loadgenerator.yaml
|
+-- kustomize/
|   +-- README.md
|   +-- kustomization.yaml
|   +-- base/
|   +-- components/
|       +-- cymbal-branding/
|       +-- google-cloud-operations/
|       +-- memorystore/
|       +-- network-policies/
|       +-- service-mesh-istio/
|       +-- spanner/
|       +-- alloydb/
|       +-- shopping-assistant/
|
+-- helm-chart/
|   +-- Chart.yaml
|   +-- values.yaml
|   +-- templates/
|
+-- src/
    +-- frontend/
    +-- cartservice/
    +-- checkoutservice/
    +-- productcatalogservice/
    +-- currencyservice/
    +-- paymentservice/
    +-- shippingservice/
    +-- emailservice/
    +-- recommendationservice/
    +-- adservice/
    +-- loadgenerator/
```

### Archivos principales

| Archivo o carpeta | Para que sirve |
| --- | --- |
| `release/kubernetes-manifests.yaml` | Manifiesto consolidado con imagenes publicas preconstruidas. Ideal para levantar rapido. |
| `kubernetes-manifests/` | Manifiestos base usados por Skaffold. No estan pensados para aplicarse directamente sin inyectar imagenes. |
| `skaffold.yaml` | Define como construir imagenes locales y desplegarlas en Kubernetes. |
| `kustomize/` | Permite variantes: branding, observabilidad, Istio, network policies, bases administradas, etc. |
| `helm-chart/` | Empaquetado alternativo usando Helm. |
| `src/*/Dockerfile` | Recetas para construir imagenes de cada microservicio. |

## Arquitectura de Online Boutique

### Microservicios

| Servicio | Lenguaje | Funcion |
| --- | --- | --- |
| `frontend` | Go | Sirve la web y llama a los servicios internos. |
| `cartservice` | C# | Administra el carrito usando Redis. |
| `productcatalogservice` | Go | Devuelve productos desde `products.json`. |
| `currencyservice` | Node.js | Convierte monedas. |
| `paymentservice` | Node.js | Simula pagos. |
| `shippingservice` | Go | Calcula y simula envios. |
| `emailservice` | Python | Simula envio de correo de confirmacion. |
| `checkoutservice` | Go | Orquesta compra, pago, envio, correo y carrito. |
| `recommendationservice` | Python | Recomienda productos. |
| `adservice` | Java | Devuelve anuncios. |
| `loadgenerator` | Python/Locust | Simula trafico de usuarios. |
| `redis-cart` | Redis | Guarda datos del carrito. |

### Tree de llamadas principales

```text
frontend
|
+-- productcatalogservice
|   +-- lee catalogo de productos
|
+-- currencyservice
|   +-- convierte precios
|
+-- cartservice
|   +-- redis-cart
|
+-- recommendationservice
|   +-- productcatalogservice
|
+-- adservice
|
+-- checkoutservice
    |
    +-- cartservice
    |   +-- redis-cart
    |
    +-- productcatalogservice
    +-- currencyservice
    +-- shippingservice
    +-- paymentservice
    +-- emailservice
```

### Flujo de compra

```text
1. Usuario abre la tienda.
2. Browser llama al frontend.
3. Frontend pide productos al productcatalogservice.
4. Frontend muestra productos y recomendaciones.
5. Usuario agrega producto al carrito.
6. Frontend llama a cartservice.
7. Cartservice guarda carrito en redis-cart.
8. Usuario hace checkout.
9. Frontend llama a checkoutservice.
10. Checkoutservice consulta carrito, productos, moneda y envio.
11. Checkoutservice llama a paymentservice.
12. Checkoutservice llama a shippingservice.
13. Checkoutservice llama a emailservice.
14. Usuario recibe pantalla de orden completada.
```

### Networking dentro del cluster

Kubernetes crea DNS interno. Por eso el YAML puede configurar servicios asi:

```text
PRODUCT_CATALOG_SERVICE_ADDR=productcatalogservice:3550
CURRENCY_SERVICE_ADDR=currencyservice:7000
CART_SERVICE_ADDR=cartservice:7070
CHECKOUT_SERVICE_ADDR=checkoutservice:5050
AD_SERVICE_ADDR=adservice:9555
REDIS_ADDR=redis-cart:6379
```

Cada nombre, como `cartservice`, corresponde a un `Service` Kubernetes.

## Como leer los manifiestos YAML

Veamos el patron general.

### Deployment

Un `Deployment` declara como correr el microservicio.

Estructura conceptual:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: server
          image: frontend
          ports:
            - containerPort: 8080
```

Puntos importantes:

- `kind: Deployment`: tipo de objeto.
- `metadata.name`: nombre del recurso.
- `selector.matchLabels`: que Pods pertenecen al Deployment.
- `template`: plantilla para crear Pods.
- `containers`: contenedores que corren dentro del Pod.
- `image`: imagen Docker.
- `containerPort`: puerto interno del contenedor.

### Service interno

Un `Service` tipo `ClusterIP` da acceso interno.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: ClusterIP
  selector:
    app: frontend
  ports:
    - name: http
      port: 80
      targetPort: 8080
```

Interpretacion:

```text
Dentro del cluster, el nombre frontend escucha en puerto 80.
Ese trafico se envia a Pods con label app=frontend, puerto 8080.
```

### Service externo

El frontend tambien tiene:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-external
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
    - name: http
      port: 80
      targetPort: 8080
```

Interpretacion:

```text
Expone el frontend hacia fuera del cluster.
En cloud crea o usa un load balancer.
En Docker Desktop se expone localmente.
```

### Variables de entorno

El frontend necesita saber donde estan los servicios internos:

```yaml
env:
  - name: PRODUCT_CATALOG_SERVICE_ADDR
    value: "productcatalogservice:3550"
  - name: CART_SERVICE_ADDR
    value: "cartservice:7070"
  - name: CHECKOUT_SERVICE_ADDR
    value: "checkoutservice:5050"
```

Esto funciona gracias al DNS interno de Kubernetes.

### Probes

Ejemplo conceptual:

```yaml
readinessProbe:
  httpGet:
    path: "/_healthz"
    port: 8080

livenessProbe:
  httpGet:
    path: "/_healthz"
    port: 8080
```

La diferencia:

- `readinessProbe`: controla si el Pod recibe trafico.
- `livenessProbe`: controla si el contenedor debe reiniciarse.

### Redis y almacenamiento temporal

En `cartservice.yaml`, Redis usa `emptyDir`:

```yaml
volumes:
  - name: redis-data
    emptyDir: {}
```

`emptyDir` es almacenamiento efimero asociado al Pod. Sirve para demo local,
pero no es almacenamiento durable de produccion.

Si el Pod de Redis desaparece, los datos pueden perderse.

Para produccion se usaria:

- Un servicio administrado como Memorystore.
- Un `PersistentVolumeClaim`.
- Otra base de datos externa.

El repo trae componentes Kustomize para Memorystore, Spanner y AlloyDB.

## Release vs kubernetes-manifests vs Skaffold vs Kustomize vs Helm

Este repo trae varias formas de desplegar. Es importante elegir la correcta.

### `release/kubernetes-manifests.yaml`

Usalo para levantar rapido.

Contiene imagenes publicas ya construidas:

```text
us-central1-docker.pkg.dev/google-samples/microservices-demo/frontend:v0.10.5
us-central1-docker.pkg.dev/google-samples/microservices-demo/cartservice:v0.10.5
...
```

Ventajas:

- No compila nada localmente.
- Es mas rapido para probar.
- Ideal para estudiar Kubernetes y la arquitectura.

Comando:

```powershell
kubectl apply -n online-boutique -f .\release\kubernetes-manifests.yaml
```

### `kubernetes-manifests/`

Contiene los manifiestos base, pero sus imagenes aparecen como nombres locales:

```yaml
image: frontend
image: cartservice
```

Por eso el README de esa carpeta indica que no estan pensados para desplegarse
directamente sin Skaffold. Skaffold construye las imagenes y reemplaza los tags.

### `skaffold.yaml`

Skaffold automatiza desarrollo local con Kubernetes.

Define:

- Que imagenes construir.
- De que carpetas salen.
- Que Dockerfiles usar.
- Que manifiestos aplicar.
- Como hacer deploy con `kubectl`.

Ejemplo del flujo:

```text
src/frontend/Dockerfile
  |
  v
skaffold build
  |
  v
imagen frontend:<tag>
  |
  v
skaffold deploy
  |
  v
Deployment frontend en Kubernetes
```

Comandos:

```powershell
skaffold run
skaffold dev
skaffold delete
```

Usa `skaffold run` cuando quieres construir y desplegar una vez.
Usa `skaffold dev` cuando estas editando codigo y quieres ciclo automatico.

### `kustomize/`

Kustomize sirve para modificar manifiestos sin copiar todo.

Ejemplos de variaciones que trae este repo:

- Cambiar branding a Cymbal Shops.
- Integrar Google Cloud Operations.
- Usar Memorystore en lugar de Redis local.
- Agregar NetworkPolicies.
- Usar Istio / service mesh.
- Integrar Spanner o AlloyDB.

Comandos:

```powershell
kubectl kustomize .\kustomize
kubectl apply -k .\kustomize
```

### `helm-chart/`

Helm empaqueta Kubernetes como un chart configurable.

Sirve cuando quieres instalar la aplicacion con valores parametrizables:

```text
helm-chart/
|
+-- Chart.yaml
+-- values.yaml
+-- templates/
```

Helm es muy usado para distribuir aplicaciones Kubernetes.

## Levantar Kubernetes en Docker Desktop

Docker Desktop incluye una integracion de Kubernetes para desarrollo y pruebas
locales. En versiones recientes, la vista de Kubernetes permite crear un cluster
desde el dashboard.

### Requisitos recomendados para este repo

Segun la guia de desarrollo del proyecto, para Docker Desktop conviene tener al
menos:

- 3 CPUs.
- 6 GiB de memoria.
- 32 GB de disco.

Online Boutique levanta bastantes servicios. Si asignas pocos recursos, puedes
ver Pods en `Pending`, reinicios o builds lentos.

### Activar Kubernetes en Docker Desktop

En Docker Desktop reciente:

1. Abre Docker Desktop.
2. Entra a la vista **Kubernetes**.
3. Selecciona **Create cluster**.
4. Elige el tipo de cluster:
   - `kubeadm`: single-node, simple.
   - `kind`: multi-node, mas realista y configurable.
5. Selecciona **Create**.
6. Espera a que Docker Desktop termine de crear el cluster.

En algunas versiones anteriores, la ruta puede ser:

```text
Settings > Kubernetes > Enable Kubernetes > Apply
```

Si estas en Windows, asegurate de usar contenedores Linux. La pestaña de
Kubernetes no esta disponible en modo Windows containers.

### Verificar el cluster

```powershell
kubectl version
kubectl config get-contexts
kubectl config use-context docker-desktop
kubectl get nodes
```

Salida esperada aproximada:

```text
NAME             STATUS   ROLES           AGE   VERSION
docker-desktop   Ready    control-plane   3h    v1.xx.x
```

Si `kubectl` apunta a otro cluster, cambia el contexto:

```powershell
kubectl config use-context docker-desktop
```

## Opcion A: levantar rapido con imagenes publicas

Esta es la ruta recomendada si quieres estudiar el proyecto y verlo funcionando
sin compilar todos los microservicios.

### 1. Ir a la raiz del repo

```powershell
cd "C:\Users\Ignacio Alvarado\Documents\GitHub\microservices-demo"
```

### 2. Verificar contexto

```powershell
kubectl config get-contexts
kubectl config use-context docker-desktop
kubectl get nodes
```

### 3. Crear namespace

```powershell
kubectl create namespace online-boutique
```

Si ya existe:

```powershell
kubectl get namespace online-boutique
```

### 4. Aplicar manifiesto release

```powershell
kubectl apply -n online-boutique -f .\release\kubernetes-manifests.yaml
```

### 5. Ver recursos

```powershell
kubectl get all -n online-boutique
```

### 6. Esperar Pods listos

```powershell
kubectl get pods -n online-boutique -w
```

Quieres ver algo parecido a:

```text
adservice-xxxxx                  1/1   Running
cartservice-xxxxx                1/1   Running
checkoutservice-xxxxx            1/1   Running
currencyservice-xxxxx            1/1   Running
emailservice-xxxxx               1/1   Running
frontend-xxxxx                   1/1   Running
loadgenerator-xxxxx              1/1   Running
paymentservice-xxxxx             1/1   Running
productcatalogservice-xxxxx      1/1   Running
recommendationservice-xxxxx      1/1   Running
redis-cart-xxxxx                 1/1   Running
shippingservice-xxxxx            1/1   Running
```

Para salir del watch:

```text
Ctrl + C
```

### 7. Acceder al frontend

Primero mira el Service:

```powershell
kubectl get svc frontend-external -n online-boutique
```

En Docker Desktop puede funcionar:

```text
http://localhost
```

Si no abre, usa port-forward:

```powershell
kubectl port-forward -n online-boutique deployment/frontend 8080:8080
```

Luego abre:

```text
http://localhost:8080
```

Mientras el port-forward este activo, deja esa terminal abierta.

### 8. Limpiar recursos

```powershell
kubectl delete namespace online-boutique
```

O si no usaste namespace:

```powershell
kubectl delete -f .\release\kubernetes-manifests.yaml
```

## Opcion B: levantar en modo desarrollo con Skaffold

Usa esta opcion si quieres modificar codigo fuente y construir imagenes locales.

### 1. Requisitos

Necesitas:

- Docker Desktop con Kubernetes activo.
- `kubectl`.
- `skaffold`.
- Recursos suficientes asignados a Docker Desktop.

Verifica:

```powershell
docker version
kubectl version
skaffold version
```

### 2. Usar contexto correcto

```powershell
kubectl config use-context docker-desktop
kubectl get nodes
```

### 3. Ejecutar Skaffold

Desde la raiz del repo:

```powershell
skaffold run
```

La primera vez puede tardar bastante porque construye varias imagenes.

Skaffold hara:

```text
1. Leer skaffold.yaml.
2. Construir imagenes desde src/*.
3. Etiquetar imagenes.
4. Renderizar manifiestos Kubernetes.
5. Aplicarlos al cluster con kubectl.
```

### 4. Ver estado

```powershell
kubectl get pods
kubectl get svc
```

### 5. Abrir frontend

```powershell
kubectl port-forward deployment/frontend 8080:8080
```

Abrir:

```text
http://localhost:8080
```

### 6. Desarrollo continuo

Si estas editando codigo:

```powershell
skaffold dev
```

Skaffold observa cambios, reconstruye y redeploya cuando corresponde.

### 7. Limpiar

Si desplegaste con Skaffold:

```powershell
skaffold delete
```

## Comandos de inspeccion y debugging

### Ver contexto actual

```powershell
kubectl config current-context
kubectl config get-contexts
```

### Cambiar a Docker Desktop

```powershell
kubectl config use-context docker-desktop
```

### Ver nodos

```powershell
kubectl get nodes -o wide
```

### Ver todo en un namespace

```powershell
kubectl get all -n online-boutique
```

### Ver Pods

```powershell
kubectl get pods -n online-boutique
kubectl get pods -n online-boutique -o wide
```

### Describir un Pod

```powershell
kubectl describe pod -n online-boutique <pod-name>
```

Este comando es clave. Mira especialmente:

- `Events`
- `Image`
- `State`
- `Last State`
- `Restart Count`
- `Readiness`
- `Liveness`

### Ver logs

```powershell
kubectl logs -n online-boutique <pod-name>
```

Seguir logs:

```powershell
kubectl logs -n online-boutique -f <pod-name>
```

Logs de un Deployment:

```powershell
kubectl logs -n online-boutique deployment/frontend
kubectl logs -n online-boutique deployment/cartservice
```

### Entrar a un Pod

No todas las imagenes tienen shell. Pero si lo tienen:

```powershell
kubectl exec -n online-boutique -it <pod-name> -- sh
```

### Ver Services

```powershell
kubectl get svc -n online-boutique
kubectl describe svc -n online-boutique frontend-external
```

### Ver endpoints

```powershell
kubectl get endpoints -n online-boutique
```

Si un Service no tiene endpoints, usualmente su selector no coincide con los
labels de los Pods o los Pods no estan Ready.

### Ver Deployments

```powershell
kubectl get deployments -n online-boutique
kubectl describe deployment -n online-boutique frontend
```

### Ver rollout

```powershell
kubectl rollout status deployment/frontend -n online-boutique
kubectl rollout history deployment/frontend -n online-boutique
```

### Reiniciar un Deployment

```powershell
kubectl rollout restart deployment/frontend -n online-boutique
```

### Escalar replicas

Ejemplo con frontend:

```powershell
kubectl scale deployment/frontend -n online-boutique --replicas=2
kubectl get pods -n online-boutique -l app=frontend
```

Volver a una replica:

```powershell
kubectl scale deployment/frontend -n online-boutique --replicas=1
```

### Port-forward

Deployment:

```powershell
kubectl port-forward -n online-boutique deployment/frontend 8080:8080
```

Service:

```powershell
kubectl port-forward -n online-boutique svc/frontend 8080:80
```

### Eliminar y recrear

```powershell
kubectl delete -n online-boutique -f .\release\kubernetes-manifests.yaml
kubectl apply -n online-boutique -f .\release\kubernetes-manifests.yaml
```

### Ver YAML aplicado

```powershell
kubectl get deployment frontend -n online-boutique -o yaml
```

### Ver eventos

```powershell
kubectl get events -n online-boutique --sort-by=.lastTimestamp
```

## Problemas comunes

### `kubectl` habla con el cluster equivocado

Sintoma:

```text
No resources found
```

O ves recursos que no tienen nada que ver.

Solucion:

```powershell
kubectl config get-contexts
kubectl config use-context docker-desktop
```

### Pods en `Pending`

Posibles causas:

- Docker Desktop no tiene CPU/RAM suficiente.
- El cluster no tiene nodos Ready.
- Hay restricciones de recursos.

Diagnostico:

```powershell
kubectl describe pod -n online-boutique <pod-name>
kubectl get nodes
```

Solucion probable:

- Aumenta recursos en Docker Desktop.
- Reinicia Docker Desktop.
- Revisa `Events` del Pod.

### `ImagePullBackOff`

Kubernetes no pudo descargar una imagen.

Diagnostico:

```powershell
kubectl describe pod -n online-boutique <pod-name>
```

Posibles causas:

- Sin internet.
- Registry inaccesible.
- Tag incorrecto.
- Estas aplicando `kubernetes-manifests/` directamente en vez de `release/`.

Solucion para primera prueba:

```powershell
kubectl apply -n online-boutique -f .\release\kubernetes-manifests.yaml
```

### `CrashLoopBackOff`

El contenedor arranca y se cae repetidamente.

Diagnostico:

```powershell
kubectl logs -n online-boutique <pod-name>
kubectl describe pod -n online-boutique <pod-name>
```

Busca:

- Variables de entorno faltantes.
- Servicio dependiente caido.
- Error de configuracion.
- Puerto incorrecto.

### `frontend-external` queda en `<pending>`

En clusters cloud, `<pending>` puede significar que todavia se crea el load
balancer. En local, dependiendo de la integracion, puede no comportarse igual
que un cloud load balancer.

Solucion practica:

```powershell
kubectl port-forward -n online-boutique deployment/frontend 8080:8080
```

### `localhost` no abre

Prueba con port-forward:

```powershell
kubectl port-forward -n online-boutique svc/frontend 8080:80
```

Abrir:

```text
http://localhost:8080
```

### Puerto ocupado

Si `8080` esta ocupado:

```powershell
kubectl port-forward -n online-boutique deployment/frontend 8081:8080
```

Abrir:

```text
http://localhost:8081
```

### Redis pierde datos

El Redis del despliegue base usa `emptyDir`, por lo que es efimero.

Esto es aceptable para demo. Para produccion, usa almacenamiento persistente o
un servicio administrado.

### Skaffold tarda demasiado

Es normal la primera vez. Construye varios lenguajes:

- Go
- C#
- Node.js
- Python
- Java

Opciones:

- Usa `release/kubernetes-manifests.yaml` para estudiar sin compilar.
- Aumenta recursos de Docker Desktop.
- Usa `skaffold dev` solo cuando ya vas a desarrollar.

## Ventajas que ofrece Kubernetes

### 1. Declaracion de estado

Tienes la infraestructura descrita en archivos YAML versionables.

```text
El repo no solo contiene codigo.
Tambien contiene como correr ese codigo.
```

### 2. Service discovery

Los servicios se llaman por nombre:

```text
cartservice:7070
redis-cart:6379
checkoutservice:5050
```

No necesitas perseguir IPs dinamicas.

### 3. Health checks

Kubernetes puede saber:

- Si un contenedor esta vivo.
- Si esta listo para recibir trafico.
- Si debe reiniciarse.

### 4. Reinicios automaticos

Si un contenedor falla, Kubernetes puede reiniciarlo.

### 5. Escalado

Puedes escalar un Deployment:

```powershell
kubectl scale deployment/frontend -n online-boutique --replicas=3
```

### 6. Rollouts y rollbacks

Kubernetes puede desplegar cambios de forma controlada.

```powershell
kubectl rollout status deployment/frontend -n online-boutique
kubectl rollout undo deployment/frontend -n online-boutique
```

### 7. Separacion entre interno y externo

No todo se expone al host.

```text
Externo:
  frontend-external

Interno:
  cartservice
  redis-cart
  paymentservice
  shippingservice
  emailservice
```

Esto reduce superficie de exposicion.

### 8. Paridad local-produccion

Puedes correr localmente en Docker Desktop y despues llevar conceptos similares
a GKE, AKS, EKS, Kind, Minikube u otro cluster.

### 9. Ecosistema

Este repo demuestra extensiones reales:

- Kustomize.
- Helm.
- Istio / service mesh.
- NetworkPolicies.
- Google Cloud Operations.
- Bases externas como Memorystore, Spanner y AlloyDB.

### 10. Mejor base para microservicios

Para una app con 11 microservicios, Kubernetes aporta orden:

- Contratos de red.
- Health checks.
- Configuracion por servicio.
- Aislamiento.
- Observabilidad potencial.
- Despliegues repetibles.

## Limitaciones y costos mentales

Kubernetes no es gratis en complejidad.

Costos:

- Mas conceptos que Docker Compose.
- Mas YAML.
- Mayor consumo de recursos local.
- Debugging distribuido.
- Hay que entender networking interno.

Para una app pequeña de un solo contenedor, podria ser demasiado. Para Online
Boutique, tiene sentido porque el sistema esta diseñado para mostrar
microservicios reales.

## Cheat sheet

### Contexto y cluster

```powershell
kubectl config get-contexts
kubectl config use-context docker-desktop
kubectl get nodes
```

### Deploy rapido

```powershell
kubectl create namespace online-boutique
kubectl apply -n online-boutique -f .\release\kubernetes-manifests.yaml
kubectl get pods -n online-boutique -w
```

### Abrir app

```powershell
kubectl port-forward -n online-boutique deployment/frontend 8080:8080
```

Abrir:

```text
http://localhost:8080
```

### Ver recursos

```powershell
kubectl get all -n online-boutique
kubectl get svc -n online-boutique
kubectl get deployments -n online-boutique
kubectl get pods -n online-boutique
```

### Debug

```powershell
kubectl describe pod -n online-boutique <pod-name>
kubectl logs -n online-boutique <pod-name>
kubectl get events -n online-boutique --sort-by=.lastTimestamp
```

### Rollout

```powershell
kubectl rollout status deployment/frontend -n online-boutique
kubectl rollout restart deployment/frontend -n online-boutique
```

### Escalar

```powershell
kubectl scale deployment/frontend -n online-boutique --replicas=2
```

### Limpiar

```powershell
kubectl delete namespace online-boutique
```

Si usaste Skaffold:

```powershell
skaffold delete
```

## Lectura sugerida de archivos del repo

Lee en este orden:

```text
1. README.md
2. docs/development-guide.md
3. kubernetes-manifests/README.md
4. release/kubernetes-manifests.yaml
5. kubernetes-manifests/frontend.yaml
6. kubernetes-manifests/cartservice.yaml
7. kubernetes-manifests/checkoutservice.yaml
8. skaffold.yaml
9. kustomize/README.md
```

Por que ese orden:

- `README.md` te da la arquitectura.
- `development-guide.md` te da el flujo local.
- `kubernetes-manifests/README.md` evita el error de aplicar manifiestos base
  sin Skaffold.
- `release/kubernetes-manifests.yaml` te muestra el despliegue listo.
- `frontend.yaml` enseña entrada, Services, probes y dependencias.
- `cartservice.yaml` enseña dependencia con Redis.
- `checkoutservice.yaml` enseña orquestacion de microservicios.
- `skaffold.yaml` enseña como se construyen imagenes.
- `kustomize/README.md` enseña variaciones.

## Mapa mental final

```text
Codigo fuente
  |
  +-- Dockerfile por microservicio
        |
        v
      Imagen Docker
        |
        v
Manifiestos Kubernetes
  |
  +-- Deployment: como correr Pods
  +-- Service: como encontrarlos
  +-- ServiceAccount: identidad
  +-- Probes: salud
  +-- Resources: CPU/memoria
        |
        v
Cluster Kubernetes en Docker Desktop
  |
  +-- frontend expuesto
  +-- servicios internos por DNS
  +-- Redis interno
  +-- health checks
  +-- reinicios automaticos
```

## Referencias

- Kubernetes Overview: https://kubernetes.io/docs/concepts/overview/
- Kubernetes Cluster Architecture: https://kubernetes.io/docs/concepts/architecture/
- Kubernetes Pods: https://kubernetes.io/docs/concepts/workloads/pods/
- Kubernetes Deployments: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- Kubernetes Services: https://kubernetes.io/docs/concepts/services-networking/service/
- Kubernetes Objects: https://kubernetes.io/docs/concepts/overview/working-with-objects/
- Docker Desktop Kubernetes: https://docs.docker.com/desktop/use-desktop/kubernetes/
- Docker Desktop Settings: https://docs.docker.com/desktop/settings-and-maintenance/settings/
- Skaffold: https://skaffold.dev/docs/
- Kustomize: https://kustomize.io/
- Helm: https://helm.sh/docs/
