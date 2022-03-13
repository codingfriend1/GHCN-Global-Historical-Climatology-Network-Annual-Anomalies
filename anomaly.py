from constants import *
import pandas as pd
import numpy as np
import math
import stations

def isnumber(num):
  return not math.isnan(num)

# Translate the Reference Start Year into an index in the data. 
def get_reference_year_index():

  INDEX_FOR_REFERENCE_START_YEAR = REFERENCE_START_YEAR - YEAR_RANGE_START

  INDEX_FOR_REFERENCE_END_YEAR = INDEX_FOR_REFERENCE_START_YEAR + REFERENCE_RANGE

  return INDEX_FOR_REFERENCE_START_YEAR, INDEX_FOR_REFERENCE_END_YEAR

def determine_readings_needed_for_reliable_average(data_range):
  
  return math.ceil(ACCEPTABLE_AVAILABLE_DATA_PERCENT * data_range)

def average_reference_years_by_month(temperatures_by_month):

  INDEX_FOR_REFERENCE_START_YEAR, INDEX_FOR_REFERENCE_END_YEAR = get_reference_year_index()

  reference_range = temperatures_by_month.iloc[:, range(INDEX_FOR_REFERENCE_START_YEAR, INDEX_FOR_REFERENCE_END_YEAR) ]

  reference_averages_by_month = reference_range.mean(axis=1, skipna=True, level=None, numeric_only=True).round(2)

  # Determine the amount of necessary values to form a reliable average
  necessary_minimum_readings_to_form_a_reliable_average = determine_readings_needed_for_reliable_average(len(reference_range))

  # If the number of readings is less than the necessary minimum for forming a reliable average, substitute the value with NaN
  for row_index, row in reference_range.iterrows():

    number_of_yearly_readings_within_reference_range = row.count()

    if number_of_yearly_readings_within_reference_range < necessary_minimum_readings_to_form_a_reliable_average:

      reference_averages_by_month.iat[row_index] = math.nan

  return reference_averages_by_month


# An anomaly is calculated by subtracting a reference average from the current reading
def calculate_anomaly(temperature, reference_average):

  # We only want to calculate an anomaly if the reference average and the current reading are not missing
  anomaly = normal_round(temperature - reference_average, 2) if isnumber(temperature) and isnumber(reference_average) else math.nan

  return anomaly


# Within each month class, calculate annual anomalies using array of fixed reference averages provided
def calculate_anomalies_by_month_class(temperatures_by_month, reference_averages_by_month):

  anomalies_by_month = [
    [], # jan
    [], # feb
    [], # mar
    [], # apr
    [], # may
    [], # jun
    [], # jul
    [], # aug
    [], # sep
    [], # oct
    [], # nov
    [], # dec
  ]

  for row_index, temperature_row in temperatures_by_month.iterrows():

    reference_average_for_row = reference_averages_by_month.iat[row_index]

    for year_value in temperature_row:

      anomaly_for_year = calculate_anomaly(year_value, reference_average_for_row)

      anomalies_by_month[row_index].append(anomaly_for_year)

  return pd.DataFrame(anomalies_by_month, columns=range(YEAR_RANGE_START, YEAR_RANGE_END))


def average_monthly_anomalies_by_year(lists_of_anomalies, axis=0):

  average_anomalies_by_year = lists_of_anomalies.mean(axis=axis, skipna=True, level=None, numeric_only=True).round(2)

  return average_anomalies_by_year

def average_anomalies_by_year_by_grid(lists_of_anomalies):

  station_gridbox_row = 2

  stations_grouped_by_gridbox = lists_of_anomalies.groupby(by=[station_gridbox_row])

  annual_anomalies_by_grid = {}

  for grid_label, stations_in_grid in stations_grouped_by_gridbox:

    # Determine the weight to give the grid based on it's land and land / water ratio
    grid_weight = normal_round(stations.determine_grid_weight(grid_label), 4)

    # Average all the land stations for this grid
    grid_average_by_year = stations_in_grid.mean(axis=0, skipna=True, level=None, numeric_only=True).round(2)

    annual_anomalies_by_grid[grid_label] = np.concatenate([ [grid_weight], grid_average_by_year])

  return pd.DataFrame(annual_anomalies_by_grid)

def calculate_trend(average_anomalies_by_year):

  y_anomalies = average_anomalies_by_year.to_numpy()
  x_years = average_anomalies_by_year.index.to_numpy()

  idx = np.isfinite(x_years) & np.isfinite(y_anomalies) & np.greater_equal(x_years, ABSOLUTE_START_YEAR) & np.less(x_years, ABSOLUTE_END_YEAR)

  trends_range = ABSOLUTE_END_YEAR - ABSOLUTE_START_YEAR

  necessary_minimum_readings_to_form_a_reliable_average = determine_readings_needed_for_reliable_average(trends_range)

  if len(x_years[idx]) >= necessary_minimum_readings_to_form_a_reliable_average:

    slope_of_yearly_averages = normal_round(np.polyfit(x_years[idx], y_anomalies[idx], 1)[0], 3)

    return slope_of_yearly_averages

  else:
    return math.nan


# For each month class, calculate the annual absolute trend and finally average all trends
def calculate_absolute_trend(temperatures_by_month):

  trends_by_month = []

  for year, month_row in temperatures_by_month.iterrows():

    trends_by_month.append(calculate_trend(month_row))

  average_absolute_trend = pd.DataFrame(trends_by_month).mean(axis=0, skipna=True, level=None, numeric_only=True).round(2)[0]

  return average_absolute_trend
