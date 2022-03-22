from constants import *
import pandas as pd
import numpy as np
import glob
import daily

def get_files():

  STATION_FILE_PATH, TEMPERATURES_FILE_PATH, COUNTRIES_FILE_PATH = "", "", ""

  if VERSION == 'v3':

    COUNTRIES_FILE_PATH = 'country-codes'

    STATION_FILE_PATH = glob.glob(f"ghcnm.v3*/*{QUALITY_CONTROL_DATASET}.inv")[0]

    TEMPERATURES_FILE_PATH = glob.glob(f"ghcnm.v3*/*{QUALITY_CONTROL_DATASET}.dat")[0]

  elif VERSION == 'v4':

    COUNTRIES_FILE_PATH = 'ghcnm-countries.txt'

    STATION_FILE_PATH = glob.glob(f"ghcnm.v4*/*{QUALITY_CONTROL_DATASET}.inv")[0]

    TEMPERATURES_FILE_PATH = glob.glob(f"ghcnm.v4*/*{QUALITY_CONTROL_DATASET}.dat")[0]
    
  elif VERSION == 'daily':

    COUNTRIES_FILE_PATH = 'ghcnd-countries.txt'

    STATION_FILE_PATH = 'ghcnd-stations.txt'

    # Check if daily data has been compiled already
    compiled_daily_data = glob.glob("ghcnd.tavg.*.all.dat")

    # If not
    if not len(compiled_daily_data):

      # Get the version of the daily data
      daily_version = open('ghcnd-version.txt', 'r').read()[37:56]

      # And compile the daily data into a GHCNm-like file
      TEMPERATURES_FILE_PATH = daily.compile_daily_data(daily_version, 'ghcnd_all')

    # If the daily data has already been compiled,
    else:

      # Return the compiled file
      TEMPERATURES_FILE_PATH = compiled_daily_data[0]

  return STATION_FILE_PATH, TEMPERATURES_FILE_PATH, COUNTRIES_FILE_PATH


# For add the associated country name to the station metadata
def merge_with_country_names(stations, country_codes_file_name):

  global country_code_df

  country_code_df = pd.read_fwf(country_codes_file_name, widths=[3,45], names=['country_code','country'])

  return pd.merge(stations, country_code_df, on='country_code', how='outer')


def get_stations(station_file_name, country_codes_file_name):

  # Name our columns
  names = ['country_code', 'station_id', 'latitude', 'longitude', 'elevation', 'name']

  # Specify the datatypes of each station metadata column
  dtypes = {
    'station_id': np.object,
    'latitude': np.float64,
    'longitude': np.float64,
    'elevation': np.float64,
    'name': np.object
  }

  if VERSION == "v3":

    names = ['country_code', 'station_id',  'latitude', 'longitude', 'elevation', 'name']

    colspecs = [(0,3), (0,11), (11,20), (21,30), (69,73), (38,68)]

    dtypes['country_code'] = "int64"

  elif VERSION == "v4":

    colspecs = [(0,2), (0,12), (12,21), (21,31), (31,38), (38,69)]

    dtypes['country_code'] = "object"

  elif VERSION == "daily":

    colspecs = [(0,2), (0,12), (12,20), (21,30), (31,37), (41,71)]

    dtypes['country_code'] = "object"

  stations = pd.read_fwf(
    station_file_name, 
    colspecs=colspecs, 
    names=names, 
    dtype=dtypes, 
    header=None, 
    encoding='utf-8', 
  )

  # If using the GHCN network, merge the station data with their associated country names
  stations = merge_with_country_names(stations, country_codes_file_name)

  return stations


'''
2.2.1 DATA FORMAT

  Variable          Columns      Type
  --------          -------      ----

  ID                 1-11        Integer
  YEAR              12-15        Integer
  ELEMENT           16-19        Character
  VALUE1            20-24        Integer
  DMFLAG1           25-25        Character
  QCFLAG1           26-26        Character
  DSFLAG1           27-27        Character
    .                 .             .
    .                 .             .
    .                 .             .
  VALUE12          108-112       Integer
  DMFLAG12         113-113       Character
  QCFLAG12         114-114       Character
  DSFLAG12         115-115       Character

  Variable Definitions:

  ID: Station identification code. First two characters are FIPS country code

  YEAR: 4 digit year of the station record.

  ELEMENT: element type, monthly mean temperature="TAVG"

When splitting the unparsed row string, we start each snippet of data one character index early since the first character is inclusive in programming languages, but they may end with the same character index because the final character is not inclusive
'''
def parse_temperature_row(unparsed_row_string):

  parsed_row = []

  # In version 4 of GHCNm, the first two alpha characters of the STATION_ID represent the abbreviated country code. We can use this to associate the country name with each station. In version 3, the first 3 digits represent the country code.
  COUNTRY_CODE = str(unparsed_row_string[0:2]) if VERSION == "v4" or NETWORK == 'USCRN' else str(unparsed_row_string[0:3])

  # The ID to associate with the station for this row
  STATION_ID = str(unparsed_row_string[0:11])

  # The Year this row represents
  YEAR = int(unparsed_row_string[11:15])

  # The Element is either TAVG, TMAX, or TMIN. In the dataset used here, this value is always TAVG, which is why we don't add it to our parsed row.
  ELEMENT = unparsed_row_string[15:19]

  # Add our meta information to our parsed row
  parsed_row.append(COUNTRY_CODE)
  parsed_row.append(STATION_ID)
  parsed_row.append(YEAR)

  # Each month in the year requires 8 characters to fit the Temperature Reading (5 characters), Data Measurement Flag (1 character), Quality Control Flag (1 character), and Data Source Flag (1 character). We'll loop through each month counting 8 characters at a time from the character index of Jan to the ending character index of Dec.
  START_CHARACTER_INDEX_FOR_JAN_TEMPERATURE = 19
  END_CHARACTER_INDEX_FOR_DEC = 115
  NUMBER_OF_CHARACTERS_NEEDED_FOR_EACH_MONTH = 8

  # For each month in the unparsed row string
  for index in range(
    START_CHARACTER_INDEX_FOR_JAN_TEMPERATURE, 
    END_CHARACTER_INDEX_FOR_DEC, 
    NUMBER_OF_CHARACTERS_NEEDED_FOR_EACH_MONTH
  ):

    try:
      
      # Extract the temperature reading value for the current month and convert it to an integer
      VALUE = int(unparsed_row_string[index:index + 5])

      # If the value is -9999 (meaning it's missing) convert it to NaN for better averaging in Python and Excel
      VALUE = VALUE if VALUE != MISSING_VALUE else math.nan

      # Extract each flag associated with this temperature reading
      DMFLAG = str(unparsed_row_string[index + 5:index + 6])
      QCFLAG = str(unparsed_row_string[index + 6:index + 7])
      DSFLAG = str(unparsed_row_string[index + 7:index + 8])

      # Combine the temperature reading and flags into an array
      value_set = [ VALUE, DMFLAG, QCFLAG, DSFLAG ]

      # Save that array as a column for this parsed row
      parsed_row.append(value_set)

    # We don't want the program to crash if one row has a problem, so we catch the mistake, discard that row and keep moving
    except:
      print('Error parsing row', unparsed_row_string)
      return False

  return parsed_row