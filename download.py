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

  Daily
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt

'''

from constants import *

import urllib.request
import tarfile
import glob
import os
from google_drive_downloader import GoogleDriveDownloader as gdd
from termcolor import colored, cprint
import daily

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


# Daily Data

DAILY_VERSION_FILE_NAME = 'ghcnd-version.txt'

DAILY_DATA_VERSION_URL = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt'

DAILY_COUNTRY_CODES_FILE_NAME = 'ghcnd-countries.txt'

DAILY_COUNTRY_CODES_URL = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt'

DAILY_STATIONS_FILE_NAME = 'ghcnd-stations.txt'

DAILY_STATIONS_METADATA_URL = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt'

COMPILED_DAILY_TEMPERATURE_FILE_REJEX = 'ghcnd.tavg*.dat'

EXTRACTED_DAILY_TEMPERATURE_FOLDER_NAME = 'ghcnd_all'

DAILY_TEMPERATURE_FILE_NAME = 'ghcnd_all.tar.gz'

DAILY_TEMPERATURE_URL = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz'


# Console output marks

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

def get_daily_version():

  DAILY_VERSION_FILE_PATH = download_if_needed(DAILY_VERSION_FILE_NAME, DAILY_DATA_VERSION_URL)

  version_text = open(DAILY_VERSION_FILE_PATH, 'r').read()

  version_name = version_text[37:56]

  return version_name

def download_GHCN_daily_data():

  # Download the Country Codes file for GHCNd
  COUNTRIES_FILE_PATH = download_if_needed(DAILY_COUNTRY_CODES_FILE_NAME, DAILY_COUNTRY_CODES_URL)

  # Download GHCNd Station Metadata
  STATION_FILE_PATH = download_if_needed(DAILY_STATIONS_FILE_NAME, DAILY_STATIONS_METADATA_URL)

  download_landmask_data_if_needed()

  # Check if the compiled daily data exists
  matching_compiled_daily_files = glob.glob(COMPILED_DAILY_TEMPERATURE_FILE_REJEX)

  TEMPERATURES_FILE_PATH = ""

  # The compiled daily data file was found
  if len(matching_compiled_daily_files):

    TEMPERATURES_FILE_PATH = matching_compiled_daily_files[0]

    print(f"\n{check_mark} Found '{COMPILED_DAILY_TEMPERATURE_FILE_REJEX}'")

    print(f"  {check_mark} {TEMPERATURES_FILE_PATH}\n")

  # If the compiled daily data doesn't exist
  else:

    # Get the latest daily version
    DAILY_VERSION = get_daily_version()

    print(f"\n{attention_mark} Missing '{COMPILED_DAILY_TEMPERATURE_FILE_REJEX}'")

    # Check if the folder of daily station files has already been extracted
    matching_extracted_daily_folder = glob.glob(os.path.join('.', EXTRACTED_DAILY_TEMPERATURE_FOLDER_NAME))

    # If so, use it when compiling the daily data
    if len(matching_extracted_daily_folder):

      print(f"  {check_mark} Found '{EXTRACTED_DAILY_TEMPERATURE_FOLDER_NAME}'\n")

    # If not, download and extract the daily data
    else:

      matching_gzipped_files = glob.glob(DAILY_TEMPERATURE_FILE_NAME)

      # If the zipped file does not exist, download and extract the daily station data
      if not len(matching_gzipped_files):

        download_if_needed(DAILY_TEMPERATURE_FILE_NAME, DAILY_TEMPERATURE_URL)

      # If the zipped file already exists, extract it
      else:

        print(f"  {check_mark} Found '{DAILY_TEMPERATURE_FILE_NAME}', extracting... (this could take a while)\n")

        ghcnd_data = tarfile.open(DAILY_TEMPERATURE_FILE_NAME, mode="r|gz")

        ghcnd_data.extractall()
      

    # Compile the extracted files into a GHCNm-like TAVG file
    TEMPERATURES_FILE_PATH = daily.compile_daily_data(DAILY_VERSION, EXTRACTED_DAILY_TEMPERATURE_FOLDER_NAME)

  # Return the file paths
  return STATION_FILE_PATH, COUNTRIES_FILE_PATH, TEMPERATURES_FILE_PATH

