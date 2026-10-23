#!/usr/bin/env bash
# =============================================================================
# Copia las credenciales TEMPORALES de AWS Academy a Vault.
#
# Las llaves del Learner Lab cambian en cada sesión. Antes había que editar a
# mano 3 secretos en GitHub; ahora se corre este script una vez por sesión y el
# pipeline las lee de Vault (única fuente de verdad).
#
# Uso (en WSL, con VAULT_ADDR, VAULT_CACERT y un token con permiso de escritura):
#   ./update-aws-creds.sh                       # lee ~/.aws/credentials de Windows
#   ./update-aws-creds.sh /ruta/a/credentials   # o de otra ruta
# =============================================================================
set -euo pipefail

: "${VAULT_ADDR:?Falta VAULT_ADDR}"
: "${VAULT_TOKEN:?Falta VAULT_TOKEN}"

WIN_USER="$(cmd.exe /c 'echo %USERNAME%' 2>/dev/null | tr -d '\r' || true)"
CRED_FILE="${1:-/mnt/c/Users/${WIN_USER}/.aws/credentials}"

[[ -f "$CRED_FILE" ]] || { echo "No encuentro $CRED_FILE"; exit 1; }

# Toma todo lo que está después del PRIMER "=" (los tokens de AWS pueden
# terminar en "=" y no deben recortarse).
get() {
  awk -v k="$1" '{
    line=$0; sub(/\r$/, "", line)
    i=index(line, "="); if (i==0) next
    key=substr(line, 1, i-1); gsub(/[ \t]/, "", key)
    if (key==k) { val=substr(line, i+1); gsub(/^[ \t]+|[ \t]+$/, "", val); print val; exit }
  }' "$CRED_FILE"
}

AKID="$(get aws_access_key_id)"
SECRET="$(get aws_secret_access_key)"
TOKEN="$(get aws_session_token)"

[[ -n "$AKID" && -n "$SECRET" && -n "$TOKEN" ]] || { echo "Faltan valores en $CRED_FILE"; exit 1; }

vault kv put kv/online-boutique/aws \
  access_key_id="$AKID" \
  secret_access_key="$SECRET" \
  session_token="$TOKEN" >/dev/null

echo "Credenciales de AWS actualizadas en kv/online-boutique/aws (llave ${AKID:0:8}...)."
