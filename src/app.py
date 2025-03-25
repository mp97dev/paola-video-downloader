from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import sys
from time import sleep
import requests
import os

import os.path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import logging
logging.basicConfig(level=logging.DEBUG)


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = "./auth.json"


def wait_for_element(driver, locator, timeout=60, condition=EC.presence_of_element_located):
    """
    Waits for an element to meet a specific condition.

    :param driver: Selenium WebDriver instance
    :param locator: Tuple (By.<METHOD>, "locator string")
    :param timeout: Time (seconds) to wait before timeout
    :param condition: Expected condition (default: presence_of_element_located)
    :return: The WebElement if found, else raises TimeoutException
    """
    return WebDriverWait(driver, timeout).until(condition(locator))

def download_instagram(driver: webdriver.Chrome, data: dict):
    print("Open fastvideo")
    driver.get('https://fastvideosave.net/')
    print(driver.title)

    # accept cookie banner if present
    print("Accept cookie banner")
    consent_buttons = wait_for_element(driver, (By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button[1]'))    
    consent_buttons.click()

    print("Insert link")
    input = wait_for_element(driver, (By.XPATH, '//*[@id="form"]/input'))
    
    input.send_keys(data.get('link'))
    input.submit()
    
    print("Wait for download area", end=" ")
    button = wait_for_element(driver, (By.XPATH, '/html/body/div[1]/main/div[1]/div/div[3]/div/div[2]/a[2]'))
    download_link = button.get_attribute('href')

    response = requests.get(download_link)
    
    print("Download video")
    filename = data.get('title')
    
    with open(filename + '.mp4', 'wb') as f:
        f.write(response.content)
    
    sendVideo(filename + '.mp4')

def sendVideo(filename: str):
    print("Send video to Google Drive")
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    try:
        drive_service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': filename,
            'mimeType': 'video/mp4',
            'parents': ['1j_mqg56mxnLPU6bI7UP5KebxN6NEkFZ6']
        }
        media = MediaFileUpload(filename, mimetype='video/mp4')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print('OK: File ID: %s' % file.get('id'))

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None



# Set up options for the WebDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")  # Important for GitHub Actions
options.add_argument("--disable-dev-shm-usage")  # Helps with shared memory issues
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.add_argument("start-maximized")

try:
    f = open('data.json', 'rb')
except OSError:
    print("Could not open/read file data.json")
    sys.exit(1)

# Set up the WebDriver using a context manager
with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
    driver.set_page_load_timeout(60)  # 60s timeout
    driver.implicitly_wait(10)  # Waits 10s for elements to appear

    with open("data.json", "r", encoding="utf-8") as f:
        content = f.read().strip()
        
        # Parse the JSON string
        try:
            data = json.loads(content)
            print("Parsed JSON:", data)
        except json.JSONDecodeError as e:
            print("Error parsing JSON:", e)
            sys.exit(1)

        link = data.get('link')

        if 'instagram' in link:
            download_instagram(driver, data)
        # if 'youtube' in link:
        #     download_youtube(driver, data)
        # if 'facebook' in link:
        #     download_facebook(driver, data)    

        

