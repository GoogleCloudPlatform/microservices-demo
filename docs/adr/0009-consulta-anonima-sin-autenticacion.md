# ADR 0009 — La consulta de seguimiento es anónima

**Estado:** Aceptada · 2026-08-25

## Contexto

Consultar un pedido exige decidir quién puede verlo. Online Boutique **no tiene login real**: usa una *cookie* de sesión anónima, y no existe entidad de usuario en ningún servicio.

Alternativas: construir identidad de usuario (fuera de proporción para el alcance), atar la consulta a la cookie de sesión, o permitir la consulta a quien tenga el número de rastreo.

Atar la consulta a la cookie rompería el escenario central de la demostración: hacer un pedido en una computadora, copiar el número, y consultarlo desde otro dispositivo.

## Decisión

**La consulta es anónima: quien tenga el número de rastreo, ve el pedido.** No requiere sesión, cookie ni haber comprado.

Es el mismo modelo que usa el rastreo de cualquier paquetería real: el número se comparte con quien uno quiera.

Queda explícitamente fuera del alcance el historial "mis pedidos" por usuario, que sí dependería de identidad.

## Consecuencias

- **+** Habilita el escenario de la demostración —otra persona, otro dispositivo, otra red— sin construir autenticación.
- **+** Mantiene el alcance acotado a lo que cabe en el semestre.
- **+** Es coherente con cómo funciona el rastreo en el mundo real.
- **−** **Los pedidos son enumerables.** Combinado con el formato de baja entropía del [ADR 0003](0003-conservar-el-tracking-id-aleatorio.md), un tercero podría adivinar números y ver pedidos ajenos.
- **−** Mitigación adoptada: **la pantalla de seguimiento no muestra dirección, correo ni datos personales** — solo estado, artículos y fecha. Conviene además que la respuesta del RPC de consulta tampoco los devuelva, no solo que la vista no los pinte.
- **−** En un producto real esto exigiría un identificador de alta entropía y limitación de intentos. Se declara como limitación aceptada de la demostración, no como diseño recomendable.

## Referencias

Propuesta de proyecto §1.3, el flujo de usuario y los mockups del frontend.
