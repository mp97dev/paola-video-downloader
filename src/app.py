from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = "./auth.json"

def download_instagram(driver: webdriver.Chrome, data: dict):
    driver.get('https://fastvideosave.net/')

    # accept cookie banner if present
    consent_buttons = driver.find_elements(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button[1]')
    if len(consent_buttons) > 0:
        consent_buttons[0].click()

    input = driver.find_elements(By.XPATH, '//*[@id="form"]/input')
    if len(input) == 0:
        print("Could not find input field")
        sys.exit()
    
    input[0].send_keys(data.get('link'))
    input[0].submit()
    
    download_area = driver.find_elements(By.CLASS_NAME, 'my-auto')
    while(len(download_area) == 0):
        sleep(2)
        download_area = driver.find_elements(By.CLASS_NAME, 'my-auto')


    if len(download_area) == 0:
        print("Not found download area")
        sys.exit()
    
    buttons = download_area[0].find_elements(By.TAG_NAME, 'a')
    if len(buttons) == 0:
        print ("Not found download links")
        sys.exit()

    download_link = buttons[0].get_attribute('href')

    response = requests.get(download_link)
    
    filename = data.get('title')
    
    with open(filename + '.mp4', 'wb') as f:
        f.write(response.content)

def sendVideo(filename: str):
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
        print('File ID: %s' % file.get('id'))

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None



# Set up options for the WebDriver
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')

try:
    f = open('data.json', 'rb')
except OSError:
    print("Could not open/read file data.json")
    sys.exit(1)

# Set up the WebDriver using a context manager
with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:

    with open('data.json') as f:
        print("data.json: ".join(f.readline(-1)))
        data = json.load(f)
        link = data.get('link')

        if 'instagram' in link:
            download_instagram(driver, data)
        # if 'youtube' in link:
        #     download_youtube(driver, data)
        # if 'facebook' in link:
        #     download_facebook(driver, data)    

        

