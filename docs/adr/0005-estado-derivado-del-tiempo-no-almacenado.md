# ADR 0005 — El estado del pedido se deriva del tiempo, no se almacena

**Estado:** Aceptada · 2026-08-25

## Contexto

El pedido debe recorrer los estados `CREADO → PAGADO → EN_PREPARACIÓN → EN_TRÁNSITO → ENTREGADO`. La pregunta real de diseño es **quién los hace avanzar**, porque en Online Boutique nadie envía nada de verdad: `shippingservice` no habla con ninguna paquetería.

Alternativas:

- Un proceso en segundo plano que actualice periódicamente los registros en Redis.
- Derivar el estado del tiempo transcurrido desde la compra, calculándolo al momento de la consulta.

## Decisión

**El estado se deriva del tiempo transcurrido desde la fecha de compra, y se calcula en el momento de la consulta.** No se almacena.

La duración de cada etapa es configurable por variable de entorno, de modo que en una demostración el pedido recorra el ciclo completo en minutos en lugar de días.

Consecuencia sobre el modelo de datos: el pedido se escribe **una sola vez** y nunca se modifica. Después del alta, el almacén es de solo lectura.

## Consecuencias

- **+** No agrega un proceso más que desplegar, vigilar y depurar.
- **+** Es una **función pura** de dos entradas —fecha de compra y momento actual—, así que se prueba unitariamente sin levantar Redis ni el clúster. Encaja directo en el CI heredado.
- **+** Sin escrituras en segundo plano no hay condiciones de carrera sobre el registro.
- **−** El estado no puede alterarse manualmente: no hay forma de marcar un pedido como cancelado o retrasado. Coherente con el alcance, que excluye cancelaciones.
- **−** **Con duraciones cortas, todo pedido viejo aparece como `ENTREGADO`.** Si la tienda queda accesible públicamente y alguien la revisa horas después, no verá progreso alguno. Hay que elegir duraciones acordes al modo de revisión, o mostrar la línea de tiempo con marcas de tiempo para que el avance se lea aunque ya haya terminado.

## Referencias

Propuesta de proyecto §2.4 y el flujo de usuario del seguimiento.
