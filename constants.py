import datetime
import math

DIRECTORY = r'~/Downloads/ghcnm'

# The unzipped folder to look for all files
FOLDER = 'ghcnm.v4.0.1.20220308'

# The name of the GHCN-M associated Station Data (ghcnm.element.v4.#.#.YYYYMMDD.version.inv)
STATION_FILE_NAME = "ghcnm.tavg.v4.0.1.20220308.qcu.inv"

# The name of the main GHCN-M data file (ghcnm.element.v4.#.#.YYYYMMDD.version.dat)
# DATA_FILE_NAME = "ghcnm.tavg.v4.0.1.20220308.qcu.dat"

DATA_FILE_NAME = "test.dat"

# GHCN-M v4 Associated Country Code to Country Name file
COUNTRIES_FILE_NAME = "ghcnm-countries.txt"

# Earliest year you want to consider in the data
YEAR_RANGE_START = 1850

# Leave blank if you wish to use a rolling average
REFERENCE_START_YEAR = 1951

# Number of years to consider in the reference average
REFERENCE_RANGE = 30

# Whether to purge all readings with Quality Control, Data Measurement, or Data Source flags
PURGE_FLAGS = False

# The acceptable amount of data available (subtracting missing data) before an anomaly calculation can be made (in decimal form)
ACCEPTABLE_AVAILABLE_DATA_PERCENT = 0.7

# 
# The range to consider when calculating trends for console output
# 
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
print("\n")

print(f"Please wait a few seconds...")
print(f"\n")
