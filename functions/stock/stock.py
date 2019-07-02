# -*- coding: utf-8 -*-
import boto3
import os
import json
from decimal import Decimal
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
    # print(event["pathParameters"]["txId"])
    txId = event["pathParameters"]["txId"] if "pathParameters" in event else event["txId"]
    print("txId for fetch: "+ str(txId))
    res = dynamodb.get_item(
        Key={
            "TxId": txId
        }   
    )   
    return res

def update(txId:str, isCompensated:bool, compTxId:str):
    print("## Start updateMaster(" + str(txId) + ", " + str(isCompensated) + ")")

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
    
    print("## stock in __isReserve: " + str(stock) + " / amount: " + str(amount))
    print("## stock - amount in __isReserve: " + str(stock - amount))

    if ("stock" in locals() and stock > amount):
        print("## START updateMaster(itemId, stock - amount): " + str(itemId) + " , " + str(stock-amount) )
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
    print("## event: " +  json.dumps(event, indent=2, default=decimal_default_proc))
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
            originTxId = req["originTxId"] if 'originTxId' in req else None
            
            createItem = {
                "TxId": txId,
                "OrderNo": orderNo,
                "ItemName": itemName,
                "ItemId": itemId,
                # "Price": decimal.Decimal(req["price"])
                "Amount": amount,
                "OriginTxId": originTxId,
                "IsCompensated": False
                
            }
        res = dynamodb.put_item(
            Item = createItem
        )
        # enQueue(createItem)
        return { 'body' : str(createItem) }

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

        if 'Amount' in item:
            amount = item["Amount"]
        else:
            print("## Amount: is NOTHING.")

        if 'ItemId' in item:
            itemId = item["ItemId"]
        else:
            print("## ItemId: is NOTHING.")

        # Get txId for compenstion
        compTxId = event["taskresult"]['compTxId']
        # if ('taskresult' in event and 'compTxId' in event['taskresult']) else 'tempCompTxId''
        # Disable old Tx
        update(txId, True, compTxId)

        # Insert Compensated Tx
        event["originTxId"] = txId
        event["txId"] = compTxId
        item["Amount"] = - amount
        event.update(item)
        
        if 'body' in  event:
            del event["body"]

        if 'Records' in  event:
            del event["Records"] 

        create(event, context)

        # resMaster = readMaster(itemId)
        # if 'Item' in resMaster:
        #     item = resMaster["Item"]
        #     print("## item: "+ str(item))

        #     if 'Stock' in item:
        #         stock = item["Stock"]
            
        #     else:
        #         print("## Stock: is NOTHING.")
        #         stock = 0

        # else:
        #     print("## Item in Master: is NOTHING.")

        return True #{'body': str(resMaster)}
        
    else:
        print("## Item: is NOTHING.")
        
    # print("## stock in createCompensated(): " + str(stock))
    # print("## amount in createCompensated(): " + str(amount))

    # if ("itemId" in locals() and "amount" in locals()):
    #     resMaster = updateMaster(itemId, stock + amount)
        
    #     return True #{'body': str(resMaster)}

    # else:
    #     print("It did not update in Compensation")

        return False #{ 'body' : str(res) }

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)