# -*- coding: utf-8 -*-
import boto3
import os
import json
import decimal
import uuid
import decimal
from datetime import datetime

# Table name
TABLE_NAME = "SagaEcOrder"
# TABLE_NAME = os.environ['TABLE_ORDER']
dynamodb = boto3.resource('dynamodb').Table(TABLE_NAME)

QUEUE_NAME = "saga-ec-order"
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/725683553534/saga-ec-order"
# QUEUE_NAME = "saga-ec-order.fifo"
# QUEUE_NAME = os.environ['QUEUE_ORDER']
sqs = boto3.resource('sqs')
client = boto3.client('sqs')


name = 'test-load-mikami'
sqs = boto3.resource('sqs')

def lambda_handler(event, context):

    print("This method is dummy.")
    # itemName = event['itemName']
    # price = event['price']

    # print(itemName)
    # print(price)

    # _insert_dynamo(str(uuid.uuid4()), itemName)

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
    txId = str(uuid.uuid4())

    createItem = {
        "TxId": txId,
        "OrderNo": orderNo,
        "ItemId": req["itemId"],
        "ItemName": req["itemName"],
        "Amount": req["amount"],
        # "Price": decimal.Decimal(req["price"])
        "Price": req["price"]
    }

    res = dynamodb.put_item(
        Item = createItem
    )
    enQueue(createItem)
    return { 'body' : str(res) }

def _insert_dynamo(txId, itemName):
    dynamo = boto3.resource('dynamodb').Table(TABLE_NAME)

    json_str = '''
    {
        "txId": txId,
        "itemName": itemName
    }
    ''' % (price)

    return {"status": "OK"}


def enQueue(msg):

    print("# msg: "+  str(msg))

    response = client.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(msg)
    )
    print(response)