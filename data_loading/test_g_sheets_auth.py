import os
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

# For instructions on how to configure the Google Sheets API, please use the README here:
# https://github.com/NOAA-Omics/noaa-omics-templates

# Load .env file
load_dotenv()

# Get the path to the credentials file from the .env file
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Make sure the path is correctly interpreted
credentials_path = credentials_path.replace('\\', '/')

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Authenticate using the credentials file
creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
client = gspread.authorize(creds)

def access_google_sheet():
    #spreadsheet_id = ''  #SHEETNAME: authtest # Replace with your actual spreadsheet ID
    spreadsheet_id = '' #SHEETNAME: practice-study-data-template-dict
    sheet = client.open_by_key(spreadsheet_id).sheet1
    data = sheet.get_all_cells()
    print(data)

if __name__ == "__main__":
    access_google_sheet()