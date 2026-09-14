# 🖼️ Multi-Cloud Duplicate Photo Detector & Manager

Automatically detect and manage duplicate photos across **Google Photos**, **Google Drive**, and **Dropbox** using AI-powered analysis with Claude. Downloads duplicates to a centralized folder and moves originals to trash.

## Features

✨ **Multi-Cloud Support**
- Google Photos Library
- Google Drive (images)
- Dropbox

🤖 **AI-Powered Detection**
- Uses Claude to analyze photos
- Identifies duplicates by filename, size, date, and visual similarity
- Confidence levels for each match
- Smart selection of which copy to keep

⬇️ **Automatic Download Management**
- Downloads all duplicate copies to "Duplicates from google" folder
- Moves Google Drive duplicates to trash
- Keeps the best quality copy in original location
- Detailed download log with file paths

📊 **Batch Operations**
- Process multiple files efficiently
- Generate detailed reports with confidence scores
- Export results and download logs as JSON
- Track all operations for verification

## Key Features

### Duplicate Handling
- ✅ **Keeps one copy**: Intelligently selects which file to keep (prefers Google Photos)
- ⬇️ **Downloads others**: All duplicate copies downloaded to "Duplicates from google" folder
- 🗑️ **Moves originals**: Google Drive duplicates moved to trash (recoverable)
- 📋 **Detailed logging**: Every action tracked in download_log.json

### Folder Structure
```
Duplicates from google/
├── google_photos_vacation_2024.jpg
├── google_drive_photo_001.jpg
├── google_drive_photo_001_v2.jpg
├── dropbox_backup_photo.png
└── ...
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable these APIs:
   - **Google Photos Library API**
   - **Google Drive API**
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the JSON file and save it as `credentials.json` in the project root

**Important:** Google Photos Library API requires these scopes:
- `photoslibrary.readonly` - to read your photos
- `photoslibrary` - to manage photos (move, delete)
- `drive` - to manage Google Drive files
- `drive.file` - for file-specific permissions

### 3. Setup Dropbox Access Token

1. Go to [Dropbox Developers](https://www.dropbox.com/developers/apps)
2. Create a new app
3. Choose "Scoped access" and "Full Dropbox"
4. Generate an access token

### 4. Setup Claude API Key

1. Get your API key from [Anthropic Console](https://console.anthropic.com/)

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:
```
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
DROPBOX_ACCESS_TOKEN=your_dropbox_token
ANTHROPIC_API_KEY=your_claude_api_key
STORAGE_PATH=./storage
DUPLICATES_FOLDER=./Duplicates from google
```

## Usage

### Run Duplicate Detection & Management

```bash
python duplicate_detector.py
```

### What It Does

1. 🔐 Authenticates with all cloud services
2. 📸 Fetches photos/images metadata from all sources
3. 🤖 Analyzes with Claude AI to find duplicates
4. ⬇️ Downloads all duplicate copies
5. 🗑️ Moves Google Drive duplicates to trash
6. 💾 Saves detailed results and logs
7. 📊 Displays summary report

### Example Output

```
============================================================
🔍 Multi-Cloud Duplicate Photo Detector & Manager
============================================================

📸 Fetching from Google Photos...
✅ Found 245 items in Google Photos

🔍 Fetching from Google Drive...
✅ Found 89 images in Google Drive

📁 Fetching from Dropbox...
✅ Found 156 images in Dropbox

📊 Total files found: 490

🤖 Analyzing with Claude AI...
Analyzing batches: 100%|████| 25/25

🔄 Processing Duplicates...

📋 Processing Group 1...
   ✅ KEEPING: google_photos - vacation_2024.jpg
   ⬇️  DOWNLOADED: google_drive - vacation_2024.jpg
   ⬇️  DOWNLOADED: dropbox - vacation_2024.jpg

📋 Processing Group 2...
   ✅ KEEPING: google_photos - photo_001.png
   ⬇️  DOWNLOADED: google_drive - photo_001.png

============================================================
🎯 DUPLICATE GROUPS FOUND & PROCESSED
============================================================

📋 Group 1 (Confidence: HIGH)
   Reason: Identical filename and size, same creation date
   Files:
     ✅ KEPT • google_photos: vacation_2024.jpg
     ⬇️ DOWNLOADED • google_drive: vacation_2024.jpg
     ⬇️ DOWNLOADED • dropbox: vacation_2024.jpg

📋 Group 2 (Confidence: MEDIUM)
   Reason: Similar filename, same dimensions, close dates
   Files:
     ✅ KEPT • google_photos: photo_001.png
     ⬇️ DOWNLOADED • google_drive: photo_001.png

============================================================
💾 Total duplicate groups found: 12
📁 Duplicates saved to: /path/to/Duplicates from google
📋 Files downloaded: 24
============================================================
```

## Results & Logs

### Duplicate Analysis (`duplicates_TIMESTAMP.json`)
```json
{
  "timestamp": "2024-09-14T10:30:45.123456",
  "duplicate_groups": [
    {
      "files": [
        {"source": "google_photos", "id": "abc123", "filename": "vacation.jpg"},
        {"source": "google_drive", "id": "def456", "filename": "vacation.jpg"}
      ],
      "keep_file": {"source": "google_photos", "id": "abc123"},
      "confidence": "high",
      "reason": "Same filename, size, and creation date"
    }
  ],
  "total_duplicates": 12,
  "duplicates_folder": "/path/to/Duplicates from google"
}
```

### Download Log (`download_log_TIMESTAMP.json`)
```json
[
  {
    "source": "google_drive",
    "filename": "vacation.jpg",
    "file_id": "def456",
    "local_path": "/path/to/Duplicates from google/google_drive_vacation.jpg",
    "action": "downloaded_and_marked_for_removal"
  }
]
```

## File Structure

```
google-photos-connector/
├── duplicate_detector.py         # Main detection & management script
├── google_auth.py               # Google OAuth 2.0 setup
├── dropbox_auth.py              # Dropbox OAuth setup
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment config template
├── .env                         # Your actual credentials (git-ignored)
├── .gitignore                   # Git ignore patterns
├── README.md                    # This file
├── SETUP_GUIDE.md              # Detailed setup instructions
├── storage/                     # Results folder
│   ├── duplicates_*.json       # Duplicate analysis results
│   └── download_log_*.json     # Download tracking logs
└── Duplicates from google/      # Downloaded duplicate files
    ├── google_photos_*.jpg
    ├── google_drive_*.png
    └── dropbox_*.jpg
```

## Important Notes

⚠️ **Before Running:**
- Back up important files before first run
- Review results before deleting anything from cloud storage
- The tool moves Google Drive duplicates to trash (recoverable for 30 days)
- Google Photos duplicates are NOT deleted - only downloaded

✅ **Security:**
- Never commit `.env`, `credentials.json`, or `token.pickle`
- These are protected by `.gitignore`
- Tokens are stored locally only

🔒 **Permissions Required:**
- Google Photos: Read and write access
- Google Drive: Read and write access (to move to trash)
- Dropbox: Read access (only downloads)

## Troubleshooting

### "credentials.json not found"
Save your Google OAuth JSON file as `credentials.json` in the project root

### "ANTHROPIC_API_KEY not found"
Add your Claude API key to `.env` file

### "No files found in any cloud storage"
- Ensure you have photos/images in each service
- Verify OAuth permissions were fully granted
- Check that credentials are still valid

### "Invalid Dropbox token"
Generate a new token from Dropbox App Console and update `.env`

### Files not downloading
- Check internet connection
- Verify file permissions in cloud services
- Ensure enough local disk space
- Check if files were moved to trash instead

## Safety Features

✅ **Google Drive duplicates moved to trash** (not permanently deleted)
✅ **Downloaded copies saved locally** (before deletion)
✅ **Detailed logging** (all operations tracked)
✅ **Confidence scoring** (only removes high-confidence duplicates)
✅ **No automatic deletion** (you verify everything first)

## License

MIT

## Support

For issues or questions:
1. Review the troubleshooting section
2. Check setup instructions in SETUP_GUIDE.md
3. Verify all APIs are enabled in Google Cloud
4. Ensure all tokens are current and valid
