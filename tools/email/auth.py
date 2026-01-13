"""
OAuth2 authentication module for Gmail API.
Handles credential management and token refresh for multiple accounts.
"""

import os
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only access to Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Base directory
BASE_DIR = Path(__file__).parent

# Available accounts (subdirectories with credentials)
# Add your account subdirectories here - each needs client_secret*.json
# Example: Create folders like 'personal/' and 'work/' with OAuth credentials
ACCOUNTS = {
    # 'account_name': BASE_DIR / 'account_name',
    # 'work': BASE_DIR / 'work',
}

# Example configuration (uncomment and modify):
# ACCOUNTS = {
#     'personal': BASE_DIR / 'personal',
#     'work': BASE_DIR / 'work',
# }


def find_client_secret(directory: Path) -> Optional[Path]:
    """Find any client_secret*.json file in the directory."""
    patterns = [
        'client_secret*.json',
        'credentials*.json',
        'oauth*.json',
    ]
    for pattern in patterns:
        matches = list(directory.glob(pattern))
        if matches:
            return matches[0]
    return None


def get_credentials(account: str = 'matbanik') -> Credentials:
    """
    Get valid OAuth2 credentials for specified account.
    
    Args:
        account: Account name ('matbanik' or 'banikm')
    
    Returns:
        Valid Credentials object.
    """
    if account not in ACCOUNTS:
        available = ', '.join(ACCOUNTS.keys())
        raise ValueError(f"Unknown account '{account}'. Available: {available}")
    
    account_dir = ACCOUNTS[account]
    token_file = account_dir / 'token.pickle'
    client_secret_file = find_client_secret(account_dir)
    
    creds = None
    
    # Load existing token if available
    if token_file.exists():
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"[{account}] Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not client_secret_file or not client_secret_file.exists():
                raise FileNotFoundError(
                    f"No OAuth client secret file found in {account_dir}\n\n"
                    "To create one:\n"
                    "1. Go to https://console.cloud.google.com/\n"
                    "2. Create or select a project\n"
                    "3. Enable Gmail API (APIs & Services → Library → Gmail API)\n"
                    "4. Create OAuth credentials (APIs & Services → Credentials → Create → OAuth client ID → Desktop app)\n"
                    f"5. Download JSON and save in {account_dir}/\n"
                )
            
            print(f"[{account}] Starting OAuth2 authorization flow...")
            print("A browser window will open for you to authorize access.")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret_file), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        print(f"[{account}] Credentials saved to {token_file}")
    
    return creds


def get_gmail_service(account: str = 'matbanik'):
    """
    Build and return an authenticated Gmail API service.
    
    Args:
        account: Account name ('matbanik' or 'banikm')
    
    Returns:
        Gmail API service object.
    """
    creds = get_credentials(account)
    service = build('gmail', 'v1', credentials=creds)
    return service


def get_all_accounts() -> list[str]:
    """Get list of available account names."""
    return list(ACCOUNTS.keys())


if __name__ == '__main__':
    import sys
    
    # Allow testing specific account
    if len(sys.argv) > 1:
        accounts = [sys.argv[1]]
    else:
        accounts = get_all_accounts()
    
    for account in accounts:
        print(f"\nTesting account: {account}")
        try:
            service = get_gmail_service(account)
            profile = service.users().getProfile(userId='me').execute()
            print(f"  ✓ Successfully authenticated as: {profile['emailAddress']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
