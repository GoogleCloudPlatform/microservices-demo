# =============================================================================
# Política ACL: online-boutique-ci
#
# Principio de menor privilegio: el pipeline de GitHub Actions SOLO puede LEER
# los secretos de Online Boutique. No puede escribirlos, borrarlos, listar otras
# rutas ni administrar Vault.
# =============================================================================

# Leer los secretos de la aplicación y las credenciales de AWS del pipeline.
path "kv/data/online-boutique/*" {
  capabilities = ["read"]
}

# Permite que el token consulte su propia información (vigencia, políticas).
path "auth/token/lookup-self" {
  capabilities = ["read"]
}
