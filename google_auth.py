"""Google OAuth 2.0 Authentication"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/photoslibrary',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

def get_google_service(service_name='photoslibrary', version='v1'):
    """Authenticate with Google and return service object"""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    
    creds = None
    
    # Load existing credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    if service_name == 'photoslibrary':
        return build('photoslibrary', version, credentials=creds)
    elif service_name == 'drive':
        return build('drive', version, credentials=creds)
    
    return None

def setup_google_credentials():
    """Setup Google OAuth credentials interactively"""
    print("\n🔐 Google OAuth Setup")
    print("-" * 50)
    
    # Instructions for getting credentials
    print("""
1. Go to: https://console.cloud.google.com/
2. Create a new project
3. Enable APIs:
   - Google Photos Library API
   - Google Drive API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download JSON and save as 'credentials.json'
    """)
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("Please follow the steps above and try again.")
        return False
    
    print("✅ credentials.json found")
    print("Run the main script to authenticate...")
    return True
