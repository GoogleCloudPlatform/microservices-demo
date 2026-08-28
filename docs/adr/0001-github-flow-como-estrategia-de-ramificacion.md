# ADR 0001 — GitHub Flow como estrategia de ramificación

**Estado:** Aceptada · 2026-08-25

## Contexto

El proyecto necesita una estrategia de ramificación, y es un criterio evaluado por sí solo (25 puntos). Las condiciones reales son:

- Equipo de **dos personas**, sin roles separados de desarrollo y operación.
- Entregas **por fases**, no por versiones de producto.
- El repositorio base ya trae automatización de construcción y despliegue, que exige una rama principal sana.
- No hay ambientes múltiples: no existe *staging* propio ni versiones soportadas en paralelo.

Alternativas consideradas:

| Estrategia | Por qué se descarta |
|---|---|
| **GitFlow** | Ramas `develop`, `release` y `hotfix` para un equipo de dos personas sin versiones soportadas en paralelo. Sobrecarga de ceremonia sin problema que resuelva |
| **Trunk-Based Development** | Depende de *feature flags* y de una suite de pruebas madura para integrar directo a `main`. El repositorio no la tiene y el equipo no puede construirla en un semestre |
| **GitLab Flow** | Introduce ramas por ambiente. El proyecto tiene un solo ambiente |

## Decisión

Se adopta **GitHub Flow**: `main` siempre desplegable, ramas de vida corta con prefijo (`feature/`, `fix/`, `docs/`, `chore/`), e integración exclusivamente por Pull Request revisado por el otro integrante.

La regla se hace cumplir por la plataforma, no por disciplina: protección de rama sobre `main` exigiendo Pull Request y al menos una aprobación.

## Consecuencias

- **+** Es la estrategia más simple que satisface la condición que la automatización necesita: una rama principal siempre sana.
- **+** El Pull Request genera documentación del proceso de forma automática — evidencia sin trabajo adicional.
- **+** Habilita el despliegue continuo del [ADR 0008](0008-despliegue-continuo-en-dos-fases.md): si `main` siempre está desplegable, cada merge puede desplegar.
- **−** Con dos personas, **el autor no puede aprobar su propio Pull Request**. Ambos integrantes deben tener permiso de escritura en el fork o el flujo se bloquea.
- **−** Sin ramas de release, no hay forma de sostener dos versiones a la vez. No se necesita hoy; sería un problema si el proyecto continuara después del semestre.

## Referencias

Estrategia de ramificación del equipo (GitHub Flow) y la actividad de la materia.
