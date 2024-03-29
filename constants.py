'''
  Author: Jon Paul Miles
  Date Created: March 11, 2022
'''

# Network
'''
  Which network of data do you wish to work with ('GHCN', 'USHCN', 'USCRN')

  GHCN - Global Historical Climatology Network
  USHCN - U.S. Historical Climatology Network
  USCRN - U.S. Climate Reference Network

'''
NETWORK = "GHCN"

'''
  Which version of the network to work with

  For GHCN - 'v3', 'v4', 'daily'
  For USHCN - 'v2.5'
  For USCRN - 'v1'

'''
VERSION = 'v3'

'''
  Which Quality Controlled dataset of the network to work with

  For GHCN v3 - 'qcu', 'qca'
  For GHCN v4 - 'qcu', 'qcf'
  For GHCN daily - 'all'
  For USHCN v2.5 - 'raw', 'tob', 'FLs'
  For USCRN v1 - 'monthly01'
  
'''
QUALITY_CONTROL_DATASET = "qcu"

# Earliest year you want to consider in the data
YEAR_RANGE_START = 1700

# Leave blank if you wish to use a rolling average
REFERENCE_START_YEAR = 1951

# Number of years to consider in the reference average
REFERENCE_RANGE = 30

# Whether to purge all readings with Quality Control, Data Measurement, or Data Source flags
PURGE_FLAGS = False

# The acceptable amount of data available (subtracting missing data) with which an anomaly calculation can be made (in decimal form)
ACCEPTABLE_AVAILABLE_DATA_PERCENT = 0.5

# Whether to create a columns for each station's annual anomalies in the final Excel sheet. With the larger number of stations in the GHCNm v4, this will cause the program to crash at the end since 27,000 columns it too large for an excel file. But it is useful for testing purposes and smaller station amounts. When set to False, annual anomaly columns are printed for each grid quadrant instead.
PRINT_STATION_ANOMALIES = False

# The range to consider when calculating trends for console output, does not effect excel results
ABSOLUTE_START_YEAR = 1700 # Inclusive

ABSOLUTE_END_YEAR = 2020 # Non-inclusive

# How many months does each year of data need to include to accept that row of data
MONTHS_REQUIRED_EACH_YEAR = 1

# Restrict data to only use stations in a certain setting in GHCNm v3 according to the population class as determined by population (POPCLS) and population class as determined by Satellite night lights (POPCSS)
# SURROUNDING_CLASS can be "rural", "suburban", "urban", "rural and suburban", or "suburban and urban", "rural and urban"
SURROUNDING_CLASS = "rural"

# Include a range of countries, use an array of strings of each Country Name
# ['China', 'United States ("of America" in v3)', 'Artic', 'Ireland']
IN_COUNTRY = False 

