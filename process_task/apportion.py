from __future__ import print_function

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from examine import b64_to_long
from collections import Counter

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SCOPES = ['https://www.googleapis.com/auth/drive']
MODULUS = 11

# DUMMY_FOLDER_ID = "1nf5BbaW_y7nAr98ae8zSH7thseFcfeaG"

# MY_FOLDER_ID = "1wYz2JCM1tYFmwkWNBJyChYLSwv5bro1wdDs93jVbMJo"

# # zebra
# MY_FOLDER_ID = "1bDdHEQylj9Nn9xIb2SGKHhUytlNRP9YC"

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

    # Should be able to do all these:
    # - list all files containing a string in the file body (not just in the name)
    # - file count within a folder
    # Specifically for our use case, we might like to
    # - list all folders, recursively
    # - list all objects within a folder
    # so we could parallelize the bulk loading by folder (or folder group)

    # Call the Drive v3 API
    c = Counter()

    def inside(c=c):
        request = service.files().list(
            pageSize=page_size,
            # fields="nextPageToken, files(id, name)",
            fields="nextPageToken, files(id, name, parents)",
            # q="mimeType='image/jpeg'"
            # q="mimeType='application/vnd.google-apps.folder' and name contains 'Dummy Files'"
            # doesn't work, should
            # q="'{id}' in parents".format(id=DUMMY_FOLDER_ID)
            # full text seems to search ONLY name, not actual text
            # q="fullText contains 'cyan'"
            # full text seems to search ONLY name, not actual text
            # q="fullText contains 'very'"
            # works
            # q="'root' in parents"
            # did not work
            # q="mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false"
            # q = "name='Dummy Folder' and mimeType='application/vnd.google-apps.folder'"
            # did not work
            # q="'{myid}' in parents".format(myid=MY_FOLDER_ID)
            # q="mimeType='application/vnd.google-apps.folder'"
            # q="'0AHs_lHBwwE6AUk9PVA' in parents"
            # q="'{f}' in parents and mimeType='application/vnd.google-apps.folder'".format(f=MY_FOLDER_ID)
            q="not 'root' in parents"
        )

        show = 500
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
                    d = (b64_to_long(item['id']) >> 2)
                    m = d % MODULUS
                    c[m] += 1
                    print(u'{n} ({i} = {d}) {m}'.format(n=item['name'],
                                                        i=item['id'],
                                                        d=d,
                                                        m=m))
                    show -= 1
                    if show <= 0:
                        return
                request = service.files().list_next(previous_request=request,
                                                    previous_response=response)

    inside()
    print(c)


if __name__ == '__main__':
    main()
