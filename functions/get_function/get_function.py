# -*- coding: utf-8 -*-
import os
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    dynamo_tbl = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])
    name = event["queryStringParameters"]["name"]

    data = dynamo_tbl.query(
        KeyConditionExpression=Key('name').eq(name)
    )['Items'][0]

    return {
        "statusCode": 200,
        "body": json.dumps({"name": data["name"], "price": str(data["price"])})
    };