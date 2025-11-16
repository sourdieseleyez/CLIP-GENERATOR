"""
YouTube OAuth setup script
Run this once to authenticate: python backend/youtube_setup.py
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 
          'https://www.googleapis.com/auth/youtube.readonly']

def setup_youtube_auth():
    """Run OAuth flow to get YouTube credentials"""
    creds = None
    token_path = 'youtube_token.pickle'
    
    # Check if we already have credentials
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            # Need client secrets file
            if not os.path.exists('client_secrets.json'):
                print("\n❌ Error: client_secrets.json not found!")
                print("\nTo get this file:")
                print("1. Go to: https://console.cloud.google.com/")
                print("2. Create a project (or select existing)")
                print("3. Enable YouTube Data API v3")
                print("4. Create OAuth 2.0 credentials (Desktop app)")
                print("5. Download JSON and save as 'client_secrets.json'")
                print("\nThen run this script again.")
                return False
            
            print("\n🔐 Starting YouTube OAuth flow...")
            print("Your browser will open. Please authorize the app.\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', 
                SCOPES
            )
            creds = flow.run_local_server(port=8080)
        
        # Save credentials
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        
        print("\n✅ YouTube authentication successful!")
        print(f"Credentials saved to: {token_path}")
        return True
    else:
        print("✅ YouTube already authenticated!")
        return True

if __name__ == "__main__":
    setup_youtube_auth()
