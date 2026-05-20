# Grid Day Features Report

## 1. Input Summary

- grid_station_rows: 9908
- weather_daily_rows: 3124
- weather_station_count: 102
- weather_date_min: 2025-03-01 00:00:00
- weather_date_max: 2025-03-31 00:00:00

## 2. Output Summary

- output: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\features\grid_day_features_202503.parquet
- output_rows: 307148
- grid_count: 9908
- date_count: 31
- date_min: 2025-03-01 00:00:00
- date_max: 2025-03-31 00:00:00

## 3. Primary Weather Source

| primary_weather_source   |   rows |   grid_count |
|:-------------------------|-------:|-------------:|
| aws                      | 302100 |         9908 |
| asos                     |   5048 |          727 |

## 4. Date Coverage Sample

| date                |   rows |   grid_count |   aws_weather_rows |   asos_weather_rows |
|:--------------------|-------:|-------------:|-------------------:|--------------------:|
| 2025-03-01 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-02 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-03 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-04 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-05 00:00:00 |   9908 |         9908 |               9542 |                9908 |
| 2025-03-06 00:00:00 |   9908 |         9908 |               9542 |                9908 |
| 2025-03-07 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-08 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-09 00:00:00 |   9908 |         9908 |               9542 |                9908 |
| 2025-03-10 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-11 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-12 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-13 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-14 00:00:00 |   9908 |         9908 |               9908 |                9908 |
| 2025-03-15 00:00:00 |   9908 |         9908 |               9908 |                9908 |

## 5. Distance Summary

| index   |   primary_station_distance_m |   nearest_aws_distance_m |   nearest_asos_distance_m |
|:--------|-----------------------------:|-------------------------:|--------------------------:|
| count   |                  307148      |              307148      |               307148      |
| mean    |                    7031.9    |                6923.35   |                16110.2    |
| std     |                    4122.63   |                3848.97   |                 8056.42   |
| min     |                      20.1547 |                  20.1547 |                   82.7907 |
| 10%     |                    2427.2    |                2424.12   |                 5764.66   |
| 25%     |                    4104.58   |                4096.77   |                 9956.23   |
| 50%     |                    6403.92   |                6384.43   |                15623.1    |
| 75%     |                    9238.93   |                9184.22   |                21258.2    |
| 90%     |                   12215.4    |               12039.2    |                27540.6    |
| 95%     |                   13978.8    |               13650.7    |                30962.3    |
| 99%     |                   20826.9    |               19110.5    |                35551.4    |
| max     |                   38361.8    |               25087.7    |                38950.2    |

## 6. Feature Summary

| index   |   primary_temp_mean |   primary_humidity_min |   primary_rain_sum |   primary_wind_max |   rain_sum_7d |   wind_max_7d |   humidity_min_7d |   no_rain_days |
|:--------|--------------------:|-----------------------:|-------------------:|-------------------:|--------------:|--------------:|------------------:|---------------:|
| count   |        307148       |            307148      |       307148       |       307137       |   307148      |  307148       |       307148      |   307148       |
| mean    |             4.76267 |                35.3966 |            1.60494 |            4.4151  |       10.6721 |       6.03622 |           20.2415 |        3.63081 |
| std     |             5.01094 |                17.4103 |            4.3235  |            1.77349 |       14.7481 |       2.12073 |            8.166  |        3.59371 |
| min     |           -11.7292  |                 7      |            0       |            0.9     |        0      |       1.2     |            7      |        0       |
| 25%     |             1.08333 |                22      |            0       |            3.2     |        0      |       4.6     |           15      |        1       |
| 50%     |             3.85417 |                31      |            0       |            4.1     |        5      |       5.6     |           18      |        3       |
| 75%     |             8.49565 |                46      |            0       |            5.3     |       16.5    |       7       |           24      |        6       |
| max     |            20.2667  |                97      |           36       |           24.6     |       92      |      24.6     |           56      |       28       |

## 7. Output Columns

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
