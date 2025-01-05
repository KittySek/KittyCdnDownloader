import os
import json
import requests

API_CHECK_URL = "http://KittyCdn.KittySec.com/check_api_key"
ACCOUNT_FILE = "account.json"

def save_api_key(api_key):
    account_data = {"API_KEY": api_key}
    with open(ACCOUNT_FILE, "w") as f:
        json.dump(account_data, f, indent=4)
    print("\nYour API key has been saved successfully in 'account.json'.")

def load_api_key():
    if os.path.exists(ACCOUNT_FILE):
        with open(ACCOUNT_FILE, "r") as f:
            account_data = json.load(f)
            return account_data.get("API_KEY")
    return None

def check_api_key(api_key):
    try:
        response = requests.post(API_CHECK_URL, json={"API_KEY": api_key})
        if response.status_code == 200:
            data = response.json()
            if data.get("exists"):
                return data.get("data")
        return None
    except Exception as e:
        print(f"Error checking API key: {e}")
        return None

def welcome_user():
    print("""
========================================
       Welcome to Kitty Downloader!       
========================================
    
Kitty Downloader is your all-in-one tool for seamless file uploads and downloads. Before you begin, please ensure you are a part of our Discord community.

Join our Discord server to stay updated, get support, and connect with other users:
Discord Link: https://discord.gg/zjn7z36Y58
    """)

def verify_discord_membership():
    while True:
        in_discord = input("Have you joined our Discord server? (yes/no): ").strip().lower()
        if in_discord in ["yes", "y"]:
            print("\nThank you for joining our community! Let's proceed.")
            break
        elif in_discord in ["no", "n"]:
            print("\nPlease join our Discord server at https://discord.gg/zjn7z36Y58 before proceeding.")
        else:
            print("\nInvalid input. Please type 'yes' or 'no'.")

def get_api_key():
    while True:
        api_key = input("\nPlease enter your API key: ").strip()
        if api_key:
            return api_key
        else:
            print("\nAPI key cannot be empty. Please try again.")

def onboarding():
    welcome_user()
    verify_discord_membership()

    existing_api_key = load_api_key()
    if existing_api_key:
        print("\nChecking your saved API key...")
        data = check_api_key(existing_api_key)
        if data:
            holders_name = data.get("HoldersName", "User")
            print(f"\nWelcome back, {holders_name}! You're all set to use Kitty Downloader.")
            return
        else:
            print("\nYour saved API key is invalid or not found. Please re-enter it.")

    while True:
        api_key = get_api_key()
        data = check_api_key(api_key)
        if data:
            holders_name = data.get("HoldersName", "User")
            print(f"\nWelcome, {holders_name}! Your API key is valid.")
            save_api_key(api_key)
            break
        else:
            print("\nThe provided API key is invalid or not found. Please try again.")

    print("\nOnboarding complete! You can now start using Kitty Downloader.")

if __name__ == "__main__":
    onboarding()
