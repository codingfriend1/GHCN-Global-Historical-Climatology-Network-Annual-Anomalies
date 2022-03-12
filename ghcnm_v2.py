from constants import *
import pandas as pd
import math
import ghcnm as ghcnm_v1

'''
https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt
'''

MISSING_VALUE = -9999
COLUMN_INDEX_FOR_JAN_GROUPING = 2

def get_permitted_reading(month_grouping):

  return ghcnm_v1.get_permitted_reading(month_grouping)

def get_station_start_and_end_year(temp_data_for_station):
  start_year = temp_data_for_station.iloc[0][1]
  end_year = temp_data_for_station.iloc[len(temp_data_for_station) - 1][1]

  return start_year, end_year

def parse_temperature_row(row):

  usable_row = []

  ID = str(row[0:11])
  YEAR = int(row[11:15])
  ELEMENT = row[15:19]

  usable_row.append(ID)
  usable_row.append(YEAR)

  for index in range(19, 115, 8):

    try:
      
      VALUE = int(row[index:index + 5])

      VALUE = VALUE if VALUE != -9999 else math.nan

      DMFLAG = str(row[index + 5:index + 6])
      QCFLAG = str(row[index + 6:index + 7])
      DSFLAG = str(row[index + 7:index + 8])

      value_set = [ VALUE, DMFLAG, QCFLAG, DSFLAG ]

      usable_row.append(value_set)

    except:
      print('Error parsing row', row)

  return usable_row


def get_ghcnm_by_station(url):

  # Read the station file
  station_temperature_data_file = pd.read_csv(url, header=None)

  # Combine all parsed rows into one array
  file_rows = []

  for file_row in station_temperature_data_file.values:

      parsed_row = parse_temperature_row(file_row[0])

      file_rows.append(parsed_row)

  ghcnm_dataframe = pd.DataFrame(file_rows)

  ghcnm_dataframe_by_station = ghcnm_dataframe.groupby([0])

  return ghcnm_dataframe_by_station

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
    matching_row = temp_data_for_station.loc[temp_data_for_station[1] == year]

    # If the station has data for this year
    if not matching_row.empty:

      # For each month of the year
      for month_iteration, month_class in enumerate(absolute_temperatures_by_month):

        month = 2 + month_iteration

        # Select the equivalent columns for that month from the station data
        month_grouping = matching_row[month].to_numpy()[0]

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