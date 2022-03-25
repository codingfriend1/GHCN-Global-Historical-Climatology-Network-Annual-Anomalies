from globals import *
import pandas as pd
import numpy as np
import glob
import daily

# When parsing rows for the temperature files for this network, these set the bounds for each column
DATA_COLUMNS = [(0,11), (11, 15)] + generate_month_boundaries([5,6,7,8], 19)


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
    'name': np.object,
    'country_code': "object"
  }

  if VERSION == "v3":

    colspecs = [(0,3), (0,11), (11,20), (21,30), (69,73), (38,68)]

    dtypes['country_code'] = "int64"

  elif VERSION == "v4":

    colspecs = [(0,2), (0,12), (12,21), (21,31), (31,38), (38,69)]

  elif VERSION == "daily":

    colspecs = [(0,2), (0,12), (12,20), (21,30), (31,37), (41,71)]

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
