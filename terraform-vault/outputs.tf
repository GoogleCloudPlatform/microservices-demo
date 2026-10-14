output "vault_public_ip" {
  description = "IP elástica (fija) del servidor de Vault."
  value       = aws_eip.vault.public_ip
}

output "vault_addr" {
  description = "Dirección de la API y la UI web de Vault."
  value       = "https://${aws_eip.vault.public_ip}:8200"
}

output "ssh_command" {
  description = "Comando para entrar al servidor desde WSL."
  value       = "ssh -i ~/.ssh/labsuser.pem ubuntu@${aws_eip.vault.public_ip}"
}
