'''
  Author: Jon Paul Miles
  Date Created: March 16, 2022

  Daily station data can be retrieved from:
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/
'''

import os
import urllib.request
import tarfile
import glob

from download import download_from_url, download_and_extract_from_url

UNEXTRACTED_DAILY_FILE = 'ghcnd_all.tar.gz'
EXTRACTED_DAILY_FOLDER = 'ghcnd_all'
WEB_URL_FOR_ALL_DAILY_DATA = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz'
WEB_URL_DAILY_DATA_VERSION_FILE = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt'

def download_from_url(url, file_name):
  urllib.request.urlretrieve(url, file_name)

def download_and_extract_from_url(url):
  ftpstream = urllib.request.urlopen(url)
  ghcnurl = tarfile.open(fileobj=ftpstream, mode="r|gz")
  ghcnurl.extractall()

# https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt
def get_version():

  FILE_NAME = 'ghcnd-version.txt'
  FILE_PATH = os.path.join('.', FILE_NAME)

  if not os.path.exists(os.path.join('.', FILE_PATH)):
    print(f"Downloading Version file: {WEB_URL_DAILY_DATA_VERSION_FILE} as {FILE_NAME}")
    version_file = download_from_url(WEB_URL_DAILY_DATA_VERSION_FILE, FILE_NAME)

  version_text = open(FILE_PATH, 'r').read()

  version_name = version_text[37:56]
  
  return version_name

def scan_for_daily_data_folder():

  daily_data_folder = glob.glob(os.path.join('.', EXTRACTED_DAILY_FOLDER))

  return daily_data_folder

def get_daily_data():

  UNEXTRACTED_FILE_PATH = os.path.join('.', UNEXTRACTED_DAILY_FILE)

  print(f"\nChecking if folder '{EXTRACTED_DAILY_FOLDER}' exists within this directory...\n")

  daily_data_folder = scan_for_daily_data_folder()

  if not len(daily_data_folder):

    print(f"Folder not found. Checking if {UNEXTRACTED_DAILY_FILE} exists in current directory...\n")

    if not os.path.exists(os.path.join('.', UNEXTRACTED_FILE_PATH)):
      print(f"Unextracted file {UNEXTRACTED_DAILY_FILE} not found. Downloading and extracting GHCN daily {UNEXTRACTED_DAILY_FILE} datasets from NOAA...\n")

      print(f"Downloading GHCN Daily data: {WEB_URL_FOR_ALL_DAILY_DATA}")
      download_and_extract_from_url(WEB_URL_FOR_ALL_DAILY_DATA)

      print(f"\nSuccessfully downloaded:")
      print(f"  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz")

    else:
      print(f"Found unextracted {UNEXTRACTED_DAILY_FILE}. Extracting now...\n")
      ghcnd_data = tarfile.open(UNEXTRACTED_FILE_PATH, mode="r|gz")
      ghcnd_data.extractall()

    daily_data_folder = scan_for_daily_data_folder()

    print("\nExtracted to:")
    print(f"  {daily_data_folder[0]}")

  else: 

    print(f"Local files:")
    print(f"============\n")
    print(f"  {daily_data_folder[0]}")
    print('\n  No downloads necessary.')

  print('')

  return daily_data_folder[0]
