# ADR 0007 — Entrega como componente opcional con kill switch

**Estado:** Aceptada · 2026-08-25

## Contexto

`docs/product-requirements.md` exige que todo cambio preserve el despliegue por defecto sobre un clúster local, no complique el recorrido de demostración y no agregue pasos obligatorios al *quickstart*. Textualmente, las extensiones "deberían agregarse como un Kustomize Component al que los usuarios opten por entrar".

Además, el proyecto necesita poder desplegar las **dos variantes** —con y sin el feature— para verificar el criterio de aceptación #8.

## Decisión

La funcionalidad completa vive en `kustomize/components/order-tracking/`, siguiendo la estructura de `kustomize/components/shopping-assistant/`. **Nada se agrega a `kustomize/base/`.**

El componente hace dos cosas:

1. Aporta los recursos nuevos: `orderservice` y `redis-orders`.
2. **Parcha los Deployments de `frontend` y `checkoutservice`** inyectando `ENABLE_ORDER_TRACKING=true` y `ORDER_SERVICE_ADDR`.

La variable la lee el código al arrancar, igual que `ENABLE_ASSISTANT` en `src/frontend/handlers.go:48`. Sin ella, el frontend no registra las rutas y `checkoutservice` no crea el cliente gRPC.

En Helm, la misma regla con `orderTracking.enabled: false` por defecto.

Para el ciclo de desarrollo se agrega un **perfil de Skaffold** llamado `order-tracking`, siguiendo el patrón del perfil `network-policies` que ya existe: `skaffold run` levanta la tienda limpia, `skaffold run -p order-tracking` la levanta con el feature.

## Consecuencias

- **+** Cumple el requisito de producto del repositorio base sin discusión.
- **+** El criterio de aceptación #8 es verificable: `kubectl apply -k .` sin el componente despliega la tienda exactamente igual que hoy.
- **+** **El mecanismo es además un interruptor de emergencia en producción.** Como la variable vive en el Deployment, un `kubectl set env` dispara un *rolling restart* y en ~30 segundos la tienda vuelve al comportamiento base — sin revertir un commit, sin reconstruir imágenes y sin redesplegar. Es el nivel 1 de **estrategia-de-rollback**.
- **+** El interruptor existe también en el ciclo de desarrollo y en el pipeline, no solo en el despliegue final.
- **−** Hay **dos rutas de manifiestos** en el repositorio (`kustomize/` para `kubectl apply -k`, `kubernetes-manifests/` para Skaffold) y el componente hay que conectarlo a las dos. Es la trampa que documenta la §2.8.1 de la propuesta.
- **−** El código de `frontend` y `checkoutservice` queda con ramas condicionales que hay que probar en los dos estados.
- **−** Apagar el feature con `kubectl set env` deja el clúster distinto de lo que dice `main`: crea deriva de configuración, y obliga a seguirlo siempre con un PR de reversión.

## Referencias

Propuesta de proyecto §2.8 y §2.8.1, y la estrategia de rollback.
