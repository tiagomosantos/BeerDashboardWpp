import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import io

# The SCOPES variable defines the permissions required for Google Drive API.
# 'https://www.googleapis.com/auth/drive' allows full access to a user's Drive.
SCOPES = ['https://www.googleapis.com/auth/drive']
api_service_name = 'drive'
api_version = 'v3'

# Function to handle authentication with Google Drive API
def authenticate():
    creds = None
    # Check if the 'token.json' file already exists (stores user credentials). 
    # If present, use this to authenticate without needing to re-login.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If no valid credentials are found, initiate a new login process.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh expired credentials.
        else:
            # Start OAuth flow by loading 'credentials.json' and allowing the user to log in.
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the new credentials to 'token.json' for future use.
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Build the Google Drive API service object using the authenticated credentials.
        service = build(api_service_name, api_version, credentials=creds)
    except Exception as e:
        # Handle errors in case the service object creation fails.
        print(f"Failed to create service object: {e}")
        service = None

    return service  # Return the service object for interacting with Google Drive API.

# Function to list all files in a specified folder on Google Drive
def list_files_in_folder(service, folder_id):
    # Query to find all files that are not in the trash and belong to the specified folder.
    query = f"'{folder_id}' in parents and trashed=false"
    # Execute the API call to list files, requesting their ID and name.
    results = service.files().list(q=query, pageSize=100, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        # If no files are found, return an empty list.
        return []
    return items  # Return the list of files in the folder.

# Function to delete all files in a folder except the most recently uploaded one
def delete_all_except_last_uploaded(service, folder_id):
    # Query to find all files in the folder that aren't in the trash.
    query = f"'{folder_id}' in parents and trashed=false"
    # Execute the API call to list files, including their created time.
    results = service.files().list(q=query, fields="nextPageToken, files(id, name, createdTime)").execute()
    items = results.get('files', [])

    if not items:
        # If no files are found, exit the function.
        return

    # Sort files by creation time in descending order (newest first).
    items.sort(key=lambda x: x['createdTime'], reverse=True)

    # Keep the most recently uploaded file and store the rest for deletion.
    last_uploaded_file = items[0]
    files_to_delete = items[1:]

    # Attempt to delete each file except the last uploaded one.
    for file in files_to_delete:
        try:
            service.files().delete(fileId=file['id']).execute()
        except Exception as e:
            print(f"Failed to delete {file['name']} (ID: {file['id']}). Reason: {e}")

    # Rename the last uploaded file to 'chat_data.zip'.
    try:
        file_id = last_uploaded_file['id']
        new_name = 'chat_data.zip'
        service.files().update(fileId=file_id, body={'name': new_name}).execute()
    except Exception as e:
        print(f"Failed to rename file ID: {file_id}. Reason: {e}")

# Function to download a file from Google Drive by its name
def download_file(service, folder_id, file_name, download_path):
    # Query to find the file with the given name in the specified folder.
    query = f"'{folder_id}' in parents and trashed=false and name='{file_name}'"
    # Execute the API call to find the file ID by name.
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        # If the file is not found, exit the function.
        return

    # Assuming there's only one file with the name, use its ID to download it.
    file_id = items[0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(download_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    # Download the file in chunks.
    done = False
    while not done:
        status, done = downloader.next_chunk()

# Function to get the ID of the most recently created file in a folder
def get_latest_file(service, folder_id='1x7v5YqdVp_deQ9q61l2McgdQgSPk30QQ'):
    # Query to get the most recent file (sorted by created time in descending order).
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, orderBy='createdTime desc', pageSize=1, fields="files(id, name, createdTime)").execute()
    items = results.get('files', [])

    if not items:
        # If no files are found, return None.
        return None

    # Return the ID of the most recently created file.
    last_created_file = items[0]
    return last_created_file['id']

# Function to get the file ID by file name in a specific folder
def get_file_id_by_name(service, file_name, folder_id='1x7v5YqdVp_deQ9q61l2McgdQgSPk30QQ'):
    # Query to find the file by name in the specified folder.
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed = false"
    
    # Execute the API call to find the file by name.
    results = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)').execute()
    items = results.get('files', [])

    # If found, return the file's ID; otherwise, return None.
    if items:
        return items[0]['id']
    else:
        return None
