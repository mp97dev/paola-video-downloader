# Paola Video Downloader

A Python-based video downloader that automatically downloads videos from multiple platforms (Instagram, YouTube, TikTok, and more) and uploads them to Google Drive. The tool features a modular architecture with robust error handling, retry logic, and support for short-form content like reels and shorts.

## 🎯 Purpose

This project automates the process of downloading videos from social media platforms and storing them in Google Drive. It's designed to run both locally and as a GitHub Actions workflow, making it ideal for scheduled or on-demand video archiving.

## ✨ Features

### Core Capabilities
- **Multi-Platform Support**: Download videos from Instagram, YouTube, TikTok, Facebook, Twitter, and many more platforms
- **Short-Form Content**: Full support for reels, shorts, stories, and other short-form video formats
- **Google Drive Integration**: Automatically upload downloaded videos to a specified Google Drive folder
- **Robust Download Engine**: Uses yt-dlp for reliable video extraction with automatic fallbacks

### Enhanced Features (New!)
- **Modular Architecture**: Clean separation between provider detection, stream extraction, and download logic
- **Automatic Provider Selection**: Intelligently detects the video source and uses the appropriate downloader
- **Filename Sanitization**: Ensures filesystem-safe filenames with proper character handling
- **Duplicate Prevention**: Optional check to prevent downloading the same file twice
- **Retry Logic**: Exponential backoff retry strategy for failed downloads
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Error Handling**: Clear, actionable error messages for troubleshooting
- **Extensible Design**: Easy to add support for new platforms

### Automation Features
- **GitHub Actions Integration**: Trigger downloads remotely via workflow dispatch
- **Command-Line Interface**: Simple JSON-based configuration for URL and title input
- **Headless Operation**: Runs without GUI for server deployments

## 📋 Prerequisites

Before using this project, ensure you have the following:

### System Requirements
- Python 3.8 or higher
- Internet connection
- ffmpeg (recommended for video post-processing)

### Required Credentials
- **Google Service Account**: A service account JSON file (`auth.json`) with Google Drive API access
- **Google Drive Folder ID**: The ID of the target folder where videos will be uploaded

## 🚀 Installation

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mp97dev/paola-video-downloader.git
   cd paola-video-downloader
   ```

2. **Install Python dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Optional: Install ffmpeg**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   ```

### Alternative: Using the Installation Script

You can also use the provided installation script (note: this includes Selenium setup which is no longer required for core functionality):

```bash
chmod +x install.sh
./install.sh
```
   - Install Google Chrome Stable (requires Chrome in apt repositories)
   - Attempt to install ChromeDriver (optional, as webdriver-manager handles this)
   - Create a Python virtual environment
   - Install all required Python dependencies

3. **Manual Installation (Alternative)**
   
   If you prefer manual setup:
   ```bash
   # Install Google Chrome (Ubuntu/Debian)
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo dpkg -i google-chrome-stable_current_amd64.deb
   sudo apt-get install -f
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### 1. Google Service Account Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API
4. Create a Service Account:
   - Navigate to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Grant necessary permissions
   - Create and download a JSON key
5. Save the downloaded JSON key as `auth.json` in the project root directory

### 2. Google Drive Folder Configuration

1. Create a folder in Google Drive where videos will be uploaded
2. Share the folder with the service account email (found in `auth.json`)
3. Get the folder ID from the URL (e.g., the alphanumeric string after `/folders/` in the URL)
4. Update the folder ID in `src/app.py`:
   - Open `src/app.py` and locate the `sendVideo()` function
   - Find the `file_metadata` dictionary
   - Update the `'parents'` field with your folder ID:
   ```python
   'parents': ['YOUR_FOLDER_ID_HERE']
   ```

### 3. Video Data Configuration

Create a `data.json` file in the project root with the following structure:

```json
{
  "title": "video_filename",
  "link": "https://www.instagram.com/p/YOUR_POST_ID/"
}
```

- **title**: The desired filename for the downloaded video (without extension)
- **link**: The URL of the Instagram video you want to download

## 📖 Usage

### Local Execution

1. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

2. **Ensure configuration files are in place**
   - `auth.json` (Google Service Account credentials)
   - `data.json` (Video information)

3. **Run the script**
   ```bash
   python3 src/app.py
   ```

The script will:
1. Read the video URL and title from `data.json`
2. Automatically detect the video platform
3. Download the video using the best available method
4. Save it locally with a sanitized, filesystem-safe filename
5. Upload it to your Google Drive folder
6. Display the uploaded file's Google Drive ID

### GitHub Actions Execution

You can trigger the download workflow remotely:

1. Go to your repository on GitHub
2. Navigate to **Actions** tab
3. Select **"Run Python Script"** workflow
4. Click **"Run workflow"**
5. Fill in the required inputs:
   - **Title**: Filename for the video
   - **Link**: Video URL (Instagram, YouTube, TikTok, etc.)
6. Click **"Run workflow"** button

The workflow will execute automatically in GitHub's infrastructure and upload the video to Google Drive.

**Note**: For GitHub Actions to work, you must configure the `auth.json` credentials as a repository secret:

1. Go to Settings > Secrets and variables > Actions
2. Create a new secret (e.g., named `GOOGLE_SERVICE_ACCOUNT`)
3. Paste the entire contents of your `auth.json` file as the secret value
4. Update the workflow file (`.github/workflows/run-python.yml`) to create the auth.json file from the secret:
   ```yaml
   - name: Create auth.json from secret
     run: echo '${{ secrets.GOOGLE_SERVICE_ACCOUNT }}' > auth.json
   ```
   Add this step before the "Run Python Script" step in the workflow.

## 📁 Project Structure

```
paola-video-downloader/
├── .github/
│   └── workflows/
│       └── run-python.yml           # GitHub Actions workflow configuration
├── src/
│   ├── app.py                       # Main application entry point
│   └── downloader/                  # Modular downloader package
│       ├── __init__.py             
│       ├── core.py                  # Core VideoDownloader class
│       ├── exceptions.py            # Custom exceptions
│       ├── providers/               # Download providers
│       │   ├── __init__.py
│       │   ├── base.py              # Base provider interface
│       │   └── ytdlp_provider.py    # yt-dlp provider implementation
│       └── utils/                   # Utility functions
│           ├── __init__.py
│           └── file_utils.py        # File handling utilities
├── tests/                           # Unit tests
│   ├── __init__.py
│   ├── test_downloader.py
│   └── test_file_utils.py
├── examples.py                      # Usage examples
├── .gitignore                       # Git ignore rules
├── install.sh                       # Installation script
├── requirements.txt                 # Python dependencies
└── README.md                        # This documentation
```

### Key Files

- **`src/app.py`**: Main application entry point
  - `main()`: Entry point that reads data.json and orchestrates the download
  - `sendVideo()`: Uploads videos to Google Drive

- **`src/downloader/core.py`**: Core downloader implementation
  - `VideoDownloader`: Main class for downloading videos
  - Provider management and selection logic
  - Duplicate detection and error handling

- **`src/downloader/providers/`**: Download provider implementations
  - `BaseProvider`: Abstract base class for all providers
  - `YtDlpProvider`: Universal provider using yt-dlp (supports 1000+ sites)

- **`src/downloader/utils/`**: Utility functions
  - Filename sanitization
  - Duplicate detection
  - File hash calculation

- **`requirements.txt`**: Python dependencies including:
  - `yt-dlp`: Universal video downloader
  - `google-api-python-client`: Google Drive API
  - `requests`: HTTP requests
  - Other supporting libraries

- **`examples.py`**: Example code demonstrating various usage patterns

## 🔧 Module Documentation

### VideoDownloader Class

The main class for downloading videos from any supported platform.

#### Initialization

```python
from downloader import VideoDownloader

downloader = VideoDownloader(
    output_dir='./downloads',      # Where to save videos
    prevent_duplicates=True         # Check for existing files
)
```

#### Methods

**`download(url: str, title: str = None) -> dict`**
- Downloads a video from the given URL
- Parameters:
  - `url`: Video URL from any supported platform
  - `title`: Optional custom title for the file
- Returns: Dictionary with:
  - `success`: Boolean indicating success
  - `filepath`: Path to downloaded file (if successful)
  - `error`: Error message (if failed)
  - `provider`: Name of provider used

**`extract_info(url: str) -> dict`**
- Extracts video metadata without downloading
- Returns: Dictionary with title, duration, uploader, etc.

**`list_providers() -> list`**
- Returns list of available provider names

**`add_provider(provider: BaseProvider)`**
- Add a custom provider to the downloader

### Usage Examples

#### Basic Download

```python
from downloader import VideoDownloader

# Initialize downloader
downloader = VideoDownloader(output_dir='./downloads')

# Download a video
result = downloader.download(
    url='https://www.instagram.com/p/example/',
    title='my_video'
)

if result['success']:
    print(f"Downloaded: {result['filepath']}")
else:
    print(f"Error: {result['error']}")
```

#### Extract Information

```python
# Get video info without downloading
info = downloader.extract_info('https://www.youtube.com/watch?v=example')
print(f"Title: {info['title']}")
print(f"Duration: {info['duration']} seconds")
```

#### Multiple Videos

```python
videos = [
    {'url': 'https://instagram.com/p/abc', 'title': 'video1'},
    {'url': 'https://youtube.com/watch?v=xyz', 'title': 'video2'},
]

for video in videos:
    result = downloader.download(video['url'], video['title'])
    print(f"{video['title']}: {'✓' if result['success'] else '✗'}")
```

For more examples, see `examples.py` in the repository.

### Supported Platforms

The downloader uses yt-dlp which supports over 1000 sites, including:

- **Social Media**: Instagram, TikTok, Facebook, Twitter, Reddit
- **Video Platforms**: YouTube, Vimeo, Dailymotion
- **Short-Form**: Instagram Reels, YouTube Shorts, TikTok videos
- **Live Streams**: Twitch, YouTube Live
- **And many more**: See [yt-dlp supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)
  2. Handles cookie consent banner
  3. Inputs Instagram URL
  4. Extracts download link
  5. Downloads video via HTTP request
  6. Saves video locally
  7. Calls `sendVideo()` to upload to Google Drive

**`sendVideo(filename)`**
- Uploads a video file to Google Drive
- Parameters:
  - `filename`: Path to the video file
- Uses Google Service Account credentials from `auth.json`
- Uploads to the configured Google Drive folder

#### Configuration Constants

- `SCOPES`: Google Drive API scope
- `SERVICE_ACCOUNT_FILE`: Path to service account JSON file
- Chrome options for headless execution and compatibility

## 📝 Usage Scenarios

### Scenario 1: Download a Video from Any Platform

1. Create `data.json`:
   ```json
   {
     "title": "my_awesome_video",
     "link": "https://www.instagram.com/p/ABC123xyz/"
   }
   ```
   
   Or for YouTube:
   ```json
   {
     "title": "tutorial_video",
     "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
   }
   ```

2. Run the script:
   ```bash
   source venv/bin/activate
   python3 src/app.py
   ```

3. The video will be downloaded, saved with a sanitized filename, and uploaded to Google Drive

### Scenario 2: Download Short-Form Content

The downloader automatically handles reels, shorts, and stories:

```json
{
  "title": "dance_reel",
  "link": "https://www.instagram.com/reel/ABC123xyz/"
}
```

```json
{
  "title": "funny_short",
  "link": "https://www.youtube.com/shorts/ABC123xyz"
}
```

### Scenario 3: Schedule Regular Downloads with GitHub Actions

1. Set up GitHub Actions secrets with your `auth.json` content
2. Use the workflow dispatch feature to trigger downloads
3. Videos will be automatically downloaded and uploaded to Google Drive

### Scenario 4: Programmatic Usage

Use the downloader in your own Python scripts:

```python
from downloader import VideoDownloader

downloader = VideoDownloader(output_dir='./my_videos')

# Download multiple videos
urls = [
    'https://instagram.com/reel/...',
    'https://youtube.com/watch?v=...',
    'https://tiktok.com/@user/video/...'
]

for url in urls:
    result = downloader.download(url, title=f'video_{urls.index(url)}')
    print(f"Downloaded: {result['success']}")
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: `Could not open/read file data.json`
- **Solution**: Ensure `data.json` exists in the project root directory with valid JSON format

**Issue**: `No module named 'yt_dlp'`
- **Solution**: Install yt-dlp: `pip install yt-dlp`

**Issue**: Google Drive upload fails
- **Solution**: 
  - Verify `auth.json` is valid and has correct permissions
  - Ensure the Google Drive folder is shared with the service account email
  - Check that the folder ID in `src/app.py` is correct (line 84)

**Issue**: Download fails with "Unsupported URL"
- **Solution**:
  - Verify the URL is correct and accessible
  - Check if the platform is supported by yt-dlp
  - Try the URL manually in a browser first

**Issue**: Download fails with network error
- **Solution**:
  - Check your internet connection
  - The retry logic will attempt the download up to 3 times automatically
  - Some platforms may be rate-limiting; wait and try again later

**Issue**: Video quality is lower than expected
- **Solution**:
  - The downloader selects the best available quality by default
  - Some platforms may restrict quality for automated downloads
  - Check if the video source has higher quality available

**Issue**: Filename has strange characters
- **Solution**: The sanitization function automatically removes invalid characters
  - If issues persist, manually specify a simpler title in data.json

### Debug Mode

The script runs with detailed logging. Check the console output for information:
```python
# Logs show:
# - Provider selection
# - Download attempts and retries
# - Error details
# - File paths
```

To increase logging verbosity, modify the logging level in `src/app.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/paola-video-downloader.git
   cd paola-video-downloader
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Test your changes locally

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Describe your changes and their benefits

### Contribution Ideas

- Add custom providers for specific platforms
- Implement parallel downloads
- Add video format/quality selection options
- Create a CLI with argument parsing
- Add progress bars for downloads
- Implement metadata extraction and storage
- Add webhook notifications
- Create a web interface

### Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Handle errors gracefully with try-except blocks
- Write unit tests for new features
- Update documentation for any API changes

## 🐛 Reporting Issues

If you encounter bugs or have feature requests:

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear, descriptive title
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Error messages or logs
   - Screenshots (if applicable)

## 📄 License

This project does not currently have a specified license. Please contact the repository owner for licensing information before using this code in production or distributing it.

## ⚠️ Disclaimer

- This tool is for personal use and educational purposes
- Respect copyright and terms of service of the platforms you download from
- Ensure you have the right to download and store content
- The tool relies on third-party services which may change without notice
- Always comply with applicable laws and regulations regarding content downloading

## 🔮 Future Enhancements

Completed in this release:
- [x] Multi-platform support (Instagram, YouTube, TikTok, etc.)
- [x] Support for short-form content (reels, shorts)
- [x] Retry logic with exponential backoff
- [x] Filename sanitization
- [x] Duplicate detection
- [x] Modular architecture
- [x] Unit tests

Planned for future releases:
- [ ] Parallel/batch downloads
- [ ] Video quality selection UI
- [ ] CLI interface with rich argument parsing
- [ ] Progress bars and status reporting
- [ ] Configuration file for settings
- [ ] Database integration for tracking downloads
- [ ] Metadata extraction and storage
- [ ] Email/webhook notifications
- [ ] Web interface for management
- [ ] Download scheduling
- [ ] Playlist support

## 📞 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Contact the repository maintainer: [@mp97dev](https://github.com/mp97dev)

---

**Happy downloading! 📹⬇️**
