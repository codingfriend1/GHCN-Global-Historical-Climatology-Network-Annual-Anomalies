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
import time


# Collect statistics on the type of data we are getting

absolute_up_count = 0

absolute_down_count = 0

absolute_trends_array = [[],[],[]]


def get_file_name_from_path(FILE_PATH):
  
  split_file_path = FILE_PATH.split('/')

  return split_file_path[len(split_file_path) - 1]

def compose_station_console_output(station_iteration, total_stations, station_id, absolute_visual, absolute_trend, start_year, end_year, station_location, station_gridbox):

  which_station = f"Station {'{:,}'.format(station_iteration)} of {'{:,}'.format(total_stations)}"

  which_station = which_station.ljust(25, " ")

  trend = " ".ljust(17, ' ')

  if not math.isnan(absolute_trend):

    trend = f"Trend: {absolute_visual} ({'{0:.3f}'.format(absolute_trend)})".ljust(17, ' ')

  year_range = f"{start_year}-{end_year}"

  padded_station_grid_box = station_gridbox.ljust(19, ' ')

  station_location = station_location.replace("  ", " ").replace("\t", " ").strip()

  print(f"{which_station} {station_id} {trend} | {year_range} | {padded_station_grid_box} | {station_location}")

def update_statistics(trend):

  global absolute_up_count

  global absolute_down_count

  if math.isnan(trend):

    visual = "?"

    return visual

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

def compose_file_name(TEMPERATURES_FILE_PATH):

  TEMPERATURE_FILE = get_file_name_from_path(TEMPERATURES_FILE_PATH)

  reference_timespan = f"{ REFERENCE_START_YEAR }-{ REFERENCE_START_YEAR + REFERENCE_RANGE }"

  acceptable_percent = normal_round(ACCEPTABLE_AVAILABLE_DATA_PERCENT * 100)

  is_purged = 'some-rejected' if PURGE_FLAGS else 'all'

  environment = f"-{SURROUNDING_CLASS}" if SURROUNDING_CLASS else ""

  in_country = f"-in-({', '.join(IN_COUNTRY)})" if IN_COUNTRY else ""

  minimum_months = f"{MONTHS_REQUIRED_EACH_YEAR}-months"

  OUTPUT_FILE_NAME = f"{TEMPERATURE_FILE}-{reference_timespan}-{acceptable_percent}-{minimum_months}-{is_purged}{environment}{in_country}.xlsx"

  return OUTPUT_FILE_NAME

def output_file(excel_data, TEMPERATURES_FILE_PATH):

  excel_data_pd = pd.DataFrame(excel_data)

  OUTPUT_FILE_NAME = compose_file_name(TEMPERATURES_FILE_PATH)

  EXCEL_WRITER = pd.ExcelWriter(OUTPUT_FILE_NAME)

  excel_data_pd.to_excel(EXCEL_WRITER, encoding='utf-8-sig', sheet_name='Anomalies', index=False)

  EXCEL_WRITER.save()


def generate_column(labels, data):

  return pd.concat([pd.Series(labels), data]).reset_index(drop = True)


def generate_column_for_output(labels, data):

  return generate_column(labels, data) if PRINT_STATION_ANOMALIES else generate_column(labels[1], data)


# Prepare our spreadsheet for output as an Excel File
def create_excel_file(
  ungridded_anomalies = [],
  ungridded_anomalies_divided = [],

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
    "Year": generate_column_for_output([ "Location", year_sublabel ], pd.Series(range(YEAR_RANGE_START, YEAR_RANGE_END)))
  }
  
  # Prepare each column of the dataframe to be saved
  excel_data["Average of stations"] = generate_column_for_output(
    [ "All Stations", stations_average_sublabel ], ungridded_anomalies
  )

  excel_data["Average of stations / 100"] = generate_column_for_output(
    [ "All Stations", stations_average_sublabel ], ungridded_anomalies_divided
  )

  excel_data["Average of Grids"] = generate_column_for_output(
    [ "All Grids", "" ], average_of_grids.iloc[1:]
  )

  excel_data["Average of Grids / 100"] = generate_column_for_output(
    [ "All Grids", "" ], average_of_grids_divided
  )

  excel_data["Average of grids weighed with land ratio"] = generate_column_for_output(
    [ "All Grids", "" ], average_of_grids_by_land_ratio.iloc[1:]
  )

  excel_data["Average of grids weighed with land ratio / 100"] = generate_column_for_output(
    [ "All Grids", "" ], average_of_grids_by_land_ratio_divided
  )

  if PRINT_STATION_ANOMALIES:

    # Print a column for each station anomaly. In GHCNm v4, using all stations, this will cause the program to crash because Excel cannot have a file with 27k columns. But it is useful for testing smaller samples.
    # anomalies_by_station.drop(columns=[2], axis=1, inplace=True)

    for grid_cell_label, grid in anomalies_by_station.iterrows():
      
      excel_data[grid.iloc[0]] = generate_column_for_output([ grid.iloc[1], grid.iloc[2] ], pd.Series(grid.iloc[3:].to_numpy()))

  else:

    # Create a column for each box of our latitude/longitude grid with it's anomalies
    for grid_cell_label, grid in anomalies_by_grid.iteritems():

      excel_data[grid_cell_label] = grid

  output_file(excel_data, data_source)


def print_settings_to_console(TEMPERATURES_FILE_PATH, STATION_FILE_PATH):

  my_table = Texttable()

  my_table.add_rows([

    ["Setting", "Value"],

    ["Temperatures file", get_file_name_from_path(TEMPERATURES_FILE_PATH)],

    ["Stations file", get_file_name_from_path(STATION_FILE_PATH)],

    ["Anomaly reference average range", f"{REFERENCE_START_YEAR}-{REFERENCE_START_YEAR + REFERENCE_RANGE - 1}"],

    ["Minimum required percent of years in baseline", f"{normal_round(ACCEPTABLE_AVAILABLE_DATA_PERCENT * 100, 0)}%"],

    ["Absolute trends range", f"{ABSOLUTE_START_YEAR}-{ABSOLUTE_END_YEAR}"],

    ["Trend range", f"{ABSOLUTE_START_YEAR}-{ABSOLUTE_END_YEAR-1}"],

    ["Purging flagged data", str(PURGE_FLAGS)],

    ["Required months", str(MONTHS_REQUIRED_EACH_YEAR)],

    ["Environment class", str(SURROUNDING_CLASS)],

    ["Countries used", str(", ".join(IN_COUNTRY) if IN_COUNTRY else "All")]

  ])

  my_table.set_deco(Texttable.HEADER | Texttable.BORDER)

  print(my_table.draw())

  print(f"Please wait a few seconds...")

  print(f"\n")

def console_performance(t0, TOTAL_STATIONS):

  end_time = time.perf_counter() - t0

  minutes, remainder_seconds = divmod(end_time, 60)

  hours, remainder_minutes = divmod(minutes, 60)

  seconds  = normal_round(end_time)

  print(f"Process completed in {int(normal_round(hours))}h:{int(normal_round(remainder_minutes))}m:{int(normal_round(remainder_seconds))}s")

  total_minutes = seconds / 60

  stations_per_minute = normal_round(TOTAL_STATIONS / total_minutes)

  print(f"With {'{:,}'.format(TOTAL_STATIONS)} stations, that's {'{:,}'.format(stations_per_minute)} stations/minute.\n")


# Print Summaries
def print_summary_to_console(total_stations, TEMPERATURES_FILE_PATH):

  absolute_upwards_trend = normal_round(np.average(absolute_trends_array[0]), 3) if len(absolute_trends_array[0]) else "Unknown"

  absolute_downwards_trend = normal_round(np.average(absolute_trends_array[1]), 3) if len(absolute_trends_array[1]) else "Unknown"

  absolute_all_trends = normal_round(np.average(absolute_trends_array[2]), 3) if len(absolute_trends_array[2]) else "Unknown"

  # print(f"\n{'Flagged data purged' if PURGE_FLAGS else 'Utilizes all data (including flagged)'}\n")

  print("-------------------------------------------------------------------------------------------------------------------------------------")

  print(f"Absolute Trends:\t\t{absolute_up_count} ↑ ({absolute_upwards_trend} Avg)  \t\t{absolute_down_count} ↓ ({absolute_downwards_trend} Avg)")

  if not absolute_all_trends == "Unknown":
    
      print(f"Total Avg: {absolute_all_trends}°C {'rise' if float(absolute_all_trends) > 0 else 'fall'} every century between ({ABSOLUTE_START_YEAR}-{ABSOLUTE_END_YEAR})")

  print("")

  print(f"File output to {compose_file_name(TEMPERATURES_FILE_PATH)}")

  print("\n")
