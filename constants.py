'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

import datetime
import math

# Which version of GHCNm to work with
VERSION = 'daily' #v3, v4, daily

# Which Quality Controlled dataset to work with, adjusted or unadjusted
QUALITY_CONTROL_DATASET = "qcu" #qca, qcf

# Earliest year you want to consider in the data
YEAR_RANGE_START = 1851

# Leave blank if you wish to use a rolling average
REFERENCE_START_YEAR = 1961

# Number of years to consider in the reference average
REFERENCE_RANGE = 30

# Whether to purge all readings with Quality Control, Data Measurement, or Data Source flags
PURGE_FLAGS = False

# The acceptable amount of data available (subtracting missing data) before an anomaly calculation can be made (in decimal form)
ACCEPTABLE_AVAILABLE_DATA_PERCENT = 0.5

# Whether to create a columns for each station's annual anomalies in the final Excel sheet. With the larger number of stations in the GHCNm v4, this will cause the program to crash at the end since 27,000 columns it too large for an excel file. But it is useful for testing purposes and smaller station amounts. When set to False, annual anomaly columns are printed for each grid quadrant instead.
PRINT_STATION_ANOMALIES = False

# The range to consider when calculating trends for console output, does not effect excel results
ABSOLUTE_START_YEAR = 1900 # Inclusive
ABSOLUTE_END_YEAR = 2000 # Non-inclusive

# Restrict data to only use stations in a certain setting in GHCNm v3 according to the population class as determined by population (POPCLS) and population class as determined by Satellite night lights (POPCSS)
# SURROUNDING_CLASS can be "rural", "suburban", "urban", "rural and suburban", or "suburban and urban"
SURROUNDING_CLASS = ""

# How many months does each year of data need to include to accept that row of data
MONTHS_REQUIRED_EACH_YEAR = 12

# Only use stations from the USHCN network in GHCNm v3
ONLY_USHCN = False

# Include country name, ex: China, United States of America, Artic, Ireland (case-insensitive)
USE_COUNTRY = False

# Include a range of countries
IN_COUNTRY = False

# 
# Calculated values
# 

# Retrieve the year as of now
TODAY = datetime.date.today()

# This year (YYYY)
YEAR_AS_OF_TODAY = int(TODAY.strftime("%Y"))

# The last year to consider
YEAR_RANGE_END = YEAR_AS_OF_TODAY + 1

SURROUNDING_CLASS = SURROUNDING_CLASS.lower()


# Methods
def normal_round(num, decimals=0):

  if math.isnan(num):
    return num

  multiplier = 10 ** decimals

  value = math.floor(num*multiplier + 0.5) / multiplier

  if decimals == 0:
    value = int(value)

  return value
