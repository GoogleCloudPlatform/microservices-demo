# ADR 0003 — Conservar el tracking ID aleatorio, solo persistirlo

**Estado:** Aceptada · 2026-08-25

## Contexto

`CreateTrackingId` en `src/shippingservice/tracker.go` arma el número de rastreo con `math/rand` y no lo guarda en ningún lado. La lectura inicial fue que "el número es falso" y que había que rediseñarlo — por ejemplo derivándolo del `order_id`, o moviendo su generación a otro servicio.

Eso habría implicado modificar `ShipOrder` y `ShipOrderResponse`, es decir, tocar un contrato gRPC que consumen servicios que nadie más va a editar.

## Decisión

**El número de rastreo se conserva aleatorio.** Lo que cambia es que ahora se persiste.

`shippingservice` sigue generándolo exactamente igual que hoy; `checkoutservice` lo recibe y se lo entrega a `orderservice` junto con el resto del pedido, que lo usa como llave de consulta.

**No se modifican `ShipOrder` ni `ShipOrderResponse`.**

## Consecuencias

- **+** El defecto real nunca fue la aleatoriedad sino la ausencia de persistencia. Un identificador aleatorio persistido es una llave de consulta perfectamente válida.
- **+** El contrato existente queda intacto y el radio de impacto del cambio se reduce al mínimo: se agrega un servicio al proto, no se modifica ninguno.
- **+** `shippingservice` no se toca en absoluto.
- **−** El formato tiene **poca entropía** (`XX-NDDD-NDDDDDDD`), así que los números son adivinables. Combinado con el [ADR 0009](0009-consulta-anonima-sin-autenticacion.md), eso significa que un tercero podría enumerar pedidos. Se acepta para la demostración y se mitiga no devolviendo datos personales en la consulta.
- **−** No hay garantía formal de unicidad. Con el volumen de una demo el riesgo de colisión es despreciable, pero existe.

## Referencias

Propuesta de proyecto §2.2.
