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
import time

import download
import stations
import temperatures
import anomaly
import output

t0 = time.perf_counter()

STATION_FILE_PATH, TEMPERATURES_FILE_PATH, COUNTRIES_FILE_PATH = download.get_files()

output.print_settings_to_console(TEMPERATURES_FILE_PATH, STATION_FILE_PATH)

STATIONS = stations.get_stations(STATION_FILE_PATH, COUNTRIES_FILE_PATH)

TEMPERATURES = temperatures.get_temperatures_by_station(TEMPERATURES_FILE_PATH, STATIONS)

# "TEMPERATURES" data is grouped by station, so counting its length will tell us the total number of Stations
TOTAL_STATIONS = len(TEMPERATURES)

station_iteration = 0

# Our goal is to have an array of annual anomalies for every station that we can then average or grid and average
annual_anomalies_by_station = []

# For each station file
for station_id, temperature_data_for_station in TEMPERATURES:

  # Create an array or arrays for each month for a range of years filling each with data from the station after rejecting unwanted data meeting certain flagged criteria
  temperatures_by_month = temperatures.fit_permitted_data_to_range(temperature_data_for_station)

  # To convert absolute temperatures to anomalies, you need to have a baseline to compare temperature changes to so you can calculate the anomalies. We will create a separate baseline for each month of the year, averaging the reference years according to the Developer Settings in "constants.py"
  baseline_by_month = anomaly.average_reference_years_by_month(temperatures_by_month)

  # Calculate anomalies for each year on a month class by month class basis (Jan to Jan, Feb to Feb, ...) relative to the baselines we calculated earlier (for each month) and return an array of month class arrays
  anomalies_by_month = anomaly.calculate_anomalies_by_month_class(temperatures_by_month, baseline_by_month)

  # For each year, average the anomalies for all 12 months and return an list of average anomalies by year. It is ok if some months are missing data since we first converted them to anomalies before averaging.
  average_anomalies_by_year = anomaly.average_monthly_anomalies_by_year(anomalies_by_month)

  station_location = stations.get_station_address(station_id, STATIONS)

  station_gridbox = stations.get_station_gridbox(station_id, STATIONS)

  # Add important metadata to the beginning of each station's column (station's ID, station's location, and station's grid box label). The grid box label is important if we wish to average by grid instead of by station.
  average_anomalies_by_year_and_station_metadata = output.generate_column([station_id, station_location, station_gridbox], average_anomalies_by_year)

  annual_anomalies_by_station.append(average_anomalies_by_year_and_station_metadata)

  absolute_trend = anomaly.calculate_absolute_trend(temperatures_by_month)

  absolute_visual = output.update_statistics(absolute_trend)

  # We wish to give the Developer a quick reference to the station's starting and ending years.
  start_year, end_year = temperatures.get_station_start_and_end_year(temperature_data_for_station)

  station_iteration += 1

  output.compose_station_console_output(station_iteration, TOTAL_STATIONS, station_id, absolute_visual, absolute_trend, start_year, end_year, station_location, station_gridbox)

# Remember those statistics we collected earlier? We finally show them to the Developer in the Console.
output.print_summary_to_console(TOTAL_STATIONS, TEMPERATURES_FILE_PATH)

# If we convert our list of station annual anomalies into a dataframe, it makes it easier to work with.
annual_anomalies_by_station_dataframe = pd.DataFrame(annual_anomalies_by_station)

# Separate stations into their respective grid boxes and average all anomalies by year per grid box
annual_anomalies_by_grid = anomaly.average_anomalies_by_year_by_grid(annual_anomalies_by_station_dataframe)

annual_anomalies_by_grid_weighed_by_land_ratio = anomaly.average_anomalies_by_year_by_grid(
  annual_anomalies_by_station_dataframe, 
  include_land_ratio_in_weight = True
)

# Weigh each grid box by the cosine of the mid-latitude point for that grid box (and possibly the land ratio) and average all grid boxes with data. The result is a list of global anomalies by year.
avg_annual_anomalies_of_all_grids = anomaly.average_weighted_grid_anomalies_by_year(annual_anomalies_by_grid)

# Also weigh each grid by land ratio
avg_annual_anomalies_of_all_grids_weighed_by_land_ratio = anomaly.average_weighted_grid_anomalies_by_year(
  annual_anomalies_by_grid_weighed_by_land_ratio
)

# Data in GHCNm arrives measured in 100ths of a degree, so we convert it into natural readings
avg_annual_anomalies_of_all_grids_divided = avg_annual_anomalies_of_all_grids.iloc[1:].apply(
  lambda v : normal_round(v / 100, 3)
)

avg_annual_anomalies_of_all_grids_weighted_by_land_ratio_divided = avg_annual_anomalies_of_all_grids_weighed_by_land_ratio.iloc[1:].apply(
    lambda v : normal_round(v / 100, 3)
  )

# Average annual anomolies across all ungridded stations
average_anomolies_of_all_stations = anomaly.average_monthly_anomalies_by_year(
  annual_anomalies_by_station_dataframe
)

# Data in GHCNm arrives measured in 100ths of a degree, so we convert it into natural readings
average_anomolies_of_all_stations_divided = average_anomolies_of_all_stations.apply(
  lambda v : normal_round(v / 100, 3)
)

# Finally prepare the data for Excel and save
output.create_excel_file(

  average_of_stations = average_anomolies_of_all_stations,
  average_of_stations_divided = average_anomolies_of_all_stations_divided,

  average_of_grids = avg_annual_anomalies_of_all_grids,
  average_of_grids_divided = avg_annual_anomalies_of_all_grids_divided,

  average_of_grids_by_land_ratio = avg_annual_anomalies_of_all_grids_weighed_by_land_ratio,
  average_of_grids_by_land_ratio_divided = avg_annual_anomalies_of_all_grids_weighted_by_land_ratio_divided,

  anomalies_by_grid = annual_anomalies_by_grid,
  anomalies_by_station = annual_anomalies_by_station_dataframe,

  data_source = TEMPERATURES_FILE_PATH
)

end_time = time.perf_counter() - t0

minutes, remainder_seconds= divmod(end_time, 60)

hours, remainder_minutes= divmod(minutes, 60)

seconds  = normal_round(end_time)

print(f"Process completed in {int(normal_round(hours))}h:{int(normal_round(remainder_minutes))}m:{int(normal_round(remainder_seconds))}s")

total_minutes = seconds / 60

stations_per_minute = normal_round(TOTAL_STATIONS / total_minutes)

print(f"With {'{:,}'.format(TOTAL_STATIONS)} stations, that's {'{:,}'.format(stations_per_minute)} stations/minute.\n")
