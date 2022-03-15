'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from constants import *
import pandas as pd
import math

'''
https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/readme.txt
'''

# The value used in the GHCNm dataset to represent missing temperature readings
MISSING_VALUE = -9999


'''
The column index on the temperature table that contains January temperature readings
1st Column [0] - Country Code
2nd Column [1] - Station ID
3rd Column [2] - Element (TAVG, TMAX, TMIN)
4th Column [3] - January temperatures
'''
COLUMN_FOR_JAN_READINGS = 3


# Perhaps the most important piece related to filtering the data. This receives a "month_grouping" which is an array containing a single temperature reading and it's associated flags ([ VALUE, DMFLAG, QCFLAG, DSFLAG ]). Based on this data, we decide whether to return the original reading or provide a missing value (NaN) if we don't trust the flagged data. Custom logic may be added here to alter the acceptable flagged data.
# 
def get_permitted_reading(month_grouping):

  # Extract the temperature reading and flags from the month grouping
  VALUE = int(month_grouping[0]) if not math.isnan(month_grouping[0]) else math.nan
  DMFLAG = month_grouping[1]
  QCFLAG = month_grouping[2]
  DSFLAG = month_grouping[3]

  # If the Developer has chosen to PURGE_Flags, we set as missing as readings that have an Estimated or Quality Control Flag
  return VALUE if not PURGE_FLAGS or (not DMFLAG == 'E' and QCFLAG == ' ') else math.nan

# Get the Starting and Ending Years that the station has data for
def get_station_start_and_end_year(temp_data_for_station):

  # Select the first and last row and extract the Year value associated with those rows
  FIRST_ROW = 0
  LAST_ROW = len(temp_data_for_station) - 1
  COLUMN_INDEX_FOR_YEAR = 2

  start_year = temp_data_for_station.iloc[FIRST_ROW][COLUMN_INDEX_FOR_YEAR]
  end_year = temp_data_for_station.iloc[LAST_ROW][COLUMN_INDEX_FOR_YEAR]

  return start_year, end_year

'''
2.2.1 DATA FORMAT

  Variable          Columns      Type
  --------          -------      ----

  ID                 1-11        Integer
  YEAR              12-15        Integer
  ELEMENT           16-19        Character
  VALUE1            20-24        Integer
  DMFLAG1           25-25        Character
  QCFLAG1           26-26        Character
  DSFLAG1           27-27        Character
    .                 .             .
    .                 .             .
    .                 .             .
  VALUE12          108-112       Integer
  DMFLAG12         113-113       Character
  QCFLAG12         114-114       Character
  DSFLAG12         115-115       Character

  Variable Definitions:

  ID: Station identification code. First two characters are FIPS country code

  YEAR: 4 digit year of the station record.

  ELEMENT: element type, monthly mean temperature="TAVG"

When splitting the unparsed row string, we start each snippet of data one character index early since the first character is inclusive in programming languages, but they may end with the same character index because the final character is not inclusive
'''
def parse_temperature_row(unparsed_row_string):

  parsed_row = []

  # In version 4 of GHCNm, the first two alpha characters of the STATION_ID represent the abbreviated country code. We can use this to associate the country name with each station. In version 3, the first 3 digits represent the country code.
  COUNTRY_CODE = str(unparsed_row_string[0:2]) if VERSION == "v4" else str(unparsed_row_string[0:3])

  # The ID to associate with the station for this row
  STATION_ID = str(unparsed_row_string[0:11])

  # The Year this row represents
  YEAR = int(unparsed_row_string[11:15])

  # The Element is either TAVG, TMAX, or TMIN. In the dataset used here, this value is always TAVG, which is why we don't add it to our parsed row.
  ELEMENT = unparsed_row_string[15:19]

  # Add our meta information to our parsed row
  parsed_row.append(COUNTRY_CODE)
  parsed_row.append(STATION_ID)
  parsed_row.append(YEAR)

  # Each month in the year requires 8 characters to fit the Temperature Reading (5 characters), Data Measurement Flag (1 character), Quality Control Flag (1 character), and Data Source Flag (1 character). We'll loop through each month counting 8 characters at a time from the character index of Jan to the ending character index of Dec.
  START_CHARACTER_INDEX_FOR_JAN_TEMPERATURE = 19
  END_CHARACTER_INDEX_FOR_DEC = 115
  NUMBER_OF_CHARACTERS_NEEDED_FOR_EACH_MONTH = 8

  # For each month in the unparsed row string
  for index in range(
    START_CHARACTER_INDEX_FOR_JAN_TEMPERATURE, 
    END_CHARACTER_INDEX_FOR_DEC, 
    NUMBER_OF_CHARACTERS_NEEDED_FOR_EACH_MONTH
  ):

    try:
      
      # Extract the temperature reading value for the current month and convert it to an integer
      VALUE = int(unparsed_row_string[index:index + 5])

      # If the value is -9999 (meaning it's missing) convert it to NaN for better averaging in Python and Excel
      VALUE = VALUE if VALUE != MISSING_VALUE else math.nan

      # Extract each flag associated with this temperature reading
      DMFLAG = str(unparsed_row_string[index + 5:index + 6])
      QCFLAG = str(unparsed_row_string[index + 6:index + 7])
      DSFLAG = str(unparsed_row_string[index + 7:index + 8])

      # Combine the temperature reading and flags into an array
      value_set = [ VALUE, DMFLAG, QCFLAG, DSFLAG ]

      # Save that array as a column for this parsed row
      parsed_row.append(value_set)

    # We don't want the program to crash if one row has a problem, so we catch the mistake, discard that row and keep moving
    except:
      print('Error parsing row', unparsed_row_string)

  return parsed_row

'''
Read the Temperature Data File and parse it into a usable table, grouping the results by Station ID so we can iterate over each station. Provide the url/path to the .dat file
'''
def get_temperatures_by_station(url):

  # Read the station's temperature file, each row will be a plain string and will not be parsed or separated already into a dataframe. Although this is inconvenient to manually parse each row before converting into a dataframe, it massively improves performance.
  station_temperature_data_file = pd.read_csv(url, sep="\t", header=None, low_memory=False)

  # Will contain an array for each row
  parsed_file_rows = []

  # For each row in the station's temperature data
  for unparsed_row_string in station_temperature_data_file.values:

    # Split the row string into usable data columns. Monthly sets of temperatures and flags will be represented as an array ([VALUE1, DMFLAG1, QCFLAG1, DSFLAG1]) each taking up one column.
    parsed_row = parse_temperature_row(unparsed_row_string[0])

    # Add the parsed row to the array of the file's parsed rows
    parsed_file_rows.append(parsed_row)

  # Convert the parsed_file_rows into a Panda's dataframe.
  temperature_dataframe = pd.DataFrame(parsed_file_rows)

  # Since the provided .dat file contains data for all stations, we need to manually group the data by station so we can individually iterate over each one
  STATION_ID_COLUMN = 1
  temperature_dataframe_by_station = temperature_dataframe.groupby([STATION_ID_COLUMN])

  # Finally return the grouped meta and temperature data
  return temperature_dataframe_by_station

# Create a range of years based on the Developer's configuration and associate it the station's temperature readings by month after first removing flagged or unwanted data
# 'temp_data_for_station' should only contain the monthly TAVG data for one station at a time
def fit_permitted_data_to_range(temp_data_for_station):

  # The data will be returned as an array containing 12 arrays (one for each month), that will have a list of absolute temperatures for that month for every year in the Year Range Settings
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
    matching_row = temp_data_for_station.loc[temp_data_for_station[2] == year]

    # If the station has data for this year
    if not matching_row.empty:

      # For all 12 months of the year
      for month_iteration, month_class in enumerate(absolute_temperatures_by_month):

        # Get the correct column index in the table to find our month's data
        month = COLUMN_FOR_JAN_READINGS + month_iteration

        # Select the equivalent columns for that month from the station data
        month_grouping = matching_row[month].to_numpy()[0]

        # Check the flags for each reading in that column and either return the value or NaN based on Developer preferences
        permitted_temperature = get_permitted_reading(month_grouping)

        # Save the value to the associated month row in our absolute_temperatures_by_month
        month_class.append(permitted_temperature)

    # If the station does not have any associated data for this year in the range, fill this year with NaN values for each month
    else:

      # Fill each month with NaN
      for month_class in absolute_temperatures_by_month:

        month_class.append(math.nan)

  # Return the absolute temperatures by month as a DataFrame
  return pd.DataFrame(absolute_temperatures_by_month, columns=range(YEAR_RANGE_START, YEAR_RANGE_END))