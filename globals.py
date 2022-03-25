
'''
  Author: Jon Paul Miles
  Date Created: March 24, 2022
'''

import datetime
import math
from constants import *


'''
  Global Constants
'''

# Retrieve the year as of now
TODAY = datetime.date.today()

# This year (YYYY)
YEAR_AS_OF_TODAY = int(TODAY.strftime("%Y"))

# The last year to consider
YEAR_RANGE_END = YEAR_AS_OF_TODAY + 1

SURROUNDING_CLASS = SURROUNDING_CLASS.lower()

MISSING_VALUE = -9999

YEAR_RANGE = range(YEAR_RANGE_START, YEAR_RANGE_END)

YEAR_RANGE_LIST = list(YEAR_RANGE)

RANGE_OF_REFERENCE_YEARS = range(REFERENCE_START_YEAR, REFERENCE_START_YEAR + REFERENCE_RANGE)

RANGE_OF_REFERENCE_YEARS_LIST = list(YEAR_RANGE)

month_columns = [str(month) for month in range(1,13)]

REFERENCE_END_YEAR = REFERENCE_START_YEAR + REFERENCE_RANGE - 1

'''
  Global Methods
'''
def normal_round(num, decimals=0):

  if math.isnan(num):
    return num

  multiplier = 10 ** decimals

  value = math.floor(num*multiplier + 0.5) / multiplier

  if decimals == 0:
    value = int(value)

  return value


  '''
  2.2.1 DATA FORMAT

    Variable          Columns      Type
    --------          -------      ----

    ID                 1-11        Integer
    YEAR              12-15        Integer
    ELEMENT           16-19        Character
    VALUE1            20-24        Integer
    DMFLAG1           25-25        Character
    QCFLAG1           26-26        Character
    DSFLAG1           27-27        Character
      .                 .             .
      .                 .             .
      .                 .             .
    VALUE12          108-112       Integer
    DMFLAG12         113-113       Character
    QCFLAG12         114-114       Character
    DSFLAG12         115-115       Character

    Variable Definitions:

    ID: Station identification code. First two characters are FIPS country code

    YEAR: 4 digit year of the station record.

    ELEMENT: element type, monthly mean temperature="TAVG"

  When splitting the unparsed row string, we start each snippet of data one character index early since the first character is inclusive in programming languages, but they may end with the same character index because the final character is not inclusive
  '''

# Generates absolute column indexes for station data for the 12 months of data
def generate_month_boundaries(month_boundaries = [5,6,7,8], start_index_for_jan = 19):

  absolute_month_boundaries = []

  for month in range(0, 12):

    start_index = start_index_for_jan + (month * month_boundaries[-1])

    month_grouping = []

    for mon_grouping_col in range(len(month_boundaries)):

      start_bound = (start_index + month_boundaries[mon_grouping_col - 1]) if mon_grouping_col > 0 else start_index

      end_bound = (start_index + month_boundaries[mon_grouping_col])

      absolute_month_boundaries.append((start_bound, end_bound))

  return absolute_month_boundaries

  