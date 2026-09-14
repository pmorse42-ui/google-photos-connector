"""Dropbox OAuth 2.0 Authentication"""
import os
from dotenv import load_dotenv
import dropbox
from dropbox.exceptions import AuthError

load_dotenv()

def get_dropbox_client():
    """Get authenticated Dropbox client"""
    token = os.getenv('DROPBOX_ACCESS_TOKEN')
    
    if not token:
        print("\n❌ DROPBOX_ACCESS_TOKEN not found in .env")
        print("Please add your Dropbox access token to .env file")
        return None
    
    try:
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()
        print("✅ Connected to Dropbox")
        return dbx
    except AuthError as e:
        print(f"❌ Dropbox authentication failed: {e}")
        return None

def setup_dropbox_token():
    """Setup Dropbox authentication"""
    print("\n🔐 Dropbox OAuth Setup")
    print("-" * 50)
    print("""
1. Go to: https://www.dropbox.com/developers/apps
2. Create a new app
3. Choose 'Scoped access' and 'Full Dropbox'
4. Generate an access token
5. Add to .env: DROPBOX_ACCESS_TOKEN=your_token
    """)
