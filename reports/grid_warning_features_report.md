# Grid Warning Features Report

## 1. Summary

- grid_input_rows: 307148
- warning_rows: 31
- output_rows: 307148
- grid_count: 9908
- date_count: 31
- date_min: 2025-03-01 00:00:00
- date_max: 2025-03-31 00:00:00

## 2. Warning Feature Sum

| feature                    |     sum |
|:---------------------------|--------:|
| dry_warning_flag           |       0 |
| strong_wind_warning_flag   |       0 |
| dry_and_windy_warning_flag |       0 |
| dry_warning_count          |       0 |
| strong_wind_warning_count  |       0 |
| dry_warning_level_max      |       0 |
| strong_wind_level_max      |       0 |
| warning_event_count        | 1198868 |

## 3. Date Warning Coverage

| date                |   rows |   dry_warning_rows |   strong_wind_warning_rows |   dry_and_windy_warning_rows |
|:--------------------|-------:|-------------------:|---------------------------:|-----------------------------:|
| 2025-03-01 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-02 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-03 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-04 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-05 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-06 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-07 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-08 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-09 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-10 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-11 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-12 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-13 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-14 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-15 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-16 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-17 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-18 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-19 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-20 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-21 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-22 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-23 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-24 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-25 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-26 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-27 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-28 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-29 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-30 00:00:00 |   9908 |                  0 |                          0 |                            0 |
| 2025-03-31 00:00:00 |   9908 |                  0 |                          0 |                            0 |

## 4. Output Columns

- grid_id
- grid_ix
- grid_iy
- pole_count
- pole_density
- center_lon
- center_lat
- x_center
- y_center
- nearest_any_station_id
- nearest_any_station_name
- nearest_any_station_source
- nearest_any_station_lon
- nearest_any_station_lat
- nearest_any_distance_m
- nearest_aws_station_id
- nearest_aws_station_name
- nearest_aws_station_source
- nearest_aws_station_lon
- nearest_aws_station_lat
- nearest_aws_distance_m
- nearest_asos_station_id
- nearest_asos_station_name
- nearest_asos_station_source
- nearest_asos_station_lon
- nearest_asos_station_lat
- nearest_asos_distance_m
- date
- aws_temp_mean
- aws_temp_max
- aws_temp_min
- aws_humidity_mean
- aws_humidity_min
- aws_rain_sum
- aws_wind_mean
- aws_wind_max
- aws_wind_dir_mean
- aws_pressure_mean
- aws_row_count
- aws_temp_obs_count
- aws_humidity_obs_count
- aws_wind_obs_count
- aws_rain_obs_count
- asos_temp_mean
- asos_temp_max
- asos_temp_min
- asos_humidity_mean
- asos_humidity_min
- asos_rain_sum
- asos_wind_mean
- asos_wind_max
- asos_wind_dir_mean
- asos_pressure_mean
- asos_row_count
- asos_temp_obs_count
- asos_humidity_obs_count
- asos_wind_obs_count
- asos_rain_obs_count
- has_aws_weather
- has_asos_weather
- primary_weather_source
- primary_temp_mean
- primary_temp_max
- primary_temp_min
- primary_humidity_mean
- primary_humidity_min
- primary_rain_sum
- primary_wind_mean
- primary_wind_max
- primary_wind_dir_mean
- primary_pressure_mean
- primary_station_distance_m
- primary_station_distance_km
- primary_humidity_deficit
- rain_sum_3d
- rain_sum_7d
- wind_max_3d
- wind_max_7d
- humidity_min_3d
- humidity_min_7d
- temp_max_3d
- temp_max_7d
- no_rain_days
- dry_warning_flag
- strong_wind_warning_flag
- dry_and_windy_warning_flag
- dry_warning_count
- strong_wind_warning_count
- dry_warning_level_max
- strong_wind_level_max
- warning_event_count
- dryness_warning_interaction
- wind_warning_interaction
- warning_risk_boost
