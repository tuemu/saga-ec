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

def readMaster(itemId):
    res = dynamodbMaster.get_item(
        Key={
            "ItemId": itemId
        }   
    )   
    return res

def updateMaster(itemId, stock):
    print("## Start updateMaster(" + str(itemId) + ", " + str(stock) + ")")

    res = dynamodbMaster.update_item(
        Key={
            'ItemId': itemId
        },
        UpdateExpression="set Stock=:stock",
        ExpressionAttributeValues={
            ':stock': stock
        },
        ReturnValues="UPDATED_NEW"
    )
    return res

    # res = dynamodb.Table(TABLE_NAME).update_item(
    #     Key={
    #         'id': event["pathParameters"]["id"]
    #     },  
    #     UpdateExpression="set isbn=:i, title=:t, price=:p",
    #     ExpressionAttributeValues={
    #         ':i': req["isbn"],
    #         ':t': req["title"],
    #         ':p': decimal.Decimal(req["price"])
    #     },  
    #     ReturnValues="UPDATED_NEW"
    # )
    # return { 'body' : str(res) }


def isReserve(event, context):
    req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
    itemId = req["itemId"]
    amount = req["amount"]
    print("## itemId: " + str(itemId))
    print("## amount: " + str(amount))

    # res = dynamodbMaster.get_item(
    #     Key={
    #         "ItemId": event["pathParameters"]["itemId"]
    #     }   
    # )
    res = readMaster(itemId)
    if 'Item' in res:
        item = res["Item"]
        print("## item: "+ str(item))

        if 'Stock' in item:
            stock = item["Stock"]
        
        else:
            print("## Stock: is NOTHING.")

    else:
        print("## item: is NOTHING.")
    
    if ("stock" in locals() and stock > amount):
        print("## stock: " + str(stock))
        resMaster = updateMaster(itemId, stock - amount)
        
        return True #{'body': str(resMaster)}

    else:
        print("## stock: is Nothing.")

    return False #{ 'body' : str(res) }


def create(event, context):
    if isReserve(event, context):
        req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
        print("req: "+ str(req))
        txId = req["txId"]
        orderNo = req["orderNo"]
        itemName = req["itemName"]
        itemId = req["itemId"]
        amount = req["amount"]
        createItem = {
            "TxId": txId,
            "OrderNo": orderNo,
            "ItemName": itemName,
            "ItemId": itemId,
            # "Price": decimal.Decimal(req["price"])
            "Amount": amount
        }

    res = dynamodb.put_item(
        Item = createItem
    )
    # enQueue(createItem)
    return { 'body' : str(res) }

def update(event, context):
    print("## amount: " + str(event["amount"]))

    req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
    res = dynamodb.Table(TABLE_NAME).update_item(
        Key={
            'id': event["pathParameters"]["id"]
        },  
        UpdateExpression="set isbn=:i, title=:t, price=:p",
        ExpressionAttributeValues={
            ':i': req["isbn"],
            ':t': req["title"],
            ':p': decimal.Decimal(req["price"])
        },  
        ReturnValues="UPDATED_NEW"
    )
    return { 'body' : str(res) }


def enQueue(msg):

    print("# msg: "+  str(msg))

    response = client.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(msg)
    )
    print(response)