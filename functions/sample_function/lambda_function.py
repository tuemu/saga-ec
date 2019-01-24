# -*- coding: utf-8 -*-
import os
import requests
import boto3
import json
import decimal

def lambda_handler(event, context):
    bf_res = requests.get("https://api.bitflyer.jp/v1/ticker?product_code=BTC_JPY")
    _insert_dynamo(bf_res.json()["ltp"])

def _insert_dynamo(price):
    dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

    json_str = '''
    {
        "name": "btc",
        "price": %f
    }
    ''' % (price)

    item = json.loads(json_str, parse_float=decimal.Decimal)
    dynamo.put_item(Item = item)

    return {"status": "OK"}
