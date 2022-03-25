'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from globals import *
import pandas as pd
import math
import os

import anomaly
from networks import ghcn
from networks import ushcn
from networks import uscrn

'''
https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt
'''

# Column for the first month reading
COLUMN_FOR_FIRST_MONTH = 2

'''
 Returns the temperature reading if the flags are approved, otherwise you may return NaN
   
   VALUE: monthly value (MISSING=-9999).  Temperature values are in hundredths of a degree Celsius, but are expressed as whole integers (e.g. divide by 100.0 to get whole degrees Celsius).

   DMFLAG: data measurement flag
   
   QCFLAG: quality control flag
   
   DSFLAG: data source flag
'''
def get_permitted_reading(VALUE, DMFLAG, QCFLAG, DSFLAG):

  # If the Developer has chosen to PURGE_Flags, we set as missing as readings that have an Estimated or Quality Control Flag
  return VALUE if not PURGE_FLAGS or (not DMFLAG == 'E' and QCFLAG == ' ') else math.nan


def parse_temperature_row(
  unparsed_row, 
  column_boundries = [(0,11), (11, 15)], 
  column_types = ([str, int] + ([int, str, str, str] * 12))
):

  parsed_row = []

  try:

    for column, bounds in enumerate(column_boundries):

      column_value = unparsed_row[bounds[0]:bounds[1]]

      column_value_as_type = column_types[column](column_value)

      parsed_row.append(column_value_as_type)

  except:

    print('Error parsing row', unparsed_row)

    return False

  return parsed_row


def get_station_start_and_end_year(temperature_data_for_station):

  # Select the first and last row and extract the Year value associated with those rows
  FIRST_ROW = 0
  LAST_ROW = len(temperature_data_for_station) - 1
  
  start_year = temperature_data_for_station.index[FIRST_ROW]
  end_year = temperature_data_for_station.index[LAST_ROW]
  
  return start_year, end_year

# Check if the station has enough data during the baseline years to be used
def has_enough_years(station, minimum_years_needed, REFERENCE_END_YEAR):

  rows_of_reference_years = station.loc[(station.name, REFERENCE_START_YEAR):(station.name, REFERENCE_END_YEAR)]

  return len(rows_of_reference_years) >= minimum_years_needed


def get_temperatures_by_station(url, STATIONS):

  # Read the station's temperature file, each row will be a plain string and will not be parsed or separated already into a dataframe. Although this is inconvenient to manually parse each row before converting into a dataframe, it massively improves performance.
  unparsed_station_data = pd.read_csv(url, sep="\t", header=None, low_memory=False)

  parsed_rows = []

  for unparsed_row_string in unparsed_station_data.values:

    parsed_row = []

    data_columns = []

    if NETWORK == 'GHCN':

      data_columns = ghcn.DATA_COLUMNS

    elif NETWORK == 'USCRN':

      data_columns = uscrn.DATA_COLUMNS

    elif NETWORK == 'USHCN':

      data_columns = ushcn.DATA_COLUMNS

    parsed_row = parse_temperature_row(unparsed_row_string[0], column_boundries=data_columns)

    if parsed_row:

      simplified_row = parsed_row[ 0 : COLUMN_FOR_FIRST_MONTH ]

      # Get approval for each reading based on its flags
      for month_column in range(0, 12 * 4, 4):

        current_column = COLUMN_FOR_FIRST_MONTH + month_column

        VALUE, DMFLAG, QCFLAG, DSFLAG = parsed_row[ current_column : current_column + 4 ]

        # Convert the reading to an integer if its not already. Convert missing values to NaN
        VALUE = int(VALUE) if not math.isnan(VALUE) and VALUE != MISSING_VALUE else math.nan

        permitted_temperature = get_permitted_reading(VALUE, DMFLAG, QCFLAG, DSFLAG)

        simplified_row = simplified_row + [ permitted_temperature ]

      parsed_rows.append(simplified_row)


  columns = ['station_id',  'year'] + month_columns

  station_temperatures = pd.DataFrame(parsed_rows, columns=columns)

  # Because we can filter stations by environment (ex: rural, urban) or by country, we want to limit our selection of temperatures to approved stations
  if SURROUNDING_CLASS or IN_COUNTRY:

    station_temperatures = station_temperatures[station_temperatures['station_id'].isin(STATIONS.index)]

  station_temperatures.set_index([ 'station_id', 'year'], inplace=True)

  # Drop rows with too many null months
  station_temperatures.dropna(thresh=MONTHS_REQUIRED_EACH_YEAR, subset=month_columns, inplace=True)

  # Drop stations with not enough years in the baseline range
  minimum_years_needed = anomaly.get_minimum_years(REFERENCE_RANGE)
  
  REFERENCE_END_YEAR = REFERENCE_START_YEAR + REFERENCE_RANGE - 1

  station_temperatures = station_temperatures.groupby('station_id').filter(

    lambda station: has_enough_years(station, minimum_years_needed, REFERENCE_END_YEAR)
    
  )

  return station_temperatures.reset_index().set_index('year').groupby('station_id')

