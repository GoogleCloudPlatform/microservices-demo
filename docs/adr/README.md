# Decisiones — ADRs del proyecto

Registro de las decisiones arquitectónicas del proyecto, una por nota. Un **ADR** (*Architecture Decision Record*) captura **qué** se decidió, **por qué**, y **qué consecuencias** trae — incluidas las malas.

El razonamiento sale de la propuesta de proyecto del equipo, que se entrega por separado. Lo que aporta este formato es que cada decisión quede **en el repositorio**, encontrable, fechada y con estado propio.

## Las decisiones

| # | Decisión | Estado | Referencia |
|---|---|---|---|
| [0001](0001-github-flow-como-estrategia-de-ramificacion.md) | GitHub Flow como estrategia de ramificación | Aceptada | **estrategia-de-ramificacion** |
| [0002](0002-servicio-nuevo-en-lugar-de-extender-shippingservice.md) | Servicio nuevo en lugar de extender `shippingservice` | Aceptada | Propuesta §2.1 |
| [0003](0003-conservar-el-tracking-id-aleatorio.md) | Conservar el tracking ID aleatorio, solo persistirlo | Aceptada | Propuesta §2.2 |
| [0004](0004-redis-con-el-pedido-serializado-como-un-valor.md) | Redis, con el pedido serializado como un solo valor | Aceptada | Propuesta §2.3 |
| [0005](0005-estado-derivado-del-tiempo-no-almacenado.md) | El estado se deriva del tiempo, no se almacena | Aceptada | Propuesta §2.4 |
| [0006](0006-registro-sincrono-sin-cola-ni-eventos.md) | Registro síncrono desde `checkoutservice`, sin cola | Aceptada | Propuesta §2.6 |
| [0007](0007-componente-opcional-con-kill-switch.md) | Componente opcional con *kill switch* | Aceptada | Propuesta §2.8 |
| [0008](0008-despliegue-continuo-en-dos-fases.md) | Despliegue continuo en dos fases | Aceptada | **pipeline-de-despliegue-continuo** |
| [0009](0009-consulta-anonima-sin-autenticacion.md) | La consulta de seguimiento es anónima | Aceptada | Propuesta §1.3 |

## Las reglas

- **Una decisión, un archivo.** Si necesitas la palabra "y" para titularlo, probablemente son dos.
- **Numeración correlativa.** El número nunca se reusa, aunque el ADR quede reemplazado.
- **Los ADR no se editan.** Cuando una decisión cambia, se escribe uno nuevo que dice *"reemplaza al 000N"*, y el viejo pasa a estado **Reemplazada por 000M**. El rastro de cómo evolucionó el pensamiento es parte del valor.
- **Las consecuencias negativas son obligatorias.** Un ADR sin la sección de lo que se está pagando no sirve para nada.
- **Prueba para saber si algo merece ADR:** ¿había una alternativa real que alguien pudo haber elegido, y la elección tiene consecuencias que se van a sentir después? Si no, es detalle de implementación y va en el README.

## Plantilla

```markdown
# ADR 00NN — <la decisión, en una frase>

**Estado:** Propuesta | Aceptada | Reemplazada por 00MM · AAAA-MM-DD

## Contexto
La situación, las restricciones y las alternativas que se consideraron.

## Decisión
Qué se eligió, en voz activa.

## Consecuencias
+ Lo que se gana.
− Lo que se paga.

## Referencias
```

## Fechas

Reflejan **cuándo quedó registrada** la decisión, no necesariamente cuándo se discutió por primera vez. Los ADR 0001 a 0007 y el 0009 documentan decisiones que ya estaban tomadas en la **propuesta de proyecto**; el 0008 se registró junto con el diseño del pipeline.

## Páginas relacionadas

- **propuesta-de-proyecto** — la fuente del razonamiento de la mayoría de estos ADR
- **pipeline-de-despliegue-continuo** · **estrategia-de-rollback** · **observabilidad-y-slis** · **seguridad-en-el-pipeline**
- **portafolio-de-evidencias** — los ADR son evidencia de la etapa *Planear*
