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


data_format_by_network = {
  
  'GHCN': ghcn.DATA_COLUMNS,

  'USCRN': uscrn.DATA_COLUMNS,

  'USHCN': ushcn.DATA_COLUMNS,

}

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

  try:

    parsed_row = []

    for column_index, bounds in enumerate(column_boundries):

      column_value = unparsed_row[bounds[0]:bounds[1]]

      column_value_as_type = column_types[column_index](column_value)

      parsed_row.append(column_value_as_type)

    return parsed_row

  except:

    print('Error parsing row', unparsed_row)

    return False


def get_station_start_and_end_year(temperature_data_for_station):

  start_year = temperature_data_for_station.index[0]

  end_year = temperature_data_for_station.index[-1]
  
  return start_year, end_year


# Check if the station has enough data during the baseline years to be used
def has_enough_years(station, minimum_years_needed):

  rows_of_reference_years = station.loc[(station.name, REFERENCE_START_YEAR):(station.name, REFERENCE_END_YEAR)]

  return len(rows_of_reference_years) >= minimum_years_needed


def approve_and_simplify_row(parsed_row):

  simplified_row = parsed_row[ 0 : COLUMN_FOR_FIRST_MONTH ]

  # Loop through all 12 months in the parsed row, 4 columns at a time (for the value and its flags)
  for month_column in range(0, 12 * 4, 4):

    current_column = COLUMN_FOR_FIRST_MONTH + month_column

    VALUE, DMFLAG, QCFLAG, DSFLAG = parsed_row[ current_column : current_column + 4 ]

    # Convert the reading to an integer if its not already. Convert missing values to NaN
    VALUE = int(VALUE) if not math.isnan(VALUE) and VALUE != MISSING_VALUE else math.nan

    # Get approval for each reading based on its flags
    permitted_temperature = get_permitted_reading(VALUE, DMFLAG, QCFLAG, DSFLAG)

    # Only include the approved temperature in the simplified row, leaving out the flags
    simplified_row = simplified_row + [ permitted_temperature ]

  return simplified_row


def get_temperatures_by_station(url, STATIONS):

  # Read the station's temperature file, each row will be a plain string and will not be parsed or separated already into a dataframe. Although this is inconvenient to manually parse each row before converting into a dataframe, it massively improves performance.
  unparsed_station_data = pd.read_csv(url, sep="\t", header=None, low_memory=False)

  parsed_rows = []

  for unparsed_row_string in unparsed_station_data.values:

    parsed_row = parse_temperature_row(unparsed_row_string[0], data_format_by_network[NETWORK])

    if parsed_row:

      simplified_row = approve_and_simplify_row(parsed_row)

      parsed_rows.append(simplified_row)

  station_temperatures = pd.DataFrame(parsed_rows, columns=['station_id',  'year'] + MONTH_COLUMNS)

  # Stations may be filtered by environment or country, therefore we only use temperature data from approved stations
  if SURROUNDING_CLASS or IN_COUNTRY:

    station_temperatures = station_temperatures[station_temperatures['station_id'].isin(STATIONS.index)]

  station_temperatures.set_index([ 'station_id', 'year'], inplace=True)

  # Drop rows with too many null months
  station_temperatures.dropna(thresh=MONTHS_REQUIRED_EACH_YEAR, subset=MONTH_COLUMNS, inplace=True)

  # Drop stations with not enough years in the baseline range
  minimum_years_needed = anomaly.get_minimum_years(REFERENCE_RANGE)

  station_temperatures = station_temperatures.groupby('station_id').filter(

    lambda station: has_enough_years(station, minimum_years_needed)
    
  )

  return station_temperatures.reset_index().set_index('year').groupby('station_id')

