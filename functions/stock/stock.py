# -*- coding: utf-8 -*-
import boto3
import os
import json
import decimal
import uuid
import decimal
from datetime import datetime

# Table name
MASTER_NAME = "SagaEcItemStock"
TABLE_NAME = "SagaEcStock"

dynamodbMaster = boto3.resource('dynamodb').Table(MASTER_NAME)
dynamodb = boto3.resource('dynamodb').Table(TABLE_NAME)

def list(event, context):
    res = dynamodb.scan()
    return { 'body' : str(res) }

def read(event, context):
    print(event["pathParameters"]["txId"])
    res = dynamodbMaster.get_item(
        Key={
            "TxId": event["pathParameters"]["txId"]
        }   
    )   
    return { 'body' : str(res) }

def reserve(event, context):
    print("## itemId: " + event["itemId"])
    print("## amount: " + str(event["amount"]))

    res = dynamodbMaster.get_item(
        Key={
            "ItemId": event["pathParameters"]["itemId"]
        }   
    )
    if 'Item' in res:
        item = res["Item"]
        print("## item: "+ str(item))

        if 'Stock' in item:
            stock = item["Stock"]
        
        else:
            print("## Stock: is NOTHING.")

    else:
        print("## item: is NOTHING.")
    
    if "stock" in locals():
        print("## stock: " + str(stock))
    else:
        print("## stock: is Nothing.")

    return { 'body' : str(res) }

def create(event, context):
    req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
    txId = req["TxId"]
    amount = req["Amount"]

    createItem = {
        "TxId": txId,
        "OrderNo": orderNo,
        "ItemName": req["itemName"],
        # "Price": decimal.Decimal(req["price"])
        "Price": req["price"]
    }

    res = dynamodb.put_item(
        Item = createItem
    )
    enQueue(createItem)
    return { 'body' : str(res) }


def enQueue(msg):

    print("# msg: "+  str(msg))

    response = client.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(msg)
    )
    print(response)