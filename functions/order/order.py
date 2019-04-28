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
# QUEUE_NAME = "saga-ec-order.fifo"
# QUEUE_NAME = os.environ['QUEUE_ORDER']
sqs = boto3.resource('sqs')


name = 'test-load-mikami'
sqs = boto3.resource('sqs')

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
    txId = str(uuid.uuid4())

    res = dynamodb.put_item(
        Item = {
            "TxId": txId,
            "OrderNo": orderNo,
            "ItemName": req["itemName"],
            "Price": decimal.Decimal(req["price"])
        }
    )
    enQueue(res)
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


def enQueue(msg):
    try:
        # キューの名前を指定してインスタンスを取得
        queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)
    except:
        # 指定したキューがない場合はexceptionが返るので、キューを作成
        queue = sqs.create_queue(QueueName=QUEUE_NAME)
    
    # メッセージ×1をキューに送信
    msg_num = 1
    # msg_list = [msg]
    msg_list = [{'Id' : '{}'.format(i+1), 'MessageBody' : 'msg_{}'.format(i+1)} for i in range(msg_num)]
    print("# msg: "+  str(msg))
    response = queue.send_messages(Entries=msg_list)
    print(response)