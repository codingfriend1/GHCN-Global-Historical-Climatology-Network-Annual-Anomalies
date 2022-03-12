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

def compose_station_console_output(station_iteration, total_stations, station_id, anomaly_visual, anomaly_trend, absolute_visual, absolute_trend, start_year, end_year, station_location):

  which_station = f"Station {station_iteration} of {total_stations}"

  anomaly_trends = f"Anomaly Trend: {anomaly_visual} ({'{0:.3f}'.format(anomaly_trend)})\t Absolute Trend: {absolute_visual} ({'{0:.3f}'.format(absolute_trend)})"

  year_range = f"{start_year}-{end_year}"

  print(f"{which_station} \t{station_id}\t  {anomaly_trends}\t| {year_range} | {station_location}")

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

def compose_file_name():
  reference_text = f"-rolling-{REFERENCE_RANGE}"
  if REFERENCE_START_YEAR:
      reference_text = f"-{REFERENCE_START_YEAR}-{REFERENCE_START_YEAR+REFERENCE_RANGE-1}r"

  acceptable_percent = normal_round(ACCEPTABLE_AVAILABLE_DATA_PERCENT * 100)
  date = TODAY.strftime("%Y-%m-%d")

  OUTPUT_FILE_NAME = f"{date}-{FOLDER}{reference_text}-{acceptable_percent}p-{'flagged-rejected' if PURGE_FLAGS else 'all'}.xlsx"

  return OUTPUT_FILE_NAME

def create_excel_file(annual_anomalies_by_station):

  OUTPUT_FILE_NAME = compose_file_name()

  # Output file
  EXCEL_WRITER = pd.ExcelWriter(OUTPUT_FILE_NAME)

  # Start the base of our xlsx data
  excel_data = {}

  # Add Year column
  excel_data["Year"] = pd.concat([pd.Series([' ']), pd.Series(range(YEAR_RANGE_START, YEAR_RANGE_END))]).reset_index(drop = True)

  # MATH - Average annual anomolies across all stations and add to excel_data
  average_anomolies_of_all_stations = anomaly.average_monthly_anomalies_by_year(annual_anomalies_by_station)

  excel_data["Average Anomolies"] = pd.concat([pd.Series(['All Stations']), average_anomolies_of_all_stations]).reset_index(drop = True)

  # for year, station in annual_anomalies_by_station.iterrows():
    
  #   excel_data[station[0]] = pd.Series(station[1:]).reset_index(drop = True)

  excel_data_pd = pd.DataFrame(excel_data)

  excel_data_pd.to_excel(EXCEL_WRITER, encoding='utf-8-sig', sheet_name='Anomalies', index=False)

  EXCEL_WRITER.save()

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

  print(f"\n{'Flagged data purged' if PURGE_FLAGS else 'Utilizes all data (including flagged)'}\n")

  print(f"Absolute Temperature Trends ({ABSOLUTE_START_YEAR}-{ABSOLUTE_END_YEAR - 1})")
  print("=======================================")

  print(f"{absolute_up_count} ↑ ({absolute_upwards_trend} Avg)")
  print(f"{absolute_down_count} ↓ ({absolute_downwards_trend} Avg)")
  if not absolute_all_trends == "Unknown":
      print(f"Total Avg: {absolute_all_trends}°C {'rise' if absolute_all_trends > 0 else 'fall'} every century")
  print("\n")

  print(f"Anomaly Temperature Trends ({ABSOLUTE_START_YEAR}-{ABSOLUTE_END_YEAR - 1})")
  print("=======================================")

  print(f"{anomaly_up_count} ↑ ({anomaly_upwards_trend} Avg)")
  print(f"{anomaly_down_count} ↓ ({anomaly_downwards_trend} Avg)")

  if not anomaly_all_trends == "Unknown":
      print(f"Total Avg: {anomaly_all_trends}°C {'rise' if anomaly_all_trends > 0 else 'fall'} every century")

  print("\n")

  if not anomaly_all_trends == "Unknown":

      diff = normal_round(absolute_all_trends - anomaly_all_trends, 3)

      relative_percent = normal_round((1 - diff / absolute_all_trends) * 100, 3)

      if REFERENCE_START_YEAR:
          reference_point_text = f"{REFERENCE_START_YEAR}-{REFERENCE_START_YEAR + REFERENCE_RANGE} year reference"
      else:
          reference_point_text = f"{REFERENCE_RANGE} year rolling reference"

      print(f"Accuracy of reference ({relative_percent}%)")
      print("================================")

      print(f"Using a {reference_point_text} {'overstates' if anomaly_all_trends > absolute_all_trends else 'understates'} the effects of global warming by {abs(diff)}°C per century\n")
      
  else:
      print("Anomaly trend unknown")

  print(f"File output to {compose_file_name()}")