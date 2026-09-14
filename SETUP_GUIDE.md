# 🚀 Step-by-Step Setup Guide

## Prerequisites
- Python 3.8+
- Internet connection
- Accounts for: Google, Dropbox, Anthropic

---

## Step 1: Clone & Install

```bash
# Clone the repository
git clone https://github.com/pmorse42-ui/google-photos-connector.git
cd google-photos-connector

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Google OAuth Setup

### 2a. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Name it "Photo Duplicate Detector"
4. Click "Create"

### 2b. Enable Required APIs

1. Search for "Google Photos Library API" in the search bar
2. Click it → Click "Enable"
3. Search for "Google Drive API"
4. Click it → Click "Enable"

### 2c. Create OAuth Credentials

1. Go to "Credentials" in the left menu
2. Click "Create Credentials" → "OAuth client ID"
3. If asked, configure OAuth consent screen:
   - Choose "External"
   - Fill in app name: "Photo Duplicate Detector"
   - Add your email
   - Save and continue
4. Select "Desktop application"
5. Click "Create"
6. Click "Download" (downloads JSON file)
7. Save as `credentials.json` in your project folder

**Important OAuth Scopes:**
The script requests these scopes automatically:
- `photoslibrary.readonly` - Read photos
- `photoslibrary` - Write/manage photos
- `drive` - Read/write Google Drive
- `drive.file` - File-specific Drive access

✅ **Check:** `credentials.json` should be in the main directory

---

## Step 3: Dropbox Setup

### 3a. Create Dropbox App

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click "Create app"
3. Choose:
   - API: Scoped access
   - Type of access: Full Dropbox
   - App name: photo-duplicate-detector
4. Click "Create app"

### 3b. Generate Access Token

1. In your app settings, go to the "Generated access token" section
2. Click "Generate"
3. Copy the token (you'll use it next)

---

## Step 4: Anthropic Claude API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Go to "API Keys" section
4. Click "Create Key"
5. Copy your API key

---

## Step 5: Create .env File

1. In your project folder, create a file named `.env`
2. Add these lines (replace with your actual values):

```
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET
DROPBOX_ACCESS_TOKEN=YOUR_DROPBOX_TOKEN
ANTHROPIC_API_KEY=YOUR_CLAUDE_API_KEY
STORAGE_PATH=./storage
DUPLICATES_FOLDER=./Duplicates from google
```

**How to find these values:**

- **GOOGLE_CLIENT_ID & SECRET:** In `credentials.json` file (open with text editor)
  - Look for `"client_id"` and `"client_secret"`

- **DROPBOX_ACCESS_TOKEN:** You generated this in Step 3b

- **ANTHROPIC_API_KEY:** You copied this in Step 4

- **DUPLICATES_FOLDER:** Leave as is (creates folder named "Duplicates from google")

---

## Step 6: First Run

```bash
python duplicate_detector.py
```

### On First Run:
1. A browser window will open for Google authentication
2. Sign in with your Google account
3. Grant permissions for:
   - Google Photos Library access
   - Google Drive access
   - Ability to manage files
4. The script will automatically save your credentials

---

## Step 7: Review Results

Results are automatically saved to:
- `storage/duplicates_TIMESTAMP.json` - Duplicate analysis
- `storage/download_log_TIMESTAMP.json` - Files downloaded and moved
- `Duplicates from google/` - All downloaded duplicate files

### Example Output Structure

```
Duplicates from google/
├── google_photos_vacation_2024.jpg
├── google_drive_photo_001.jpg
├── google_drive_photo_001_v2.jpg
├── dropbox_backup_photo.png
└── ...
```

---

## What Happens to Your Files

### Files That Are Kept
✅ One copy remains in its original location
- Usually the Google Photos copy (best quality)
- Original files are NOT deleted

### Files That Are Downloaded
⬇️ All duplicate copies are downloaded to "Duplicates from google" folder
- Organized by source (google_photos_, google_drive_, dropbox_)
- Local backup of everything

### Files That Are Moved
🗑️ Google Drive duplicates are moved to trash
- NOT permanently deleted - you can recover them
- Trash auto-purges after 30 days
- Dropbox files are only downloaded, not deleted

---

## Common Issues & Fixes

### ❌ "credentials.json not found"
**Solution:** 
1. Make sure you downloaded the Google OAuth JSON file
2. Save it exactly as `credentials.json` in the main folder
3. Run the script again

### ❌ "ANTHROPIC_API_KEY not found in .env"
**Solution:** 
1. Create `.env` file (if missing)
2. Add: `ANTHROPIC_API_KEY=your_key_here`
3. Save and run again

### ❌ "Invalid Dropbox token"
**Solution:**
1. Go back to Dropbox App Console
2. Generate a new access token
3. Update `.env` with new token
4. Run script again

### ❌ "No files found in any cloud storage"
**Solution:**
- Make sure you have photos/images in each service
- Check that OAuth permissions were fully granted
- Try running again (sometimes first run needs retry)
- Verify you have internet connection

### ❌ "Permission denied when moving Google Drive files"
**Solution:**
- Make sure you authorized the script with write permissions
- Re-run the first step to re-authenticate
- Check that your Google Cloud project has Drive API enabled

### ❌ Script runs but finds no duplicates
**This is normal!** If you don't have many duplicate photos across services, the detector won't find any.

### ❌ Out of disk space
**Solution:**
- Free up local storage
- Run script again
- You can delete the `Duplicates from google` folder after verifying files

---

## Next Steps

Once setup is complete:

1. **Run the detector:** `python duplicate_detector.py`
2. **Review results** in `storage/` folder and console output
3. **Check the "Duplicates from google" folder** to see downloaded copies
4. **Verify confidence levels** before final cleanup
5. **Optional:** Manually delete from "Duplicates from google" when satisfied

---

## Security Checklist

- ✅ Never share your `.env` file
- ✅ Keep `credentials.json` private
- ✅ Don't commit API keys to GitHub
- ✅ Revoke tokens if you stop using the app
- ✅ `.gitignore` already protects these files
- ✅ All credentials stored locally only

---

## Advanced: Manual OAuth Re-authentication

If your credentials expire:

```bash
# Delete old credentials
rm token.pickle

# Run script again to re-authenticate
python duplicate_detector.py
```

---

## Advanced: Multiple Runs

You can run the script multiple times:
- Each run generates new result files with timestamps
- Previous results are preserved
- Downloaded duplicates folder accumulates files

To start fresh:
```bash
rm -rf Duplicates\ from\ google/
rm -rf storage/
python duplicate_detector.py
```

---

## Need Help?

1. Check error messages carefully
2. Review the troubleshooting section above
3. Verify all APIs are enabled in Google Cloud
4. Ensure all tokens are current and valid
5. Check internet connection
6. Make sure you have space available locally

Good luck! 🎉
