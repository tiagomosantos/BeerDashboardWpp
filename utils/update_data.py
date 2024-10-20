from utils.google_api import download_file, delete_all_except_last_uploaded
import zipfile
from utils.data_extraction import delete_files_except_txt, rename_unique_txt
import time

def update_chat_data(service):
    # Define the Google Drive folder ID where the chat data is stored.
    folder_id = '1x7v5YqdVp_deQ9q61l2McgdQgSPk30QQ'  
    # Define the name of the ZIP file that contains the chat data.
    file_name = 'chat_data.zip'   
    # Define the path where the ZIP file will be downloaded.
    download_path = 'data/chat_data.zip' 
    # Define the local folder where the unzipped files will be extracted.
    data_folder = 'data'    

    # Step 1: Delete all files in the Google Drive folder except the most recent one.
    # This ensures that only the last uploaded file is kept in the folder.
    delete_all_except_last_uploaded(service, folder_id)

    # Step 2: Download the last uploaded file (chat_data.zip) from Google Drive.
    # This file contains the chat data that will be processed locally.
    download_file(service, folder_id, file_name, download_path)

    # Step 3: Introduce a delay (5 seconds) to ensure the download completes before proceeding.
    time.sleep(5)

    # Step 4: Unzip the downloaded file into the specified data folder.
    # This will extract all the files inside 'chat_data.zip' to the 'data' directory.
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(data_folder)

    # Step 5: Introduce another delay (5 seconds) after extraction.
    time.sleep(5)

    # Step 6: Delete all non-.txt files in the extracted folder.
    # This function removes any file that isn't a .txt file, ensuring only chat data files remain.
    delete_files_except_txt(data_folder)

    # Step 7: Rename the remaining .txt file in the folder to '_chat.txt', provided there is exactly one.
    # If there are multiple or no .txt files, it handles those cases with appropriate messages.
    rename_unique_txt(data_folder)
