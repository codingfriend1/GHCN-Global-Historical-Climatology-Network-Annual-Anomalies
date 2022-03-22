'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from constants import *
import pandas as pd
import numpy as np
import os
import download
import glob

from networks import ghcn
from networks import ushcn
from networks import uscrn

country_code_df = False

land_mask = {}

# Arctic Circle, i.e., 66° 33′N.
ARTIC_CIRCLE_LATITUDE = 60

'''
When forming a grid of latitude and longitude boxes around the earth, this is represents the size of each grid box in degrees
What a 5x5 Grid looks like:
https://modernsurvivalblog.com/wp-content/uploads/2013/09/united-states-latitude-longitude.jpg
'''
GRID_SIZE = 5

def read_land_mask():

  global land_mask

  land_mask = pd.read_stata(download.LAND_MASK_FILE_NAME)


'''
  Determine what setting/environment the station is in based on its popcls and popcss
  https://www.ncei.noaa.gov/pub/data/ghcn/v3/README

  POPCLS: population class 
    (U=Urban (>50,000 persons); 
    (S=Suburban (>=10,000 and <= 50,000 persons);
    (R=Rural (<10,000 persons)
    City and town boundaries are determined from location of station
    on Operational Navigation Charts with a scale of 1 to 1,000,000.
    For cities > 100,000 persons, population data were provided by
    the United Nations Demographic Yearbook. For smaller cities and
    towns several atlases were uses to determine population.

  POPCSS: population class as determined by Satellite night lights 
   (C=Urban, B=Suburban, A=Rural)
'''
def get_environment(row):

  if (row['popcls'] == 'R') & (row['popcss'] == 'A'):

    return 'rural'

  elif (row['popcls'] == 'U') & (row['popcss'] == 'C'):

    return 'urban'

  else:

    return 'suburban'


def get_station_environment_list():

  v3_station_file_name = glob.glob(f"ghcnm.v3*/*qcu.inv")[0]

  dtypes = { 'station_id': str }

  names = ['station_id', 'popcls', 'popcss']

  colspecs = [(0,11), (73, 74), (106,107)]

  stations = pd.read_fwf(
    v3_station_file_name, 
    colspecs=colspecs, 
    names=names, 
    dtype=dtypes, 
    header=None, 
    encoding='utf-8', 
  )

  stations['partial_station_id'] = stations['station_id'].str[3:]

  stations['environment'] = stations.apply(get_environment, axis=1)

  stations.drop(['popcls', 'popcss', 'station_id'], axis=1, inplace=True)

  return stations


def limit_stations_by_environment(stations, environment):

  if environment == 'rural':

    stations = stations[(stations['environment'] == 'rural')]

  elif environment == 'suburban':

    stations = stations[(stations['environment'] == 'suburban')]

  elif environment == 'urban':

    stations = stations[(stations['environment'] == 'urban')]

  elif environment == 'rural and suburban':

    stations = stations[(stations['environment'] == 'rural') | (stations['environment'] == 'suburban')]

  elif environment == 'suburban and urban':

    stations = stations[(stations['environment'] == 'suburban') | (stations['environment'] == 'urban')]

  elif environment == 'rural and urban':

    stations = stations[(stations['environment'] == 'rural') | (stations['environment'] == 'urban')]

  return stations

# Read the station file, parse it into a usable table, and join relevant information
def get_stations(station_file_name, country_codes_file_name):

  stations = []

  if NETWORK == 'GHCN':

    stations = ghcn.get_stations(station_file_name, country_codes_file_name)

  elif NETWORK == 'USHCN':

    stations = ushcn.get_stations(station_file_name)

  elif NETWORK == 'USCRN':

    stations = uscrn.get_stations(station_file_name)

  # After dividing the world into grid boxes by latitude and longitude, assign each station to a grid box and save the grid box label to the stations table
  stations = set_station_grid_cells(stations)

  stations_by_environment = get_station_environment_list()

  stations = merge_with_environment(stations, stations_by_environment)

  stations = stations.set_index('station_id')

  read_land_mask()

  stations = limit_stations_by_environment(stations, SURROUNDING_CLASS)

  if IN_COUNTRY and NETWORK == 'GHCN':

    UPPERCASE_COUNTRIES = list(map(str.upper, IN_COUNTRY))

    if 'ARTIC' in UPPERCASE_COUNTRIES:

      stations = stations.loc[
        (stations['country'].isin(UPPERCASE_COUNTRIES)) | 
        (stations['latitude'] >= ARTIC_CIRCLE_LATITUDE)
      ]
      
    else:

      stations = stations.loc[
        stations['country'].isin(UPPERCASE_COUNTRIES)
      ]

  # Return our parsed and joined table
  return stations

# For add the associated country name to the station metadata
def merge_with_environment(stations, stations_by_environment):

  stations['partial_station_id'] = stations['station_id'].str[3:]

  df = stations.merge(stations_by_environment, on='partial_station_id', how='left')

  df.drop(['partial_station_id'], axis=1, inplace=True)

  return df

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
def determine_grid_weight(grid_label, include_land_ratio_in_weight = False):

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
  if include_land_ratio_in_weight:
    # Since we are only considering land temperatures and not water, we need to determine the percent of the land that consists of land
    matching_land_mask_row = land_mask.loc[land_mask['gridbox'] == grid_label].to_numpy()[0]
    land_percent = float(matching_land_mask_row[0])

    # Since we are only measuring land temperatures, we want to reduce the weight of the grid box by the ratio of land to water
    return normal_round(grid_weight * land_percent, 4)

  else:

    return normal_round(grid_weight, 4)

# Return the name and country for a provided station_id
def get_station_address(station_id, stations):

  station_row = []

  if NETWORK == 'GHCN':

    station_row = stations.loc[[station_id], ['name', 'country']].to_numpy()[0]

  elif NETWORK in ['USHCN', 'USCRN']:

    station_row = stations.loc[[station_id], ['name', 'state']].to_numpy()[0]

  if not len(station_row):
    
    return 'Unknown'

  station_name = " ".join([x[0].upper() + x[1:] for x in station_row[0].lower().split("_")])

  station_province = station_row[1]

  return f"{station_name}, {station_province}"

  

# Get the grid label of the station's assigned grid box
def get_station_gridbox(station_id, stations):

  station_row = stations.loc[[station_id], ['gridbox']].to_numpy()[0]

  if not len(station_row):
    return False

  return station_row[0]
