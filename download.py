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

  Land / Water Ratio per Grid Quadrant
  https://drive.google.com/file/d/1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj/view
'''

from constants import *

import urllib.request
import tarfile
import glob
import os
from google_drive_downloader import GoogleDriveDownloader as gdd

EXTRACTED_FILES = []
COUNTRY_CODES_FILE_NAME = 'country-codes' if VERSION == 'v3' else 'ghcnm-countries.txt'
LAND_MASK_FILE_NAME = "./landmask.dta"
USHCN_STATION_METADATA_FILE_URL = 'ushcn-v2.5-stations.txt'
USHCN_STATIONS_WEB_URL = 'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn-v2.5-stations.txt'


def download_landmask_data():
  '''
  Google Drive Land Mask obtained from https://github.com/aljones1816/GHCNV4_Analysis
  Author: Alan (aljones1816) (Twitter: @TheAlonJ) https://github.com/aljones1816
  License: GNU General Public License v3.0
  Code for retrieving this file has been slightly modified from original: https://github.com/aljones1816/GHCNV4_Analysis/blob/main/analysis_code.py
  '''
  gdd.download_file_from_google_drive(file_id='1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj', dest_path=LAND_MASK_FILE_NAME, unzip=False)

def download_and_extract_from_url(url):
  ftpstream = urllib.request.urlopen(url)
  ghcnurl = tarfile.open(fileobj=ftpstream, mode="r|gz")
  ghcnurl.extractall()

def download_from_url(url, file_name):
  urllib.request.urlretrieve(url, file_name)

def download_ushcn_station_metadata():

  print(f"Checking if {USHCN_STATION_METADATA_FILE_URL} exists...")

  # If the file does not exist, download it
  if not os.path.exists(USHCN_STATION_METADATA_FILE_URL):

    print(f"USHCN Station Metadata does not exist. Downloading from: {USHCN_STATIONS_WEB_URL}\n")

    download_from_url(USHCN_STATIONS_WEB_URL, USHCN_STATION_METADATA_FILE_URL)

  else:

    print("USHCN station metadata file was found. No need to download.\n")

  return USHCN_STATION_METADATA_FILE_URL

def get_local_country_file():

  # Get the Country Codes File
  COUNTRIES_FILE_PATH = glob.glob(f"./{COUNTRY_CODES_FILE_NAME}")

  if len(COUNTRIES_FILE_PATH):

    COUNTRIES_FILE_PATH = COUNTRIES_FILE_PATH[0]

  else:

    print(f"File '{COUNTRY_CODES_FILE_NAME}' is missing. Please delete the folder named 'ghcnm.{VERSION}*' and run this script again.\n")
    quit()

  return COUNTRIES_FILE_PATH

def download_GHCN_data():

  # Validate VERSION and QUALITY_CONTROL_DATASET
  if VERSION == 'v4' and not QUALITY_CONTROL_DATASET in ['qcu', 'qce', 'qcf']:
    print("\nFor Version 4 of GHCNm, set `QUALITY_CONTROL_DATASET` to either 'qcu' (quality-control unadjusted), or 'qcf' (quality-control adjusted).")
    print('See this readme file to decide which one to use: https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt\n')
    quit()
  elif VERSION == 'v3' and not QUALITY_CONTROL_DATASET in ['qcu', 'qca']:
    print("\nFor Version 3 of GHCNm, set `QUALITY_CONTROL_DATASET` to either 'qcu' (quality-control unadjusted) or 'qca' (quality-control adjusted).")
    print('See this readme file to decide which one to use: https://www.ncei.noaa.gov/pub/data/ghcn/v3/README\n')
    quit()
  elif not VERSION in ['v3', 'v4']:
    print("Sorry, but only GHCNm version's 3 and 4 are supported at this time. In `constants.py` please set `VERSION = 'v4'` to 'v3' or 'v4'")
    quit()

  VERSION_FOLDER = glob.glob(f"ghcnm.{VERSION}*")
  VERSION_FOLDER = [file for file in VERSION_FOLDER if not file.endswith('.xlsx')]
  COUNTRIES_FILE_PATH = ""

  print(f"\nChecking if folder 'ghcnm.{VERSION}*' exists within this directory...\n")

  if not len(VERSION_FOLDER):

    print(f"Folder not found. Downloading and extracting both Quality Controlled and Unadjusted GHCNm {VERSION} datasets from NOAA...\n")

    QUALITY_CONTROL_ADJUSTED_NAME = 'qca' if VERSION == 'v3' else 'qcf'

    BASE_URL = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/{VERSION}"
    GHCNm_UNADJUSTED_URL = f"{BASE_URL}/ghcnm.tavg.latest.qcu.tar.gz"
    GHCNm_ADJUSTED_URL = f"{BASE_URL}/ghcnm.tavg.latest.{QUALITY_CONTROL_ADJUSTED_NAME}.tar.gz"
    COUNTRY_CODES_URL = f"{BASE_URL}/{COUNTRY_CODES_FILE_NAME}"

    print(f"  Downloading unadjusted dataset: {GHCNm_UNADJUSTED_URL}")
    download_and_extract_from_url(GHCNm_UNADJUSTED_URL)

    print(f"  Downloading adjusted dataset: {GHCNm_ADJUSTED_URL}")
    download_and_extract_from_url(GHCNm_ADJUSTED_URL)

    print(f"  Downloading country codes for {VERSION}: {COUNTRY_CODES_URL}\n")
    download_from_url(COUNTRY_CODES_URL, COUNTRY_CODES_FILE_NAME)

    VERSION_FOLDER = glob.glob(f"ghcnm.{VERSION}*")[0]

    EXTRACTED_FILES = glob.glob(f"{VERSION_FOLDER}/*")

    print(f"\nSuccessfully downloaded:")
    print(f"  {GHCNm_UNADJUSTED_URL}")
    print(f"  {GHCNm_ADJUSTED_URL}")
    print(f"  {COUNTRY_CODES_URL}")
    print("\nExtracted to:")

    for file in EXTRACTED_FILES:

      print(f"  {file}")

    COUNTRIES_FILE_PATH = get_local_country_file()
    print(f"  {COUNTRY_CODES_FILE_NAME}")
    print("")

    download_landmask_data()

  else:

    COUNTRIES_FILE_PATH = get_local_country_file()

    print(f"Local files:")
    print(f"============\n")

    EXTRACTED_FILES = glob.glob(f"{VERSION_FOLDER[0]}/*")

    for file in EXTRACTED_FILES:

      print(f"  {file}")

    print(f"  {COUNTRIES_FILE_PATH}")
    print('\n  No downloads necessary.')


  

  STATION_FILE_PATH = ""
  GHCN_TEMPERATURES_FILE_PATH = ""

  for file in EXTRACTED_FILES:
    if QUALITY_CONTROL_DATASET in file:
      if '.dat' in file:
        GHCN_TEMPERATURES_FILE_PATH = file
      elif '.inv' in file:
        STATION_FILE_PATH = file

  return STATION_FILE_PATH, COUNTRIES_FILE_PATH, GHCN_TEMPERATURES_FILE_PATH

