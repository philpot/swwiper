from __future__ import print_function

import datetime
import pickle
import os.path
import boto3

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

QUEUE_NAME = "vdf-informatics-swwiper-tasks"
QUEUE_ARN = "arn:aws:sqs:us-west-2:322501851660:vdf-informatics-swwiper-tasks"
QUEUE_URL = "https://sqs.us-west-2.amazonaws.com/322501851660/vdf-informatics-swwiper-tasks"

# Get the service resource
# sqs = boto3.resource('sqs')
sqs = boto3.client('sqs')

# Get the queue. This returns an SQS.Queue instance
# queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

# # You can now access identifiers and attributes
# print(queue.url)
# print(queue.attributes.get('DelaySeconds'))


def main():
    """Enqueue all files belonging to this user
    """
    page_size = 1000
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../vault/token.pickle'):
        with open('../vault/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../vault/credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('../vault/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    request = service.files().list(
        pageSize=page_size,
        fields="nextPageToken, files(id, name)")

    page = 0
    seen = False
    while request:
        response = request.execute()
        items = response.get('files', [])
        if not items:
            print('No files found.')
            return
        else:
            print('Page: {page}'.format(page=page))
            for item in items:
                if page == 0 and not seen:
                    print(item)
                    seen = True
                # Insert message into SQS queue
                response = sqs.send_message(
                    QueueUrl=QUEUE_URL,
                    DelaySeconds=0,
                    MessageAttributes={
                        'Name': {
                            'DataType': 'String',
                            'StringValue': item['name']},
                        'Id': {
                            'DataType': 'String',
                            'StringValue': item['id']},
                        'Timestamp': {
                            'DataType': 'Number.utcmicroseconds',
                            'StringValue': str(int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()*1000000))}
                        },
                    MessageBody=(item['name'])
                )
            request = service.files().list_next(previous_request=request,
                                                previous_response=response)
            page += 1


if __name__ == '__main__':
    main()
