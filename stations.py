from constants import *
import pandas as pd

'''
https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt
'''

unknown_unaddress_text = 'Unknown'

def get_stations(station_file_name, country_codes_file_name):

  stations = pd.read_fwf(
    station_file_name, 
    colspecs=[(0,2), (0,12), (12,21), (21,31), (31,38), (38,69)], 
    names=['country_code','station_id', 'latitude','longitude','elevation','name'],
    header=None, encoding='utf-8'
  )

  stations_and_country_name = merge_with_country_names(stations, country_codes_file_name)

  stations_and_country_name = stations_and_country_name.set_index('station_id')

  return stations_and_country_name

def merge_with_country_names(stations, country_codes_file_name):

  country_code_df = pd.read_fwf(country_codes_file_name, widths=[3,45], names=['country_code','country'])

  return pd.merge(stations, country_code_df, on='country_code', how='outer')


def get_station_address(station_id, stations):

  station_row = stations.loc[[station_id], ['name', 'country']].to_numpy()[0]

  if not len(station_row):
    return 'Unknown'

  station_name = " ".join([x[0].upper() + x[1:] for x in station_row[0].lower().split("_")])

  station_country = station_row[1]

  return f"{station_name}, {station_country}"
