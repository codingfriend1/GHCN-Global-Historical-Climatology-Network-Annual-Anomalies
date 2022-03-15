'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from constants import *
import math
import pandas as pd
import anomaly
import numpy as np

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

def compose_station_console_output(station_iteration, total_stations, station_id, anomaly_visual, anomaly_trend, absolute_visual, absolute_trend, start_year, end_year, station_location, station_gridbox):

  which_station = f"Station {station_iteration} of {total_stations}"

  anomaly_trends = f"Anomaly Trend: {anomaly_visual} ({'{0:.3f}'.format(anomaly_trend)})\t Absolute Trend: {absolute_visual} ({'{0:.3f}'.format(absolute_trend)})"

  year_range = f"{start_year}-{end_year}"

  print(f"{which_station} \t{station_id}\t  {anomaly_trends}\t| {year_range} | {station_gridbox}  \t\t| {station_location}")

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

def compose_file_name(country_code=""):
  reference_text = f"-rolling-{REFERENCE_RANGE}"
  if REFERENCE_START_YEAR:
      reference_text = f"-{REFERENCE_START_YEAR}-{REFERENCE_START_YEAR+REFERENCE_RANGE-1}r"

  acceptable_percent = normal_round(ACCEPTABLE_AVAILABLE_DATA_PERCENT * 100)
  date = TODAY.strftime("%Y-%m-%d")

  country_code_text = ""
  if country_code:
    country_code_text = f"{country_code}-"

  gridding_text = ""
  if USE_GRIDDING:
    gridding_text = f"-gridded-weighted-by-cosine"
    if INCLUDE_LAND_RATIO_IN_WEIGHT:
      gridding_text = gridding_text + "-and-land-ratio"

  OUTPUT_FILE_NAME = f"{country_code_text}{DATA_FILE_NAME}-{REFERENCE_START_YEAR}-{REFERENCE_START_YEAR+REFERENCE_RANGE-1}-{acceptable_percent}-{'some-rejected' if PURGE_FLAGS else 'all'}{gridding_text}.xlsx"

  return OUTPUT_FILE_NAME

def output_file(excel_data, country_code=""):

  excel_data_pd = pd.DataFrame(excel_data)

  OUTPUT_FILE_NAME = compose_file_name(country_code)

  EXCEL_WRITER = pd.ExcelWriter(OUTPUT_FILE_NAME)

  excel_data_pd.to_excel(EXCEL_WRITER, encoding='utf-8-sig', sheet_name='Anomalies', index=False)

  EXCEL_WRITER.save()

def generate_year_range_series(label):
  return pd.concat([pd.Series([label]), pd.Series(range(YEAR_RANGE_START, YEAR_RANGE_END))]).reset_index(drop = True)

def generate_average_anomalies_list(label, average_of_all_anomalies):
  return pd.concat([pd.Series([label]), average_of_all_anomalies]).reset_index(drop = True)

# Prepare our spreadsheet for output as an Excel File
def create_excel_file(annual_anomalies_by_grid, average_anomolies_of_all_stations_in_country, avg_annual_anomalies_of_all_grids_divided, country_name="", country_code=""):

  # When gridding this row represents the weight of each grid box, without gridding it represents the City, Country of each station
  year_sub_label = 'Weight' if USE_GRIDDING else "Location"

  # Start the base of our xlsx data
  excel_data = {
    "Year": generate_year_range_series(year_sub_label)
  }

  # Use a different label depending on if we are gridding the results or simply averaging all stations
  sub_label = "All grids" if USE_GRIDDING else "All Stations"

  # Print a column with the average anomalies by year for all stations or grid boxes
  excel_data["Average Anomolies"] = generate_average_anomalies_list(sub_label, average_anomolies_of_all_stations_in_country)

  # Print a column with the average anomalies by year for all stations or grid boxes divided by 100
  excel_data["Average Anomolies / 100"] = generate_average_anomalies_list(sub_label, avg_annual_anomalies_of_all_grids_divided)

  if USE_GRIDDING:

    # Create a column for each box of our latitude/longitude grid with it's anomalies
    for grid_cell_label, grid in annual_anomalies_by_grid.iteritems():

      excel_data[grid_cell_label] = grid

  elif PRINT_STATION_ANOMALIES:

    # Print a column for each station anomaly. In GHCNm v4, using all stations, this will cause the program to crash because Excel cannot have a file with 27k columns. But it is useful for testing smaller samples.

    annual_anomalies_by_grid.drop(columns=[2], axis=1, inplace=True)

    for grid_cell_label, grid in annual_anomalies_by_grid.iterrows():
      
      excel_data[grid.iloc[0]] = grid.iloc[1:].to_numpy()

  output_file(excel_data)

def create_final_excel_file(anomalies_by_country, country_name, country_code):

  year_label = 'Weight' if USE_GRIDDING else "Location"

  # Start the base of our xlsx data
  excel_data = {
    "Year": generate_year_range_series(year_label)
  }

  # MATH - Average annual anomolies across all stations and add to excel_data
  average_anomolies_of_all_countries = anomaly.average_monthly_anomalies_by_year(anomalies_by_country.iloc[1:].astype("float"), axis=1)

  excel_data["Average Anomolies"] = generate_average_anomalies_list("All countries", average_anomolies_of_all_countries)

  for cc, series in anomalies_by_country.iteritems():
    
    excel_data[cc] = pd.concat([pd.Series([series.iloc[0]]), pd.Series(series.iloc[1:]).astype("float")]).reset_index(drop = True)

  output_file(excel_data, "000-Summary")

# Print Summaries
def print_summary_to_console(total_stations):

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
  print(f"File output to {compose_file_name()}")
  print("")
  print("\n")
