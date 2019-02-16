from __future__ import print_function

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of all files the user has access to, in passes
    Assumes all files can be managed in single session
    """
    page_size = 1000
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    request = service.files().list(
        pageSize=page_size, fields="nextPageToken, files(id, name)")

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


if __name__ == '__main__':
    main()
