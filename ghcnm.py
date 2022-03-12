from constants import *
import pandas as pd
import math

'''
https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt
'''

MISSING_VALUE = -9999
COLUMN_INDEX_FOR_JAN_GROUPING = 2

def get_permitted_reading(month_grouping):

  VALUE = int(month_grouping[0]) if not math.isnan(month_grouping[0]) else math.nan
  DMFLAG = month_grouping[1]
  QCFLAG = month_grouping[2]
  DSFLAG = month_grouping[3]

  return VALUE if not PURGE_FLAGS or (not DMFLAG == 'E' and QCFLAG == ' ' and DSFLAG == ' ') else math.nan

def get_station_start_and_end_year(temp_data_for_station):
  start_year = temp_data_for_station.iloc[0]['year']
  end_year = temp_data_for_station.iloc[len(temp_data_for_station) - 1]['year']

  return start_year, end_year

# Read .dat file and parse into a usable dataframe, replacing -9999 with NaN
def get_ghcnm_by_station(url):

  colspecs = [ (0, 2), (0,11), (11,15), (15,19) ]

  names = ['country_code', 'station_id', 'year', 'element']

  i = 19

  for m in range(1,13):

    month = str(m)

    month_colspecs = [ (i, i + 5), (i + 5, i + 6), (i + 6, i + 7), (i + 7, i + 8) ]

    month_names = [ 'VALUE' + month, 'DMFLAG' + month, 'QCFLAG' + month, 'DSFLAG' + month ]

    for cell in range(0, 4):
        colspecs.append(month_colspecs[cell]) 
        names.append(month_names[cell])

    i += 8

  ghcnm_dataframe = pd.read_fwf(url, colspecs=colspecs, names=names, header=None)

  ghcnm_dataframe.replace(to_replace=MISSING_VALUE, value=math.nan, inplace=True)

  ghcnm_dataframe_by_station_by_country = ghcnm_dataframe.groupby(['station_id'])

  return ghcnm_dataframe

# Create a range of years based on the Developer's configuration and fill it with the matching data from the station's temperature readings by month after first removing flagged or unwanted data
def fit_permitted_data_to_range(temp_data_for_station):

  absolute_temperatures_by_month = [
    [], # jan average
    [], # feb average
    [], # mar average
    [], # apr average
    [], # may average
    [], # jun average
    [], # jul average
    [], # aug average
    [], # sep average
    [], # oct average
    [], # nov average
    [], # dec average        
  ]

  # Data - For each year in the range, find a matching row in the file and divide the temperature readings in that row into separate arrays of months
  for year in range(YEAR_RANGE_START, YEAR_RANGE_END):

    # Check if the station's temperature data includes this year
    matching_row = temp_data_for_station.loc[temp_data_for_station['year'] == year]

    # If the station has data for this year
    if not matching_row.empty:

      # For each month of the year
      for month_iteration, month_class in enumerate(absolute_temperatures_by_month):

        month = str(1 + month_iteration)

        # Select the equivalent columns for that month from the station data
        cols = [ 'VALUE' + month, 'DMFLAG' + month, 'QCFLAG' + month, 'DSFLAG' + month ]

        month_grouping = matching_row[cols].to_numpy()[0]

        # Check the flags and either return the value or NaN
        permitted_temperature = get_permitted_reading(month_grouping)

        # Save the value to the associated month row in our absolute_temperatures_by_month
        month_class.append(permitted_temperature)

    else:

      # Data - Since we need to fill the full range of years, place a NaN for data that doesn't exist in a station's file
      for month_class in absolute_temperatures_by_month:

        month_class.append(math.nan)

  # Return the absolute temperatures by month as a DataFrame
  return pd.DataFrame(absolute_temperatures_by_month, columns=range(YEAR_RANGE_START, YEAR_RANGE_END))