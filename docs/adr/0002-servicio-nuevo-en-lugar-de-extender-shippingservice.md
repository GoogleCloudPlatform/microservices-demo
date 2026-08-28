# ADR 0002 — Servicio nuevo en lugar de extender shippingservice

**Estado:** Aceptada · 2026-08-25

## Contexto

El seguimiento de pedidos necesita persistir los pedidos y consultarlos por número de rastreo. `shippingservice` ya genera ese número (`src/shippingservice/tracker.go`), así que agregarle ahí la persistencia y la consulta parecía la opción de menor esfuerzo.

## Decisión

Se crea un microservicio nuevo, **`orderservice`**, en Go, en lugar de extender `shippingservice`.

Razones:

- **Responsabilidad distinta.** `shippingservice` cotiza y despacha; guardar el historial de pedidos es otra cosa. Mezclarlas produce el acoplamiento que una arquitectura de microservicios existe para evitar.
- **Estado.** `shippingservice` hoy no tiene estado. Convertirlo en un servicio con estado cambia su naturaleza operativa: pasa a necesitar respaldo, arranque ordenado y una dependencia externa.
- **Valor para la materia.** Un servicio nuevo obliga a recorrer los 8 pasos de `docs/adding-new-microservice.md` — imagen, manifiestos, Skaffold, Helm, documentación. Una extensión no construye ninguna pieza de despliegue nueva, que es justo lo que el proyecto evalúa.

El repositorio ya trae el molde: `shoppingassistantservice` es un servicio agregado después del diseño original y entregado como componente opcional. Se sigue ese patrón.

## Consecuencias

- **+** Separación de responsabilidades clara; `shippingservice` se mantiene sin estado.
- **+** Ejercita el ciclo DevOps completo, que es el objetivo real del proyecto.
- **+** Hay un ejemplo dentro del propio repositorio a copiar en lugar de inventar convenciones.
- **−** Un servicio más que construir, desplegar, observar y mantener.
- **−** Un salto de red adicional en el camino del checkout, con su latencia y su modo de falla — que es lo que obliga al [ADR 0006](0006-registro-sincrono-sin-cola-ni-eventos.md).

## Referencias

Propuesta de proyecto §2.1 y el análisis del feature.
