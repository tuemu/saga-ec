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
    return { "body" : str(res) }

def read(event, context):
    # print(event["pathParameters"]["txId"])
    txId = event["pathParameters"]["txId"] if "pathParameters" in event else event["txId"]
    print("txId for fetch: "+ str(txId))
    res = dynamodb.get_item(
        Key={
            "TxId": txId
        }   
    )   
    return res

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
        UpdateExpression="set Stock=:stock, UpdateDate=:updateDate",
        ExpressionAttributeValues={
            ':stock': stock,
            ':updateDate': datetime.now().isoformat()
        },
        ReturnValues="UPDATED_NEW"
    )
    return res


def __isReserve(req):
    # req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
    itemId = req["itemId"] if 'itemId' in req else req['ItemId']
    amount = req["amount"] if 'amount' in req else req['Amount']
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

def __extractRequest(event, context):
    requestList = []
    if "Records" in event.keys():
        recordList = json.loads(event["Records"]) if type(event["Records"]) == str else event["Records"]
        print("## recordList: "+ str(recordList))

        for record in recordList:
            req = json.loads(record["body"]) if type(record["body"]) == str else record["body"]
            requestList.append(req)
    
    elif "body" in event.keys():
        req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
        requestList.append(req)

    else :
        req = json.loads(event) if type(event) == str else event
        requestList.append(req)

    return requestList


def create(event, context):
    requestList = __extractRequest(event, context)
    for req in requestList:
        if __isReserve(req):
            # req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
            print("req: "+ str(req))
            txId = req["txId"] if 'txId' in req else req['TxId']
            orderNo = req["orderNo"] if 'orderNo' in req else req['OrderNo']
            itemName = req["itemName"] if 'itemName' in req else req['ItemName']
            itemId = req["itemId"] if 'itemId' in req else req['ItemId']
            amount = req["amount"] if 'amount' in req else req['Amount']
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
        return { 'body' : str(createItem) }

def createCompensated(event, context):
    #requestList = __extractRequest(event, context)
    #for req in requestList:
    res = read(event, context)
    if 'Item' in res:
        item = res["Item"]
        print("## item: "+ str(item))

        if 'Amount' in item:
            amount = item["Amount"]
        else:
            print("## Amount: is NOTHING.")

        if 'ItemId' in item:
            itemId = item["ItemId"]
        else:
            print("## ItemId: is NOTHING.")

        resMaster = readMaster(itemId)
        if 'Item' in resMaster:
            item = resMaster["Item"]
            print("## item: "+ str(item))

            if 'Stock' in item:
                stock = item["Stock"]
            
            else:
                print("## Stock: is NOTHING.")
                stock = 0

        else:
            print("## Item in Master: is NOTHING.")

    else:
        print("## Item: is NOTHING.")

    if ("itemId" in locals() and "amount" in locals()):
        resMaster = updateMaster(itemId, stock + amount)
        
        return True #{'body': str(resMaster)}

    else:
        print("It did not update in Compensation")

    return False #{ 'body' : str(res) }


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
