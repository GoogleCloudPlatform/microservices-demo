# ADR 0010 — La fase B se despliega en AWS, con k3s sobre EC2

**Estado:** Aceptada · 2026-09-10 · reemplaza la **fase B** del [ADR 0008](0008-despliegue-continuo-en-dos-fases.md)

## Contexto

El ADR 0008 dejó el despliegue continuo construido en dos fases sobre un mismo workflow, y fijó GKE como destino de la fase B. Esa elección salió de una comparativa técnica de GKE, AKS y AWS que colocaba a AWS en último lugar por tres razones: el control plane de EKS cuesta alrededor de 73 USD/mes y ningún *free tier* lo cubre, las cuentas de AWS Academy imponen restricciones fuertes, y las instancias baratas de AWS son ARM mientras que las imágenes de Online Boutique son solo `amd64`.

**La institución otorgó acceso a AWS Academy y es el entorno en el que hay que trabajar.** El proveedor deja de ser resultado de la comparativa y pasa a ser una restricción del proyecto. La comparativa no se invalida — describe correctamente por qué AWS era la peor opción *cuando se podía elegir* — pero ya no es la que decide.

Con el proveedor fijo, la pregunta que queda es **qué forma toma Kubernetes dentro de AWS**:

- **EKS** arrastra el costo de control plane que la comparativa señaló, y en un entorno de AWS Academy la creación de proveedores de identidad OIDC de IAM suele estar bloqueada, lo que impide la autenticación federada desde GitHub Actions.
- **k3s sobre una instancia EC2** conserva los manifiestos de Kubernetes, el componente de Kustomize y las plantillas de Helm — que son el entregable — a cambio de operar el control plane nosotros.

Se suma una restricción de la propia rúbrica de la fase 2: la construcción de la infraestructura **en Terraform** es un criterio evaluado por sí solo. El plan de GKE creaba el clúster con comandos `gcloud` ejecutados a mano, de modo que ese criterio se quedaba sin contenido real.

## Decisión

**La fase B se despliega en AWS, sobre un clúster k3s que corre en una instancia EC2 `x86_64`, provisionada íntegramente con Terraform.**

| | Fase A — ya | Fase B — AWS |
|---|---|---|
| Runner | Self-hosted en la máquina del equipo | `ubuntu-24.04` |
| Clúster | Docker Desktop local | k3s sobre EC2 `x86_64` |
| Registro | Ninguno | GitHub Container Registry (`ghcr.io`) |
| Infraestructura | Ninguna | Terraform, con estado remoto en S3 |

Tres precisiones que sostienen la decisión:

- **La instancia es `x86_64`, no Graviton.** Las imágenes de Online Boutique no tienen variante ARM. Es una línea de Terraform, pero equivocarla rompe los doce pods.
- **Las imágenes se publican en `ghcr.io`, no en ECR.** Las credenciales de AWS Academy rotan en cada sesión — clave, secreto y *session token* —, así que un secreto de GitHub Actions apuntando a ECR caduca cada pocas horas y hay que rotarlo a mano. `ghcr.io` se autentica con el `GITHUB_TOKEN` del propio workflow. El criterio de la rúbrica es construir las imágenes en CI; no exige un registro determinado.
- **`cd-main.yaml` no se reescribe.** Cambian el `runs-on`, la obtención del *kubeconfig* y el `--default-repo`. Los pasos de espera, los smoke tests y el rollback no cambian, que es exactamente lo que el ADR 0008 predijo que pasaría al cambiar de destino.

## Consecuencias

- **+** El criterio de infraestructura en Terraform pasa a tener contenido real: VPC, grupo de seguridad, instancia, IP elástica y arranque de k3s quedan descritos como código, no como comandos escritos a mano una vez.
- **+** Los manifiestos de Kubernetes, el componente de Kustomize y las plantillas de Helm siguen sirviendo sin cambios. k3s es Kubernetes conforme.
- **+** El registro de imágenes queda desacoplado del proveedor de nube, así que las credenciales rotatorias del entorno académico dejan de tocar la construcción.
- **+** Se confirma la tesis del ADR 0008 con un caso más duro: el destino de despliegue cambió de proveedor, y los pasos de despliegue, verificación y rollback siguieron intactos.
- **−** **Se pierde Kubernetes gestionado.** El control plane lo operamos nosotros: si k3s se cae, no hay proveedor que lo levante.
- **−** **Un solo nodo es un único punto de falla**, y sin `cluster-autoscaler` ni tolerancia a fallos. Aceptable en una tienda de demostración, inaceptable en producción, y así hay que declararlo.
- **−** **El temporizador de sesión del entorno académico rompe la disponibilidad permanente.** El criterio de aceptación 7 de la propuesta —que alguien externo consulte un pedido desde otra red— pasa a cumplirse solo durante una sesión activa. Es una degradación real frente a lo que prometía la fase B con GKE, y se reencuadra en la propuesta en lugar de darse por cumplida.
- **−** El dimensionamiento de la instancia depende de qué tamaños permite el entorno. Online Boutique pide del orden de 4 vCPU y 8–16 GB para sus doce pods; si el límite es menor, hay que reducir los `resources.requests` o desplegar sin `loadgenerator`, y sin `loadgenerator` los dos smoke tests dejan de funcionar.
- **−** La comparativa de nubes queda como registro de una decisión que las circunstancias revirtieron. Se conserva: explica por qué esta configuración tiene las asperezas que tiene.

## Referencias

[ADR 0008](0008-despliegue-continuo-en-dos-fases.md) — el diseño en dos fases cuya fase B reemplaza este ADR · [`docs/despliegue-continuo.md`](../despliegue-continuo.md) · la comparativa de opciones de despliegue en la nube y la propuesta §3.5
