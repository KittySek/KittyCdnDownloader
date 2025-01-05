import os
import json
import requests
from tqdm import tqdm
import sys
import time

# Configuration
BASE_URL = "https://kittycdn.kittysec.com/"  # Server base URL
CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB
ACCOUNT_FILE = "account.json"
ONBOARDING_SCRIPT = os.path.join("onboarding", "onboarding.py")
TEMP_FOLDER = "TempPart"

# Function to load API key from account.json
def load_api_key():
    if not os.path.exists(ACCOUNT_FILE):
        print(f"'{ACCOUNT_FILE}' not found. Loading onboarding script...")
        if os.path.exists(ONBOARDING_SCRIPT):
            os.system(f"python {ONBOARDING_SCRIPT}")
        else:
            print(f"Error Code: experiment")
            print(f"Onboarding script '{ONBOARDING_SCRIPT}' not found.")
        sys.exit()

    try:
        with open(ACCOUNT_FILE, 'r') as f:
            account_data = json.load(f)
            return account_data.get("API_KEY")
    except json.JSONDecodeError:
        print(f"'{ACCOUNT_FILE}' Error Code: exhibition")
        print(f"'{ACCOUNT_FILE}' contains invalid JSON. Please delete account.json and rerun.")
        sys.exit()
    except Exception as e:
        print(f"An error occurred while reading '{ACCOUNT_FILE}': {e}")
        sys.exit()

# Read API key
API_KEY = load_api_key()
if not API_KEY:
    print("Error Code: coincidence")
    print("API key not found in account.json. Please delete account.json and rerun.")
    sys.exit()

# Function to ensure TempPart folder exists
def ensure_temp_folder():
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)

# Function to split file into .part files
def split_file_into_parts(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        chunk_number = 1
        while chunk := f.read(CHUNK_SIZE):
            part_filename = os.path.join(TEMP_FOLDER, f"{filename}.part{chunk_number}")
            with open(part_filename, 'wb') as part_file:
                part_file.write(chunk)
            chunk_number += 1
    return chunk_number - 1

# Upload a file to the server
def upload_file(filepath):
    try:
        print(f"\nStarting upload for file: {filepath}...")
        ensure_temp_folder()

        # Clone and split the file into parts
        print(f"Cloning and splitting file into parts in {TEMP_FOLDER}...")
        total_chunks = split_file_into_parts(filepath)

        filename = os.path.basename(filepath)
        for chunk_number in range(1, total_chunks + 1):
            part_filepath = os.path.join(TEMP_FOLDER, f"{filename}.part{chunk_number}")
            with open(part_filepath, 'rb') as part_file:
                chunk = part_file.read()
                headers = {"API-KEY": API_KEY}
                files = {"file": (f"{filename}.part{chunk_number}", chunk)}
                data = {
                    "chunk_number": chunk_number,
                    "total_chunks": total_chunks,
                    "original_filename": filename
                }

                print(f"Uploading part {chunk_number}/{total_chunks}...")
                response = requests.post(f"{BASE_URL}/upload", headers=headers, files=files, data=data)

                if response.status_code != 200:
                    print(f"Failed to upload part {chunk_number}: {response.json().get('error', 'Unknown error')}")
                    return

                time.sleep(0.1)  # Delay between uploads

        print(f"\nFile '{filename}' uploaded successfully!")
    except Exception as e:
        print(f"An error occurred during upload: {e}")
    finally:
        # Cleanup TempPart folder
        print(f"Cleaning up temporary parts in {TEMP_FOLDER}...")
        for part_file in os.listdir(TEMP_FOLDER):
            os.remove(os.path.join(TEMP_FOLDER, part_file))
    try:
        print(f"\nStarting upload for file: {filepath}...")
        ensure_temp_folder()

        # Clone and split the file into parts
        print(f"Cloning and splitting file into parts in {TEMP_FOLDER}...")
        total_chunks = split_file_into_parts(filepath)

        filename = os.path.basename(filepath)
        for chunk_number in range(1, total_chunks + 1):
            part_filepath = os.path.join(TEMP_FOLDER, f"{filename}.part{chunk_number}")
            with open(part_filepath, 'rb') as part_file:
                chunk = part_file.read()
                # No API-KEY header here
                files = {"file": (f"{filename}.part{chunk_number}", chunk)}
                data = {
                    "chunk_number": chunk_number,
                    "total_chunks": total_chunks,
                    "original_filename": filename
                }

                print(f"Uploading part {chunk_number}/{total_chunks}...")
                response = requests.post(f"{BASE_URL}/upload", files=files, data=data)

                if response.status_code != 200:
                    print(f"Failed to upload part {chunk_number}: {response.json().get('error', 'Unknown error')}")
                    return

                time.sleep(0.1)  # Delay between uploads

        print(f"\nFile '{filename}' uploaded successfully!")
    except Exception as e:
        print(f"An error occurred during upload: {e}")
    finally:
        # Cleanup TempPart folder
        print(f"Cleaning up temporary parts in {TEMP_FOLDER}...")
        for part_file in os.listdir(TEMP_FOLDER):
            os.remove(os.path.join(TEMP_FOLDER, part_file))

# Function to download a file
def download_file(filename):
    try:
        print(f"\nStarting download for file: {filename}...")

        headers = {"API-KEY": API_KEY}
        response = requests.get(f"{BASE_URL}/download/{filename}", stream=True, headers=headers)

        if response.status_code == 200:
            # Extract original filename from response headers
            file_name = response.headers.get('Content-Disposition', f'filename={filename}').split('filename=')[-1].strip('"')
            print(f"Saving as: {file_name}")

            # Download the file with a progress bar
            with open(file_name, 'wb') as f, tqdm(total=int(response.headers.get('Content-Length', 0)), unit='B', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            print(f"\nFile '{file_name}' downloaded successfully!")
        else:
            print(f"Failed to download file: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to fetch and parse file list
def fetch_file_list():
    try:
        print("\nFetching file list from the server...")
        headers = {"API-KEY": API_KEY}
        response = requests.get(f"{BASE_URL}/api/files", headers=headers)

        if response.status_code == 200:
            file_list = response.json().get("files", [])
            print("\nAvailable files:")
            print(json.dumps({"files": file_list}, indent=2))
        else:
            print(f"Failed to fetch file list: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        print(f"An error occurred while fetching the file list: {e}")

# Main function
def main():
    print("\n=== File Client ===")
    choice = input("Choose an option: [1] Download, [2] Upload, [3] Fetch File List: ").strip()

    if choice == "1":
        filename = input("Enter the filename to download: ").strip()
        if filename:
            download_file(filename)
        else:
            print("Filename cannot be empty.")
    elif choice == "2":
        filepath = input("Enter the full path of the file to upload: ").strip()
        if os.path.exists(filepath):
            upload_file(filepath)
        else:
            print("File does not exist.")
    elif choice == "3":
        fetch_file_list()
    else:
        print("Invalid option. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
