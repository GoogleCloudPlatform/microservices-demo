import json
import os

import boto3

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    table = dynamodb.Table(os.environ["TABLE_NAME"])
    response = table.scan(Select="COUNT")

    body = {
        "mensaje": "Hola desde el backend de catalogo",
        "productos_en_tabla": response["Count"],
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
