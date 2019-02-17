from __future__ import print_function

import json
import boto3

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
        response = client.get_object(Bucket=self.bucket, Key=self.key)
        serialized = response['Body'].read().decode("utf-8")
        deserialized = json.loads(serialized)
        return deserialized

    def put(self, content):
        return None
