'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from constants import *
import pandas as pd
import numpy as np
from google_drive_downloader import GoogleDriveDownloader as gdd

'''
https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt
'''

country_code_df = False

'''
When forming a grid of latitude and longitude boxes around the earth, this is represents the size of each grid box in degrees
What a 5x5 Grid looks like:
https://modernsurvivalblog.com/wp-content/uploads/2013/09/united-states-latitude-longitude.jpg
'''
GRID_SIZE = 5

'''
Google Drive Land Mask obtained from https://github.com/aljones1816/GHCNV4_Analysis
Author: Alan (aljones1816) (Twitter: @TheAlonJ) https://github.com/aljones1816
License: GNU General Public License v3.0
Code for retrieving this file has been slightly modified from original: https://github.com/aljones1816/GHCNV4_Analysis/blob/main/analysis_code.py
'''
LAND_MASK_FILE_NAME = "./landmask.dta"
gdd.download_file_from_google_drive(file_id='1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj', dest_path=LAND_MASK_FILE_NAME, unzip=False)
land_mask = pd.read_stata(LAND_MASK_FILE_NAME)

# Read the station file, parse it into a usable table, and join relevant information
def get_stations(station_file_name, country_codes_file_name):

  # Specify the datatypes of each station metadata column
  dtypes = {
    'station_id': np.object,
    'latitude': np.float64,
    'longitude': np.float64,
    'elevation': np.float64,
    'name': np.object
  }

  # Name our columns
  names = ['country_code','station_id', 'latitude','longitude','elevation','name']

  # Specify how many characters needed to separate data in the station text metadata
  colspecs = []

  if VERSION == "v3":
    colspecs = [(0,3), (0,11), (11,20), (21,30), (69,73), (38,68)]
    dtypes['country_code'] = "int64"
  elif VERSION == "v4":
    colspecs = [(0,2), (0,12), (12,21), (21,31), (31,38), (38,69)]
    dtypes['country_code'] = "object"

  # Read the station file, and parse it into a usable table
  stations = pd.read_fwf(
    station_file_name, 
    colspecs=colspecs, 
    names=names, 
    dtype=dtypes, 
    header=None, 
    encoding='utf-8', 
  )

  # Merge the station data with their associated country names
  stations_and_country_name = merge_with_country_names(stations, country_codes_file_name)

  # Set the index of the station table to the station_id for easier access
  stations_and_country_name = stations_and_country_name.set_index('station_id')

  # After dividing the world into grid boxes by latitude and longitude, assign each station to a grid box and save the grid box label to the stations table
  gridded_stations_and_country_name = set_station_grid_cells(stations_and_country_name)

  # Return our parsed and joined table
  return gridded_stations_and_country_name

# For add the associated country name to the station metadata
def merge_with_country_names(stations, country_codes_file_name):

  global country_code_df

  country_code_df = pd.read_fwf(country_codes_file_name, widths=[3,45], names=['country_code','country'])

  return pd.merge(stations, country_code_df, on='country_code', how='outer')

'''
Use latitude and longitude lines to divide the world into a grid. Assign each station to a grid and save the grid label in the station's meta data. This can be used to average anomalies by grid using all the stations within that grid. All grid boxes with data can then be averaged to form a world wide average.

Code for set_station_grid_cells() is loosely based on gridding logic from: 

https://github.com/aljones1816/GHCNV4_Analysis/blob/main/analysis_code.py
Author: Alan (aljones1816) (Twitter: @TheAlonJ) https://github.com/aljones1816
https://github.com/aljones1816/GHCNV4_Analysis
License: GNU General Public License v3.0

Some variable names have been renamed but most logic remains intact. I was unable to contact aljones1816 to get his permission to use this code. It should be assumed that the use of the gridding logic in this project should not be construed as a reflection on his work since the context for my code and his are very different. If this code is found to be flawed here, it should in no way reflect poorly on him. aljones1816 if you see this code, please reach out to me at codingfriend1@gmail.com.
'''

def set_station_grid_cells(stations):

  # Latitude
  mid_latitude = -90 + (GRID_SIZE / 2)
  stations['latitude_cell'] = 0

  for x in range(-90, 90, GRID_SIZE):
    stations.loc[stations['latitude'].between(x, x + GRID_SIZE), 'latitude_cell'] = mid_latitude
    mid_latitude = mid_latitude + GRID_SIZE

  # Longitude
  mid_longitude = -180 + (GRID_SIZE / 2)
  stations['longitude_cell'] = 0

  for x in range(-180, 180, GRID_SIZE):
    stations.loc[stations['longitude'].between(x, x + GRID_SIZE), 'longitude_cell'] = mid_longitude
    mid_longitude = mid_longitude + GRID_SIZE

  stations['gridbox'] = stations['latitude_cell'].map(str) + " lat " + stations['longitude_cell'].map(str) + " lon"

  return stations

'''
"The surface area of a grid box decreases with latitude according to the cosine of the latitude. Therefore, when calculating the regional average for a given year, the grid boxes with data [are] weighted by the cosine of the mid-latitude for that box."

Connolly, Ronan & Soon, Willie & Connolly, Michael & Baliunas, Sallie & Berglund, Johan & Butler, C. & Cionco, Rodolfo & Elías, Ana & Fedorov, Valery & Harde, Hermann & Henry, Gregory & Hoyt, Douglas & Humlum, Ole & Legates, David & Luening, Sebastian & Scafetta, Nicola & Solheim, J.-E & Szarka, Laszlo & Van Loon, Harry & Zhang, Weijia. (2021). How much has the Sun influenced Northern Hemisphere temperature trends? An ongoing debate. 

'''
def determine_grid_weight(grid_label):

  # Extract the center latitude and longitude of the cell from the grid_label
  mid_latitude = float(grid_label.split(" ")[0])

  '''
  Since the grid boxes have smaller surface area closer to the earth's poles, we need to reduce the influence/weight of the smaller boxes to account for the smaller area using the mid-latitude of the grid box
  
    "A degree of longitude is widest at the equator with a distance of 69.172 miles (111.321 kilometers). The distance gradually shrinks to zero as they meet at the poles. At 40 degrees north or south, the distance between a degree of longitude is 53 miles (85 kilometers). The line at 40 degrees north runs through the middle of the United States and China, as well as Turkey and Spain. Meanwhile, 40 degrees south is south of Africa, goes through the southern part of Chile and Argentina, and runs almost directly through the center of New Zealand." 

    (Matt Rosenberg)
    ("The Distance Between Degrees of Latitude and Longitude." 24 Jan. 2020, https://www.thoughtco.com/degree-of-latitude-and-longitude-distance-4070616. Accessed 14 Mar. 2022.)

  '''

  # Calculate the weight of the grid box using the cosine of the mid latitude for that box
  grid_weight = np.cos( mid_latitude * (np.pi / 180 ) )

  # If the user wishes to reduce the weight of the grid box further by the percentage of the grid that is made of water, they may enable this in the constants.py file
  if INCLUDE_LAND_RATIO_IN_WEIGHT:
    # Since we are only considering land temperatures and not water, we need to determine the percent of the land that consists of land
    matching_land_mask_row = land_mask.loc[land_mask['gridbox'] == grid_label].to_numpy()[0]
    land_percent = float(matching_land_mask_row[0])

    # Since we are only measuring land temperatures, we want to reduce the weight of the grid box by the ratio of land to water
    return normal_round(grid_weight * land_percent, 4)

  else:

    return normal_round(grid_weight, 4)

# Return the Country name for a provided country_code (could be a 3-digit number or 2 character acronym)
def get_country_name_from_code(country_code):

  return country_code_df.loc[country_code_df['country_code'] == country_code].to_numpy()[0][1]

# Return the name and country for a provided station_id
def get_station_address(station_id, stations):

  station_row = stations.loc[[station_id], ['name', 'country']].to_numpy()[0]

  if not len(station_row):
    return 'Unknown'

  station_name = " ".join([x[0].upper() + x[1:] for x in station_row[0].lower().split("_")])

  station_country = station_row[1]

  return f"{station_name}, {station_country}"

# Get the grid label of the station's assigned grid box
def get_station_gridbox(station_id, stations):

  station_row = stations.loc[[station_id], ['gridbox']].to_numpy()[0]

  if not len(station_row):
    return False

  return station_row[0]
