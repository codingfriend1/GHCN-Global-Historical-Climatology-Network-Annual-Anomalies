'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from constants import *
import download
import math
import pandas as pd
import anomaly
import numpy as np
from texttable import Texttable

# Collect statistics on the type of data we are getting
num_of_temperature_readings = 0
num_of_estimated_temperature_readings = 0
absolute_up_count = 0
absolute_down_count = 0

anomaly_up_count = 0
anomaly_down_count = 0

downwards_start_year_array = []
downwards_end_year_array = []

anomaly_trends_array = [[],[],[]]
absolute_trends_array = [[],[],[]]

def get_file_name_from_path(FILE_PATH):
  split_file_path = FILE_PATH.split('/')

  return split_file_path[len(split_file_path) - 1]

def compose_station_console_output(station_iteration, total_stations, station_id, anomaly_visual, anomaly_trend, absolute_visual, absolute_trend, start_year, end_year, station_location, station_gridbox):

  which_station = f"Station {'{:,}'.format(station_iteration)} of {'{:,}'.format(total_stations)}"

  anomaly_trends = f"Anomaly Trend: {anomaly_visual} ({'{0:.3f}'.format(anomaly_trend)})\t Absolute Trend: {absolute_visual} ({'{0:.3f}'.format(absolute_trend)})"

  year_range = f"{start_year}-{end_year}"

  print(f"{which_station} \t{station_id}\t  {anomaly_trends}\t| {year_range} | {station_gridbox}  \t| {station_location}")

def update_statistics(trend, type):

  global anomaly_up_count
  global anomaly_down_count
  global absolute_up_count
  global absolute_down_count

  if math.isnan(trend):

    visual = "?"

    return visual

  if type == 'anomaly':
    if trend > 0:
      visual = "↑"
      anomaly_up_count += 1
      anomaly_trends_array[0].append(trend)
    else:
      visual = "↓"
      anomaly_down_count += 1
      anomaly_trends_array[1].append(trend)

    anomaly_trends_array[2].append(trend)

  elif type == 'absolute':

    if trend > 0:
      visual = "↑"
      absolute_up_count += 1
      absolute_trends_array[0].append(trend)
    else:
      visual = "↓"
      absolute_down_count += 1
      absolute_trends_array[1].append(trend)

    absolute_trends_array[2].append(trend)

  return visual

def compose_file_name(GHCN_TEMPERATURES_FILE_PATH):
  reference_text = f"-rolling-{REFERENCE_RANGE}"
  if REFERENCE_START_YEAR:
      reference_text = f"-{REFERENCE_START_YEAR}-{REFERENCE_START_YEAR+REFERENCE_RANGE-1}r"

  acceptable_percent = normal_round(ACCEPTABLE_AVAILABLE_DATA_PERCENT * 100)
  date = TODAY.strftime("%Y-%m-%d")

  TEMPERATURE_FILE = get_file_name_from_path(GHCN_TEMPERATURES_FILE_PATH)

  rural_text = ""
  if ONLY_RURAL:
    rural_text = "-only-rural"

  if ONLY_URBAN:
    rural_text = "-only-urban"

  OUTPUT_FILE_NAME = f"{TEMPERATURE_FILE}-{REFERENCE_START_YEAR}-{REFERENCE_START_YEAR+REFERENCE_RANGE-1}-{acceptable_percent}-{'some-rejected' if PURGE_FLAGS else 'all'}{rural_text}.xlsx"

  return OUTPUT_FILE_NAME

def output_file(excel_data, GHCN_TEMPERATURES_FILE_PATH):

  excel_data_pd = pd.DataFrame(excel_data)

  OUTPUT_FILE_NAME = compose_file_name(GHCN_TEMPERATURES_FILE_PATH)

  EXCEL_WRITER = pd.ExcelWriter(OUTPUT_FILE_NAME)

  excel_data_pd.to_excel(EXCEL_WRITER, encoding='utf-8-sig', sheet_name='Anomalies', index=False)

  EXCEL_WRITER.save()

def generate_column_for_output(label, sublabel, data):

  if PRINT_STATION_ANOMALIES:
    return pd.concat([pd.Series([label, sublabel]), data]).reset_index(drop = True)
  else:
    return pd.concat([pd.Series([sublabel]), data]).reset_index(drop = True)

def generate_average_anomalies_list(label, average_of_all_anomalies):
  return pd.concat([pd.Series([label]), average_of_all_anomalies]).reset_index(drop = True)

# Prepare our spreadsheet for output as an Excel File
def create_excel_file(
  average_of_stations = [],
  average_of_stations_divided = [],

  average_of_grids = [],
  average_of_grids_divided = [],

  average_of_grids_by_land_ratio = [],
  average_of_grids_by_land_ratio_divided = [],

  anomalies_by_grid = [],
  anomalies_by_station = [],

  data_source = "unknown",
):

  year_sublabel = "Grid Weight" if not PRINT_STATION_ANOMALIES else "Grid Box"

  stations_average_sublabel = "Equal Weight" if not PRINT_STATION_ANOMALIES else ""

  # Start the base of our xlsx data
  excel_data = {
    "Year": generate_column_for_output("Location", year_sublabel, pd.Series(range(YEAR_RANGE_START, YEAR_RANGE_END)))
  }
  
  # Prepare each column of the dataframe to be saved
  excel_data["Average of stations"] = generate_column_for_output(
    "All Stations", stations_average_sublabel, average_of_stations
  )

  excel_data["Average of stations / 100"] = generate_column_for_output(
    "All Stations", stations_average_sublabel, average_of_stations_divided
  )

  excel_data["Average of Grids"] = generate_column_for_output(
    "All Grids", "", average_of_grids.iloc[1:]
  )

  excel_data["Average of Grids / 100"] = generate_column_for_output(
    "All Grids", "", average_of_grids_divided
  )

  excel_data["Average of grids weighed with land ratio"] = generate_column_for_output(
    "All Grids", "", average_of_grids_by_land_ratio.iloc[1:]
  )

  excel_data["Average of grids weighed with land ratio / 100"] = generate_column_for_output(
    "All Grids", "", average_of_grids_by_land_ratio_divided
  )

  if PRINT_STATION_ANOMALIES:

    # Print a column for each station anomaly. In GHCNm v4, using all stations, this will cause the program to crash because Excel cannot have a file with 27k columns. But it is useful for testing smaller samples.
    # anomalies_by_station.drop(columns=[2], axis=1, inplace=True)

    for grid_cell_label, grid in anomalies_by_station.iterrows():
      
      excel_data[grid.iloc[0]] = generate_column_for_output(grid.iloc[1], grid.iloc[2], pd.Series(grid.iloc[3:].to_numpy()))

  else:

    # Create a column for each box of our latitude/longitude grid with it's anomalies
    for grid_cell_label, grid in anomalies_by_grid.iteritems():

      excel_data[grid_cell_label] = grid

  output_file(excel_data, data_source)

def print_settings_to_console(GHCN_TEMPERATURES_FILE_PATH, STATION_FILE_PATH):

  my_table = Texttable()

  my_table.add_rows([
    ["Setting", "Value"],
    ["Temperatures file", get_file_name_from_path(GHCN_TEMPERATURES_FILE_PATH)],
    ["Stations file", get_file_name_from_path(STATION_FILE_PATH)],
    ["Anomaly reference average range", f"{REFERENCE_START_YEAR}-{REFERENCE_START_YEAR + REFERENCE_RANGE - 1}"],
    ["Trend range", f"{ABSOLUTE_START_YEAR}-{ABSOLUTE_END_YEAR-1}"],
    ["Purging flagged data", str(PURGE_FLAGS)],
    ["Rural only", str(ONLY_RURAL)],
    ["Urban only", str(ONLY_URBAN)]
  ])

  my_table.set_deco(Texttable.HEADER | Texttable.BORDER)

  print(my_table.draw())

  print(f"Please wait a few seconds...")
  print(f"\n")

# Print Summaries
def print_summary_to_console(total_stations, GHCN_TEMPERATURES_FILE_PATH):

  # print('\n')
  # print('Estimated temperature percent', normal_round(num_of_estimated_temperature_readings / num_of_temperature_readings, 2))

  anomaly_upwards_trend = normal_round(np.average(anomaly_trends_array[0]), 3) if len(anomaly_trends_array[0]) else "Unknown"
  anomaly_downwards_trend = normal_round(np.average(anomaly_trends_array[1]), 3) if len(anomaly_trends_array[1]) else "Unknown"
  anomaly_all_trends = normal_round(np.average(anomaly_trends_array[2]), 3) if len(anomaly_trends_array[2]) else "Unknown"

  absolute_upwards_trend = normal_round(np.average(absolute_trends_array[0]), 3) if len(absolute_trends_array[0]) else "Unknown"
  absolute_downwards_trend = normal_round(np.average(absolute_trends_array[1]), 3) if len(absolute_trends_array[1]) else "Unknown"
  absolute_all_trends = normal_round(np.average(absolute_trends_array[2]), 3) if len(absolute_trends_array[2]) else "Unknown"

  # print(f"\n{'Flagged data purged' if PURGE_FLAGS else 'Utilizes all data (including flagged)'}\n")

  print("-------------------------------------------------------------------------------------------------------------------------------------")

  print(f"Absolete Trends:\t\t{absolute_up_count} ↑ ({absolute_upwards_trend} Avg)  \t\t{absolute_down_count} ↓ ({absolute_downwards_trend} Avg)")
  if not absolute_all_trends == "Unknown":
      print(f"Total Avg: {absolute_all_trends}°C {'rise' if float(absolute_all_trends) > 0 else 'fall'} every century")

  print(f"Anomaly Trends: \t\t{anomaly_up_count} ↑ ({anomaly_upwards_trend} Avg)  \t\t{anomaly_down_count} ↓ ({anomaly_downwards_trend} Avg)")
  if not anomaly_all_trends == "Unknown":
    print(f"Total Avg: {anomaly_all_trends}°C {'rise' if float(anomaly_all_trends) > 0 else 'fall'} every century")
  print("")
  print(f"File output to {compose_file_name(GHCN_TEMPERATURES_FILE_PATH)}")
  print("\n")
