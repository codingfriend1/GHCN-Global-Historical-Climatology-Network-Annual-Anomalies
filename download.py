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
from termcolor import colored, cprint

EXTRACTED_FILES = []

# Country Codes File and URL

COUNTRY_CODES_FILE_NAME = 'country-codes' if VERSION == 'v3' else 'ghcnm-countries.txt'

COUNTRY_CODES_URL = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/{VERSION}/{COUNTRY_CODES_FILE_NAME}"


# Station metadata and temperature data URL

UNADJUSTED_TAVG_LATEST_URL = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/{VERSION}/ghcnm.tavg.latest.qcu.tar.gz"

ADJUSTED_ACRONYM = "qca" if VERSION == 'v3' else "qcf"

ADJUSTED_TAVG_LATEST_URL = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/{VERSION}/ghcnm.tavg.latest.{ADJUSTED_ACRONYM}.tar.gz"

# USHCN Stations File and URL

USHCN_STATION_METADATA_FILE_NAME = 'ushcn-v2.5-stations.txt'

USHCN_STATIONS_WEB_URL = 'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn-v2.5-stations.txt'

# Landmask data 

LAND_MASK_FILE_NAME = "landmask.dta"

check_mark = colored(u'\u2713', 'green', attrs=['bold'])
attention_mark = colored('!', 'yellow', attrs=['bold'])


def get_ushcn_metadata_file_name():

  return USHCN_STATION_METADATA_FILE_NAME


def download_and_extract_from_url(url):

  ftpstream = urllib.request.urlopen(url)

  ghcnurl = tarfile.open(fileobj=ftpstream, mode="r|gz")

  ghcnurl.extractall()

  extracted_file_names = ghcnurl.getnames()

  return extracted_file_names


def download_from_url(url, file_name):

  urllib.request.urlretrieve(url, file_name)


def download_if_needed(file_name, url, expected_count = 1):

  # Find files matching rejex file_name
  matching_files = glob.glob(file_name)

  # If the number of files found matches the expected count:
  if len(matching_files) >= expected_count:

    # Sort the files
    matching_files.sort()

    # Let the Developer know we don't need to download them
    print(f"\n{check_mark} Found '{file_name}':")
    print(f'  {check_mark} ' + f'\n  {check_mark} '.join(matching_files))

    # Return the file(s)
    return matching_files if expected_count > 1 else matching_files[0]

  # If we are missing 1 or more expected files for this glob
  else:

    # Let the developer know we need to download these files
    print(f"\n{attention_mark} Missing ({expected_count - len(matching_files)}) from '{file_name}'. Downloading from {url}")

    # If the ending of the url is a tar gzip file, prepare to extract the download
    if url.endswith('.tar.gz'):

      # Download and extract the files
      extracted_file_names = download_and_extract_from_url(url)

      # Sort the files
      extracted_file_names.sort()

      # Let the Developer know the extracted file names
      print(f"\n  {check_mark} Downloaded and extracted:")
      print(f'    {check_mark} ' + f'\n    {check_mark} '.join(extracted_file_names))

      # Return the sorted, extracted file names
      return extracted_file_names

    else:

      # Download the file
      download_from_url(url, file_name)

      # Inform the Developer the file has been downloaded
      print(f"\n  {check_mark} Downloaded '{file_name}'")

      # Return the file
      return file_name

def download_landmask_data_if_needed():

  if not os.path.exists(LAND_MASK_FILE_NAME):

    print(f"\n{attention_mark} Missing '{LAND_MASK_FILE_NAME}'.")

    '''
    Google Drive Land Mask obtained from https://github.com/aljones1816/GHCNV4_Analysis
    Author: Alan (aljones1816) (Twitter: @TheAlonJ) https://github.com/aljones1816
    License: GNU General Public License v3.0
    Code for retrieving this file has been slightly modified from original: https://github.com/aljones1816/GHCNV4_Analysis/blob/main/analysis_code.py
    '''
    gdd.download_file_from_google_drive(file_id='1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj', dest_path=os.path.join('.', LAND_MASK_FILE_NAME), unzip=False)

  else:

    print(f"\n{check_mark} Found '{LAND_MASK_FILE_NAME}'")

  return LAND_MASK_FILE_NAME


def validate_constants():

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


def download_GHCN_data():

  # Validate that the constants in `constants.py` are appropriate
  validate_constants()

  # Download the Country Codes file for GHCNm
  COUNTRIES_FILE_PATH = download_if_needed(COUNTRY_CODES_FILE_NAME, COUNTRY_CODES_URL)

  # Download the GHCNm Unadjusted data if needed
  TEMPERATURES_FILE_PATH, STATION_FILE_PATH = download_if_needed(
    f"ghcnm.{VERSION}*/*qcu.*", UNADJUSTED_TAVG_LATEST_URL, expected_count = 2
  )

  # Download the GHCNm Adjusted data if needed
  ADJUSTED_TEMPERATURES_FILE_PATH, ADJUSTED_STATION_METADATA_FILE_PATH = download_if_needed(
    f"ghcnm.{VERSION}*/*{ADJUSTED_ACRONYM}.*", ADJUSTED_TAVG_LATEST_URL, expected_count = 2
  )

  # Download the USHCN Station Metadata file if needed
  USHCN_STATION_METADATA_FILE = download_if_needed(
    USHCN_STATION_METADATA_FILE_NAME, USHCN_STATIONS_WEB_URL
  ) if ONLY_USHCN and VERSION == 'v3' else ''

  # Download the landmask if needed
  download_landmask_data_if_needed()

  print()

  # If the Developer is not using the unadjusted dataset, return the adjusted dataset
  if QUALITY_CONTROL_DATASET != 'qcu':

    TEMPERATURES_FILE_PATH = ADJUSTED_TEMPERATURES_FILE_PATH

    STATION_FILE_PATH = ADJUSTED_STATION_METADATA_FILE_PATH

  # Return the file paths
  return STATION_FILE_PATH, COUNTRIES_FILE_PATH, TEMPERATURES_FILE_PATH

