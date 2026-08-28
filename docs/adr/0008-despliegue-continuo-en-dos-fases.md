# ADR 0008 — Despliegue continuo en dos fases sobre el mismo workflow

**Estado:** Aceptada · 2026-08-27

## Contexto

La etapa *Desplegar* del ciclo DevOps se resolvía con "corremos Skaffold en la laptop", que es un desarrollador ejecutando un comando, no despliegue continuo. Es el corazón de lo que la materia evalúa.

Dos hallazgos delimitan el problema:

- Los workflows de despliegue heredados (`deploy-pr.yaml`, y el job `deployment-tests` de `ci-main.yaml`) apuntan a un proveedor de identidad y a un clúster de Google (`prs-gke-cluster`) que el equipo no controla, así que **fallan siempre tal como vienen**.
- Pero `ci-main.yaml` **no es inservible**: es una pipeline de CD completa. Lo único atado a Google son cinco valores.

Restricciones: la ventana de la prueba gratuita de Google Cloud es limitada, y activarla ahora para desplegar en noviembre la desperdicia.

## Decisión

**Cada integración a `main` despliega sola**, mediante un workflow propio (`cd-main.yaml`) construido en **dos fases sobre el mismo archivo**:

| | Fase A — ya | Fase B — cerca de la demo |
|---|---|---|
| Runner | Self-hosted en la máquina del equipo | `ubuntu-24.04` |
| Clúster | Docker Desktop local | GKE zonal, nodo spot |
| Registro | Ninguno | Artifact Registry |

Entre una y otra cambian el *runner* y cinco valores. Los pasos de despliegue, espera, verificación y rollback son idénticos.

Los workflows heredados **se desactivan pasándolos a `workflow_dispatch`, no se borran**: son la referencia de la que sale `cd-main.yaml`.

## Consecuencias

- **+** El proyecto tiene entrega continua real desde la primera semana, sin cuenta de nube y sin consumir crédito.
- **+** Cuando llegue la fase B, el pipeline ya estará probado. Migrar es cambiar configuración, no escribir un pipeline bajo presión.
- **+** En la fase A **no hace falta registro de imágenes**: Docker Desktop comparte su almacén con el clúster y Skaffold reconoce `docker-desktop` como clúster local.
- **+** Habilita el rollback automático y vuelve medibles tres de las cuatro métricas DORA.
- **+** Demuestra que el destino de despliegue es **configuración, no arquitectura**, que es un argumento fuerte para la materia.
- **−** Un *runner* self-hosted en un repositorio público es un riesgo real. Obliga a tres mitigaciones no negociables: disparo solo por `push` a `main`, Environment con revisor requerido y `permissions: contents: read`.
- **−** En la fase A no hay tienda si la máquina está apagada. La fase B lo resuelve.
- **−** El nodo *spot* de la fase B puede ser reclamado. Hay que recrearlo sin `--spot` la semana de la entrega.
- **−** Dependencia de la ventana de la prueba gratuita para la fase B.

## Referencias

Diseño del pipeline de despliegue continuo, la comparativa de nubes y la propuesta §3.5.
