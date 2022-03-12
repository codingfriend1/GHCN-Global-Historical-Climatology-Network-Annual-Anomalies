from constants import *
import pandas as pd
import numpy as np
import math
import os
import datetime

import stations as stations
import ghcnm_v2 as ghcnm
import anomaly
import utilities as ut

# Important File URLs
STATION_URL = os.path.join(DIRECTORY, FOLDER, STATION_FILE_NAME)
COUNTRIES_URL = os.path.join(DIRECTORY, COUNTRIES_FILE_NAME)
GHCNM_DAT_URL = os.path.join(DIRECTORY, FOLDER, DATA_FILE_NAME)

STATIONS = False
GHCNM_DATA = False

# Parse Station data into a DataFrame
# try:
STATIONS = stations.get_stations(STATION_URL, COUNTRIES_URL)

# except Exception as e:

#   print(f"\nFailed to parse GHCN-M Station Data from\n\n{STATION_URL}\n{COUNTRIES_URL}\n\n", e, "\n")

#   print(f"Check if you referenced the right file and path. The file should be in the format ghcnm.ELEMENT.v4.#.#.YYYYMMDD.VERSION.inv")

#   quit()

# Parse GHCN-M data into a DataFrame
# try:
GHCNM_DATA = ghcnm.get_ghcnm_by_station(GHCNM_DAT_URL)

# except Exception as e:

#   print(f"\nFailed to parse GHCN-M Temperature Data from:\n\n{GHCNM_DAT_URL}\n\n", e, "\n")

#   print(f"Check if you referenced the right file and path. The file should be in the format ghcnm.ELEMENT.v4.#.#.YYYYMMDD.VERSION.dat")

#   quit()

# Prepare station progress counter
TOTAL_STATIONS = len(GHCNM_DATA)
station_iteration = 0

# Prepare final array of station data
annual_anomalies_by_station = []

# For each station file
for station_id, temp_data_for_station in GHCNM_DATA:

  # Increate the progress iterator
  station_iteration += 1

  # Get the Station Location
  station_location = stations.get_station_address(station_id, STATIONS)

  # Build an array based on the Year Range constants and include the matching line from the file on each year if its data evaluates as acceptable based on its flags
  temperatures_by_month = ghcnm.fit_permitted_data_to_range(temp_data_for_station)

  # Calculate the Reference Average per month
  reference_averages_by_month = anomaly.average_reference_years_by_month(temperatures_by_month)

  # Calculate anomalies for each year on a month class by month class basis (Jan to Jan, Feb to Feb, ...) and return an array of month class arrays
  anomalies_by_month = anomaly.calculate_anomalies_by_month_class(temperatures_by_month, reference_averages_by_month)

  # MATH - Calculate average anomalies for each year. For each year, average the anomalies for all 12 months and return an array of average annual anomalies
  average_anomalies_by_year = anomaly.average_monthly_anomalies_by_year(anomalies_by_month)

  anomaly_trend = anomaly.calculate_trend(average_anomalies_by_year)

  absolute_trend = anomaly.calculate_absolute_trend(temperatures_by_month)

  # Update statistics and console output
  anomaly_visual = ut.update_statistics(anomaly_trend, "anomaly")
  absolute_visual = ut.update_statistics(absolute_trend, "absolute")

  start_year, end_year = ghcnm.get_station_start_and_end_year(temp_data_for_station)

  # Output Progress and Trends to Console
  ut.compose_station_console_output(station_iteration, TOTAL_STATIONS, station_id, anomaly_visual, anomaly_trend, absolute_visual, absolute_trend, start_year, end_year, station_location)

  # ORDER - Replace the first cell with the station location
  average_anomalies_by_year_and_station_metadata = pd.concat([ pd.Series([station_id]), pd.Series([station_location]), average_anomalies_by_year ]).reset_index(drop = True)

  annual_anomalies_by_station.append(average_anomalies_by_year_and_station_metadata)

#
# Output File
ut.create_excel_file(pd.DataFrame(annual_anomalies_by_station))

ut.print_summary_to_console(TOTAL_STATIONS)
