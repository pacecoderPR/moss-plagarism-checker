import os
from configparser import ConfigParser
import re
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Read the submissions directory path from config file
configObject = ConfigParser()
configObject.read("config.ini")
paths = configObject["PATHS"]
sheets = configObject["GOOGLE SHEETS"]

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = None

if os.path.exists("token.json"):
    credentials = Credentials.from_authorized_user_file("token.json", SCOPES)


if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        credentials = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(credentials.to_json())

def fetch_usernames(SPREADSHEET_ID, RANGE):
    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()

        result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
        values = result.get("values", [])
        
        usernames = []
        print(f"Fetching usernames from range `{RANGE}`\n")
        for i, row in enumerate(values):
            if i == 0:  #Skip header row
                continue
            if row != [] and row[0] not in ["NA", "#N/A"]:
                username = row[0]
                usernames.append(username)

        return usernames

    except HttpError as error:
        print(error)

def write_links(SPREADSHEET_ID, data):
    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()

        sheets.values().append(spreadsheetId=SPREADSHEET_ID, range="Atcoder!A:I", valueInputOption = "USER_ENTERED",
        body = {"values" : [data]}).execute()

    except HttpError as error:
        print(error)

