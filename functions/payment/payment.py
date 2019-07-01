# -*- coding: utf-8 -*-
import boto3
import os
import json
import decimal
import uuid
import decimal
from datetime import datetime

# Table name
MASTER_NAME = "SagaEcUserPayment"
TABLE_NAME = "SagaEcPayment"

dynamodbMaster = boto3.resource('dynamodb').Table(MASTER_NAME)
dynamodb = boto3.resource('dynamodb').Table(TABLE_NAME)

def list(event, context):
    res = dynamodb.scan()
    data = res['Items']
    return _response(data, '200')

def listMaster(event, context):
    res = dynamodbMaster.scan()
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


def read(event, context):
    print(event["pathParameters"]["txId"])
    res = dynamodbMaster.get_item(
        Key={
            "TxId": event["pathParameters"]["txId"]
        }   
    )   
    return { 'body' : str(res) }

def readMaster(userId):
    res = dynamodbMaster.get_item(
        Key={
            "UserId": userId
        }   
    )   
    return res

def updateMaster(userId, credit):
    print("## Start updateMaster(" + str(userId) + ", " + str(credit) + ")")

    res = dynamodbMaster.update_item(
        Key={
            'UserId': userId
        },
        UpdateExpression="set Credit=:credit, UpdateDate=:updateDate",
        ExpressionAttributeValues={
            ':credit': credit,
            ':updateDate': datetime.now().isoformat()
        },
        ReturnValues="UPDATED_NEW"
    )
    return res


def __isReserve(req):
    # req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
    userId = req["userId"] if 'userId' in req else req['UserId']
    price = req["price"] if 'price' in req else req['Price']
    print("## userId: " + str(userId))
    print("## price: " + str(price))

    res = readMaster(userId)
    if 'Item' in res:
        item = res["Item"]
        print("## item: "+ str(item))

        if 'Credit' in item:
            credit = item["Credit"]
        
        else:
            print("## Credit: is NOTHING.")

    else:
        print("## item: is NOTHING.")
    
    if ("credit" in locals() and credit > price):
        print("## credit: " + str(credit))
        resMaster = updateMaster(userId, credit - price)
        
        return True #{'body': str(resMaster)}

    else:
        print("## credit: is Not enough.")

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
            userId = req["userId"] if 'userId' in req else req['UserId']
            price = req["price"] if 'price' in req else req['Price']
            createItem = {
                "TxId": txId,
                "OrderNo": orderNo,
                "ItemName": itemName,
                "UserId": userId,
                # "Price": decimal.Decimal(req["price"])
                "Price": price
            }
        res = dynamodb.put_item(
            Item = createItem
        )
        # enQueue(createItem)
        return { 'body' : str(res) }

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)