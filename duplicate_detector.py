"""
Multi-cloud Duplicate Photo Detector & Manager
Detects duplicates across Google Photos, Google Drive, and Dropbox
Moves/downloads duplicates to a centralized folder
Uses AI (Claude) to identify duplicates
"""

import os
import hashlib
import json
import io
import requests
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import anthropic
from googleapiclient.http import MediaIoBaseDownload

load_dotenv()

class DuplicateManager:
    def __init__(self):
        self.storage_path = Path('./storage')
        self.storage_path.mkdir(exist_ok=True)
        
        # Create "Duplicates from google" folder
        duplicates_folder = os.getenv('DUPLICATES_FOLDER', './Duplicates from google')
        self.duplicates_path = Path(duplicates_folder)
        self.duplicates_path.mkdir(exist_ok=True)
        
        self.duplicates = []
        self.file_hashes = {}
        self.file_metadata = {}
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.download_log = []
    
    def calculate_file_hash(self, file_path, algorithm='md5'):
        """Calculate hash of a file"""
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def download_google_drive_file(self, service, file_id, filename):
        """Download file from Google Drive"""
        try:
            request = service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False
            
            while not done:
                status, done = downloader.next_chunk()
            
            file_handle.seek(0)
            
            # Save to duplicates folder
            safe_filename = self.sanitize_filename(filename)
            file_path = self.duplicates_path / f"google_drive_{safe_filename}"
            
            with open(file_path, 'wb') as f:
                f.write(file_handle.getvalue())
            
            return str(file_path)
        except Exception as e:
            print(f"❌ Error downloading Google Drive file: {e}")
            return None
    
    def download_google_photos_file(self, url, filename):
        """Download file from Google Photos"""
        try:
            response = requests.get(f"{url}=d")  # =d forces download
            if response.status_code == 200:
                safe_filename = self.sanitize_filename(filename)
                file_path = self.duplicates_path / f"google_photos_{safe_filename}"
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                return str(file_path)
        except Exception as e:
            print(f"❌ Error downloading Google Photos file: {e}")
        
        return None
    
    def download_dropbox_file(self, dbx, path, filename):
        """Download file from Dropbox"""
        try:
            metadata, response = dbx.files_download(path)
            
            safe_filename = self.sanitize_filename(filename)
            file_path = self.duplicates_path / f"dropbox_{safe_filename}"
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return str(file_path)
        except Exception as e:
            print(f"❌ Error downloading Dropbox file: {e}")
        
        return None
    
    def move_google_drive_file(self, service, file_id, filename):
        """Move Google Drive file to trash (equivalent of moving)"""
        try:
            # Instead of deleting, move to trash
            service.files().update(
                fileId=file_id,
                body={'trashed': True}
            ).execute()
            
            return True
        except Exception as e:
            print(f"⚠️  Error moving Google Drive file to trash: {e}")
            return False
    
    def sanitize_filename(self, filename):
        """Sanitize filename for safe file system storage"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def fetch_google_photos(self):
        """Fetch metadata from Google Photos"""
        print("\n📸 Fetching from Google Photos...")
        from google_auth import get_google_service
        
        try:
            service = get_google_service('photoslibrary', 'v1')
            photos_data = []
            
            request = service.mediaItems().list(pageSize=100)
            
            while request:
                results = request.execute()
                items = results.get('mediaItems', [])
                
                for item in items:
                    photo_info = {
                        'source': 'google_photos',
                        'id': item['id'],
                        'filename': item['filename'],
                        'url': item['baseUrl'],
                        'created': item.get('mediaMetadata', {}).get('creationTime', ''),
                        'size': item.get('mediaMetadata', {}).get('width', 0) * item.get('mediaMetadata', {}).get('height', 0),
                    }
                    photos_data.append(photo_info)
                
                request = service.mediaItems().list_next(request, results)
            
            print(f"✅ Found {len(photos_data)} items in Google Photos")
            return photos_data
            
        except Exception as e:
            print(f"❌ Error fetching Google Photos: {e}")
            return []
    
    def fetch_google_drive(self):
        """Fetch image metadata from Google Drive"""
        print("\n🔍 Fetching from Google Drive...")
        from google_auth import get_google_service
        
        try:
            service = get_google_service('drive', 'v3')
            drive_files = []
            
            query = "mimeType contains 'image/'"
            request = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, createdTime, size, md5Checksum, webContentLink)',
                pageSize=100
            )
            
            while request:
                results = request.execute()
                files = results.get('files', [])
                
                for file in files:
                    file_info = {
                        'source': 'google_drive',
                        'id': file['id'],
                        'filename': file['name'],
                        'mime_type': file['mimeType'],
                        'created': file.get('createdTime', ''),
                        'size': int(file.get('size', 0)),
                        'md5': file.get('md5Checksum', ''),
                        'download_link': file.get('webContentLink', ''),
                    }
                    drive_files.append(file_info)
                
                request = service.files().list_next(request, results)
            
            print(f"✅ Found {len(drive_files)} images in Google Drive")
            return drive_files
            
        except Exception as e:
            print(f"❌ Error fetching Google Drive: {e}")
            return []
    
    def fetch_dropbox(self):
        """Fetch image metadata from Dropbox"""
        print("\n📁 Fetching from Dropbox...")
        from dropbox_auth import get_dropbox_client
        
        try:
            import dropbox
            dbx = get_dropbox_client()
            if not dbx:
                return []
            
            dropbox_files = []
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            
            for entry in dbx.files_list_folder('', recursive=True).entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    if Path(entry.name).suffix.lower() in image_extensions:
                        file_info = {
                            'source': 'dropbox',
                            'id': entry.id,
                            'filename': entry.name,
                            'path': entry.path_display,
                            'created': entry.client_modified.isoformat(),
                            'size': entry.size,
                        }
                        dropbox_files.append(file_info)
            
            print(f"✅ Found {len(dropbox_files)} images in Dropbox")
            return dropbox_files
            
        except Exception as e:
            print(f"❌ Error fetching Dropbox: {e}")
            return []
    
    def analyze_with_claude(self, files_batch):
        """Use Claude to analyze and identify duplicates"""
        print("\n🤖 Analyzing with Claude AI...")
        
        file_summary = json.dumps(files_batch, indent=2, default=str)
        
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze these files from Google Photos, Google Drive, and Dropbox. 
                    Identify likely duplicates based on:
                    - Similar filenames
                    - Same file size
                    - Same creation date
                    - Image characteristics
                    
                    Return a JSON array with duplicate groups. Each group should contain files that are likely the same image.
                    Mark which file in each group should be KEPT (keep the one from google_photos preferably).
                    
                    Files to analyze:
                    {file_summary}
                    
                    Return ONLY valid JSON in this format:
                    {{"duplicate_groups": [{{"files": [{{"source": "...", "id": "...", "filename": "..."}}], "keep_file": {{"source": "...", "id": "..."}}, "confidence": "high/medium/low", "reason": "..."}}]}}"""
                }
            ]
        )
        
        try:
            response_text = message.content[0].text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result.get('duplicate_groups', [])
        except (json.JSONDecodeError, IndexError) as e:
            print(f"⚠️  Error parsing Claude response: {e}")
        
        return []
    
    def process_duplicates(self, duplicates, google_photos, google_drive, dropbox_files):
        """Process detected duplicates: download and move them"""
        print("\n" + "="*60)
        print("🔄 Processing Duplicates...")
        print("="*60)
        
        from google_auth import get_google_service
        from dropbox_auth import get_dropbox_client
        import dropbox
        
        drive_service = get_google_service('drive', 'v3')
        dbx = get_dropbox_client()
        
        # Create a map of files by ID
        files_map = {}
        for f in google_photos:
            files_map[f['id']] = f
        for f in google_drive:
            files_map[f['id']] = f
        for f in dropbox_files:
            files_map[f['id']] = f
        
        for group_idx, group in enumerate(duplicates, 1):
            print(f"\n📋 Processing Group {group_idx}...")
            
            keep_file = group.get('keep_file', {})
            keep_id = keep_file.get('id')
            
            for file in group.get('files', []):
                file_id = file['id']
                source = file['source']
                filename = file['filename']
                
                # Skip the file we want to keep
                if file_id == keep_id:
                    print(f"   ✅ KEEPING: {source} - {filename}")
                    continue
                
                # Download and track
                downloaded_path = None
                
                if source == 'google_photos':
                    file_obj = files_map.get(file_id)
                    if file_obj:
                        downloaded_path = self.download_google_photos_file(
                            file_obj['url'], filename
                        )
                
                elif source == 'google_drive':
                    downloaded_path = self.download_google_drive_file(
                        drive_service, file_id, filename
                    )
                    # Move original to trash
                    self.move_google_drive_file(drive_service, file_id, filename)
                
                elif source == 'dropbox':
                    file_obj = files_map.get(file_id)
                    if file_obj:
                        downloaded_path = self.download_dropbox_file(
                            dbx, file_obj['path'], filename
                        )
                
                if downloaded_path:
                    print(f"   ⬇️  DOWNLOADED: {source} - {filename}")
                    self.download_log.append({
                        'source': source,
                        'filename': filename,
                        'file_id': file_id,
                        'local_path': downloaded_path,
                        'action': 'downloaded_and_marked_for_removal'
                    })
                else:
                    print(f"   ⚠️  FAILED to download: {source} - {filename}")
    
    def save_results(self):
        """Save detection results and download log"""
        # Save duplicate analysis
        output_file = self.storage_path / f"duplicates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'duplicate_groups': self.duplicates,
            'total_duplicates': len(self.duplicates),
            'duplicates_folder': str(self.duplicates_path.absolute()),
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save download log
        log_file = self.storage_path / f"download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(log_file, 'w') as f:
            json.dump(self.download_log, f, indent=2, default=str)
        
        print(f"\n✅ Results saved to {output_file}")
        print(f"✅ Download log saved to {log_file}")
    
    def display_results(self):
        """Display duplicate detection results"""
        if not self.duplicates:
            print("\n✅ No duplicates found!")
            return
        
        print("\n" + "="*60)
        print("🎯 DUPLICATE GROUPS FOUND & PROCESSED")
        print("="*60)
        
        for i, group in enumerate(self.duplicates, 1):
            print(f"\n📋 Group {i} (Confidence: {group.get('confidence', 'unknown').upper()})")
            print(f"   Reason: {group.get('reason', 'N/A')}")
            print(f"   Files:")
            
            keep_file = group.get('keep_file', {})
            
            for file in group.get('files', []):
                status = "✅ KEPT" if file['id'] == keep_file.get('id') else "⬇️ DOWNLOADED"
                print(f"     {status} • {file['source']}: {file['filename']}")
        
        print("\n" + "="*60)
        print(f"💾 Total duplicate groups found: {len(self.duplicates)}")
        print(f"📁 Duplicates saved to: {self.duplicates_path.absolute()}")
        print(f"📋 Files downloaded: {len(self.download_log)}")
        print("="*60)
    
    def run_detection(self):
        """Run full duplicate detection and management"""
        print("\n" + "="*60)
        print("🔍 Multi-Cloud Duplicate Photo Detector & Manager")
        print("="*60)
        
        # Fetch from all sources
        google_photos = self.fetch_google_photos()
        google_drive = self.fetch_google_drive()
        dropbox_files = self.fetch_dropbox()
        
        all_files = google_photos + google_drive + dropbox_files
        
        if not all_files:
            print("\n❌ No files found in any cloud storage")
            return
        
        print(f"\n📊 Total files found: {len(all_files)}")
        
        # Batch files for analysis
        batch_size = 20
        all_duplicates = []
        
        for i in tqdm(range(0, len(all_files), batch_size), desc="Analyzing batches"):
            batch = all_files[i:i+batch_size]
            duplicates = self.analyze_with_claude(batch)
            all_duplicates.extend(duplicates)
        
        self.duplicates = all_duplicates
        
        if self.duplicates:
            # Process duplicates
            self.process_duplicates(all_duplicates, google_photos, google_drive, dropbox_files)
        
        self.save_results()
        self.display_results()

def main():
    """Main entry point"""
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not found in .env")
        print("Please add your Claude API key to .env file")
        return
    
    manager = DuplicateManager()
    manager.run_detection()

if __name__ == '__main__':
    main()
