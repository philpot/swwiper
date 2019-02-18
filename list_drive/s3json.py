from __future__ import print_function

import json
import boto3
import logging

FORMAT = "[%(levelname)s]\t[%(name)s]\t%(asctime)s.%(msecs)dZ\t%(message)s\n"
logging.basicConfig(format=FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = boto3.client('s3')


class S3Json(object):
    def __init__(self,
                 bucket=None,
                 key=None,
                 uri=None):

        if uri:
            # TBD compute bucket and key
            # TBD warn and ignore if bucket and/or key provided
            pass
        else:
            self.bucket = bucket
            self.key = key

    def get(self):
        logger.info("S3Json({bucket}, {key}).get()"
                    .format(bucket=self.bucket,
                            key=self.key))
        response = client.get_object(Bucket=self.bucket, Key=self.key)
        serialized = response['Body'].read().decode("utf-8")
        deserialized = json.loads(serialized)
        return deserialized

    def put(self, content):
        return None
