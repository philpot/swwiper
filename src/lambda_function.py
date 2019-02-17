from __future__ import print_function

import os
import logging

from s3json import S3Json
from s3pickle import S3Pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# from google.oauth2 import service_account

BUCKET = "vdf-informatics"
PROJ = "swwiper"
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

FORMAT = "[%(levelname)s]\t[%(name)s]\t%(asctime)s.%(msecs)dZ\t%(message)s\n"
logging.basicConfig(format=FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of all files the user has access to, in passes
    Assumes all files can be managed in single session
    """
    page_size = 1000
    bucket = BUCKET
    credentials = S3Json(bucket=bucket,
                         key=os.path.join(PROJ, "config", "credentials.json")).get()
    print(credentials)

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    try:
        creds = S3Pickle(bucket=bucket,
                         key=os.path.join(PROJ, "config", "token.pickle")).get()
    except Exception:
        logger.warn("No creds could be loaded")
        creds = None
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # might just be Flow?
            flow = InstalledAppFlow.from_client_config(
                credentials, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        S3Pickle(bucket=bucket,
                 key=os.path.join(PROJ, "config", "token.pickle")).put(creds)

    logging.info("Creds = {creds}".format(creds=creds))
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    request = service.files().list(
        pageSize=page_size,
        fields="nextPageToken, files(id, name)",
        q="mimeType='image/jpeg'")

    page = 0
    while request:
        response = request.execute()
        items = response.get('files', [])
        if not items:
            print('No files found.')
            return
        else:
            print('Files: {page}'.format(page=page))
            page += 1
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
            request = service.files().list_next(previous_request=request,
                                                previous_response=response)
