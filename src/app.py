import json
import sys
import os
import os.path
import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Import the new modular downloader
from downloader import VideoDownloader
from downloader.exceptions import DownloadError, UnsupportedPlatformError, DuplicateFileError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = "./auth.json"
# Google Drive folder ID - can be overridden with GDRIVE_FOLDER_ID environment variable
DEFAULT_GDRIVE_FOLDER_ID = '1j_mqg56mxnLPU6bI7UP5KebxN6NEkFZ6'


def sendVideo(filename: str):
    """
    Upload a video file to Google Drive.
    
    Args:
        filename: Path to the video file to upload
    """
    logger.info(f"Uploading video to Google Drive: {filename}")
    
    # Get folder ID from environment or use default
    folder_id = os.environ.get('GDRIVE_FOLDER_ID', DEFAULT_GDRIVE_FOLDER_ID)
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        drive_service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': os.path.basename(filename),
            'mimeType': 'video/mp4',
            'parents': [folder_id]
        }
        media = MediaFileUpload(filename, mimetype='video/mp4')
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        logger.info(f'Successfully uploaded to Google Drive. File ID: {file.get("id")}')
        print(f'OK: File ID: {file.get("id")}')
        
        return file.get('id')

    except HttpError as error:
        logger.error(f"Google Drive upload error: {error}")
        print(f"An error occurred: {error}")
        return None


def main():
    """Main application entry point."""
    # Load video data
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            data = json.loads(content)
            logger.info(f"Loaded data: {data}")
    except OSError as e:
        logger.error("Could not open/read file data.json")
        print(f"Error: Could not open/read file data.json: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    url = data.get('link')
    title = data.get('title')
    
    if not url:
        logger.error("No 'link' field found in data.json")
        print("Error: No 'link' field found in data.json")
        sys.exit(1)
    
    # Basic URL validation
    if not isinstance(url, str) or not url.strip():
        logger.error("Invalid URL: URL must be a non-empty string")
        print("Error: Invalid URL format")
        sys.exit(1)
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        logger.error(f"Invalid URL format: {url}")
        print(f"Error: URL must start with http:// or https://")
        sys.exit(1)
    
    if not title:
        logger.warning("No 'title' field found in data.json, using default")
        title = 'video'
    
    logger.info(f"Starting download for: {url}")
    logger.info(f"Title: {title}")
    
    # Initialize the video downloader
    downloader = VideoDownloader(
        output_dir='.',
        prevent_duplicates=False  # Allow overwrites for now
    )
    
    # Download the video
    try:
        result = downloader.download(url, title)
        
        if result['success']:
            filepath = result['filepath']
            logger.info(f"Download successful: {filepath}")
            print(f"Successfully downloaded: {filepath}")
            
            # Upload to Google Drive
            file_id = sendVideo(filepath)
            
            if file_id:
                logger.info("Video successfully uploaded to Google Drive")
            else:
                logger.warning("Video download succeeded but upload failed")
        else:
            error = result.get('error', 'Unknown error')
            logger.error(f"Download failed: {error}")
            print(f"Error: Download failed: {error}")
            sys.exit(1)
            
    except UnsupportedPlatformError as e:
        logger.error(f"Unsupported platform: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except DuplicateFileError as e:
        logger.error(f"Duplicate file: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except DownloadError as e:
        logger.error(f"Download error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()