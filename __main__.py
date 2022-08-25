'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from globals import *
import pandas as pd
import math
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

  # We wish to give the Developer a quick reference to the station's starting and ending years.
  start_year, end_year = temperatures.get_station_start_and_end_year(temperature_data_for_station)

  # Reindex the station data to fit our year range
  temperatures_by_month = temperature_data_for_station.reindex(YEAR_RANGE_LIST, fill_value=math.nan)

  # To convert absolute temperatures to anomalies, you need to have a baseline to compare temperature changes to so you can calculate the anomalies. We will create a separate baseline for each month of the year, averaging the reference years according to the Developer Settings in "constants.py"
  baseline_by_month = anomaly.average_reference_years_by_month(temperatures_by_month)

  # Calculate anomalies for each year on a month class by month class basis (Jan to Jan, Feb to Feb, ...) relative to the baselines we calculated earlier (for each month) and return an array of month class arrays
  anomalies_by_month = anomaly.calculate_anomalies_by_month(temperatures_by_month, baseline_by_month)

  # For each year, average the anomalies for all 12 months and return an list of average anomalies by year. It is ok if some months are missing data since we first converted them to anomalies before averaging.
  average_anomalies_by_year = anomaly.average_anomalies(anomalies_by_month)

  station_location, station_quadrant = stations.get_station_metadata(station_id, STATIONS)

  # Add important metadata to the beginning of each station's column (station's ID, station's location, and station's grid box label). The grid box label is important if we wish to average by grid instead of by station.
  annual_anomalies_and_metadata = [station_id, station_location, station_quadrant] + list(average_anomalies_by_year)

  annual_anomalies_by_station.append(annual_anomalies_and_metadata)

  absolute_trend = anomaly.average_trends(temperatures_by_month)

  absolute_visual = output.update_statistics(absolute_trend)
    
  station_iteration += 1

  output.compose_station_console_output(station_iteration, TOTAL_STATIONS, station_id, absolute_visual, absolute_trend, start_year, end_year, station_location, station_quadrant)

# Remember those statistics we collected earlier? We finally show them to the Developer in the Console.
output.print_summary_to_console(TOTAL_STATIONS, TEMPERATURES_FILE_PATH)

# If we convert our list of station annual anomalies into a dataframe, it makes it easier to work with.
annual_anomalies_by_station_dataframe = pd.DataFrame(
  annual_anomalies_by_station,
  columns = ['station_id', "location", "quadrant" ] + YEAR_RANGE_LIST
)

# Average annual anomolies across all ungridded stations
ungridded_anomalies = anomaly.average_anomalies(annual_anomalies_by_station_dataframe, axis=0)

# Data in GHCNm arrives measured in 100ths of a degree, so we convert it into natural readings
ungridded_anomalies_divided = ungridded_anomalies.apply(anomaly.divide_by_one_hundred)

# Separate stations into their respective grid boxes and average all anomalies by year per grid box
annual_anomalies_by_grid = anomaly.average_stations_per_grid(annual_anomalies_by_station_dataframe)

annual_anomalies_by_grid_of_land = anomaly.average_stations_per_grid(
  annual_anomalies_by_station_dataframe, use_land_ratio = True
)

# Weigh each grid box by the cosine of the mid-latitude point for that grid box (and possibly the land ratio) and average all grid boxes with data. The result is a list of global anomalies by year.
gridded_anomalies = anomaly.average_all_grids(annual_anomalies_by_grid)

# Data in GHCNm arrives measured in 100ths of a degree, so we convert it into natural readings
gridded_anomalies_divided = gridded_anomalies.apply(anomaly.divide_by_one_hundred)

# Also weigh each grid by land ratio
gridded_anomalies_of_land = anomaly.average_all_grids(annual_anomalies_by_grid_of_land)

gridded_anomalies_of_land_divided = gridded_anomalies_of_land.apply(anomaly.divide_by_one_hundred)

# Finally prepare the data for Excel and save
output.create_excel_file(

  ungridded_anomalies = ungridded_anomalies,
  ungridded_anomalies_divided = ungridded_anomalies_divided,

  average_of_grids = gridded_anomalies,
  average_of_grids_divided = gridded_anomalies_divided,

  average_of_grids_by_land_ratio = gridded_anomalies_of_land,
  average_of_grids_by_land_ratio_divided = gridded_anomalies_of_land_divided,

  anomalies_by_grid = annual_anomalies_by_grid,
  anomalies_by_station = annual_anomalies_by_station_dataframe,

  data_source = TEMPERATURES_FILE_PATH
)

output.console_performance(t0, TOTAL_STATIONS)
