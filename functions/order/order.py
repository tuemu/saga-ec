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

def read(event, context):
    # print(json.dumps(event, indent=2))
    txId = event["pathParameters"]["txId"] if "pathParameters" in event else event["txId"]
    print("txId for fetch: "+ str(txId))
    res = dynamodb.get_item(
        Key={
            "TxId": txId
        }   
    )   
    return res

def lambda_handler(event, context):
    print("This method is dummy.")

def list(event, context):
    res = dynamodb.scan()
    data = res['Items']

    return _response(data, '200')

def _response(message, status_code):
    return {
        "statusCode": str(status_code),
        "body": json.dumps(message, cls=DecimalEncoder),
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            },
        }

def update(txId:str, isCompensated:bool, compTxId:str):
    print("## Start update(" + str(txId) + ", " + str(isCompensated) + ")")

    res = dynamodb.update_item(
        Key={
            'TxId': txId
        },
        UpdateExpression="set IsCompensated=:isCompensated, CompTxId=:compTxId, UpdateDate=:updateDate",
        ExpressionAttributeValues={
            ':isCompensated': isCompensated,
            ':compTxId': compTxId,
            ':updateDate': datetime.now().isoformat()
        },
        ReturnValues="UPDATED_NEW"
    )
    return res


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
        "Price": req["price"],
        "UserId": req["userId"],
    }

    res = dynamodb.put_item(
        Item = createItem
    )
    enQueue(createItem)
    return { 'body' : str(res) }

def createCompensated(event, context):
    #requestList = __extractRequest(event, context)
    #for req in requestList:
    txId = event["txId"] if 'txId' in event else event['TxId']
    temp = {"pathParameters": {"txId":txId}}
    temp = event.update(temp)
    res = read(event, context)
    if 'Item' in res:
        item = res["Item"]
        print("## item: "+ str(item))

        # Disable old Tx
        compTxId = str(uuid.uuid4())
        update(txId, True, compTxId)

    else:
        print("## Item: is NOTHING.")
        return False

    return {"compTxId": compTxId}

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

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
