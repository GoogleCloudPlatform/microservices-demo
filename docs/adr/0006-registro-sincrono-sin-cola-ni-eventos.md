# ADR 0006 — Registro síncrono desde checkoutservice, sin cola ni eventos

**Estado:** Aceptada · 2026-08-25

## Contexto

`checkoutservice` debe registrar el pedido en `orderservice` al completar la compra. Hoy `PlaceOrder` arma un `OrderResult`, lo manda por correo, lo devuelve y lo olvida (`src/checkoutservice/main.go:265`).

Alternativas para el registro:

- **Publicar un evento** en una cola o *broker*, que `orderservice` consuma de forma asíncrona.
- **Llamada gRPC síncrona** desde `checkoutservice`, como las otras seis que ya hace.

La primera da entrega garantizada; la segunda no introduce infraestructura nueva.

## Decisión

**Una sola llamada gRPC síncrona nueva en `PlaceOrder`**, justo después de armar el `OrderResult` y antes de responder.

El registro **no puede tumbar la compra**: se intenta con un tiempo límite corto y hasta **tres intentos con espera incremental**, únicamente ante errores transitorios. `RecordOrder` es **idempotente por número de rastreo**, así que repetir la llamada no crea pedidos duplicados.

Si `orderservice` sigue sin responder, se deja una advertencia estructurada en el log, una métrica y el error en la traza; después la compra se completa igual. Es el mismo criterio que el repositorio aplica al correo de confirmación: una función secundaria no debe provocar que el cliente repita una compra que ya pudo haber sido cobrada.

## Consecuencias

- **+** No agrega *broker*, cola ni consumidor: ninguna pieza de infraestructura nueva que desplegar y mantener.
- **+** Sigue el patrón que `checkoutservice` ya usa con sus otras seis dependencias — nada nuevo que aprender.
- **+** El fallo queda observable en log, métrica y traza, en lugar de desaparecer.
- **−** **Si los tres intentos fallan, ese pedido no podrá rastrearse nunca.** No hay cola ni *outbox* que lo recupere. La garantía de "pedido recuperable" aplica a la operación normal, no a la degradada.
- **−** Es una falla **silenciosa para el cliente**: la compra se completa sin avisar que el rastreo no va a funcionar. Por eso el SLI de tasa de registro del **plan de observabilidad** es el más importante de los cuatro: es lo único que vuelve visible esta limitación.
- **−** Agrega latencia al checkout en el peor caso (tiempo límite × 3 intentos). Hay que dimensionar el límite para que no se note.

Si el SLI de registro baja del objetivo, la evolución prevista es un *outbox* — y sería un ADR nuevo que reemplace a este.

## Referencias

Propuesta de proyecto §2.6 y el plan de observabilidad y SLIs.
