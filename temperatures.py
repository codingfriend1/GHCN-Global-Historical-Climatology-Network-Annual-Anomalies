'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from constants import *
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


# Perhaps the most important piece related to filtering the data. This receives a "month_grouping" which is an array containing a single temperature reading and it's associated flags ([ VALUE, DMFLAG, QCFLAG, DSFLAG ]). Based on this data, we decide whether to return the original reading or provide a missing value (NaN) if we don't trust the flagged data. Custom logic may be added here to alter the acceptable flagged data.
# 
def get_permitted_reading(month_grouping):

  # Extract the temperature reading and flags from the month grouping
  VALUE = int(month_grouping[0]) if not math.isnan(month_grouping[0]) and month_grouping[0] != MISSING_VALUE else math.nan
  DMFLAG = month_grouping[1]
  QCFLAG = month_grouping[2]
  DSFLAG = month_grouping[3]

  # If the Developer has chosen to PURGE_Flags, we set as missing as readings that have an Estimated or Quality Control Flag
  return VALUE if not PURGE_FLAGS or (not DMFLAG == 'E' and QCFLAG == ' ') else math.nan

def get_station_start_and_end_year(temperature_data_for_station):

  # Select the first and last row and extract the Year value associated with those rows
  FIRST_ROW = 0
  LAST_ROW = len(temperature_data_for_station) - 1
  
  start_year = temperature_data_for_station.index[FIRST_ROW]
  end_year = temperature_data_for_station.index[LAST_ROW]
  
  return start_year, end_year


def has_enough_years(station, minimum_years_needed, REFERENCE_END_YEAR):

  rows_of_reference_years = station.loc[(station.name, REFERENCE_START_YEAR):(station.name, REFERENCE_END_YEAR)]

  return len(rows_of_reference_years) >= minimum_years_needed


def get_temperatures_by_station(url, STATIONS):

  # Read the station's temperature file, each row will be a plain string and will not be parsed or separated already into a dataframe. Although this is inconvenient to manually parse each row before converting into a dataframe, it massively improves performance.
  station_temperature_data_file = pd.read_csv(url, sep="\t", header=None, low_memory=False)

  parsed_rows = []

  for unparsed_row_string in station_temperature_data_file.values:

    parsed_row = []

    if NETWORK in ['GHCN', 'USCRN']:

      parsed_row = ghcn.parse_temperature_row(unparsed_row_string[0])

    elif NETWORK == 'USHCN':

      parsed_row = ushcn.parse_temperature_row(unparsed_row_string[0])

    for index, month_grouping in enumerate(parsed_row[2:]):

      permitted_temperature = get_permitted_reading(month_grouping)

      parsed_row[2 + index] = permitted_temperature

    parsed_rows.append(parsed_row)

  columns = ['station_id',  'year'] + month_columns

  station_temperatures = pd.DataFrame(parsed_rows, columns=columns)

  # Because we can filter stations by environment (ex: rural, urban) or country, we want to limit our selection of temperatures to approved stations
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

