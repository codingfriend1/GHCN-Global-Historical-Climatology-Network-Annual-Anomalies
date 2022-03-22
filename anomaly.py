'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

from constants import *
import pandas as pd
import numpy as np
import math
import stations

def get_minimum_years(data_length):
  
  return math.ceil(ACCEPTABLE_AVAILABLE_DATA_PERCENT * data_length)


def mean_if_enough_data(row, minimum_years_needed):

  return row.mean(skipna=True).round(2) if row.count() >= minimum_years_needed else math.nan


def average_reference_years_by_month(temperatures_by_month):

  reference_years = temperatures_by_month[ range(REFERENCE_START_YEAR, REFERENCE_START_YEAR + REFERENCE_RANGE) ]

  minimum_years_needed = get_minimum_years(REFERENCE_RANGE)

  baseline_by_month = reference_years.apply(mean_if_enough_data, args=(minimum_years_needed,), axis=1)

  return baseline_by_month


def calculate_anomaly(temperature, baseline_by_month):

  month = temperature.name

  reference_average_for_month = baseline_by_month[month]

  return temperature.subtract(reference_average_for_month, fill_value=math.nan).apply(normal_round, args=(2,))


# Within each month class, calculate annual anomalies using array of fixed reference averages provided
def calculate_anomalies_by_month_class(temperatures_by_month, baseline_by_month):

  return temperatures_by_month.apply(calculate_anomaly, args=(baseline_by_month,), axis=1)


def average_monthly_anomalies_by_year(lists_of_anomalies):

  average_anomalies_by_year = lists_of_anomalies.mean(

    axis=0, skipna=True, level=None, numeric_only=True
    
  ).apply(normal_round, args=(2,))

  return average_anomalies_by_year


def weighted_avg(df, weights):
  
  indices = ~np.isnan(df)

  if np.isnan(df).all():

    return math.nan

  else:
    
    return (df[indices] * weights[indices]).sum() / weights[indices].sum()


def average_weighted_grid_anomalies_by_year(anomalies_by_grid):

  weights = anomalies_by_grid.iloc[0].to_numpy()

  average_anomalies_by_year = anomalies_by_grid.apply(weighted_avg, args=(weights,), axis=1)

  return average_anomalies_by_year.apply(normal_round, args=(2,))


def average_anomalies_by_year_by_grid(lists_of_anomalies, include_land_ratio_in_weight = False):

  station_gridbox_row = 2

  stations_grouped_by_gridbox = lists_of_anomalies.groupby(by=[station_gridbox_row])

  annual_anomalies_by_grid = {}

  for grid_label, stations_in_grid in stations_grouped_by_gridbox:

    # Determine the weight to give the grid based on it's land and land / water ratio
    grid_weight = stations.determine_grid_weight(grid_label, include_land_ratio_in_weight = include_land_ratio_in_weight)

    # Average all the land stations for this grid
    grid_average_by_year = stations_in_grid.mean(axis=0, skipna=True, level=None, numeric_only=True).apply(normal_round, args=(2,))

    annual_anomalies_by_grid[grid_label] = np.concatenate([ [grid_weight], grid_average_by_year])

  return pd.DataFrame(annual_anomalies_by_grid)


def calculate_trend(average_anomalies_by_year):

  y = average_anomalies_by_year.to_numpy()

  years = average_anomalies_by_year.index.to_numpy()

  # Limit our range to only numbers and only years between the ABSOLUTE_START_YEAR and ABSOLUTE_END_YEAR
  idx = (np.isfinite(years) & np.isfinite(y) & 
    np.greater_equal(years, ABSOLUTE_START_YEAR) & np.less(years, ABSOLUTE_END_YEAR))


  minimum_for_reliable_average = get_minimum_years(ABSOLUTE_END_YEAR - ABSOLUTE_START_YEAR)

  if len(years[idx]) >= minimum_for_reliable_average:

    slope_of_annual_temperatures = normal_round(np.polyfit(years[idx], y[idx], 1)[0], 3)

    return slope_of_annual_temperatures

  else:

    return math.nan


# For each month class, calculate the annual absolute trend and finally average all trends
def calculate_absolute_trend(temperatures_by_month):

  absolute_trends = temperatures_by_month.apply(calculate_trend, axis=1)

  average_absolute_trend = normal_round(absolute_trends.mean(skipna=True), 3)

  return average_absolute_trend
