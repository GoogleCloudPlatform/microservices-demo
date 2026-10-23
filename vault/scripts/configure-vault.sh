#!/usr/bin/env bash
# =============================================================================
# Configura Vault para Online Boutique (Fase III - Semana 3). Se corre UNA vez,
# después de `vault operator init` y `vault operator unseal`.
#
#   1. Habilita el motor KV v2 en la ruta kv/
#   2. Habilita el registro de auditoría
#   3. Carga la política de solo lectura online-boutique-ci
#   4. Guarda los secretos de la aplicación (con un JWT_SECRET NUEVO)
#   5. Crea el token único para GitHub Actions
#
# Requisitos (en WSL):
#   export VAULT_ADDR=https://<IP>:8200
#   export VAULT_CACERT=<ruta>/ansible/out/vault-ca.crt
#   export VAULT_TOKEN=<root token del init>
#
# Es seguro correrlo otra vez: no duplica nada, salvo que crea un token nuevo.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
POLICY_FILE="$SCRIPT_DIR/../policies/online-boutique-ci.hcl"

: "${VAULT_ADDR:?Falta VAULT_ADDR}"
: "${VAULT_TOKEN:?Falta VAULT_TOKEN (root token)}"

echo "==> Estado de Vault"
vault status

echo "==> 1. Motor KV v2 en kv/"
if vault secrets list -format=json | jq -e '."kv/"' >/dev/null; then
  echo "    ya estaba habilitado"
else
  vault secrets enable -path=kv -version=2 kv
fi

echo "==> 2. Auditoría (quién leyó qué y cuándo)"
if vault audit list -format=json 2>/dev/null | jq -e '."file/"' >/dev/null; then
  echo "    ya estaba habilitada"
else
  vault audit enable file file_path=/var/log/vault/vault_audit.log
fi

echo "==> 3. Política online-boutique-ci (solo lectura)"
vault policy write online-boutique-ci "$POLICY_FILE"

echo "==> 4. Secretos de la aplicación"
if vault kv get kv/online-boutique/app >/dev/null 2>&1; then
  echo "    kv/online-boutique/app ya existe; no se sobrescribe."
  echo "    (para rotar el JWT: vault kv patch kv/online-boutique/app jwt_secret=\$(openssl rand -hex 32))"
else
  # Se ROTA el JWT: el valor anterior quedó expuesto en notas en texto plano.
  vault kv put kv/online-boutique/app \
    jwt_secret="$(openssl rand -hex 32)" \
    openai_api_key="sin-configurar"
  echo "    creado con un JWT_SECRET nuevo y aleatorio"
fi

echo "==> 5. Token para GitHub Actions"
vault token create \
  -policy=online-boutique-ci \
  -display-name=github-actions \
  -ttl=720h \
  -renewable=true \
  -format=json | jq -r '"\n    TOKEN (guárdalo como secreto VAULT_TOKEN en GitHub):\n    " + .auth.client_token + "\n    vigencia: " + (.auth.lease_duration|tostring) + " s"'

echo
echo "Listo. Falta cargar las credenciales de AWS con: ./update-aws-creds.sh"
