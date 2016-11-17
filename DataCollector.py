# -*- coding: utf-8 -*-
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

class datacollector():
	def __init__(self):
		self.credentials = self.get_credentials()

	def get_credentials(self):
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
	                                   'sheets.googleapis.com-python-quickstart.json')

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

	def append(self, username, action, time):
	    """Shows basic usage of the Sheets API.

	    Creates a Sheets API service object and prints the names and majors of
	    students in a sample spreadsheet:
	    https://docs.google.com/spreadsheets/d/1cMLc7hbRG64R7Fbd_mc0QfXjuN71QG1OEY3leYYWhas/edit
	    """
	    credentials = self.get_credentials()
	    http = credentials.authorize(httplib2.Http())
	    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
	                    'version=v4')
	    service = discovery.build('sheets', 'v4', http=http,
	                              discoveryServiceUrl=discoveryUrl)

	    spreadsheetId = '1cMLc7hbRG64R7Fbd_mc0QfXjuN71QG1OEY3leYYWhas'
	    rangeName = 'Sheet1!A1:C1'
	    valueInputOption = 'RAW'
	    body = {
	    	'range': 'Sheet1!A1:C1',
	    	'majorDimension': 'ROWS',
	    	'values': [
	    		[username, action, time],
	    	]
	    }

	    result = service.spreadsheets().values().append(
	    	spreadsheetId=spreadsheetId, range=rangeName, valueInputOption=valueInputOption, body=body).execute()


if __name__ == '__main__':
    main()