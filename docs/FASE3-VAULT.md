# Fase III — Ciudadela DevSecOps: HashiCorp Vault + Ansible

Este documento explica la arquitectura y da las **instrucciones exactas** para
levantar el servidor de secretos de Online Boutique y conectarlo al pipeline.

## Arquitectura

```
                    VAULT_TOKEN (único secreto en GitHub, solo lectura)
GitHub Actions ───────────────────────────────────────────────► HashiCorp Vault
  (aws-ci.yml)  ◄─────── secretos en tiempo de ejecución ─────── EC2 t3.small + IP elástica
      │                                                          https://<IP>:8200  (TLS, UI)
      │ helm upgrade --set-string jwtSecret=...                  kv/online-boutique/app
      ▼                                                          kv/online-boutique/aws
Amazon EKS (accountservice, frontend, supportassistantservice)
                                                    ▲
Ansible (WSL) ── SSH :22 solo desde la IP del admin ┘  instala y configura Vault
Terraform (terraform-vault/) ── crea la EC2, el Security Group y la IP elástica
```

| Componente | Archivo | Función |
|---|---|---|
| Infraestructura de Vault | `terraform-vault/` | EC2 fuera del clúster, SG (8200 + 22 restringido), IP elástica, inventario de Ansible |
| Aprovisionamiento | `ansible/playbook.yml`, `ansible/roles/vault/` | Instala Vault, genera TLS, escribe `vault.hcl` (`ui = true`), levanta el servicio |
| Política ACL | `vault/policies/online-boutique-ci.hcl` | Solo **lectura** sobre `kv/data/online-boutique/*` |
| Configuración | `vault/scripts/configure-vault.sh` | Motor KV v2, auditoría, política, secretos y token del pipeline |
| Credenciales AWS | `vault/scripts/update-aws-creds.sh` | Copia las llaves temporales del Lab a Vault (1 vez por sesión) |
| Pipeline | `.github/workflows/aws-ci.yml` | Lee los secretos con `hashicorp/vault-action` |

### Inventario de secretos (antes → después)

| Secreto | Antes | Después |
|---|---|---|
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` | 3 GitHub Secrets editados a mano cada sesión | `kv/online-boutique/aws` |
| `JWT_SECRET` | GitHub Secret (y su valor copiado en notas en texto plano) | `kv/online-boutique/app` — **rotado** al migrar |
| `OPENAI_API_KEY` | GitHub Secret | `kv/online-boutique/app` |
| Secretos en GitHub | **5** | **3**: `VAULT_ADDR`, `VAULT_CA_CERT` (no son sensibles) y `VAULT_TOKEN` (solo lectura) |

---

## 0. Preparación (una sola vez, en WSL)

```bash
# Ansible, el CLI de Vault y jq
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install -y ansible vault jq

# Llave SSH del Lab: AWS Academy → AWS Details → SSH key → Download PEM
mkdir -p ~/.ssh
cp /mnt/c/Users/$(cmd.exe /c 'echo %USERNAME%' | tr -d '\r')/Downloads/labsuser.pem ~/.ssh/
chmod 400 ~/.ssh/labsuser.pem
```

> La llave se copia a la carpeta de Linux porque en `/mnt/c` no se pueden poner
> permisos `400` y SSH la rechazaría.

## 1. Crear el servidor (PowerShell, Terraform)

```powershell
cd "C:\Ultimo semestre\devops\online-boutique\terraform-vault"
$ip = (Invoke-RestMethod https://checkip.amazonaws.com).Trim()
terraform init
terraform apply -var "admin_cidr=$ip/32"
```

Al terminar imprime `vault_addr` y `ssh_command`, y genera `ansible/inventory.ini`.

## 2. Instalar Vault con Ansible (WSL)

```bash
cd "/mnt/c/Ultimo semestre/devops/online-boutique/ansible"
ansible-playbook -i inventory.ini playbook.yml
```

**Prueba de idempotencia:** córrelo una segunda vez; debe terminar con `changed=0`.

Abre la UI en el navegador: `https://<IP>:8200/ui`. El navegador avisará que el
certificado es autofirmado: *Avanzado → Continuar*.

### Prueba de fuego (hacerla ANTES de cargar secretos reales)

```powershell
cd "C:\Ultimo semestre\devops\online-boutique\terraform-vault"
terraform destroy -var "admin_cidr=$ip/32"
terraform apply   -var "admin_cidr=$ip/32"
```
```bash
ansible-playbook -i inventory.ini playbook.yml   # recrea todo desde cero
```

## 3. Inicializar y desprecintar (WSL)

```bash
export VAULT_ADDR="https://$(grep -m1 -oE '^[0-9.]+' inventory.ini):8200"
export VAULT_CACERT="$PWD/out/vault-ca.crt"

# 5 fragmentos de llave, se necesitan 3 para abrir (Shamir's Secret Sharing)
vault operator init -key-shares=5 -key-threshold=3 > ~/vault-init.txt
cat ~/vault-init.txt
```

> ⚠️ `~/vault-init.txt` contiene las llaves de desprecintado y el root token.
> **Nunca** lo subas al repositorio. Guarda una copia en un lugar seguro.

```bash
vault operator unseal    # pega la Unseal Key 1
vault operator unseal    # pega la Unseal Key 2
vault operator unseal    # pega la Unseal Key 3  → "Sealed: false"
export VAULT_TOKEN=$(grep 'Initial Root Token' ~/vault-init.txt | awk '{print $NF}')
```

## 4. Configurar Vault (WSL)

```bash
cd "/mnt/c/Ultimo semestre/devops/online-boutique"
bash vault/scripts/configure-vault.sh      # imprime el TOKEN del pipeline
bash vault/scripts/update-aws-creds.sh     # copia las llaves del Lab a Vault
```

## 5. Conectar GitHub Actions

En GitHub → Settings → Secrets and variables → Actions, crea:

| Secreto | Valor |
|---|---|
| `VAULT_ADDR` | `https://<IP>:8200` |
| `VAULT_TOKEN` | el token que imprimió `configure-vault.sh` |
| `VAULT_CA_CERT` | salida de `base64 -w0 ansible/out/vault-ca.crt` |

Cuando el pipeline corra en verde leyendo de Vault, **borra** los secretos
viejos: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`,
`JWT_SECRET` y `OPENAI_API_KEY`.

## 6. Rutina de cada sesión del Lab

Al terminar la sesión, AWS Academy **detiene** la EC2 y Vault se **sella** solo.
Al empezar una sesión nueva:

```bash
# 1) Start Lab y actualizar ~/.aws/credentials (como siempre)
# 2) Desprecintar Vault (3 de las 5 llaves)
vault operator unseal   # ×3
# 3) Llevar las credenciales nuevas a Vault
bash vault/scripts/update-aws-creds.sh
```

El `terraform destroy` del **clúster** (`terraform-aws/`) no toca Vault, porque
vive en otra carpeta con su propio estado.

## 7. Pruebas de resiliencia

| Prueba | Cómo provocarla | Resultado esperado | Cómo recuperar |
|---|---|---|---|
| Token revocado | `vault token revoke <VAULT_TOKEN>` | El paso "Leer secretos desde Vault" falla con `403 permission denied`; **no se despliega nada** | Crear token nuevo con `vault token create -policy=online-boutique-ci -ttl=720h` y actualizar el secreto |
| Política cambiada | Quitar `kv/data/online-boutique/*` de la política | `403` al leer; el deploy no corre | `vault policy write online-boutique-ci vault/policies/online-boutique-ci.hcl` |
| Vault sellado | `vault operator seal` | `503 Vault is sealed`; el pipeline se detiene antes de tocar EKS | `vault operator unseal` ×3 |
| Escritura con el token del pipeline | `VAULT_TOKEN=<token CI> vault kv put kv/online-boutique/app x=1` | `permission denied` (solo lectura) | — |
| Ruta fuera de la política | `VAULT_TOKEN=<token CI> vault kv get kv/otra-app/secreto` | `permission denied` (menor privilegio) | — |

En todos los casos la tienda **sigue funcionando** con la última versión
desplegada: un fallo de Vault bloquea despliegues nuevos, no la aplicación.

## 8. Auditoría

```bash
ssh -i ~/.ssh/labsuser.pem ubuntu@<IP> \
  "sudo tail -n 5 /var/log/vault/vault_audit.log | jq '{time, type, path: .request.path, policies: .auth.policies}'"
```

Cada lectura del pipeline queda registrada con la hora, la ruta y la política usada.
