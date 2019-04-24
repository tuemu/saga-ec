# -*- coding: utf-8 -*-
import boto3
import json
import decimal
import uuid

def lambda_handler(event, context):

    itemName = event['itemName']
    price = event['price']

    print(itemName)
    print(price)

    _insert_dynamo(str(uuid.uuid4()), event)


def _insert_dynamo(txId, ):
    dynamo = boto3.resource('dynamodb').Table("SagaEcOrder")

    json_str = '''
    {
        "name": "btc",
        "price": %f
    }
    ''' % (price)

    item = json.loads(json_str, parse_float=decimal.Decimal)
    dynamo.put_item(Item = item)

    return {"status": "OK"}