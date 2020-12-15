import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle


class SpreadSheets():

    def __init__(self, scopes, id_spreadsheet, sample_range):
        self.scopes = scopes
        self.id_spreadsheet = id_spreadsheet
        self.sample_range = sample_range
        self.service = None
        self.df = None

    def create_service(self, client_secret_file, api_service_name, api_version, path_token, *scopes):
        # SCOPES = [scope for scope in scopes[0]]
        # print(SCOPES)
        SCOPES = self.scopes

        cred = None

        if os.path.exists(path_token):
            with open(path_token, 'rb') as token:
                cred = pickle.load(token)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_file, SCOPES)
                cred = flow.run_local_server()

            with open(path_token, 'wb') as token:
                pickle.dump(cred, token)

        try:
            self.service = build(
                api_service_name, api_version, credentials=cred)
            print(api_service_name, 'service created successfully')
        except Exception as e:
            self.service = None
            print(e)

    def export_data_to_sheets(self):
        if self.service is None:
            print("Service not found!")
            return

        if self.df is None:
            print("Dataframe not found!")
            return

        response_date = self.service.spreadsheets().values().update(
            spreadsheetId=self.id_spreadsheet,
            valueInputOption='RAW',
            range=self.sample_range,
            body=dict(
                majorDimension='ROWS',
                values=self.df.T.reset_index().T.values.tolist())
        ).execute()
        print('Sheet successfully Updated')

    def read_sheets(self):
        if self.service is None:
            print("Service not found!")
            return

        # Call the Sheets API
        sheet = self.service.spreadsheets()
        result_input = sheet.values().get(spreadsheetId=self.id_spreadsheet,
                                          range=self.sample_range).execute()
        values_input = result_input.get('values', [])

        if not values_input and not values_expansion:
            print('No data found.')
            self.df = None
        else:
            self.df = pd.DataFrame(values_input[1:], columns=values_input[0])


if __name__ == "__main__":
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    # here enter the id of your google sheet
    SAMPLE_SPREADSHEET_ID_input = '1DM_ZboLH0N0tnoa81vvKy9qLbPGlvkb3nZHByH45mno'
    SAMPLE_RANGE_NAME = 'Página2!A1:AA100000'

    spread_sheats = SpreadSheets(
        SCOPES, SAMPLE_SPREADSHEET_ID_input, SAMPLE_RANGE_NAME)
    spread_sheats.create_service('credentials.json', 'sheets', 'v4')
    spread_sheats.read_sheets()
    # spread_sheats.df["available"][0] = 1
    print(spread_sheats.df.head())
    # spread_sheats.export_data_to_sheets()
