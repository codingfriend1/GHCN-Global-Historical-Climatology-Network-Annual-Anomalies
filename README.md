# GHCN
This work is designed to produce annual temperature anomalies for all land based temperatures from the Global Historical Climatology Network using either an average of all individual station anomalies or an average of gridded station anomalies. The process is highly customizable through settings in `constants.py`. 

Works with:
  - Version 3 (v3)
  - Version 4 (v4)
  - Daily Station data (daily)

No adjustments or algorithms are run on the data, unless you choose to remove flagged data.

## Author
- Author: Jon Paul Miles
- Date Created: March 11, 2022

## Diclaimer
I am not a scientist. I'm an experienced web developer with an interest in researching the truth about global warming as a hobby, but I hope the transparency of my process will show that my methods are reliable and offer a competent understanding of the raw, unadjusted data.

## License
MIT License - You are welcome to use and modify your copy of this code. If I have referenced anyone else's code in the comments, please retain the credit given for their work.

## How to run

- Install Python 3 if not already installed on your system (https://docs.python-guide.org/starting/install3/osx/).
- Open a folder to this project in terminal.
- Install project dependencies by running this command  `pip3 install -r requirements.txt`.
- Set your variables/settings in `constants.py`
- Run the program: `python3 .` or replace `.` with whatever path leads to this project folder.

## Settings

Settings may be adjusted in `constants.py` before running the program:

 - `VERSION` (`'v3'`, `'v4'`, `'daily'`) - What version of GHCN to use

 - `QUALITY_CONTROL_DATASET` (`'qcu`, `'qca'`, `'qcf'`) - What quality adjusted dataset to use. The unadjusted data for both `v3` and `v4` is `'qcu'`. The adjusted dataset for version 3 is `'qca'`, for version 4 it's (`'qcf'`). This field is irrevelant for `'daily'` data.

 - `YEAR_RANGE_START` (Ex: `1851`) - The earliest year you want to consider in the data.

 - `REFERENCE_START_YEAR` (Ex: `1961`) - Anomalies need a baseline average to compare themselves to. This sets the start year for the baseline range.

 - `REFERENCE_RANGE` (Ex: `30`) - Sets the number of years the baseline range should cover starting at the `REFERENCE_START_YEAR`.

 - `PURGE_FLAGS` (Boolean) - If `True`, before processing, estimated data (`DMFLAG = 'E'`) or data with a presented quality control flag (`QCFLAG`) will be rejected as `NaN`. This has no effect on GHCN daily, but you may customize its effect in `daily.py` in the method `has_passing_flags(MFLAG, QFLAG, SFLAG)`.

 - `ACCEPTABLE_AVAILABLE_DATA_PERCENT` (Ex: `0.5`) - You may demand that missing data be kept to a minimum when calculating the baseline by setting `ACCEPTABLE_AVAILABLE_DATA_PERCENT = 0.5` to a value between 1 and 0. If the value is 1, the station must have data for every year in the baseline for that month class or the baseline will become NaN resulting in no useable data from that station for that month class. If you set the value to 0, a baseline average will be calculated even if the station only has one available year in the range. A value between `0.3`-`0.7` is recommended that allows for a fair average to be formed. This is also used for setting the minimum number of required years when calculating the absolute temperature trends for each station for the console output.

 - `PRINT_STATION_ANOMALIES` (Boolean) - Because GHCNm v4 and GHCNd have over 27k stations, the individual station anomalies cannot be printed to the Excel file without resulting in a file too large to save. However, annual anomalies for each grid quadrant will be saved. If you believe the resulting file will not be too large, setting `PRINT_STATION_ANOMALIES = True` will attempt to save the annual anomalies for each station to the Excel file instead of each grid quadrant. This may be useful when testing smaller number of stations.

 - `ABSOLUTE_START_YEAR` (Ex: `1880`) - The range starting year to consider when calculating each station's absolute temperature trends for console output. This does not effect excel results.

 - `ABSOLUTE_END_YEAR` (Ex: `2000`) - The range ending year to consider when calculating each station's absolute temperature trends.

 - `MONTHS_REQUIRED_EACH_YEAR` (Ex: `12`) -  How many months does each year of data need to be included in the calculation.

 - `SURROUNDING_CLASS` (`"rural"`, `"suburban"`, `"urban"`, `"rural and suburban"`, or `"suburban and urban"`) - For version 3 of GHCNm only, this limits the stations used in the calculations to those marked with a particular surrounding environment according to the population class (`POPCLS`) and population class as determined by Satellite night lights (`POPCSS`). When both POPCLS and POPCSS are rural, a station is marked as rural. When both POPCLS and POPCSS are urban, a station is marked as urban. Suburban includes everything in-between.

 - `ONLY_USHCN` (Boolean) - Limit the stations in GHCN v3 to the 1,218 stations (as of Mar 21, 2022) from the U.S. Historical Climatology Network (USHCN) network before making the calculations. This only works with `v3`.

 - `USE_COUNTRY` (Ex: `'China'`, `'United States of America'`, `'Ireland'`, `'Artic'`, etc...) - Limit the stations in GHCN v3 to stations from one specific country. This only works with `v3`.

 - `IN_COUNTRY` (Ex: `['China', 'United States of America', 'Ireland', 'Artic']`) - Limit the stations in GHCN v3 to stations from a range of countries. Should be provided as an array. This only works with `v3`.

## Steps

These are the steps used to recreate the results:

1. If not already downloaded, download GHCN station metadata, both adjusted and unadjusted TAVG temperature data, and country codes from the NOAA website to the folder where the terminal command is run from. If using GHCNd, compile the daily data into a GHCNm-like file and then use that as the TAVG temperature data.

2. When extracting the data, missing (`-9999`) and purged values (`PURGE_FLAGS = True`) are replaced with `NaN`.

3. For each station, calculate a separate fixed baseline (average of reference years) for each month. Before averaging the temperatures of all 12 months into a single average by year, we want to convert each month's temperatures into anomalies to minimize the impact of missing months. For instance if we have only ten months available and the two missing months are from the winter season, then averaging absolute temperatures would result in an average that's skewed warmer. However if we calculate anomalies for each month separately, then missing winter months would have less of an impact because we are only calculating the difference between January of this year to Januaries of other years and are averaging anomalies, not absolute temperatures.

4. For each month class (Jan to Jan, Feb to Feb, Mar to Mar), calculate anomalies from their respective fixed baselines.

5. For each year in the station's data, average all available monthly anomalies for that year.

6. Divide the world into a grid of latitude and longitude quadrants (5°x5°) and associate each station with a grid quadrant based on the station's latitude and longitude.

7. Average the station anomalies within each grid quadrant by year. An average for a grid quadrant is calculated if it has at least one station.

8. Because the surface area of each grid quadrant decreases with latitude according to the cosine of latitude, we average all grid quadrant anomalies (that have a station) by year weighing each grid by the cosine of the mid-latitude for that grid (`grid_weight = np.cos( mid_latitude * (np.pi / 180 ) )`).

9. In a separate list, repeat step 8, but calculate the weight of each grid quadrant by multiplying the cosine weighting of each grid by the percent of land in each grid quadrant.
  
10. Create a global annual anomaly list by average all stations, a separate global annual anomaly list by averaging all grid quadrants, and a third global annual anomaly list by averaging all grid quadrants with alternative, land-based weighting. Since data from GHCN comes in 100ths of a degree, also create equivalent lists for each of these with data divided by 100.

11. Save the result to an Excel file in the folder where the console/terminal command was run from.

12. While the Developer waits for the calculations to process, the console will display each station ID, start and end year for the station being processed, name and country, grid quadrant, anomaly and absolute temperature trends (slope) for each station. The absolute temperature trend is calculated from the absolute temperature data for each month class separately and all resulting slopes are averaged into one slope for the station. The trend will only use temperature data between the `ABSOLUTE_START_YEAR` and `ABSOLUTE_END_YEAR` and will require the same minimum amount of available data in this range based on the `ACCEPTABLE_AVAILABLE_DATA_PERCENT`. These trends do not factor into the Excel sheet, but statistics will be collected on each station's trends and a final average of all absolute temperature trends will be displayed in the console at the end of the process.
