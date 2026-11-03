output "vault_instance_id" {
  description = "Identificador de la instancia EC2 de Vault"
  value       = aws_instance.vault.id
}

output "vault_public_ip" {
  description = "Dirección IP pública del servidor de Vault"
  value       = aws_instance.vault.public_ip
}

output "vault_security_group_id" {
  description = "Identificador del Security Group de Vault"
  value       = aws_security_group.vault.id
}

output "vault_ui_url" {
  description = "Dirección futura de la interfaz web de Vault"
  value       = "http://${aws_instance.vault.public_ip}:8200/ui"
}

output "ssh_connection" {
  description = "Comando base para conectarse a la instancia"
  value       = "ssh -i RUTA_DE_LA_LLAVE ubuntu@${aws_instance.vault.public_ip}"
}
