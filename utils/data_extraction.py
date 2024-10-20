import os 
import emoji
import re
import pandas as pd
import shutil
import datetime

# Function to read the file and return its content
def read_file(file_path):
    # Open and read the file with UTF-8 encoding, returning the lines as a list.
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

# Function to parse the chat log using a regular expression pattern to extract date, time, author, and message
def parse_chat(lines):
    # Define a regular expression pattern to match the date, time, author, and message in the chat log.
    pattern = re.compile(r'(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}) - (.*?): (.*)')
    chat_data = []
    
    # Loop through each line and attempt to match it with the pattern.
    for line in lines:
        match = pattern.match(line)
        if match:
            # Extract date, time, author, and message from the matched pattern.
            date, time, author, message = match.groups()
            # Convert the date string to a datetime object for easier manipulation later.
            date = datetime.datetime.strptime(date, "%d/%m/%y")
            # Append the parsed data (date, time, author, message) as a tuple to the chat_data list.
            chat_data.append((date, time, author, message))
    
    return chat_data

# Function to extract emojis from the chat messages
def extract_emojis(chat_data):
    # Define a mapping between specific emojis and their descriptions.
    emoji_mapping = {'🍺': 'mini', '🍻': 'média', '🍾': 'litrosa', '🍷': 'vinho'}
    data = []

    # Loop through each entry in the chat data.
    for date, time, author, message in chat_data:
        # For each emoji in the mapping, count how many times it appears in the message.
        for emoji in emoji_mapping.keys():
            count = message.count(emoji)
            # Append a new entry for each occurrence of the emoji.
            for _ in range(count):
                data.append((date, time, author, emoji))
    
    return data

# Function to load and process the chat data into a DataFrame
def load_data(file_path):
    # Read the file's content
    lines = read_file(file_path)
    
    # Parse the chat data from the lines
    chat_data = parse_chat(lines)
    
    # Extract emojis from the chat data
    emoji_data = extract_emojis(chat_data)
    
    # Create a DataFrame from the emoji data, with columns for Date, Hour, Author (Pessoa), and Emoji.
    df = pd.DataFrame(emoji_data, columns=['Date', 'Hour', 'Pessoa', 'Emoji'])

    # Replace the extracted emojis with their corresponding descriptions.
    emoji_replacements = {
            emoji.emojize(':beer_mug:'): 'Mini',
            emoji.emojize(':bottle_with_popping_cork:'): 'Litrosa',
            emoji.emojize(':clinking_beer_mugs:'): 'Média',
            emoji.emojize(':wine_glass:'): 'Vinho',
    }
    df['Emoji'] = df['Emoji'].replace(emoji_replacements)

    # Map each emoji description to its corresponding volume (in liters).
    emoji_volumes = {
        'Mini': 0.25,
        'Litrosa': 1.0,
        'Média': 0.33,
        'Vinho': 0.25,
    }
    df['Quantidade (L)'] = df['Emoji'].map(emoji_volumes)  # Map emoji to volume
    df['Quantidade'] = 1  # Add a quantity column (always 1 for each emoji)

    # Format the date column as a string with the format 'dd/mm/YYYY'.
    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')

    return df  # Return the final DataFrame with parsed data.

# Function to delete all files in a specified folder
def delete_all_files_in_folder(folder_path):
    # Loop through all files in the folder.
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            # If it's a file or a symbolic link, delete it.
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # If it's a directory, delete it and its contents.
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            # Print any errors that occur during deletion.
            print(f'Failed to delete {file_path}. Reason: {e}')

# Function to delete all files in a folder except for .txt files
def delete_files_except_txt(folder_path):
    try:
        # Get a list of all files in the folder.
        files = os.listdir(folder_path)
        
        # Loop through each file.
        for file in files:
            # Create the full file path.
            file_path = os.path.join(folder_path, file)
            
            # Check if the file is not a .txt file.
            if os.path.isfile(file_path) and not file.lower().endswith('.txt'):
                # Delete the file.
                os.remove(file_path)
    except Exception as e:
        # Print any errors that occur.
        print(f"An error occurred: {e}")

# Function to rename a unique .txt file in a folder to '_chat.txt'
def rename_unique_txt(folder_path):
    try:
        # Get a list of all files in the folder.
        files = os.listdir(folder_path)
        
        # Filter out files that have the .txt extension.
        txt_files = [file for file in files if os.path.isfile(os.path.join(folder_path, file)) and file.lower().endswith('.txt')]
        
        # Check if there is exactly one .txt file.
        if len(txt_files) == 1:
            # Get the full file path for renaming.
            old_file_path = os.path.join(folder_path, txt_files[0])
            new_file_path = os.path.join(folder_path, '_chat.txt')
            
            # Rename the file.
            os.rename(old_file_path, new_file_path)
        elif len(txt_files) == 0:
            print("No .txt files found in the folder.")
        else:
            print("Multiple .txt files found in the folder.")
    except Exception as e:
        # Print any errors that occur.
        print(f"An error occurred: {e}")
