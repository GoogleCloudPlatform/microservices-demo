# ADR 0004 — Redis, con el pedido serializado como un solo valor

**Estado:** Aceptada · 2026-08-25

## Contexto

`orderservice` necesita guardar pedidos. El patrón de acceso es uno solo: *"dame el pedido con este número de rastreo"*. No hay listados, ni búsquedas por otro campo, ni reportes.

Alternativas: una base relacional (PostgreSQL, Cloud SQL), un almacén de documentos, o Redis.

El repositorio impone además una restricción dura en `docs/product-requirements.md`: el despliegue por defecto debe funcionar en un clúster local sin nube y sin agregar pasos al *quickstart*.

## Decisión

Se despliega una instancia de **Redis dedicada (`redis-orders`)**, replicando lo que `kustomize/base/cartservice.yaml` hace con `redis-cart`: imagen `redis:alpine`, volumen `emptyDir`, servicio interno del clúster.

**El pedido completo se serializa y se guarda como un solo valor**, bajo la llave del número de rastreo:

```
llave:  "OS-4A9F21"
valor:  { order_id, tracking_id, fecha_compra,
          shipping_address, shipping_cost,
          items: [ { product_id, cantidad, costo }, ... ] }
```

Los artículos viven **dentro** del pedido, no en registros aparte. Una escritura al comprar, una lectura al consultar, cero uniones.

**Los nombres e imágenes de producto no se guardan:** se resuelven contra `productcatalogservice` al pintar la pantalla, igual que ya hace la vista del carrito (`src/frontend/handlers.go:285`).

## Consecuencias

- **+** Redis ya está en el repositorio: no introduce tecnología ni pasos nuevos.
- **+** El acceso por llave directa es exactamente para lo que Redis sirve.
- **+** Corre gratis en local; no exige Cloud SQL, Spanner ni AlloyDB.
- **+** No se duplican datos que son propiedad de `productcatalogservice`, así que un cambio de catálogo no deja el pedido mostrando información obsoleta.
- **−** **`emptyDir` no sobrevive a la eliminación o recreación del pod.** Los pedidos se pierden. Es aceptable porque la demostración ocurre dentro de una sesión, pero no se presenta como almacenamiento duradero.
- **−** La pantalla de rastreo depende de `productcatalogservice` en tiempo de lectura. Si un producto desapareciera del catálogo, hay que degradar mostrando el `product_id` en lugar de fallar.
- **−** No hay consultas por otro campo. Un "mis pedidos" futuro exigiría un índice adicional o cambiar de almacén.

Si una fase posterior exige durabilidad, la evolución prevista es sustituir `emptyDir` por un volumen persistente o un almacén gestionado.

## Referencias

Propuesta de proyecto §2.3 y §2.3.1.
