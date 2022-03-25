'''
  Author: Jon Paul Miles
  Date Created: March 15, 2022

  Daily data README:
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
'''

from globals import *
import pandas as pd
import numpy as np
import glob
from bs4 import BeautifulSoup
import urllib.request
from termcolor import colored, cprint
import os

# When parsing rows for the temperature files for this network, these set the bounds for each column
DATA_COLUMNS = [(0,11), (11, 15)] + generate_month_boundaries([5,6,7,8], 19)

check_mark = colored(u'\u2713', 'green', attrs=['bold'])

attention_mark = colored('!', 'yellow', attrs=['bold'])

# All GHCNd .dly station files have 31 days even if some days are missing
DAYS_IN_MONTH = 31

def download_and_compile_uscrn_data(compiled_file, folder_name, url):

  TEMPERATURES_FILE_PATH = ""

  # Check if the compiled USCRN data exists
  matching_compiled_uscrn_files = glob.glob(compiled_file)

  # The compiled daily data file was found
  if len(matching_compiled_uscrn_files):

    TEMPERATURES_FILE_PATH = matching_compiled_uscrn_files[0]

    print(f"{check_mark} Found '{compiled_file}'")

  # If the compiled daily data doesn't exist
  else:

    print(f"{attention_mark} Missing '{compiled_file}'")

    # Check if the folder of USCRN station files has already been downloaded
    matching_extracted_uscrn_files = glob.glob(os.path.join('.', folder_name, '*'))

    # If so, use it when compiling the data
    if len(matching_extracted_uscrn_files):

      print(f"{check_mark} Found '{folder_name}':")

      print(f'  {check_mark} ' + f'\n  {check_mark} '.join(matching_extracted_uscrn_files))

    # If not, download the USCRN data
    else:

      station_files = []

      print(f"{attention_mark} Missing '{folder_name}'. Downloading from {url}")

      # Make a folder to save the USCRN station files to
      if not os.path.exists(folder_name):

        os.mkdir(folder_name)

      # Read the link to all the station files
      soup = BeautifulSoup(urllib.request.urlopen(url), features="html.parser")

      # Get the links for this HTML page
      for a in soup.find_all('a'):

        link = a['href']

        # If the link is a CRN station .txt file:
        if 'CRN' in link and link.endswith('.txt'):

          # Join the link file name with the url
          station_url = os.path.join(url, link)

          # Join the folder name with the file name
          station_file_path = os.path.join(folder_name, link)

          # Download the file
          urllib.request.urlretrieve(station_url, station_file_path)

          # Add to our station file list for displaying in the console later
          station_files.append(station_file_path) 

      print(f"  {check_mark} Downloaded:")

      print(f'    {check_mark} ' + f'\n  {check_mark} '.join(station_files))

    TEMPERATURES_FILE_PATH = compile_uscrn_data(VERSION, folder_name)

  return TEMPERATURES_FILE_PATH

def get_files():

  COUNTRIES_FILE_PATH = ""

  STATION_FILE_PATH = 'stations.tsv'

  TEMPERATURES_FILE_PATH = download_and_compile_uscrn_data(
    compiled_file = 'uscrn.tavg.v1.dat', 
    folder_name = 'uscrn_stations_v1',
    url = 'https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/'
  )

  return STATION_FILE_PATH, TEMPERATURES_FILE_PATH, COUNTRIES_FILE_PATH


def get_stations(station_file_name):

  names = [ 'station_id', 'country_code', 'state', 'LOCATION', 'VECTOR', 'name', 'latitude', 'longitude', 'elevation', 'STATUS', 'COMMISSIONING', 'CLOSING', 'OPERATION', 'PAIRING', 'network', 'other_station_id' ]
  # names=names,

  stations = pd.read_csv(
    station_file_name, 
    sep="\t",
    names = names,
    header=None,
    skiprows=[0],
    encoding='utf-8', 
  ).reset_index()

  # Pad Station ID
  stations['station_id'] = 'USCRN' + stations['station_id'].astype('str').apply(lambda s: str(s).rjust(6, '0') )

  stations = stations[['country_code', 'station_id', 'latitude', 'longitude', 'elevation', 'name', 'state']]

  stations['country'] = 'United States of America'

  return stations

def has_passing_flags(MFLAG, QFLAG, SFLAG):

  return True

def average_tmax_and_tmin(TMAX_AND_TMIN):

  tavg = math.nan if len(TMAX_AND_TMIN) != 2 or TMAX_AND_TMIN.isnull().any() else int(normal_round(TMAX_AND_TMIN.mean()))

  return tavg

def parse_daily_row(unparsed_row):

  parsed_row = []

  ELEMENT = str(unparsed_row[17:21])

  if not ELEMENT == "TMAX" and not ELEMENT == "TMIN":
    return False

  try:

    STATION_ID = str(unparsed_row[0:11]).strip()
    YEAR = int(unparsed_row[11:15])
    MONTH = int(unparsed_row[15:17])

    parsed_row.append(STATION_ID)
    parsed_row.append(YEAR)
    parsed_row.append(MONTH)
    parsed_row.append(ELEMENT)

    DAYS_IN_MONTH = 31
    FIRST_DAY_INDEX = 21
    CHARACTERS_NEEDED_FOR_READING_AND_FLAGS = 8

    FULL_RANGE = (DAYS_IN_MONTH * CHARACTERS_NEEDED_FOR_READING_AND_FLAGS) + FIRST_DAY_INDEX

    for index in range(FIRST_DAY_INDEX, FULL_RANGE, CHARACTERS_NEEDED_FOR_READING_AND_FLAGS):

      # Temperature comes in tenths of degrees C
      temperature_reading = int(unparsed_row[index:index + 5])

      '''
        https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
        MFLAG1     is the measurement flag for the first day of the month.  There are
                   ten possible values:

                   Blank = no measurement information applicable
                   B     = precipitation total formed from two 12-hour totals
                   D     = precipitation total formed from four six-hour totals
             H     = represents highest or lowest hourly temperature (TMAX or TMIN) 
                     or the average of hourly values (TAVG)
             K     = converted from knots 
             L     = temperature appears to be lagged with respect to reported
                     hour of observation 
                   O     = converted from oktas 
             P     = identified as "missing presumed zero" in DSI 3200 and 3206
                   T     = trace of precipitation, snowfall, or snow depth
             W     = converted from 16-point WBAN code (for wind direction)
        
      '''
      MFLAG = str(unparsed_row[index+5:index+6])

      '''
        https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
        QFLAG1     is the quality flag for the first day of the month.  There are 
                   fourteen possible values:

                   Blank = did not fail any quality assurance check
                   D     = failed duplicate check
                   G     = failed gap check
                   I     = failed internal consistency check
                   K     = failed streak/frequent-value check
             L     = failed check on length of multiday period 
                   M     = failed megaconsistency check
                   N     = failed naught check
                   O     = failed climatological outlier check
                   R     = failed lagged range check
                   S     = failed spatial consistency check
                   T     = failed temporal consistency check
                   W     = temperature too warm for snow
                   X     = failed bounds check
             Z     = flagged as a result of an official Datzilla 
                     investigation
      '''
      QFLAG = str(unparsed_row[index+6:index+7])

      '''
        https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
        SFLAG1     is the source flag for the first day of the month.  There are 
                   thirty possible values (including blank, upper and 
             lower case letters):

                   Blank = No source (i.e., data value missing)
                   0     = U.S. Cooperative Summary of the Day (NCDC DSI-3200)
                   6     = CDMP Cooperative Summary of the Day (NCDC DSI-3206)
                   7     = U.S. Cooperative Summary of the Day -- Transmitted 
                     via WxCoder3 (NCDC DSI-3207)
                   A     = U.S. Automated Surface Observing System (ASOS) 
                           real-time data (since January 1, 2006)
             a     = Australian data from the Australian Bureau of Meteorology
                   B     = U.S. ASOS data for October 2000-December 2005 (NCDC 
                           DSI-3211)
             b     = Belarus update
             C     = Environment Canada
             D     = Short time delay US National Weather Service CF6 daily 
                     summaries provided by the High Plains Regional Climate
               Center
             E     = European Climate Assessment and Dataset (Klein Tank 
                     et al., 2002)     
                   F     = U.S. Fort data 
                   G     = Official Global Climate Observing System (GCOS) or 
                           other government-supplied data
                   H     = High Plains Regional Climate Center real-time data
                   I     = International collection (non U.S. data received through
                     personal contacts)
                   K     = U.S. Cooperative Summary of the Day data digitized from
                     paper observer forms (from 2011 to present)
                   M     = Monthly METAR Extract (additional ASOS data)
             m     = Data from the Mexican National Water Commission (Comision
                     National del Agua -- CONAGUA)
             N     = Community Collaborative Rain, Hail,and Snow (CoCoRaHS)
             Q     = Data from several African countries that had been 
                     "quarantined", that is, withheld from public release
               until permission was granted from the respective 
                     meteorological services
                   R     = NCEI Reference Network Database (Climate Reference Network
                     and Regional Climate Reference Network)
             r     = All-Russian Research Institute of Hydrometeorological 
                     Information-World Data Center
                   S     = Global Summary of the Day (NCDC DSI-9618)
                           NOTE: "S" values are derived from hourly synoptic reports
                           exchanged on the Global Telecommunications System (GTS).
                           Daily values derived in this fashion may differ significantly
                           from "true" daily data, particularly for precipitation
                           (i.e., use with caution).
             s     = China Meteorological Administration/National Meteorological Information Center/
                     Climatic Data Center (http://cdc.cma.gov.cn)
                   T     = SNOwpack TELemtry (SNOTEL) data obtained from the U.S. 
                     Department of Agriculture's Natural Resources Conservation Service
             U     = Remote Automatic Weather Station (RAWS) data obtained
                     from the Western Regional Climate Center    
             u     = Ukraine update    
             W     = WBAN/ASOS Summary of the Day from NCDC's Integrated 
                     Surface Data (ISD).  
                   X     = U.S. First-Order Summary of the Day (NCDC DSI-3210)
             Z     = Datzilla official additions or replacements 
             z     = Uzbekistan update
             
             When data are available for the same time from more than one source,
             the highest priority source is chosen according to the following
             priority order (from highest to lowest):
             Z,R,D,0,6,C,X,W,K,7,F,B,M,m,r,E,z,u,b,s,a,G,Q,I,A,N,T,U,H,S
      '''
      SFLAG = str(unparsed_row[index+7:index+8])

      corrected_temperature = math.nan if temperature_reading == -9999 or not has_passing_flags(MFLAG, QFLAG, SFLAG) else int(temperature_reading)

      parsed_row.append(corrected_temperature)

    return parsed_row

  except:

    print(f"\nCould not parse row:")
    print(unparsed_row)
    print()

    return False

def gather_station_files(FOLDER_WITH_DAILY_DATA):

  # Find all station data files in folder
  station_files = []

  all_stations = os.listdir(FOLDER_WITH_DAILY_DATA)

  # Create an array of all our .dly station file URLs
  for station_file_url in all_stations:

    if 'CRN' in station_file_url and station_file_url.endswith('.txt'):

      station_files.append(os.path.join(FOLDER_WITH_DAILY_DATA, station_file_url))

  return station_files

def convert_to_hundreds(tavg):

  if math.isnan(tavg):

    return math.nan

  elif tavg == -9999.0:

    return -9999

  else:

    return int(normal_round(tavg * 100))

def compile_uscrn_data(VERSION, FOLDER_WITH_DAILY_DATA):

  # Prepare our mega file to save all combined station temperatures too
  OUTPUT_FILE_URL = f"./uscrn.tavg.{VERSION}.dat"

  if os.path.exists(OUTPUT_FILE_URL):
    
    os.remove(OUTPUT_FILE_URL)

  print(f"\nCompiling USCRN data into a GHCNm-like monthly TAVG file to be named '{OUTPUT_FILE_URL}'\n")

  # Prepare the file for editing
  OUTPUT_CONTENT = open(OUTPUT_FILE_URL, 'a')

  station_files = gather_station_files(FOLDER_WITH_DAILY_DATA)

  total_stations = len(station_files)

  station_iterator = 0

  # For each daily station file
  for station_file_url in station_files:

    station_iterator += 1

    print(f"Composing station {station_iterator} of {total_stations}")

    names = [ 'station_id', 'year', 'month', 'tavg' ]

    colspecs = [ (0,5), (6,10), (10, 12), (56,64) ]

    station_daily_values = pd.read_fwf(station_file_url, names = names, colspecs=colspecs)

    # Convert each tavg into an int
    station_daily_values['tavg'] = station_daily_values['tavg'].apply(convert_to_hundreds).astype('Int64')

    station_daily_values['station_id'] = 'USCRN' + station_daily_values['station_id'].astype('str').apply(lambda s: str(s).rjust(6, '0') )

    # Convert the vertical months, into horizontal ones across each year
    station_daily_values = station_daily_values.pivot(

      index=['station_id', 'year'], columns='month', values='tavg'
      
    ).reset_index()

    # If the file has 12 columns, one for each month
    if len(station_daily_values.columns) == 14 and len(station_daily_values.values) > 1:

      # For each row in the station's data
      for year, row in station_daily_values.iterrows():

        # Create a representative string line to save in the output file
        output_row_string = f"\n{row['station_id']}{row['year']}TAVG"

        for month in range(1, 13):

          month_string = str(row[month]).replace('<NA>', '-9999').rjust(5, " ")

          output_row_string = output_row_string + f"{month_string}   "

        # Add the representative line to the output file
        OUTPUT_CONTENT.write(output_row_string)

  print(f"\n{check_mark} USCRN station data compiled into '{OUTPUT_FILE_URL}'\n")

  return OUTPUT_FILE_URL
