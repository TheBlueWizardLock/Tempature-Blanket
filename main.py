import os
from dotenv import load_dotenv
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import date
import requests
import json
import re

load_dotenv(".env")
today = str(date.today())
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("SHEET_ID")
SAMPLE_RANGE_NAME = 'temperatures!A:A'

def handler(event,context):
    """Need to put this here for lambda"""
    pass


def get_temp():
    """Gets the current days temp for slc"""
    location_data = {
        "salt_lake_city": {"latitude": 40.758701,
                           "longitude": -111.876183}
    }
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": location_data["salt_lake_city"]["latitude"],
        "lon": location_data["salt_lake_city"]["longitude"],
        "appid": os.getenv("WEATHER"),
        "units": "imperial",
    }
    response = requests.get(url=url, params=params)
    temp = response.json()["main"]["temp"]
    return temp

todays_temp = get_temp()
with open("hex_color_temps.json", "r") as f:
    color_temp_data = json.load(f)
temp_list = [int(x) for x in color_temp_data]

index = min(range(len(temp_list)), key=lambda i: abs(temp_list[i] - todays_temp))

temp_color_hex_code = color_temp_data[str(temp_list[index])]["hex"]
rgb = tuple(int(temp_color_hex_code[i:i + 2], 16) for i in (1, 3, 5))


def change_color(service, row, red, green, blue):
    """Gets the row of the data that was added then changes the background color of the hex cell"""
    body = {
        "requests": [
            {
                "updateCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": row,
                        "endRowIndex": row + 1,
                        "startColumnIndex": 2,
                        "endColumnIndex": 3
                    },
                    "rows": [
                        {
                            "values": [
                                {
                                    "userEnteredFormat": {
                                        # for what ever damn reason its the percentage of the rbg value
                                        "backgroundColor": {
                                            "red": red / 255,
                                            "green": green / 255,
                                            "blue": blue / 255
                                        }
                                    }
                                }
                            ]
                        }
                    ],
                    "fields": "userEnteredFormat.backgroundColor"
                }
            }
        ]
    }
    res = service.spreadsheets().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body)
    res.execute()


def add_value(sheet):
    """pulls the data of date temp and today temp's color and adds it into the google sheet."""
    test_range = 'temperatures!A1:D1'
    append_results = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                           range=test_range,
                                           valueInputOption='RAW',
                                           insertDataOption='OVERWRITE',
                                           body={"values": [[today, int(todays_temp), temp_color_hex_code]],
                                                 })
    r = append_results.execute()
    updatedRange = r["updates"]["updatedRange"]
    result = re.search(r'A(\d+)', updatedRange)
    number = int(result.group(1))
    return number - 1


def main():
    """"""
    creds = None
    # if token.json doesn't exist then we run with the credentials file and then save the tokens for later
    # use so we don't have to auth everytime.
    if os.path.exists('tmp/token.json'):
        creds = Credentials.from_authorized_user_file(r'tmp/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('tmp/token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        if not values:
            print('No data found.')
            return
        else:
            date_stamp = [i[0] for i in values]
            # if today hasnt been logged and theres data
            if today not in date_stamp:

                # updates the colors and values in google sheet
                change_color(service, row=add_value(sheet), red=rgb[0], green=rgb[1], blue=rgb[-1])

    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()

