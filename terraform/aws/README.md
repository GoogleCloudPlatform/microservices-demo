# Infraestructura AWS (Learner Lab) — Módulo 0

Esta carpeta es independiente del `terraform/` de la raíz (ese es de Google
Cloud / GKE). Aquí vive la infraestructura serverless para los backends del
Admin Panel (catálogo, inventario, pedidos), pensada para correr dentro de un
**AWS Academy Learner Lab**.

## Por qué hay una carpeta `bootstrap/`

Terraform necesita guardar su "state" (qué recursos ya creó) en algún lado
que no desaparezca entre sesiones. Usamos un bucket S3 para eso. Pero ese
bucket también es un recurso de Terraform — y no puede guardar su propio
state en un bucket que todavía no existe. Por eso `bootstrap/` se corre una
sola vez, por separado, con state local, y crea el bucket que usará todo lo
demás.

## Paso 1: crear el bucket de state (una sola vez)

1. Inicia el Learner Lab ("Iniciar") y copia las 3 credenciales de "AWS Details".
2. Expórtalas en tu terminal:
   ```sh
   export AWS_ACCESS_KEY_ID="..."
   export AWS_SECRET_ACCESS_KEY="..."
   export AWS_SESSION_TOKEN="..."
   ```
3. Copia el archivo de variables de ejemplo y pon un nombre de bucket único:
   ```sh
   cd terraform/aws/bootstrap
   cp terraform.tfvars.example terraform.tfvars
   # edita terraform.tfvars y cambia el nombre del bucket
   ```
4. Aplica:
   ```sh
   terraform init
   terraform apply
   ```
5. Anota el valor de `state_bucket_name` que imprime al final — lo necesitas en el paso 2.

Este paso normalmente solo se hace una vez en la vida del proyecto (o si el bucket se borra).

## Paso 2: desplegar el stack principal (catálogo, y luego inventario/pedidos)

Cada vez que quieras aplicar cambios (con una sesión del Lab activa y credenciales frescas):

```sh
cd terraform/aws
terraform init -backend-config="bucket=<el-nombre-del-paso-1>"
terraform plan
terraform apply
```

Una vez aplicado, la tabla DynamoDB, la Lambda y el API Gateway quedan creados
y disponibles — siguen existiendo aunque cierres el Learner Lab. Solo
necesitas sesión activa para volver a correr `terraform apply` (es decir,
para desplegar cambios nuevos).

Al final del `apply` vas a ver un output `api_url`. Pruébalo así (sirve
aunque el Lab ya esté cerrado):

```sh
curl <api_url>/catalogo
```

Debería responder algo como:
```json
{"mensaje": "Hola desde el backend de catalogo", "productos_en_tabla": 0}
```

## Paso 3: dejar que GitHub Actions lo haga por ti

El workflow `.github/workflows/deploy-aws-backend.yaml` corre `terraform
apply` automáticamente en cada push a `main` que toque `terraform/aws/**`.
Para que funcione, hay que definir estos secrets en el repo (Settings >
Secrets and variables > Actions):

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` — las 3
  credenciales de "AWS Details". Hay que **actualizarlas cada vez que
  reinicias la sesión del Lab**, si no, el workflow falla al autenticarse
  (pero lo que ya está desplegado sigue funcionando igual).
- `TF_STATE_BUCKET` — el nombre del bucket del Paso 1. Este **no cambia**,
  se define una sola vez.

Forma rápida de actualizar los 3 secrets que cambian, con GitHub CLI en vez
de la interfaz web:
```sh
gh secret set AWS_ACCESS_KEY_ID --body "..."
gh secret set AWS_SECRET_ACCESS_KEY --body "..."
gh secret set AWS_SESSION_TOKEN --body "..."
```
