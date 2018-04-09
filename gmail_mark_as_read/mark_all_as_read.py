from __future__ import print_function

import os

import httplib2
import progressbar
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Gmail Mark all as read'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-mark-as-read.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def mark_as_read(service):
    response = {'nextPageToken':''}
    total_number = service.users().labels().get(id='UNREAD',userId='me').execute()['messagesUnread']
    bar = None
    q = 0
    while 'nextPageToken' in response:
        response = service.users().messages().list(userId='me',labelIds=['UNREAD'],pageToken=response['nextPageToken'],maxResults=1000).execute()
        if 'messages' not in response:
            print('All messages are already read.')
            return
        if bar is None:
            bar = progressbar.ProgressBar(max_value=total_number)
        message_ids = [i['id'] for i in response['messages']]
        service.users().messages().batchModify(userId='me',body={'ids':message_ids,'removeLabelIds':['UNREAD']}).execute()
        q += len(message_ids)
        bar.update(q)

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    mark_as_read(service=service)


if __name__ == '__main__':
    main()
