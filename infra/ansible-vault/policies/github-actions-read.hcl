# Permite que GitHub Actions lea únicamente el secreto autorizado.
path "online-boutique/data/ci/github" {
  capabilities = ["read"]
}
