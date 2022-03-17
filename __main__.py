'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from constants import *
import pandas as pd
import numpy as np
import math
import os
import datetime

import download
import stations
import temperatures
import anomaly
import output
import download_daily

STATION_FILE_PATH, COUNTRIES_FILE_PATH, GHCN_TEMPERATURES_FILE_PATH = ("", "", "")

# Check if files exist and if not, download them
if VERSION == 'daily':
  STATION_FILE_PATH, COUNTRIES_FILE_PATH, GHCN_TEMPERATURES_FILE_PATH = download_daily.download_GHCNm_data()
else:
  STATION_FILE_PATH, COUNTRIES_FILE_PATH, GHCN_TEMPERATURES_FILE_PATH = download.download_GHCNm_data()

# Show the Developer the settings they've chosen
output.print_settings_to_console(GHCN_TEMPERATURES_FILE_PATH, STATION_FILE_PATH)

# Parse Station metadata (.inv) into a DataFrame
STATIONS = stations.get_stations(STATION_FILE_PATH, COUNTRIES_FILE_PATH)

# Parse GHCN-M temperature data (.dat) into a DataFrame
TEMPERATURES = temperatures.get_temperatures_by_station(GHCN_TEMPERATURES_FILE_PATH)

# "TEMPERATURES" data is grouped by station, so counting its length will tell us the total number of Stations
TOTAL_STATIONS = len(TEMPERATURES)

# Represents the current station being iterated over (useful for keeping the Developer updated in the console)
station_iteration = 0

# Our goal is to have an array of annual anomalies for every station that we can then average or grid and average
annual_anomalies_by_station = []

# For each station file
for station_id, temperature_data_for_station in TEMPERATURES:

  # Build an array based on the Year Range constants and include the matching line from the file on each year if its data evaluates as acceptable based on its flags
  temperatures_by_month = temperatures.fit_permitted_data_to_range(temperature_data_for_station)

  # To convert absolute temperatures to anomalies, you need to have a baseline to compare temperature changes to so you can calculate the anomalies. We will create a separate baseline for each month of the year, averaging the reference years according to the Developer Settings in "constants.py"
  baseline_by_month = anomaly.average_reference_years_by_month(temperatures_by_month)

  # Calculate anomalies for each year on a month class by month class basis (Jan to Jan, Feb to Feb, ...) relative to the baselines we calculated earlier (for each month) and return an array of month class arrays
  anomalies_by_month = anomaly.calculate_anomalies_by_month_class(temperatures_by_month, baseline_by_month)

  # For each year, average the anomalies for all 12 months and return an list of average anomalies by year. It is ok if some months are missing data since we first converted them to anomalies before averaging.
  average_anomalies_by_year = anomaly.average_monthly_anomalies_by_year(anomalies_by_month)

  # Get the station's location
  station_location = stations.get_station_address(station_id, STATIONS)

  # Get the station's grid box label
  station_gridbox = stations.get_station_gridbox(station_id, STATIONS)

  # Add important metadata to the beginning of each station's column (station's ID, station's location, and station's grid box label). The grid box label is important if we wish to average by grid instead of by station.
  average_anomalies_by_year_and_station_metadata = pd.concat([ pd.Series([station_id, station_location, station_gridbox]), average_anomalies_by_year ]).reset_index(drop = True)

  # Remember that array we created at the beginning to contain lists of annual anomalies for every station? It's no good unless we add the annual anomalies for this station to it
  annual_anomalies_by_station.append(average_anomalies_by_year_and_station_metadata)

  # We make console output interesting by calculating the trend/slope of the annual anomalies for this station using least squares fitting. Values above 0 indicate a warming trend, values below zero indicate a cooling trend.
  anomaly_trend = anomaly.calculate_trend(average_anomalies_by_year)

  # To make sure our logic isn't getting carried away, we should check the absolute temperature trends/slopes for each month and average the slopes into one annual slope to see that our anomaly trend lines up. If our anomaly uses a fixed baseline, the trends should perfectly match unless some data is missing.
  absolute_trend = anomaly.calculate_absolute_trend(temperatures_by_month)

  # We will gather statistics on our trends for end of command summaries
  anomaly_visual = output.update_statistics(anomaly_trend, "anomaly")
  absolute_visual = output.update_statistics(absolute_trend, "absolute")

  # We wish to give the Developer a quick reference to the station's starting and ending years.
  start_year, end_year = temperatures.get_station_start_and_end_year(temperature_data_for_station)

  # Increase the station iteration for console output
  station_iteration += 1

  # Output Progress and Trends to Console
  output.compose_station_console_output(station_iteration, TOTAL_STATIONS, station_id, anomaly_visual, anomaly_trend, absolute_visual, absolute_trend, start_year, end_year, station_location, station_gridbox)

# Remember those statistics we collected earlier? We finally show them to the Developer in the Console.
output.print_summary_to_console(TOTAL_STATIONS, GHCN_TEMPERATURES_FILE_PATH)

# If we convert our list of station annual anomalies into a dataframe, it makes it easier to work with.
annual_anomalies_by_station_dataframe = pd.DataFrame(annual_anomalies_by_station)

# If the Developer wishes to grid the data:
if USE_GRIDDING:

  # Separate stations into their respective grid boxes and average all anomalies by year per grid box
  annual_anomalies_by_grid = anomaly.average_anomalies_by_year_by_grid(annual_anomalies_by_station_dataframe)

  # Weight each grid box by the cosine of the mid-latitude point for that grid box (and possibly the land ratio) and average all grid boxes with data. The results is a list of global anomalies by year.
  avg_annual_anomalies_of_all_grids = anomaly.average_weighted_grid_anomalies_by_year(annual_anomalies_by_grid)

  # Data in GHCNm arrives measured in 100ths of a degree, so we convert it into natural readings
  avg_annual_anomalies_of_all_grids_divided = avg_annual_anomalies_of_all_grids.iloc[1:].apply(lambda v : normal_round(v / 100, 3))

  # Finally prepare the data for Excel and save
  output.create_excel_file(annual_anomalies_by_grid, avg_annual_anomalies_of_all_grids[1:], avg_annual_anomalies_of_all_grids_divided, GHCN_TEMPERATURES_FILE_PATH)

# If we are skipping gridding:
else:

  # Average annual anomolies across all stations
  average_anomolies_of_all_stations = anomaly.average_monthly_anomalies_by_year(annual_anomalies_by_station_dataframe)

  # Data in GHCNm arrives measured in 100ths of a degree, so we convert it into natural readings
  average_anomolies_of_all_stations_divided = average_anomolies_of_all_stations.apply(lambda v : normal_round(v / 100, 3))

  # Finally prepare the data for Excel and save
  output.create_excel_file(annual_anomalies_by_station_dataframe, average_anomolies_of_all_stations, average_anomolies_of_all_stations_divided)
