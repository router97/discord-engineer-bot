# from pathlib import Path

# from googleapiclient.discovery import build, Resource
# from google.oauth2 import service_account


# cwd = Path.cwd()

# SCOPES = ['https://www.googleapis.com/auth/drive']
# SERVICE_ACCOUNT_FILE = cwd / 'bot' / 'database' / 'service_account.json'


# def authenticate() -> service_account.Credentials:
#     creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     return creds

# creds = authenticate()
# service: Resource = build('drive', 'v3', credentials=creds)

