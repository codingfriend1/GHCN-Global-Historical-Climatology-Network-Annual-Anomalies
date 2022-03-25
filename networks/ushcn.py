from globals import *
import pandas as pd
import numpy as np
import glob
import os


# When parsing rows for the temperature files for this network, these set the bounds for each column
DATA_COLUMNS = [(0,11), (12, 16)] + generate_month_boundaries([6,7,8,9], 16)

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

