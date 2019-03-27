# -*- coding: utf-8 -*-
import os
import requests
import boto3
import json
import decimal
import uuid
from datetime import datetime as dt

def lambda_handler(event, context):
#    bf_res = requests.get("https://api.bitflyer.jp/v1/ticker?product_code=BTC_JPY")
    price = event["queryStringParameters"]["price"]

#    _insert_dynamo(bf_res.json()["ltp"])
    _insert_dynamo(price)

def _insert_dynamo(price):
    dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

    u4 = str(uuid.uuid4())
    tdatetime = dt.now()
    tstr = tdatetime.strftime('%Y/%m/%d')

    json_str = '''
    {
        "TxId": u4,
        "OrderNo": tstr,
        "name": "btc"+ tstr,
        "price": %f
    }
    ''' % (price)
    item = json.loads(json_str, parse_float=decimal.Decimal)
    dynamo.put_item(Item = item)
    return {"status": "OK"}
