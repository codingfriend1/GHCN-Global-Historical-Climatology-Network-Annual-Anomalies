from constants import *
import pandas as pd
import numpy as np

'''
https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt
'''

unknown_unaddress_text = 'Unknown'
country_code_df = False

def get_stations(station_file_name, country_codes_file_name):

  dtypes = {
    'station_id': np.object,
    'latitude': np.float64,
    'longitude': np.float64,
    'elevation': np.float64,
    'name': np.object
  }

  names = ['country_code','station_id', 'latitude','longitude','elevation','name']

  colspecs = []

  if VERSION == "v3":
    colspecs = [(0,3), (0,11), (11,20), (21,30), (69,73), (38,68)]
    dtypes['country_code'] = "int64"
  elif VERSION == "v4":
    colspecs = [(0,2), (0,12), (12,21), (21,31), (31,38), (38,69)]
    dtypes['country_code'] = "object"

  stations = pd.read_fwf(
    station_file_name, 
    colspecs=colspecs, 
    names=names, 
    dtype=dtypes, 
    header=None, 
    encoding='utf-8', 
  )

  stations_and_country_name = merge_with_country_names(stations, country_codes_file_name)

  stations_and_country_name = stations_and_country_name.set_index('station_id')

  return stations_and_country_name

def merge_with_country_names(stations, country_codes_file_name):

  global country_code_df

  country_code_df = pd.read_fwf(country_codes_file_name, widths=[3,45], names=['country_code','country'])

  return pd.merge(stations, country_code_df, on='country_code', how='outer')

def get_country_name_from_code(country_code):

  return country_code_df.loc[country_code_df['country_code'] == country_code].to_numpy()[0][1]


def get_station_address(station_id, stations):

  station_row = stations.loc[[station_id], ['name', 'country']].to_numpy()[0]

  if not len(station_row):
    return 'Unknown'

  station_name = " ".join([x[0].upper() + x[1:] for x in station_row[0].lower().split("_")])

  station_country = station_row[1]

  return f"{station_name}, {station_country}"
