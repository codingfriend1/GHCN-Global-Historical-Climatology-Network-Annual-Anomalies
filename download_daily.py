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
    print(f"Downloading Version file: https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt as {FILE_NAME}")
    version_file = download_from_url('https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt', FILE_NAME)

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
      print(f"Folder not found. Downloading and extracting GHCN daily {VERSION} datasets from NOAA...\n")

      print(f"Downloading GHCN Daily data: https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz")
      download_and_extract_from_url('https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz')

      print(f"\nSuccessfully downloaded:")
      print(f"  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz")

    else:
      print(f"Folder unextracted {UNEXTRACTED_DAILY_FILE}. Extracting now...\n")
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

  return daily_data_folder[0]
