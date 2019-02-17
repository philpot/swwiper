from __future__ import print_function

import pickle
import boto3

client = boto3.client('s3')


class S3Pickle(object):
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
        body_string = response['Body'].read()
        deserialized = pickle.loads(body_string)
        return deserialized

    def put(self, content):
        serialized = pickle.dumps(content)
        client.put_object(Bucket=self.bucket, Key=self.key, Body=serialized)
        return True
