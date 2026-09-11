# En Learner Lab no se pueden crear roles IAM nuevos: reusamos el rol que
# ya existe en la cuenta (LabRole) como identidad de ejecución de la Lambda.
data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

data "archive_file" "catalogo_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_src/catalogo"
  output_path = "${path.module}/lambda_src/catalogo.zip"
}

resource "aws_lambda_function" "catalogo" {
  function_name    = "${var.project_name}-catalogo"
  filename         = data.archive_file.catalogo_lambda.output_path
  source_code_hash = data.archive_file.catalogo_lambda.output_base64sha256
  handler          = "handler.lambda_handler"
  runtime          = "python3.13"
  role             = data.aws_iam_role.lab_role.arn
  timeout          = 10

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.productos.name
    }
  }
}

resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "catalogo" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.catalogo.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "catalogo_root" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /catalogo"
  target    = "integrations/${aws_apigatewayv2_integration.catalogo.id}"
}

resource "aws_lambda_permission" "apigw_catalogo" {
  statement_id  = "AllowAPIGatewayInvokeCatalogo"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.catalogo.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
