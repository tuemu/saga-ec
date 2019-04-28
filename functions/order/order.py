# -*- coding: utf-8 -*-
import boto3
import json
import decimal
import uuid
import decimal
from datetime import datetime

# Table name
TABLE_NAME = "SagaEcOrder"
dynamodb = boto3.resource('dynamodb').Table(TABLE_NAME)


def lambda_handler(event, context):

    itemName = event['itemName']
    price = event['price']

    print(itemName)
    print(price)

    _insert_dynamo(str(uuid.uuid4()), itemName)

def list(event, context):
    res = dynamodb.scan()
    return { 'body' : str(res) }

def read(event, context):
    print(event["pathParameters"]["txId"])
    res = dynamodb.get_item(
        Key={
            "TxId": event["pathParameters"]["txId"]
        }   
    )   
    return { 'body' : str(res) }


def create(event, context):
    req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
    # req = event # json.loads(event["body"]) if type(event["body"]) == str else event["body"]
    orderNo = "OR-"+ datetime.now().isoformat()
    
    res = dynamodb.put_item(
        Item = {
            "TxId": str(uuid.uuid4()),
            "OrderNo": orderNo,
            "ItemName": req["itemName"],
            "Price": decimal.Decimal(req["price"])
        }
        # ,
        # UpdateExpression='set OrderNo = OrderNo + :val',
        # ExpressionAttributeValues={
        #     ':val': 1
        # },
        # ReturnValues='UPDATED_NEW'        }  
    )
#    print(Item)
    # print(json.dumps(res, indent=4, cls=DecimalEncoder))
    return { 'body' : str(res) }

def _insert_dynamo(txId, itemName):
    dynamo = boto3.resource('dynamodb').Table(TABLE_NAME)

    json_str = '''
    {
        "txId": txId,
        "itemName": itemName
    }
    ''' % (price)

    # item = json.loads(json_str, parse_float=decimal.Decimal)
    # dynamo.put_item(Item = item)

    return {"status": "OK"}