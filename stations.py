from constants import *
import pandas as pd
import numpy as np
from google_drive_downloader import GoogleDriveDownloader as gdd

'''
https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt
'''

unknown_unaddress_text = 'Unknown'
country_code_df = False

'''
What a 5x5 Grid looks like:
https://modernsurvivalblog.com/wp-content/uploads/2013/09/united-states-latitude-longitude.jpg
'''
GRID_SIZE = 5

'''
Google Drive Land Mask obtained from https://github.com/aljones1816/GHCNV4_Analysis
Author: Alan (aljones1816) (Twitter: @TheAlonJ) https://github.com/aljones1816
License: GNU General Public License v3.0
Code for retrieving this file has been modified from original: https://github.com/aljones1816/GHCNV4_Analysis/blob/main/analysis_code.py
'''

gdd.download_file_from_google_drive(file_id='1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj', dest_path='./landmask.dta', unzip=False)

LAND_MASK_FILE_NAME = "./landmask.dta"

land_mask = pd.read_stata(LAND_MASK_FILE_NAME)



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

  gridded_stations_and_country_name = set_station_grid_cells(stations_and_country_name)

  return gridded_stations_and_country_name

def merge_with_country_names(stations, country_codes_file_name):

  global country_code_df

  country_code_df = pd.read_fwf(country_codes_file_name, widths=[3,45], names=['country_code','country'])

  return pd.merge(stations, country_code_df, on='country_code', how='outer')


'''
Code for set_station_grid_cells() and determine_grid_weight() are loosely based on gridding logic from: 
https://github.com/aljones1816/GHCNV4_Analysis/blob/main/analysis_code.py
Author: Alan (aljones1816) (Twitter: @TheAlonJ) https://github.com/aljones1816
https://github.com/aljones1816/GHCNV4_Analysis
License: GNU General Public License v3.0
Some variable names have been renamed but most logic remains intact. I was unable to contact aljones1816 to get his permission to use this code. It should be assumed that the use of the gridding logic in this project should not be construed as a reflection on his work. The contexts for this code is completely different for his use and it's use here, if found to be flawed, should in no way reflect poorly on him. aljones1816 if you see this code, please reach out to me at codingfriend1@gmail.com.
'''

def set_station_grid_cells(stations):

  # Latitude
  count = -90 + (GRID_SIZE / 2)
  stations['latitude_cell'] = 0

  for x in range(-90, 90, GRID_SIZE):
    stations.loc[stations['latitude'].between(x, x + GRID_SIZE), 'latitude_cell'] = count
    count = count + GRID_SIZE

  # Longitude
  count = -180 + (GRID_SIZE / 2)
  stations['longitude_cell'] = 0

  for x in range(-180, 180, GRID_SIZE):
    stations.loc[stations['longitude'].between(x, x + GRID_SIZE), 'longitude_cell'] = count
    count = count + GRID_SIZE

  stations['gridbox'] = stations['latitude_cell'].map(str) + " lat " + stations['longitude_cell'].map(str) + " lon"

  return stations

def determine_grid_weight(grid_label):

  # Since we are only considering land temperatures and not water, we need to determine the percent of the land that consists of land
  matching_land_mask_row = land_mask.loc[land_mask['gridbox'] == grid_label].to_numpy()[0]
  land_percent = float(matching_land_mask_row[0])

  # Extract the center latitude and longitude of the cell from the grid_label
  lat, lat_lab, lon, lon_label = grid_label.split(" ")
  latitude = float(lat)
  longitude = float(lon)

  # Since grids get smaller near the polls, we need to adjust the weight of the grid to give it equal representation to other grids of larger size
  grid_weight = np.sin((latitude + GRID_SIZE / 2) * np.pi / 180) - np.sin(
      (longitude - GRID_SIZE / 2) * np.pi / 180)

  return grid_weight * land_percent

def get_country_name_from_code(country_code):

  return country_code_df.loc[country_code_df['country_code'] == country_code].to_numpy()[0][1]


def get_station_address(station_id, stations):

  station_row = stations.loc[[station_id], ['name', 'country']].to_numpy()[0]

  if not len(station_row):
    return 'Unknown'

  station_name = " ".join([x[0].upper() + x[1:] for x in station_row[0].lower().split("_")])

  station_country = station_row[1]

  return f"{station_name}, {station_country}"

def get_station_gridbox(station_id, stations):

  station_row = stations.loc[[station_id], ['gridbox']].to_numpy()[0]

  if not len(station_row):
    return False

  return station_row[0]
