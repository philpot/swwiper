from __future__ import print_function

import logging
import datetime
import boto3
import json
import decimal

BUCKET = "vdf-informatics"
PROJ = "swwiper"
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

FORMAT = "[%(levelname)s]\t[%(name)s]\t%(asctime)s.%(msecs)dZ\t%(message)s\n"
logging.basicConfig(format=FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


#
#  Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#  This file is licensed under the Apache License, Version 2.0 (the "License").
#  You may not use this file except in compliance with the License. A copy of
#  the License is located at
#
#  http://aws.amazon.com/apache2.0/
#
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
#  CONDITIONS OF ANY KIND, either express or implied. See the License for the
#  specific language governing permissions and limitations under the License.
#

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

# arn:aws:dynamodb:us-west-2:322501851660:table/vdf-informatics-swwiper-metadata-store


dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

table = dynamodb.Table('vdf-informatics-swwiper-metadata-store')


"""
{
  "Records": [
    {
      "body": "Hello from SQS!",
      "receiptHandle": "MessageReceiptHandle",
      "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
      "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
      "eventSource": "aws:sqs",
      "awsRegion": "us-east-1",
      "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
      "attributes": {
        "ApproximateFirstReceiveTimestamp": "1523232000001",
        "SenderId": "123456789012",
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1523232000000"
      },
      "messageAttributes": {}
    }
  ]
}
"""

"""
{
  "Records": [
    {
      "body": "khaki/reliable/fig/leaf.txt",
      "receiptHandle": "AQEBK2pC0D14RXxrRnpg6mpJP3awbB+OEWO2YyDHI/9TQam6jXNC8dX48aTw/7JBkgLhkZz9/r/HwCZqLWC007q2FQAfdASjYEKLG300ogM4FVSl6W58e+ffL6yV6QwG+7tv4AtQlAtKWv82V5clXX9M1jxrMIWiSFnzt905nWBSAfjYTE+sIWEpCgRWAU56XW3w7Nr0Q3DqpFBVkJvunkLHZzL2OSm241ONiq7lcvMUvoAFqOwBwIQBvQlDhHCy17u1+p3078Dj6rDKBbWUC/lmulRULDBT7+kAUcsVSKXrF49+W7CvpIe9GPSc48LoWRcPP2KCX+8y3pqDaGFIkb+58k7G1PkqLui8NX4k1DHQRKIgMCDHfy57LgBZ+y8c/9nfTvkAuZ/OBKaA4yavVjckPFAjTS9sILn4aHYeMQ3FEbQ=",
      "md5OfBody": "4abad207d1441f5194e8acaa36275e31",
      "md5OfMessageAttributes": "cd3687d8d80a466cf9129ee1601de514",
      "eventSourceARN": "arn:aws:sqs:us-west-2:322501851660:vdf-informatics-swwiper-tasks",
      "eventSource": "aws:sqs",
      "awsRegion": "us-west-2",
      "messageId": "4ec3b251-a74e-4950-83a9-a9eff50dc34e",
      "attributes": {
        "ApproximateFirstReceiveTimestamp": "1550555011848",
        "SenderId": "AIDAIHVVFN2SSZ2HLYT5Y",
        "ApproximateReceiveCount": "41",
        "SentTimestamp": "1550555011848"
      },
      "messageAttributes": {
        "Timestamp": {
          "dataType": "Number.utcmicroseconds",
          "stringValue": "1550555011820577",
          "binaryListValues": [],
          "stringListValues": []
        },
        "Id": {
          "dataType": "String",
          "stringValue": "1T3jYOiEOwkcZzfLASiwfgaOozuok0jMg",
          "binaryListValues": [],
          "stringListValues": []
        },
        "Name": {
          "dataType": "String",
          "stringValue": "khaki/reliable/fig/leaf.txt",
          "binaryListValues": [],
          "stringListValues": []
        }
      }
    }
  ]
}
"""


def lambda_handler(event, context):

    """Select messages from SQS and insert them into Dynamo
    """

    logger.info("event {event} of type {t}"
                .format(event=event, t=type(event)))

    for record in event.get("Records", []):
        queue_arn = record['eventSourceARN']
        logger.info("from queue {arn}".format(arn=queue_arn))
        id = record["messageAttributes"]["Id"]["stringValue"]
        name = record["messageAttributes"]["Name"]["stringValue"]
        # when it was last fetched
        timestamp = record["messageAttributes"]["Timestamp"]["stringValue"]
        if False:
            metadata = {"GoogleAttr1": "GoogleValue1",
                        "GoogleAttr2": "GoogleValue2"}
        else:
            # call API
            metadata = {}
        item = {
            'id': id,
            'name': name,
            'fetched': int(timestamp),
            'analyzed': int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()*1000000)}
        item.update(metadata)
        response = table.put_item(Item=item)
        return response
