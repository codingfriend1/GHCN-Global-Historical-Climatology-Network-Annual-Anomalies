# GHCNm
This work is designed to produce a single annual temperature anomaly trend for the Global Historical Climatology Network using either an average of all individual station anomalies or an average of gridded station anomalies. The process is highly customizable through settings in `constants.py`. It works both with version 3 (v3) and version 4 (v4), adjusted or unadjusted datasets.

No adjustments or algorithms are run on the data. The Developer may choose to accept or reject flagged data and enable or disable gridding, but the original data is never corrected.

## Author
- Author: Jon Paul Miles
- Date Created: March 11, 2022

## License
MIT License

## Steps
These are the steps used to recreate the results.

1. Download GHCN Monthly Data T-Averages from https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcu.tar.gz to the folder the terminal command is run from using the `fetch_qc[a|u|f]_v[3|4]` scripts provided. Missing values (-9999) are replaced with NaN. If the Developer enables `PURGE_FLAGS = True`, any temperature reading that has an associated Quality Control flag or is an Estimated value, will be converted to NaN. Make sure the `DIRECTORY`, `FOLDER`, `STATION_FILE_NAME`, `DATA_FILE_NAME`, `VERSION` and `COUNTRIES_FILE_NAME` are set appropriately so the program can find the correct data.
2. For each station, calculate a separate fixed baseline (average of reference years) for each month. Reference years are set in `constants.py` with `REFERENCE_START_YEAR = 1961` and `REFERENCE_RANGE = 30`. If the Developer wishes, they may demand that missing data be kept to a minimum when calculating the baseline by setting `ACCEPTABLE_AVAILABLE_DATA_PERCENT` to a value between 1 and 0. If the value is 1, the station must have data for every year in the baseline for that month class or the baseline will become NaN resulting in no useable data from that station for that month class. If the Developer sets the value to 0, a baseline average will be calculated even if the station only has one available year in the range. A value between 0.3-0.7 is recommended that allows for a fair average to be formed.

  Before averaging the temperatures of all 12 months into a single average by year, we want to convert each month's temperatures into anomalies to minimize the impact of missing months. For instance if we have only ten months available and the two missing months are from the winter season, then averaging absolute temperatures would result in an average that's skewed warmer. However if we calculate anomalies for each month separately, then missing winter months would have less of an impact because we are only calculating the difference between January of this year to Januaries of other years and are averaging anomalies, not absolute temperatures.

3. For each month class (Jan to Jan, Feb to Feb, Mar to Mar), calculate anomalies from their respective fixed baselines.
4. For each year in the station's data, average all twelve monthly anomalies for that year into a single value. Up to eleven missing months are allowed since we are averaging anomalies.
5. Divide the world into a grid of latitude and longitude values and associate each station with a grid quadrant based on the station's latitude and longitude.
6. If the Developer chooses to use gridding (`USE_GRIDDING = True`), group stations by grid quadrant and average the grid quadrant anomalies by year. An average for the grid quadrant is calculated if it has one or greater number of stations.
7. The surface area of each grid quadrant decreases with latitude according to the cosine of latitude, so if the Developer is using gridding, we average all grid quadrant anomalies (that have a station) by year weighing each grid by the cosine of the mid-latitude for that grid.
8. If the Developer wishes to weigh each grid quadrant by it's land / water ratio (`INCLUDE_LAND_RATIO_IN_WEIGHT = True`) to get a strict land temperature, the cosine of latitude weighing will be multiplied by the percent of land making up that grid quadrant.
9. If the Developer ignores gridding, all stations will be averaged by year into an average by year for all stations.
10. The final average of either the grid quadrants or stations will be saved to an Excel file. Because GHCNm v4 has over 27k stations, the individual station anomalies cannot be printed to the Excel file without the resulting file being too big to save. However, if the Developer enables gridding, the anomalies for each grid quadrant are included in the file. If the Developer believes the resulting file will not be too big, setting `PRINT_STATION_ANOMALIES = True` will attempt to save the annual anomaly trends for each station to the Excel file when not gridding.
11. While the Developer waits for the calculations to process, the console will display each station ID, start and end year for that station, name and country, grid quadrant, anomaly and absolute temperature trends (slope) for each station. The absolute temperature trend is calculated from the absolute temperature data for each month class separately and all resulting trends are averaged into one trend for the station. The trend will only use temperature data between the `ABSOLUTE_START_YEAR` and `ABSOLUTE_END_YEAR` and will require the same minimum amount of available data in this range based on the `ACCEPTABLE_AVAILABLE_DATA_PERCENT`. These trends do not factor into the Excel sheet, but statistics will be collected on each station's trends and a final average of all absolute temperature trends will be displayed in the console at the end of the process. 
12. Finally, the entire range of the annual data is set by `YEAR_RANGE_START = 1850` and ends with the current year. However, if you wish use a shorter range you may specify the end year with `YEAR_RANGE_END = ????`.
13. The resulting Excel file will be printed to the folder where the command/terminal command is run from.

## Plans

I hope to make a script that will compile daily GHCN data into a monthly file that can be run by this script with no adjustments or corrections applied.