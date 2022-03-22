'''
  Author: Jon Paul Miles
  Date Created: March 15, 2022

  Daily data README:
  https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
'''

from constants import *
import pandas as pd
import numpy as np
from termcolor import colored, cprint
import os

check_mark = colored(u'\u2713', 'green', attrs=['bold'])

# All GHCNd .dly station files have 31 days even if some days are missing
DAYS_IN_MONTH = 31

def has_passing_flags(MFLAG, QFLAG, SFLAG):

  return True

def average_tmax_and_tmin(TMAX_AND_TMIN):

  tavg = math.nan if len(TMAX_AND_TMIN) != 2 or TMAX_AND_TMIN.isnull().any() else int(normal_round(TMAX_AND_TMIN.mean()))

  return tavg

def parse_daily_row(unparsed_row):

  parsed_row = []

  ELEMENT = str(unparsed_row[17:21])

  if not ELEMENT == "TMAX" and not ELEMENT == "TMIN":
    return False

  try:

    STATION_ID = str(unparsed_row[0:11]).strip()
    YEAR = int(unparsed_row[11:15])
    MONTH = int(unparsed_row[15:17])

    parsed_row.append(STATION_ID)
    parsed_row.append(YEAR)
    parsed_row.append(MONTH)
    parsed_row.append(ELEMENT)

    DAYS_IN_MONTH = 31
    FIRST_DAY_INDEX = 21
    CHARACTERS_NEEDED_FOR_READING_AND_FLAGS = 8

    FULL_RANGE = (DAYS_IN_MONTH * CHARACTERS_NEEDED_FOR_READING_AND_FLAGS) + FIRST_DAY_INDEX

    for index in range(FIRST_DAY_INDEX, FULL_RANGE, CHARACTERS_NEEDED_FOR_READING_AND_FLAGS):

      # Temperature comes in tenths of degrees C
      temperature_reading = int(unparsed_row[index:index + 5])

      '''
        https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
        MFLAG1     is the measurement flag for the first day of the month.  There are
                   ten possible values:

                   Blank = no measurement information applicable
                   B     = precipitation total formed from two 12-hour totals
                   D     = precipitation total formed from four six-hour totals
             H     = represents highest or lowest hourly temperature (TMAX or TMIN) 
                     or the average of hourly values (TAVG)
             K     = converted from knots 
             L     = temperature appears to be lagged with respect to reported
                     hour of observation 
                   O     = converted from oktas 
             P     = identified as "missing presumed zero" in DSI 3200 and 3206
                   T     = trace of precipitation, snowfall, or snow depth
             W     = converted from 16-point WBAN code (for wind direction)
        
      '''
      MFLAG = str(unparsed_row[index+5:index+6])

      '''
        https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
        QFLAG1     is the quality flag for the first day of the month.  There are 
                   fourteen possible values:

                   Blank = did not fail any quality assurance check
                   D     = failed duplicate check
                   G     = failed gap check
                   I     = failed internal consistency check
                   K     = failed streak/frequent-value check
             L     = failed check on length of multiday period 
                   M     = failed megaconsistency check
                   N     = failed naught check
                   O     = failed climatological outlier check
                   R     = failed lagged range check
                   S     = failed spatial consistency check
                   T     = failed temporal consistency check
                   W     = temperature too warm for snow
                   X     = failed bounds check
             Z     = flagged as a result of an official Datzilla 
                     investigation
      '''
      QFLAG = str(unparsed_row[index+6:index+7])

      '''
        https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
        SFLAG1     is the source flag for the first day of the month.  There are 
                   thirty possible values (including blank, upper and 
             lower case letters):

                   Blank = No source (i.e., data value missing)
                   0     = U.S. Cooperative Summary of the Day (NCDC DSI-3200)
                   6     = CDMP Cooperative Summary of the Day (NCDC DSI-3206)
                   7     = U.S. Cooperative Summary of the Day -- Transmitted 
                     via WxCoder3 (NCDC DSI-3207)
                   A     = U.S. Automated Surface Observing System (ASOS) 
                           real-time data (since January 1, 2006)
             a     = Australian data from the Australian Bureau of Meteorology
                   B     = U.S. ASOS data for October 2000-December 2005 (NCDC 
                           DSI-3211)
             b     = Belarus update
             C     = Environment Canada
             D     = Short time delay US National Weather Service CF6 daily 
                     summaries provided by the High Plains Regional Climate
               Center
             E     = European Climate Assessment and Dataset (Klein Tank 
                     et al., 2002)     
                   F     = U.S. Fort data 
                   G     = Official Global Climate Observing System (GCOS) or 
                           other government-supplied data
                   H     = High Plains Regional Climate Center real-time data
                   I     = International collection (non U.S. data received through
                     personal contacts)
                   K     = U.S. Cooperative Summary of the Day data digitized from
                     paper observer forms (from 2011 to present)
                   M     = Monthly METAR Extract (additional ASOS data)
             m     = Data from the Mexican National Water Commission (Comision
                     National del Agua -- CONAGUA)
             N     = Community Collaborative Rain, Hail,and Snow (CoCoRaHS)
             Q     = Data from several African countries that had been 
                     "quarantined", that is, withheld from public release
               until permission was granted from the respective 
                     meteorological services
                   R     = NCEI Reference Network Database (Climate Reference Network
                     and Regional Climate Reference Network)
             r     = All-Russian Research Institute of Hydrometeorological 
                     Information-World Data Center
                   S     = Global Summary of the Day (NCDC DSI-9618)
                           NOTE: "S" values are derived from hourly synoptic reports
                           exchanged on the Global Telecommunications System (GTS).
                           Daily values derived in this fashion may differ significantly
                           from "true" daily data, particularly for precipitation
                           (i.e., use with caution).
             s     = China Meteorological Administration/National Meteorological Information Center/
                     Climatic Data Center (http://cdc.cma.gov.cn)
                   T     = SNOwpack TELemtry (SNOTEL) data obtained from the U.S. 
                     Department of Agriculture's Natural Resources Conservation Service
             U     = Remote Automatic Weather Station (RAWS) data obtained
                     from the Western Regional Climate Center    
             u     = Ukraine update    
             W     = WBAN/ASOS Summary of the Day from NCDC's Integrated 
                     Surface Data (ISD).  
                   X     = U.S. First-Order Summary of the Day (NCDC DSI-3210)
             Z     = Datzilla official additions or replacements 
             z     = Uzbekistan update
             
             When data are available for the same time from more than one source,
             the highest priority source is chosen according to the following
             priority order (from highest to lowest):
             Z,R,D,0,6,C,X,W,K,7,F,B,M,m,r,E,z,u,b,s,a,G,Q,I,A,N,T,U,H,S
      '''
      SFLAG = str(unparsed_row[index+7:index+8])

      corrected_temperature = math.nan if temperature_reading == -9999 or not has_passing_flags(MFLAG, QFLAG, SFLAG) else int(temperature_reading)

      parsed_row.append(corrected_temperature)

    return parsed_row

  except:

    print(f"\nCould not parse row:")
    print(unparsed_row)
    print()

    return False

def gather_daily_station_files(FOLDER_WITH_DAILY_DATA):

  # Find all station data files in folder
  daily_station_files = []

  all_stations = os.listdir(FOLDER_WITH_DAILY_DATA)

  # Create an array of all our .dly station file URLs
  for station_file_url in all_stations:
    if 'dly' in station_file_url:
      daily_station_files.append(os.path.join(FOLDER_WITH_DAILY_DATA, station_file_url))

  return daily_station_files

def compile_daily_data(DAILY_VERSION, FOLDER_WITH_DAILY_DATA):

  # Prepare our mega file to save all combined station temperatures too
  OUTPUT_FILE_URL = f"./ghcnd.tavg.{DAILY_VERSION}.all.dat"

  if os.path.exists(OUTPUT_FILE_URL):
    
    os.remove(OUTPUT_FILE_URL)

  print(f"\nCompiling daily data into a GHCNm-like monthly TAVG file to be named '{OUTPUT_FILE_URL}'\n")

  # Prepare the file for editing
  OUTPUT_CONTENT = open(OUTPUT_FILE_URL, 'a')

  daily_station_files = gather_daily_station_files(FOLDER_WITH_DAILY_DATA)

  total_stations = len(daily_station_files)

  station_iterator = 0

  # For each daily station file
  for station_file_url in daily_station_files:

    station_iterator += 1

    print(f"Composing station {station_iterator} of {total_stations}")

    # Read the station file. We will manually parse each line instead of relying on colspecs to improve performance
    station_daily_values = pd.read_csv(station_file_url, header=None)

    # Prepare our columns
    columns = [ 'station_id', 'year', 'month', 'element' ]

    for day in range(DAYS_IN_MONTH):

      columns.append('value' + str(day + 1))

    # Prepare to combine all parsed lines into one array
    parsed_lines = []

    # Manually parse each line of the station data
    for file_row in station_daily_values.values:

      parsed_row = parse_daily_row(file_row[0])

      if parsed_row:

        parsed_lines.append(parsed_row)

    # Convert the parsed file rows into a dataframe
    station_temperature_data = pd.DataFrame(parsed_lines, columns=columns)

    # Average daily values for Each (Year, Month, Element) combo
    # We multiply each temperature by 10 to keep it consistent with GHCNm
    station_temperature_data['average'] = station_temperature_data.iloc[:,3:].mean(
      axis=1, 
      skipna=True, 
      level=None, 
      numeric_only=True
    ).apply(lambda d : d if math.isnan(d) else int(normal_round(d * 10))).astype('Int64')

    # Since we now have the averages of all days, we no longer need the daily values, so drop them
    station_temperature_data.drop(station_temperature_data.columns[3:34], axis=1, inplace=True)

    # Transform vertical month columns to horizontal row columns on the year and average TMAX and TMIN averages to combine them
    station_temperature_data = station_temperature_data.pivot_table(
      index=["station_id", "year"], 
      columns='month', 
      values='average', 
      fill_value=math.nan, 
      aggfunc=average_tmax_and_tmin, 
      dropna=False
    ).astype('Int64').reset_index()

    # If the file has 12 columns, one for each month
    if len(station_temperature_data.columns) == 14 and len(station_temperature_data.values) > 1:

      # For each row in the station's data
      for year, row in station_temperature_data.iterrows():

        # Create a representative string line to save in the output file
        output_row_string = f"\n{row['station_id']}{row['year']}TAVG"

        for month in range(1, 13):

          month_string = str(row[month]).replace('<NA>', '-9999').rjust(5, " ")
          output_row_string = output_row_string + f"{month_string}   "

        # Add the representative line to the output file
        OUTPUT_CONTENT.write(output_row_string)

  print(f"\n{check_mark} Daily station data compiled into '{OUTPUT_FILE_URL}'\n")

  return OUTPUT_FILE_URL
