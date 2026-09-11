# Módulo: Catálogo de productos.
# Terraform solo define la llave primaria de la tabla; el resto de los
# atributos (nombre, precio, descripción, variantes, etc.) los define el
# código de la Lambda al leer/escribir items, no el esquema de la tabla.
resource "aws_dynamodb_table" "productos" {
  name         = "${var.project_name}-productos"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "product_id"

  attribute {
    name = "product_id"
    type = "S"
  }
}
