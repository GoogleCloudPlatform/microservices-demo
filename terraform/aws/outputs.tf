output "productos_table_name" {
  value = aws_dynamodb_table.productos.name
}

output "api_url" {
  description = "URL publica del API Gateway. Ej: GET <api_url>/catalogo"
  value       = aws_apigatewayv2_stage.default.invoke_url
}
