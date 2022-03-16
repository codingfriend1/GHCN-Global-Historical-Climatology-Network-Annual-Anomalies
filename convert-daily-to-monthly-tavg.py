'''
  Author: Jon Paul Miles
  Date Created: March 15, 2022

  Daily station data can be retrieved from:
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/by_station/
'''

from constants import *
import pandas as pd
import numpy as np
import os

TODAY_DATE = TODAY.strftime("%Y%m%d")

DAYS_IN_MONTH = 31


OUTPUT_FILE_URL = f"./ghcnd.tavg.v4.{TODAY_DATE}.qcu.dat"

if os.path.exists(OUTPUT_FILE_URL):
  os.remove(OUTPUT_FILE_URL)

OUTPUT_CONTENT = open(OUTPUT_FILE_URL, 'a')

def average_tmax_and_tmin(TMAX_AND_TMIN):

  tavg = math.nan if len(TMAX_AND_TMIN) != 2 or TMAX_AND_TMIN.isnull().any() else math.trunc(normal_round(TMAX_AND_TMIN.mean()))

  return tavg

def parse_daily_row(unparsed_row):

  parsed_row = []

  ELEMENT = str(unparsed_row[17:21])

  if not ELEMENT == "TMAX" and not ELEMENT == "TMIN":
    return False

  STATION_ID = str(unparsed_row[0:11]).strip()
  YEAR = int(unparsed_row[11:15])
  MONTH = int(unparsed_row[15:17])

  parsed_row.append(STATION_ID)
  parsed_row.append(YEAR)
  parsed_row.append(MONTH)
  parsed_row.append(ELEMENT)

  DAYS_IN_MONTH = 31
  FIRST_DAY_INDEX = 21
  CHARACTERS_NEEDED_FOR_READING_AND_FLAGS = 8

  FULL_RANGE = (DAYS_IN_MONTH * CHARACTERS_NEEDED_FOR_READING_AND_FLAGS) + FIRST_DAY_INDEX

  for index in range(FIRST_DAY_INDEX, FULL_RANGE, CHARACTERS_NEEDED_FOR_READING_AND_FLAGS):

    temperature_reading = int(unparsed_row[index:index + 5])
        
    corrected_temperature = math.nan if temperature_reading == -9999 else normal_round(int(temperature_reading))

    MFLAG = str(unparsed_row[index+5:index+6])
    QFLAG = str(unparsed_row[index+6:index+7])
    SFLAG = str(unparsed_row[index+7:index+8])

    parsed_row.append(corrected_temperature)

  return parsed_row



def average_daily(row):

  index_of_first_day_value_in_row = 5

  index_of_last_day_in_row = DAYS_IN_MONTH + index_of_first_day_value_in_row

  daily_values = row[index_of_first_day_value_in_row:index_of_last_day_in_row]

  available_daily_values = []
  missing_count = 0
  months_average = math.nan

  for daily_group in daily_values:

    value = daily_group[0]

    if value != math.nan:

      available_daily_values.append(value)

    else:

      missing_count += 1

  if missing_count <= 9:

    months_average = normal_round(np.average(available_daily_values), 2)

  return normal_round(months_average), (letters_for_missing_number[missing_count - 1] if missing_count > 0 and missing_count <= 9 else " ")


folder_with_daily_station_data = r'./dly_files'  # os.path.join(DIRECTORY, 'test_daily_by_station')

# Find all station data files in folder
daily_station_files = []

for station_file_url in os.listdir(folder_with_daily_station_data):

  if 'dly' in station_file_url:

    daily_station_files.append(os.path.join(folder_with_daily_station_data, station_file_url))


for station_file_url in daily_station_files:

  # Read the station file
  state_daily_values = pd.read_csv(station_file_url, header=None)

  columns = [ 'station_id', 'year', 'month', 'element' ]

  for day in range(DAYS_IN_MONTH):
    columns.append('value' + str(day + 1))

  # Combine all parsed rows into one array
  parsed_file_rows = []

  for file_row in state_daily_values.values:

    parsed_row = parse_daily_row(file_row[0])

    if parsed_row:
      parsed_file_rows.append(parsed_row)

  station_temperature_data = pd.DataFrame(parsed_file_rows, columns=columns)

  station_temperature_data.set_index(['year'], inplace=True)

  station_temperature_data['average'] = station_temperature_data.iloc[:,4:].mean(
    axis=1, 
    skipna=True, 
    level=None, 
    numeric_only=True
  ).apply(lambda d : d if math.isnan(d) else normal_round(d)).astype('Int64')

  station_temperature_data.drop(station_temperature_data.columns[3:34], axis=1, inplace=True)

  station_temperature_data = station_temperature_data.pivot_table(
    index=["station_id", "year"], 
    columns='month', 
    values='average', 
    fill_value=math.nan, 
    aggfunc=average_tmax_and_tmin, 
    dropna=False
  ).astype('Int64').reset_index()

  repeating_tavg = pd.Series(np.tile(['TAVG'], len(station_temperature_data)) )

  station_temperature_data.insert(loc=2, column='tavg', value=repeating_tavg)

  if len(station_temperature_data.columns) == 15 and len(station_temperature_data.values) > 1:

    for year, row in station_temperature_data.iterrows():

      output_row_string = f"\n{row['station_id']}{row['year']}{row['tavg']}"

      for month in range(1, 13):

        month_string = str(row[month]).replace('<NA>', '-9999').rjust(5, " ")
        output_row_string = output_row_string + f"{month_string}   "

      OUTPUT_CONTENT.write(output_row_string)



