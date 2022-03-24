from constants import *
import pandas as pd
import numpy as np
import glob
import os

def compile_station_files_into_dat_file(station_files):

  total_stations = '{:,}'.format(len(station_files))

  station_folder = station_files[0].split('/')[0]

  OUTPUT_FILE_URL = f"{station_folder}.{QUALITY_CONTROL_DATASET}.dat"

  print(f"\n Compiling {total_stations} station files into '{OUTPUT_FILE_URL}'\n")

  if os.path.exists(OUTPUT_FILE_URL):
    
    os.remove(OUTPUT_FILE_URL)

  with open(OUTPUT_FILE_URL, "wb") as output_file:

    for station_file_path in station_files:

      with open(station_file_path, "rb") as station_file_contents:

        output_file.write(station_file_contents.read())

  return OUTPUT_FILE_URL
  

def get_files():

  COUNTRIES_FILE_PATH = ""

  STATION_FILE_PATH = 'ushcn-v2.5-stations.txt'

  station_files = glob.glob(f'ushcn.v2.5*/*.{QUALITY_CONTROL_DATASET}*.tavg')

  TEMPERATURES_FILE_PATH = compile_station_files_into_dat_file(station_files)

  return STATION_FILE_PATH, TEMPERATURES_FILE_PATH, COUNTRIES_FILE_PATH


def get_stations(station_file_name):

  # Specify the datatypes of each station metadata column
  dtypes = {
    'station_id': np.object,
    'latitude': np.float64,
    'longitude': np.float64,
    'elevation': np.float64,
    'name': np.object
  }

  names = ['country_code', 'station_id', 'latitude', 'longitude', 'elevation', 'name', 'state']

  colspecs = [(0,2), (0,11), (12,20), (21,30), (32,37), (41,71), (38, 40)]

  stations = pd.read_fwf(
    station_file_name, 
    colspecs=colspecs, 
    names=names, 
    dtype=dtypes, 
    header=None, 
    encoding='utf-8', 
  )

  stations['country'] = 'United States of America'

  return stations

def parse_temperature_row(unparsed_row_string):

  parsed_row = []

  # The ID to associate with the station for this row
  STATION_ID = str(unparsed_row_string[0:11])

  # The Year this row represents
  YEAR = int(unparsed_row_string[12:16])

  # Add our meta information to our parsed row
  parsed_row.append(STATION_ID)
  parsed_row.append(YEAR)

  # Each month in the year requires 8 characters to fit the Temperature Reading (6 characters), Data Measurement Flag (1 character), Quality Control Flag (1 character), and Data Source Flag (1 character). We'll loop through each month counting 8 characters at a time from the character index of Jan to the ending character index of Dec.
  START_CHARACTER_INDEX_FOR_JAN_TEMPERATURE = 16
  END_CHARACTER_INDEX_FOR_DEC = 124
  NUMBER_OF_CHARACTERS_NEEDED_FOR_EACH_MONTH = 9

  # For each month in the unparsed row string
  for index in range(
    START_CHARACTER_INDEX_FOR_JAN_TEMPERATURE, 
    END_CHARACTER_INDEX_FOR_DEC, 
    NUMBER_OF_CHARACTERS_NEEDED_FOR_EACH_MONTH
  ):

    try:
      
      # Extract the temperature reading value for the current month and convert it to an integer
      VALUE = int(unparsed_row_string[index:index + 6])

      # If the value is -9999 (meaning it's missing) convert it to NaN for better averaging in Python and Excel
      VALUE = VALUE if VALUE != MISSING_VALUE else math.nan

      # Extract each flag associated with this temperature reading
      DMFLAG = str(unparsed_row_string[index + 6:index + 7])
      QCFLAG = str(unparsed_row_string[index + 7:index + 8])
      DSFLAG = str(unparsed_row_string[index + 8:index + 9])

      # Combine the temperature reading and flags into an array
      value_set = [ VALUE, DMFLAG, QCFLAG, DSFLAG ]

      # Save that array as a column for this parsed row
      parsed_row.append(value_set)

    # We don't want the program to crash if one row has a problem, so we catch the mistake, discard that row and keep moving
    except:
      print('Error parsing row', unparsed_row_string)
      return False

  return parsed_row