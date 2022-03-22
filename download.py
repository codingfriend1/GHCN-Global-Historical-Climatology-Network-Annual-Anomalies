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
from bs4 import BeautifulSoup
from google_drive_downloader import GoogleDriveDownloader as gdd
from termcolor import colored, cprint
import daily
import uscrn

DOWNLOADABLES = {
  
  'GHCN': {

    'v3': {

      'countries': {
        'file_name': 'country-codes',
        'url': 'https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/country-codes'
      },

      'quality_adjusted_version': {

        'qcu': {
          'file_name': f"ghcnm.v3*/*qcu.*",
          'url': 'https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/ghcnm.tavg.latest.qcu.tar.gz',
          'expected_count': 2
        },

        'qca': {
          'file_name': f"ghcnm.v3*/*qca.*",
          'url': 'https://www1.ncdc.noaa.gov/pub/data/ghcn/v3/ghcnm.tavg.latest.qca.tar.gz',
          'expected_count': 2
        }

      }

    },

    'v4': {

      'countries': {
        'file_name': 'ghcnm-countries.txt',
        'url': 'https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm-countries.txt'
      },

      'quality_adjusted_version': {

        'qcu': {
          'file_name': f"ghcnm.v4*/*qcu.*",
          'url': 'https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcu.tar.gz',
          'expected_count': 2
        },

        'qcf': {
          'file_name': f"ghcnm.v4*/*qcf.*",
          'url': 'https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcf.tar.gz',
          'expected_count': 2
        }

      }

    },

  },

  'USHCN': {

    'v2.5': {

      'stations': {
        'file_name': 'ushcn-v2.5-stations.txt',
        'url': 'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn-v2.5-stations.txt'
      },

      'quality_adjusted_version': {

        'raw': {
          'file_name': 'ushcn.v2.5*/*.raw.tavg',
          'url': 'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn.tavg.latest.raw.tar.gz'
        },

        'tob': {
          'file_name': 'ushcn.v2.5*/*.tob.tavg',
          'url': 'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn.tavg.latest.tob.tar.gz'
        },

        'FLs': {
          'file_name': 'ushcn.v2.5*/*.FLs*.tavg',
          'url': 'https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/ushcn.tavg.latest.FLs.52j.tar.gz'
        }

      },

    }

  },

  'USCRN': {

    'v1': {

      'stations': {
        'file_name': 'stations.tsv',
        'url': 'https://www.ncei.noaa.gov/pub/data/uscrn/products/stations.tsv'
      },

      'quality_adjusted_version': {

        'monthly01': {
          'file_name': 'monthly01',
          'folder_name': 'uscrn_stations_v1',
          'compiled_file': 'uscrn.tavg.v1.dat',
          'url': 'https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/'
        }

      }

    }
    
  }

}

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


def get_correct_bundles(NETWORK, VERSION, QUALITY_CONTROL_DATASET):

  STATIONS_BUNDLE = False
  COUNTRIES_BUNDLE = False
  TEMPERATURE_BUNDLE = False

  if NETWORK in DOWNLOADABLES:

    NETWORK_DOWNLOADABLES = DOWNLOADABLES[NETWORK]

    if VERSION in NETWORK_DOWNLOADABLES:

      NETWORK_VERSION_DOWNLOADABLES = NETWORK_DOWNLOADABLES[VERSION]

      STATIONS_BUNDLE = NETWORK_VERSION_DOWNLOADABLES['stations'] if 'stations' in NETWORK_VERSION_DOWNLOADABLES else False

      COUNTRIES_BUNDLE = NETWORK_VERSION_DOWNLOADABLES['countries'] if 'countries' in NETWORK_VERSION_DOWNLOADABLES else False

      if QUALITY_CONTROL_DATASET in NETWORK_VERSION_DOWNLOADABLES['quality_adjusted_version']:

        TEMPERATURE_BUNDLE = NETWORK_VERSION_DOWNLOADABLES['quality_adjusted_version'][QUALITY_CONTROL_DATASET]

      else:

        QUALITY_DATASET_CHOICES = NETWORK_VERSION_DOWNLOADABLES['quality_adjusted_version'].keys()

        print(f"Sorry, but version '{QUALITY_CONTROL_DATASET}' is not supported in network '{NETWORK} {VERSION}'. Please use one of:")
        print(f"  " + "\n  ".join(QUALITY_DATASET_CHOICES))

        quit()

    else:

      version_choices = NETWORK_DOWNLOADABLES.keys()

      print(f"Sorry, but version '{VERSION}' is not supported in network '{NETWORK}'. Please use one of:")
      print(f"  " + "\n  ".join(version_choices))

      quit()

  else:

    network_choices = DOWNLOADABLES.keys()

    print(f"Sorry, but network '{NETWORK}' is not supported. Please use one of:")
    print(f"  " + "\n  ".join(network_choices))

    quit()


  return STATIONS_BUNDLE, COUNTRIES_BUNDLE, TEMPERATURE_BUNDLE

def compile_station_files_into_dat_file(STATION_FILES):

  total_stations = '{:,}'.format(len(STATION_FILES))

  STATION_FOLDER = STATION_FILES[0].split('/')[0]

  OUTPUT_FILE_URL = f"{STATION_FOLDER}.{QUALITY_CONTROL_DATASET}.dat"

  print(f"\n Compiling {total_stations} station files into '{OUTPUT_FILE_URL}'\n")

  if os.path.exists(OUTPUT_FILE_URL):
    
    os.remove(OUTPUT_FILE_URL)

  with open(OUTPUT_FILE_URL, "wb") as output_file:

    for station_file_path in STATION_FILES:

      with open(station_file_path, "rb") as station_file_contents:

        output_file.write(station_file_contents.read())

  return OUTPUT_FILE_URL

def download_and_compile_uscrn_data(TEMPERATURE_BUNDLE):

  TEMPERATURES_FILE_PATH = ""

  # Check if the compiled USCRN data exists
  matching_compiled_uscrn_files = glob.glob(TEMPERATURE_BUNDLE['compiled_file'])

  # The compiled daily data file was found
  if len(matching_compiled_uscrn_files):

    TEMPERATURES_FILE_PATH = matching_compiled_uscrn_files[0]

    print(f"\n{check_mark} Found '{TEMPERATURE_BUNDLE['compiled_file']}'")

    print(f"  {check_mark} {TEMPERATURES_FILE_PATH}\n")

  # If the compiled daily data doesn't exist
  else:

    print(f"\n{attention_mark} Missing '{TEMPERATURE_BUNDLE['compiled_file']}'")

    # Check if the folder of USCRN station files has already been downloaded
    matching_extracted_uscrn_files = glob.glob(os.path.join('.', TEMPERATURE_BUNDLE['folder_name'], '*'))

    # If so, use it when compiling the data
    if len(matching_extracted_uscrn_files):

      print(f"\n{check_mark} Found '{TEMPERATURE_BUNDLE['folder_name']}':")
      print(f'  {check_mark} ' + f'\n  {check_mark} '.join(matching_extracted_uscrn_files))

    # If not, download the USCRN data
    else:

      station_files = []

      print(f"\n{attention_mark} Missing '{TEMPERATURE_BUNDLE['folder_name']}'. Downloading from {TEMPERATURE_BUNDLE['url']}")

      # Make a folder to save the USCRN station files to
      os.mkdir(TEMPERATURE_BUNDLE['folder_name'])

      # Read the link to all the station files
      soup = BeautifulSoup(urllib.request.urlopen(TEMPERATURE_BUNDLE['url']), features="html.parser")

      # Get the links for this HTML page
      for a in soup.find_all('a'):

        link = a['href']

        # If the link is a CRN station .txt file:
        if 'CRN' in link and link.endswith('.txt'):

          # Join the link file name with the url
          station_url = os.path.join(TEMPERATURE_BUNDLE['url'], link)

          # Join the folder name with the file name
          station_file_path = os.path.join(TEMPERATURE_BUNDLE['folder_name'], link)

          # Download the file
          download_from_url(station_url, station_file_path)

          # Add to our station file list for displaying in the console later
          station_files.append(station_file_path) 

      print(f"\n  {check_mark} Downloaded:")
      print(f'  {check_mark} ' + f'\n  {check_mark} '.join(station_files))

    TEMPERATURES_FILE_PATH = uscrn.compile_uscrn_data(VERSION, TEMPERATURE_BUNDLE['folder_name'])

  return TEMPERATURES_FILE_PATH

def download_data():

  if NETWORK == 'GHCN' and VERSION == 'daily':

    return download_GHCN_daily_data()

  else:

    STATIONS_BUNDLE, COUNTRIES_BUNDLE, TEMPERATURE_BUNDLE = get_correct_bundles(
      NETWORK, VERSION, QUALITY_CONTROL_DATASET
    )

    COUNTRIES_FILE_PATH, STATION_FILE_PATH, TEMPERATURES_FILE_PATH, TEMPERATURES_FOLDER = ("", "", "", "")

    if STATIONS_BUNDLE:

      STATION_FILE_PATH = download_if_needed(STATIONS_BUNDLE['file_name'], STATIONS_BUNDLE['url'])

    if COUNTRIES_BUNDLE:

      COUNTRIES_FILE_PATH = download_if_needed(COUNTRIES_BUNDLE['file_name'], COUNTRIES_BUNDLE['url'])

    if TEMPERATURE_BUNDLE:

      expected_count = TEMPERATURE_BUNDLE['expected_count'] if 'expected_count' in TEMPERATURE_BUNDLE else 1

      if expected_count == 2:

        TEMPERATURES_FILE_PATH, STATION_FILE_PATH = download_if_needed(
          TEMPERATURE_BUNDLE['file_name'], TEMPERATURE_BUNDLE['url'], expected_count
        )

      # If the expected_count is not 2, then it is likely the USHCN or USCRN network in which case we will expect a folder of station files rather than a single .dat file
      else:

        STATION_FILES = []

        if NETWORK == 'USCRN':

          TEMPERATURES_FILE_PATH = download_and_compile_uscrn_data(TEMPERATURE_BUNDLE)

        else:
          
          STATION_FILES = download_if_needed(
            TEMPERATURE_BUNDLE['file_name'], TEMPERATURE_BUNDLE['url'], expected_count = 3
          )

          # Compile the station files into a single .dat file
          TEMPERATURES_FILE_PATH = compile_station_files_into_dat_file(STATION_FILES)

    download_landmask_data_if_needed()

    return STATION_FILE_PATH, TEMPERATURES_FILE_PATH, COUNTRIES_FILE_PATH


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
  return STATION_FILE_PATH, TEMPERATURES_FILE_PATH, COUNTRIES_FILE_PATH

