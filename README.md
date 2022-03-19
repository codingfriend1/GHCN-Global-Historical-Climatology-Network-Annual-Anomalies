# GHCNm
This work is designed to produce annual temperature anomalies for all land based temperatures from the Global Historical Climatology Network using either an average of all individual station anomalies or an average of gridded station anomalies. The process is highly customizable through settings in `constants.py`. It works with both version 3 (v3) and version 4 (v4), adjusted and unadjusted datasets.

No adjustments or algorithms are run on the data. The Developer may choose to accept or reject flagged data and enable or disable gridding, but the original data is never corrected.

## Author
- Author: Jon Paul Miles
- Date Created: March 11, 2022

## License
MIT License

## How to run

- Install Python 3 if not already installed.
- Open a folder to this project in terminal.
- Install project dependencies by running this command  `pip3 install -r requirements.txt`.
- Set your variables/settings in `constants.py`
- Run the script: `python3 .` or replace `.` with whatever path leads to this project folder.

## Steps
These are the steps used to recreate the results.

1. If not already downloaded, the program downloads GHCN monthly station metadata, both adjusted and unadjusted TAVG temperature data, and country codes from the NOAA website (https://www1.ncdc.noaa.gov/pub/data/ghcn/) to the folder where the terminal command is run from. Setting `VERSION = 'v3'` will download version 3, `'v4'` will download version 4. `QUALITY_CONTROL_DATASET = "qcu"` sets which Quality Adjusted/Unadjusted dataset will be used. `"qca"` is used for version 3 adjusted data and `"qcf"` is used for version 4 adjusted data.

2. When extracting the data, missing values (`-9999`) are replaced with `NaN`. If the Developer enables `PURGE_FLAGS = True`, any estimated temperature readings or natural temperature readings with an associated Quality Control flag will be converted to NaN.

3. For each station, calculate a separate fixed baseline (average of reference years) for each month. Reference years are set in `constants.py` with `REFERENCE_START_YEAR = 1961` and `REFERENCE_RANGE = 30`. If the Developer wishes, they may demand that missing data be kept to a minimum when calculating the baseline by setting `ACCEPTABLE_AVAILABLE_DATA_PERCENT = 0.5` to a value between 1 and 0. If the value is 1, the station must have data for every year in the baseline for that month class or the baseline will become NaN resulting in no useable data from that station for that month class. If the Developer sets the value to 0, a baseline average will be calculated even if the station only has one available year in the range. A value between `0.3`-`0.7` is recommended that allows for a fair average to be formed.
  Before averaging the temperatures of all 12 months into a single average by year, we want to convert each month's temperatures into anomalies to minimize the impact of missing months. For instance if we have only ten months available and the two missing months are from the winter season, then averaging absolute temperatures would result in an average that's skewed warmer. However if we calculate anomalies for each month separately, then missing winter months would have less of an impact because we are only calculating the difference between January of this year to Januaries of other years and are averaging anomalies, not absolute temperatures.

4. For each month class (Jan to Jan, Feb to Feb, Mar to Mar), calculate anomalies from their respective fixed baselines.

5. For each year in the station's data, average all twelve monthly anomalies. Each annual average must have at least one monthly anomaly.

6. Divide the world into a grid of latitude and longitude quadrants (5°x5°) and associate each station with a grid quadrant based on the station's latitude and longitude.

7. Average the station anomalies within each grid quadrant by year. An average for a grid quadrant is calculated if it has at least one station.

8. Because the surface area of each grid quadrant decreases with latitude according to the cosine of latitude, we average all grid quadrant anomalies (that have a station) by year weighing each grid by the cosine of the mid-latitude for that grid (`grid_weight = np.cos( mid_latitude * (np.pi / 180 ) )`).

9. In a separate list, calculate the weight of each grid quadrant by multiplying the cosine weighting of each grid by the percent of land in each grid quadrant.

10. Create a global annual anomaly list by average all stations, a separate global annual anomaly list by averaging all grid quadrants, and a third global annual anomaly list by averaging all grid quadrants with alternative, land-based weighting.

11. Save the result to an Excel file. Because GHCNm v4 has over 27k stations, the individual station anomalies cannot be printed to the Excel file without resulting in a file too large to save. However, annual anomalies for each grid quadrant will be saved. If the Developer believes the resulting file will not be too large, setting `PRINT_STATION_ANOMALIES = True` will attempt to save the annual anomaly trends for each station to the Excel file instead of each grid quadrant. This may be useful when testing smaller number of stations.

12. While the Developer waits for the calculations to process, the console will display each station ID, start and end year for the station being processed, name and country, grid quadrant, anomaly and absolute temperature trends (slope) for each station. The absolute temperature trend is calculated from the absolute temperature data for each month class separately and all resulting slopes are averaged into one slope for the station. The trend will only use temperature data between the `ABSOLUTE_START_YEAR` and `ABSOLUTE_END_YEAR` and will require the same minimum amount of available data in this range based on the `ACCEPTABLE_AVAILABLE_DATA_PERCENT`. These trends do not factor into the Excel sheet, but statistics will be collected on each station's trends and a final average of all absolute temperature trends will be displayed in the console at the end of the process. 

13. Finally, the entire range of the annual data is set by `YEAR_RANGE_START = 1850` and ends with the current year. If the range specified is larger than each station's annual range, the monthly data for missing years will be filled with `NaN`. If you wish use a shorter range you may specify the end year with `YEAR_RANGE_END = ????`.

14. The resulting Excel file will be printed to the folder where the command/terminal command is run from.

## Plans

I hope to make a script that will compile daily GHCN data into a monthly file that can be run by this script with no adjustments or corrections applied.