import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CLIENT_SECRET_FILE = r'credentials.json' # replace credentials.json with the path to your .json file for your OAuth 2.0 Client ID
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

LOCAL_FOLDER = r'path_to_your_local_folder'

def listFiles(service, folderID):
    results = service.files().list(q=f"'{folderID}' in parents", fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    return files

def downloadFiles(service, file_id, LOCAL_FOLDER):
    request = service.files().get_media(fileId = file_id)
    fileInfo = service.files().get(fileId = file_id, fields = "name").execute()
    fileName = fileInfo.get('name', '')
    filePath = os.path.join(LOCAL_FOLDER, fileName)

    with open(filePath, 'wb') as file:
        file.write(request.execute())

    print(f'File downloaded: {fileName}')

def main():
    
    creds = None
    if os.path.exists("token.json") and os.path.getsize("token.json") > 0:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    
    else:
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

    if creds is not None:
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build(API_NAME, API_VERSION, credentials=creds)

    driveFolderID = 'your_drive_folder_ID'

    driveFiles = listFiles(service, driveFolderID)
    localFiles = set([file.replace(".id", "") for file in os.listdir(LOCAL_FOLDER) if os.path.isfile(os.path.join(LOCAL_FOLDER, file))])
    filesToDownload = [file for file in driveFiles if file['id'] not in localFiles]

    for file in filesToDownload:
        downloadFiles(service, file['id'], LOCAL_FOLDER)

if __name__ == "__main__":
  main()
