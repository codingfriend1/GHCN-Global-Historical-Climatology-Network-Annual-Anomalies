'''
  Author: Jon Paul Miles
  Date Created: March 16, 2022

  Daily station data can be retrieved from:
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/
'''

import os
import urllib.request

def download_from_url(url, file_name):
  urllib.request.urlretrieve(url, file_name)

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
