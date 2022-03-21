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

# Country Codes File and URL

COUNTRY_CODES_FILE_NAME = 'country-codes' if VERSION == 'v3' else 'ghcnm-countries.txt'

COUNTRY_CODES_URL = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/{VERSION}/{COUNTRY_CODES_FILE_NAME}"


# Station metadata and temperature data URL

ADJUSTED_ACRONYM = "qca" if VERSION == 'v3' else "qcf"

UNADJUSTED_TAVG_LATEST_URL = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/{VERSION}/ghcnm.tavg.latest.qcu.tar.gz"

ADJUSTED_TAVG_LATEST_URL = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/{VERSION}/ghcnm.tavg.latest.{ADJUSTED_ACRONYM}.tar.gz"

# USHCN Stations File and URL

USHCN_STATION_METADATA_FILE_NAME = 'ushcn-v2.5-stations.txt'

USHCN_STATIONS_WEB_URL = 'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn-v2.5-stations.txt'

# Landmask data 

LAND_MASK_FILE_NAME = "landmask.dta"


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

  # In the console, inform the Developer that we are checking if the file exists
  print(f"\nChecking if '{file_name}' exists...")

  # Find files matching rejex file_name
  matching_files = glob.glob(file_name)

  # If the number of files found matches the expected count:
  if len(matching_files) >= expected_count:

    # Sort the files
    matching_files.sort()

    # Let the Developer know we don't need to download them
    print(f"  No need for a download. Found:")
    print('    ' + '\n    '.join(matching_files))

    # Return the files
    return matching_files

  else:

    # If the ending of the url is a tar gzip file, prepare to extract the download
    needs_extraction = url.endswith('.tar.gz')

    # Let the developer know we need to download these files
    print(f"  Expected {expected_count} file(s). Found ({len(matching_files)}). Downloading{' and extracting' if needs_extraction else ''} from {url}")

    # If the files are zipped:
    if needs_extraction:

      # Download and extract the files
      extracted_file_names = download_and_extract_from_url(url)

      # Sort the files
      extracted_file_names.sort()

      # Let the Developer know the extracted file names
      print(f"  Successfully downloaded and extracted:")
      print('    ' + '\n    '.join(extracted_file_names))

      # Return the sorted, extracted file names
      return extracted_file_names

    else:

      # Download the file
      download_from_url(url, file_name)

      # Inform the Developer the file has been downloaded
      print(f"  Successfully downloaded:")
      print(f"    {file_name}")

      # Return the file
      return [ file_name ]

def download_landmask_data_if_needed():

  print(f"\nChecking if '{LAND_MASK_FILE_NAME}' exists...")

  if not os.path.exists(LAND_MASK_FILE_NAME):
    '''
    Google Drive Land Mask obtained from https://github.com/aljones1816/GHCNV4_Analysis
    Author: Alan (aljones1816) (Twitter: @TheAlonJ) https://github.com/aljones1816
    License: GNU General Public License v3.0
    Code for retrieving this file has been slightly modified from original: https://github.com/aljones1816/GHCNV4_Analysis/blob/main/analysis_code.py
    '''
    gdd.download_file_from_google_drive(file_id='1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj', dest_path=os.path.join('.', LAND_MASK_FILE_NAME), unzip=False)

  else:

    print(f"  Found '{LAND_MASK_FILE_NAME}'. No need for a download.")

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
  COUNTRIES_FILE_PATH = download_if_needed(COUNTRY_CODES_FILE_NAME, COUNTRY_CODES_URL)[0]

  # Download the GHCNm Unadjusted data if needed
  GHCN_TEMPERATURES_FILE_PATH, STATION_FILE_PATH = download_if_needed(
    f"ghcnm.{VERSION}*/*qcu.*",UNADJUSTED_TAVG_LATEST_URL, expected_count = 2
  )

  # Download the GHCNm Adjusted data if needed
  download_if_needed(
    f"ghcnm.{VERSION}*/*{ADJUSTED_ACRONYM}.*", ADJUSTED_TAVG_LATEST_URL, expected_count = 2
  )

  # Download the USHCN Station Metadata file if needed
  USHCN_STATION_METADATA_FILE = download_if_needed(USHCN_STATION_METADATA_FILE_NAME, USHCN_STATIONS_WEB_URL)[0] if ONLY_USHCN and VERSION == 'v3' else ''

  # Download the landmask if needed
  download_landmask_data_if_needed()

  print()

  # Return the file paths
  return STATION_FILE_PATH, COUNTRIES_FILE_PATH, GHCN_TEMPERATURES_FILE_PATH

