import datetime
import math

VERSION = 'v4' #v3

DIRECTORY = r'~/Downloads/ghcnm/v4'

# The unzipped folder to look for all files
FOLDER = 'ghcnm.v4.0.1.20220308'
# FOLDER = 'ghcnm.v3.3.0.20190821'

# The name of the GHCN-M associated Station Data (ghcnm.element.v4.#.#.YYYYMMDD.version.inv)
# STATION_FILE_NAME = "ghcnm.tavg.v3.3.0.20190821.qcu.inv"
# STATION_FILE_NAME = "ghcnm.tavg.v3.3.0.20190821.qca.inv"
STATION_FILE_NAME = "ghcnm.tavg.v4.0.1.20220308.qcu.inv"
# STATION_FILE_NAME = "ghcnm.tavg.v4.0.1.20220311.qcf.inv"

# The name of the main GHCN-M data file (ghcnm.element.v4.#.#.YYYYMMDD.version.dat)
# DATA_FILE_NAME = "ghcnm.tavg.v3.3.0.20190821.qcu.dat"
# DATA_FILE_NAME = "ghcnm.tavg.v3.3.0.20190821.qca.dat"
# DATA_FILE_NAME = "ghcnm.tavg.v4.0.1.20220308.qcu.dat"
# DATA_FILE_NAME = "ghcnm.tavg.v4.0.1.20220311.qcf.dat"
DATA_FILE_NAME = "test.dat"

# GHCN-M v4 Associated Country Code to Country Name file
# COUNTRIES_FILE_NAME = "country-codes"
COUNTRIES_FILE_NAME = "ghcnm-countries.txt"

# Earliest year you want to consider in the data
YEAR_RANGE_START = 1850

# Leave blank if you wish to use a rolling average
REFERENCE_START_YEAR = 1961

# Number of years to consider in the reference average
REFERENCE_RANGE = 30

# Whether to purge all readings with Quality Control, Data Measurement, or Data Source flags
PURGE_FLAGS = False

# The acceptable amount of data available (subtracting missing data) before an anomaly calculation can be made (in decimal form)
ACCEPTABLE_AVAILABLE_DATA_PERCENT = 0.5

# Do you wish to assign each station to a 5x5 Latitude / Longitude grid and average the grid boxes weighted by the cosine of the mid-latitude point for that grid?
USE_GRIDDING = True

# Do you also wish to include land to water ratios in the calculation of the weight of each grid box? To get a purely land based result?
INCLUDE_LAND_RATIO_IN_WEIGHT = False

# Whether to create a column in our final excel sheet by station for its anomalies. With the larger number of stations in the GHCNm v4, this will cause the program to crash at the end since 27,000 columns it too large for an excel file. But it is useful for testing purposes and smaller station amount.
PRINT_STATION_ANOMALIES = False


# The range to consider when calculating trends for console output, does not effect excel results
ABSOLUTE_START_YEAR = 1900 # Inclusive
ABSOLUTE_END_YEAR = 2000 # Non-inclusive

# 
# Calculated values
# 

# Retrieve the year as of now
TODAY = datetime.date.today()

# This year (YYYY)
YEAR_AS_OF_TODAY = int(TODAY.strftime("%Y"))

# The last year to consider
YEAR_RANGE_END = YEAR_AS_OF_TODAY + 1


# Methods
def normal_round(num, decimals=0):

  if math.isnan(num):
    return num

  multiplier = 10 ** decimals

  value = math.floor(num*multiplier + 0.5) / multiplier

  if decimals == 0:
    value = int(value)

  return value

print("\n")
print("Settings")
print("========")
print(f"Temperatures file: {DATA_FILE_NAME}")
print(f"Stations file: {STATION_FILE_NAME}")
print(f"Anomaly reference average range: {REFERENCE_START_YEAR}-{REFERENCE_START_YEAR + REFERENCE_RANGE - 1}")
print(f"Percent of data necessary for reliable reference average: {normal_round(ACCEPTABLE_AVAILABLE_DATA_PERCENT * 100)}%")
print(f"Trend range: {ABSOLUTE_START_YEAR}-{ABSOLUTE_END_YEAR-1}")
print(f"Purging flagged data: {PURGE_FLAGS}")
print(f"Use Gridding: {USE_GRIDDING}")
print(f"Include land / water ratio in Grid Weight: {INCLUDE_LAND_RATIO_IN_WEIGHT}")
print("\n")

print(f"Please wait a few seconds...")
print(f"\n")
