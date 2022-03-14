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

# Parse Station data into a DataFrame
STATIONS = stations.get_stations(STATION_URL, COUNTRIES_URL)

# Parse GHCN-M data into a DataFrame
TEMPERATURES = ghcnm.get_ghcnm_by_station(GHCNM_DAT_URL)

# unique_countries = TEMPERATURES[0].unique()

# TOTAL_COUNTRIES = len(unique_countries)
# country_iteration = 0

# anomalies_by_country = {}

# for country_code in unique_countries:

#   unique_stations_in_country = TEMPERATURES.loc[TEMPERATURES[0] == country_code][1].unique()

#   country_iteration += 1

#   country_name = stations.get_country_name_from_code(country_code)

#   print(f"Country {country_iteration} of {TOTAL_COUNTRIES} - {country_name} ({country_code})")
#   print("="*133)

# Prepare station progress counter
TOTAL_STATIONS_IN_COUNTRY = len(TEMPERATURES)

station_iteration = 0

# Prepare final array of station data
annual_anomalies_by_station_in_country = []

# For each station file
# for station_id in unique_stations_in_country:
for station_id, temperature_data_for_station in TEMPERATURES:  

  # temperature_data_for_station = TEMPERATURES.loc[(TEMPERATURES[0] == country_code) & (TEMPERATURES[1] == station_id)]

  # Increate the progress iterator
  station_iteration += 1

  # Get the Station Location
  station_location = stations.get_station_address(station_id, STATIONS)

  station_gridbox = stations.get_station_gridbox(station_id, STATIONS)

  # Build an array based on the Year Range constants and include the matching line from the file on each year if its data evaluates as acceptable based on its flags
  temperatures_by_month = ghcnm.fit_permitted_data_to_range(temperature_data_for_station)

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

  start_year, end_year = ghcnm.get_station_start_and_end_year(temperature_data_for_station)

  # Output Progress and Trends to Console
  ut.compose_station_console_output(station_iteration, TOTAL_STATIONS_IN_COUNTRY, station_id, anomaly_visual, anomaly_trend, absolute_visual, absolute_trend, start_year, end_year, station_location, station_gridbox)

  # ORDER - Replace the first cell with the station location
  average_anomalies_by_year_and_station_metadata = pd.concat([ pd.Series([station_id, station_location, station_gridbox]), average_anomalies_by_year ]).reset_index(drop = True)

  annual_anomalies_by_station_in_country.append(average_anomalies_by_year_and_station_metadata)

  # anomalies_by_country[country_code] = np.concatenate([[f"{country_name} station averages"], average_anomalies_by_year ])



ut.print_summary_to_console(TOTAL_STATIONS_IN_COUNTRY)

annual_anomalies_by_station_in_country_dataframe = pd.DataFrame(annual_anomalies_by_station_in_country)

# Average annual anomolies across all stations
average_anomolies_of_all_stations_in_country = anomaly.average_monthly_anomalies_by_year(annual_anomalies_by_station_in_country_dataframe)

annual_anomalies_by_grid = anomaly.average_anomalies_by_year_by_grid(annual_anomalies_by_station_in_country_dataframe)

avg_annual_anomalies_of_all_grids = anomaly.average_weighted_grid_anomalies_by_year(annual_anomalies_by_grid)

# Output File
ut.create_excel_file(annual_anomalies_by_grid, avg_annual_anomalies_of_all_grids[1:])

# ut.create_final_excel_file(pd.DataFrame(anomalies_by_country), country_name, country_code)
