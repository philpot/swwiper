from __future__ import print_function

import os
from s3json import S3Json

BUCKET = "vdf-informatics"
PROJ = "swwiper"


def lambda_handler(event, context):

    credentials = S3Json(bucket=BUCKET,
                         key=os.path.join(PROJ, "config", "credentials.json")).get()
    print(credentials)
