'''
  Author: Jon Paul Miles
  Date Created: March 15, 2022

  Data Sources:
  
  v3
  https://www.ncei.noaa.gov/pub/data/ghcn/v3/README
  https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/ghcnm.tavg.latest.qcu.tar.gz
  https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/ghcnm.tavg.latest.qca.tar.gz
  https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/country-codes
  
  v4
  https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcu.tar.gz
  https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcf.tar.gz
  https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm-countries.txt

  USHCN
  https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/readme.txt
  https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn-v2.5-stations.txt
  https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn.tavg.latest.raw.tar.gz
  https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn.tavg.latest.tob.tar.gz
  https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn.tavg.latest.FLs.52j.tar.gz

  USCRN
  https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/readme.txt
  https://www.ncei.noaa.gov/pub/data/uscrn/products/stations.tsv
  https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/

  Land / Water Ratio per Grid Quadrant

  Google Drive Land Mask obtained from https://github.com/aljones1816/GHCNV4_Analysis
  Author: Alan (aljones1816) (Twitter: @TheAlonJ) https://github.com/aljones1816
  License: GNU General Public License v3.0
  Code for retrieving this file has been slightly modified from original: https://github.com/aljones1816/GHCNV4_Analysis/blob/main/analysis_code.py

  https://drive.google.com/file/d/1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj/view
  https://drive.google.com/uc?export=download&id=1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj

  Daily
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt

'''

from globals import *

import urllib.request
import tarfile
import os
from google_drive_downloader import GoogleDriveDownloader as gdd
from termcolor import colored, cprint

from networks import ghcn
from networks import ushcn
from networks import uscrn



REQUIRED_DOWNLOADS = {
  
  'GHCN': {

    'v3': {
      'qcu': [
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/country-codes',
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/ghcnm.tavg.latest.qcu.tar.gz'
      ],
      'qca': [
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/country-codes',
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/ghcnm.tavg.latest.qca.tar.gz'
      ],
    },

    'v4': {
      'qcu': [
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm-countries.txt',
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcu.tar.gz'
      ],
      'qcf': [
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm-countries.txt',
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcf.tar.gz'
      ],
    },

    'daily': {
      'all': [
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt',
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt',
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt',
        'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz'
      ]
    }

  },

  'USHCN': {

    'v2.5': {
      'raw': [
        'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn-v2.5-stations.txt',
        'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn.tavg.latest.raw.tar.gz'
      ],
      'tob': [
        'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn-v2.5-stations.txt',
        'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn.tavg.latest.tob.tar.gz'
      ],
      'FLs': [
        'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn-v2.5-stations.txt',
        'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn.tavg.latest.FLs.52j.tar.gz'
      ],

    }

  },

  'USCRN': {

    'v1': {
      'monthly01': ['https://www.ncei.noaa.gov/pub/data/uscrn/products/stations.tsv']
    }
    
  }

}

# Landmask data 

LAND_MASK_FILE_NAME = "landmask.dta"

LAND_MASK_URL = 'https://drive.google.com/uc?export=download&id=1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj'


# GHCN Daily Data

DAILY_ARCHIVE_FILE = 'ghcnd_all.tar.gz'

EXTRACTED_DAILY_FOLDER = 'ghcnd_all'

COMPILED_DAILY = 'ghcnd.tavg*.dat'

# Exception

v3_unadjusted = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/ghcnm.tavg.latest.qcu.tar.gz'

v3_unadjusted_file = 'ghcnm.v3.tavg.latest.qcu.tar.gz'


# Console output marks

check_mark = colored(u'\u2713', 'green', attrs=['bold'])

attention_mark = colored('!', 'yellow', attrs=['bold'])


def download_landmask_data_if_needed():

  if os.path.exists(LAND_MASK_FILE_NAME):

    print(f"{check_mark} Found '{LAND_MASK_FILE_NAME}'")

  else:

    print(f"{attention_mark} Missing '{LAND_MASK_FILE_NAME}'.")

    gdd.download_file_from_google_drive(file_id='1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj', dest_path=os.path.join('.', LAND_MASK_FILE_NAME), unzip=False)

  return LAND_MASK_FILE_NAME

# Search within a dictionary for a value. If it doesn't exist end the program and inform the user that the value doesn't exist in the provided `label` and offer options that do exist.
def get_tree(value, dictionary, label):

  if value in dictionary:

    return dictionary[value]

  else:

    print(f"Sorry, but '{value}' is not an available {label}. Try:")

    print(f"  " + "\n  ".join(dictionary.keys()))

    quit()

# For each url provided, check if the file has already been downloaded and if not then download the file and return a list of downloaded files
def download_if_needed(urls):

  downloaded_files = []

  for url in urls:

    file_name = os.path.basename(url) if url != v3_unadjusted else v3_unadjusted_file

    downloaded_files.append(file_name)
    
    if os.path.exists(file_name):

      print(f"{check_mark} Found '{file_name}'")

    else:

      print(f"{attention_mark} Missing '{file_name}'. Downloading from {url}")

      urllib.request.urlretrieve(url, file_name)

      print(f"  {check_mark} Downloaded '{file_name}'")

  return downloaded_files

# Check if any file in the files to be extracted doesn't already exist, then it needs to be extracted
def needs_extraction(files_to_be_extracted):

  for potential_extraction in files_to_be_extracted:

    if not os.path.exists(potential_extraction):

      return True

# For each file provided, check if the file is zipped and if its unzipped contents don't already exist, unzip the file
def extract_if_needed(downloaded_files):

  for file_name in downloaded_files:

    if file_name.endswith('.tar.gz'):

      file_preview = tarfile.open(file_name, mode="r|gz")

      # See the names of the files to be unzipped without actually extracting them
      files_to_be_extracted = file_preview.getnames()

      is_needing_extraction = needs_extraction(files_to_be_extracted)

      if is_needing_extraction:

        print(f"Extracting '{file_name}' to:")

        tarfile.open(file_name, mode="r|gz").extractall()

        print(f'  {check_mark} ' + f'\n  {check_mark} '.join(files_to_be_extracted)) 

# If the compiled daily data exists, or if the daily data folder is already extracted, do nothing. Otherwise, extract the daily data.
def extract_daily_if_needed():

  if NETWORK == 'GHCN':

    if not os.path.exists(COMPILED_DAILY) and not os.path.exists(EXTRACTED_DAILY_FOLDER):

      tarfile.open(DAILY_ARCHIVE_FILE, mode="r|gz").extractall()


# Download and compile the necessary files and return the associated STATION_FILE_PATH, TEMPERATURES_FILE_PATH, COUNTRIES_FILE_PATH for the given NETWORK, VERSION, and QUALITY_CONTROL_DATASET
def get_files():

  versions = get_tree(NETWORK, REQUIRED_DOWNLOADS, 'network')

  datasets = get_tree(VERSION, versions, f"version of '{NETWORK}'")

  downloadables = get_tree(QUALITY_CONTROL_DATASET, datasets, f"dataset in '{NETWORK} {VERSION}'")

  # We always need the Station Metadata for GHCN v3 since it's the only metadata that includes station environment
  if not v3_unadjusted in downloadables:

    downloadables.append(v3_unadjusted) 

  downloaded_files = download_if_needed(downloadables)
  
  extract_daily_if_needed() if VERSION == 'daily' else extract_if_needed(downloaded_files) 

  download_landmask_data_if_needed()
  
  if NETWORK == 'GHCN':

    return ghcn.get_files()

  elif NETWORK == 'USHCN':

    return ushcn.get_files()

  elif NETWORK == 'USCRN':

    return uscrn.get_files()
