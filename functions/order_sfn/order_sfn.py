# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# This file is licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License. A copy of the
# License is located at
#
# http://aws.amazon.com/apache2.0/
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import boto3
import json

# The Amazon Resource Name (ARN) of the state machine to execute.
# Example - arn:aws:states:us-west-2:112233445566:stateMachine:HelloWorld-StateMachine
STATE_MACHINE_ARN = 'arn:aws:states:us-east-1:725683553534:stateMachine:SagaEcOrder'
STATE_MACHINE_ARN_COMPENSATED = 'arn:aws:states:us-east-1:725683553534:stateMachine:SagaEcOrder_Copmensated'

#The name of the execution
EXECUTION_NAME = 'Exec-After-Order'

#The string that contains the JSON input data for the execution

def create(event, context):
    requestList = __extractRequest(event, context)
    for req in requestList:
        INPUT = json.dumps(req)
        sfn = boto3.client('stepfunctions')

        response = sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            # name=EXECUTION_NAME,
            input=INPUT
        )

        #display the arn that identifies the execution
        print(response.get('executionArn'))

def createCompensated(event, context):
    requestList = __extractRequest(event, context)
    for req in requestList:
        INPUT = json.dumps(req)
        sfn = boto3.client('stepfunctions')

        response = sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN_COMPENSATED,
            # name=EXECUTION_NAME,
            input=INPUT
        )

        #display the arn that identifies the execution
        print(response.get('executionArn'))

def __extractRequest(event, context):
    requestList = []
    if "Records" in event.keys():
        recordList = json.loads(event["Records"]) if type(event["Records"]) == str else event["Records"]

        for record in recordList:
            req = json.loads(record["body"]) if type(record["body"]) == str else record["body"]
            requestList.append(req)
    
    elif "body" in event.keys():
        req = json.loads(event["body"]) if type(event["body"]) == str else event["body"]
        requestList.append(req)

    print("## recordList: "+ json.dumps(recordList, indent=2))
    return requestList
