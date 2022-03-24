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

def mean_and_round(df, rounding_decimals = 2, axis=1):

  if isinstance(df, pd.Series):

    return normal_round(df.mean(skipna=True), rounding_decimals)

  else:  

    return df.mean(skipna=True, numeric_only=True, axis=axis).apply(normal_round, args=(rounding_decimals,))


def divide_by_one_hundred(num):

  return normal_round(num / 100, 3)


def mean_if_enough_data(row, minimum_years_needed):

  return mean_and_round(row) if row.count() >= minimum_years_needed else math.nan


def average_reference_years_by_month(temperatures_by_month):

  reference_years = temperatures_by_month.loc[ RANGE_OF_REFERENCE_YEARS, month_columns ]

  minimum_years_needed = get_minimum_years(REFERENCE_RANGE)

  baseline_by_month = reference_years.apply(mean_if_enough_data, args=(minimum_years_needed,))

  return baseline_by_month


def calculate_anomaly(temperature, baseline_by_month):

  month = int(temperature.name) - 1

  reference_average_for_month = baseline_by_month[month]

  return temperature.subtract(reference_average_for_month, fill_value=math.nan).apply(normal_round, args=(2,))


# Within each month class, calculate annual anomalies using array of fixed reference averages provided
def calculate_anomalies_by_month(temperatures_by_month, baseline_by_month):

  return temperatures_by_month[ month_columns ].apply(calculate_anomaly, args=(baseline_by_month,))


def average_anomalies(lists_of_anomalies, axis=1):

  return mean_and_round(lists_of_anomalies, axis=axis)


def weighted_avg(df, weights):
  
  # Only average grids and weights that are not NaN
  indices = ~np.isnan(df)

  if np.isnan(df).all():

    return math.nan

  else:
    
    return (df[indices] * weights[indices]).sum() / weights[indices].sum()


def average_all_grids(anomalies_by_grid):

  return anomalies_by_grid[ YEAR_RANGE ].apply(

    weighted_avg, args=(anomalies_by_grid['weight'],),

  ).apply(normal_round, args=(2,))


def average_by_grid(stations_in_grid, use_land_ratio = False):

  quadrant = stations_in_grid.name

  weight = stations.determine_grid_weight(quadrant, use_land_ratio=use_land_ratio)

  average_by_year = mean_and_round(stations_in_grid, axis=0)

  index = [ "weight" ] + list(YEAR_RANGE)

  values = [ weight ] + list(average_by_year)

  return pd.Series(values, index=index)


def average_stations_per_grid(lists_of_anomalies_by_station, use_land_ratio = False):

  return lists_of_anomalies_by_station.groupby('quadrant').apply(average_by_grid, use_land_ratio)


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
def average_trends(temperatures_by_month):

  absolute_trends = temperatures_by_month[ month_columns ].apply(calculate_trend)

  average_absolute_trend = mean_and_round(absolute_trends, 3)

  return average_absolute_trend
