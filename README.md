# Paola Video Downloader

A Python-based video downloader that automatically downloads videos from Instagram (and potentially other platforms) and uploads them to Google Drive. The tool uses Selenium WebDriver for web automation and integrates with Google Drive API for cloud storage.

## 🎯 Purpose

This project automates the process of downloading videos from social media platforms and storing them in Google Drive. It's designed to run both locally and as a GitHub Actions workflow, making it ideal for scheduled or on-demand video archiving.

## ✨ Features

- **Instagram Video Download**: Download videos from Instagram using fastvideosave.net
- **Google Drive Integration**: Automatically upload downloaded videos to a specified Google Drive folder
- **Headless Browser Support**: Runs without GUI using Chrome in headless mode
- **GitHub Actions Integration**: Trigger downloads remotely via workflow dispatch
- **Cookie Consent Handling**: Automatically handles cookie banners
- **Robust Error Handling**: Includes timeout management and error logging

## 📋 Prerequisites

Before using this project, ensure you have the following:

### System Requirements
- Python 3.8 or higher (Python 3.7 reached end-of-life in June 2023)
- Google Chrome browser (for local execution)
- Internet connection

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

2. **Run the installation script**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   
   **Note**: The install.sh script uses the deprecated chromedriver.storage.googleapis.com endpoint. Since this project uses `webdriver-manager` (included in requirements.txt), ChromeDriver will be automatically downloaded and managed when you run the script. If the install.sh script fails to install ChromeDriver, you can skip that step as webdriver-manager will handle it automatically.
   
   This script will:
   - Update system packages
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
1. Read the video URL from `data.json`
2. Navigate to fastvideosave.net
3. Download the Instagram video
4. Save it locally with the specified title
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
   - **Link**: Instagram video URL
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
│       └── run-python.yml      # GitHub Actions workflow configuration
├── src/
│   └── app.py                  # Main application script
├── .gitignore                  # Git ignore rules
├── install.sh                  # Installation script for dependencies
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation file
```

### Key Files

- **`src/app.py`**: Main Python script containing:
  - `download_instagram()`: Downloads videos from Instagram
  - `sendVideo()`: Uploads videos to Google Drive
  - `wait_for_element()`: Selenium helper function for waiting on elements
  
- **`install.sh`**: Bash script for automated setup
  
- **`requirements.txt`**: Lists all Python dependencies including:
  - `selenium`: Web automation
  - `webdriver-manager`: Automatic ChromeDriver management
  - `google-api-python-client`: Google Drive API interaction
  - `requests`: HTTP requests for video download
  - `python-dotenv`: Environment variable management

- **`.github/workflows/run-python.yml`**: Defines the GitHub Actions workflow for remote execution

## 🔧 Module Documentation

### Main Application (`src/app.py`)

#### Functions

**`wait_for_element(driver, locator, timeout=60, condition=EC.presence_of_element_located)`**
- Waits for a web element to appear on the page
- Parameters:
  - `driver`: Selenium WebDriver instance
  - `locator`: Tuple with (By.METHOD, "selector")
  - `timeout`: Maximum wait time in seconds (default: 60)
  - `condition`: Expected condition to check
- Returns: WebElement if found
- Raises: TimeoutException if element not found within timeout

**`download_instagram(driver, data)`**
- Downloads a video from Instagram using fastvideosave.net
- Parameters:
  - `driver`: Selenium WebDriver instance
  - `data`: Dictionary containing 'link' and 'title' keys
- Process:
  1. Navigates to fastvideosave.net
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

### Scenario 1: Download a Single Instagram Video

1. Create `data.json`:
   ```json
   {
     "title": "my_awesome_video",
     "link": "https://www.instagram.com/p/ABC123xyz/"
   }
   ```

2. Run the script:
   ```bash
   source venv/bin/activate
   python3 src/app.py
   ```

3. The video will be saved as `my_awesome_video.mp4` and uploaded to Google Drive

### Scenario 2: Schedule Regular Downloads with GitHub Actions

1. Set up GitHub Actions secrets with your `auth.json` content
2. Create a workflow schedule (modify `.github/workflows/run-python.yml`)
3. Videos will be automatically downloaded and archived on schedule

### Scenario 3: Batch Processing (Future Enhancement)

Currently, the tool processes one video at a time. To process multiple videos, you can:
1. Modify `data.json` to include an array of videos
2. Update the script to loop through the array
3. Add error handling for individual video failures

## 🐛 Troubleshooting

### Common Issues

**Issue**: `Could not open/read file data.json`
- **Solution**: Ensure `data.json` exists in the project root directory with valid JSON format

**Issue**: Google Drive upload fails
- **Solution**: 
  - Verify `auth.json` is valid and has correct permissions
  - Ensure the Google Drive folder is shared with the service account email
  - Check that the folder ID in the code is correct

**Issue**: ChromeDriver version mismatch
- **Solution**: 
  - Run `pip install --upgrade webdriver-manager`
  - The webdriver-manager should automatically download the correct version

**Issue**: Timeout waiting for elements
- **Solution**:
  - Check your internet connection
  - The third-party site (fastvideosave.net) might have changed its structure or URL
  - If the service URL changes, update the URL in the `download_instagram()` function in `src/app.py`
  - Increase timeout values in the code
  - Inspect the page structure to update XPath selectors if needed

**Issue**: Cookie banner not handled
- **Solution**: 
  - The script includes cookie handling for fastvideosave.net
  - If it fails, the XPath selector for the consent button may have changed
  - In `src/app.py`, locate the `download_instagram()` function around line 50
  - Look for the XPath selector: `'/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button[1]'`
  - Inspect the website in your browser to find the updated selector
  - Update the XPath in the code accordingly

### Debug Mode

The script runs with debug logging enabled. Check the console output for detailed information:
```python
logging.basicConfig(level=logging.DEBUG)
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

- Add support for other platforms (YouTube, Facebook, TikTok)
- Implement batch processing for multiple videos
- Add retry logic for failed downloads
- Create a web interface or CLI tool
- Add unit tests and integration tests
- Improve error handling and logging
- Add video format/quality selection
- Implement progress bars for downloads

### Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings to functions
- Keep functions focused and single-purpose
- Handle errors gracefully with try-except blocks

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

Planned features for future releases:

- [ ] Support for YouTube, Facebook, and TikTok
- [ ] Video quality selection
- [ ] Batch download support
- [ ] CLI interface with argument parsing
- [ ] Progress indicators and detailed status reporting
- [ ] Configuration file for settings
- [ ] Database integration for tracking downloads
- [ ] Duplicate detection
- [ ] Automatic retry on failure
- [ ] Email notifications on completion
- [ ] Web interface for easier management

## 📞 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Contact the repository maintainer: [@mp97dev](https://github.com/mp97dev)

---

**Happy downloading! 📹⬇️**
