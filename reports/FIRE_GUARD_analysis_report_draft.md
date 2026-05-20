# FIRE-GUARD 3.0 분석 보고서 초안

생성일: 2026-05-20 16:24:59

## 0. 한 줄 정의

FIRE-GUARD 3.0은 ASOS/AWS 관측자료, 건조·강풍 특보, 전력설비 위치 데이터를 결합하여 전력설비 주변 화재위험도를 산정하고, 고위험 설비의 예방점검 우선순위를 제시하는 2-Stage 기상·공간 융합 위험도 분석 시스템이다.

## 1. 핵심 산출물

- 전력설비 위치 정제 데이터
- 1km grid 기반 전력설비 밀도 분석
- AWS/ASOS 관측소와 grid 거리 매칭
- station-date 단위 일별 기상 feature
- grid-date 단위 기상·공간 feature
- rule-based grid risk score
- pole-level risk score
- top1/top3/top5/top10 제출 후보
- 최종 baseline 후보: top5
- 위험지도 HTML
- 고위험 grid/pole 우선순위 표

## 2. 방법론 요약

1. 전력설비 좌표를 정제하고 1km grid로 공간 집계했다.
2. 강원권 AWS/ASOS 관측소 102개를 추출하고, grid 중심점과 가장 가까운 관측소를 매칭했다.
3. 시간자료를 일 단위 기상 feature로 변환했다.
4. 건조도, 무강수 지속일, 강풍, 전력설비 밀도, 특보 여부를 결합해 grid risk score를 계산했다.
5. grid 위험도를 pole 단위로 확장하고, 상위 percentile 기반 제출 후보를 생성했다.
6. top5 후보를 1차 baseline submission으로 선택했다.



---

<!-- Source: poles_profile_report.md -->

# Poles Profile Report

## 1. Source

- ZIP: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\raw\contest\contest_data_1.zip
- CSV inside ZIP: hanjeon/gangwon_poles_4326.csv

## 2. Raw Data Profile

- rows_raw: 1387831
- columns: ['pole_id', 'lon', 'lat']
- missing_required_columns: []
- pole_id_missing: 0
- lon_missing_or_invalid: 0
- lat_missing_or_invalid: 0
- pole_id_duplicates: 0
- lon_min: 127.50888371330925
- lon_max: 129.36334879138315
- lat_min: 37.03725721266511
- lat_max: 38.2304451198568
- rough_korea_bbox_outliers: 0
- rough_gangwon_bbox_outliers_reference_only: 0

## 3. Clean Data Profile

- rows_clean: 1387831
- columns_clean: ['pole_id', 'lon', 'lat']
- lon_min_clean: 127.50888371330925
- lon_max_clean: 129.36334879138315
- lat_min_clean: 37.03725721266511
- lat_max_clean: 38.2304451198568

## 4. Output Files

- raw preview: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\interim\poles_raw_preview.csv
- clean parquet: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\interim\poles_clean.parquet

## 5. Notes

- 원본 좌표계는 파일명 기준 EPSG:4326으로 추정합니다.
- 거리, buffer, grid 계산 전에는 EPSG:5179 또는 EPSG:5186으로 변환해야 합니다.
- rough_gangwon_bbox_outliers_reference_only는 참고용이며, 실제 제거 기준으로 사용하지 않았습니다.



---

<!-- Source: grid_1km_profile_report.md -->

# Grid 1km Profile Report

## 1. Input

- input_file: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\interim\poles_clean.parquet
- input_rows: 1387831

## 2. Grid Settings

- source_crs: EPSG:4326
- analysis_crs: EPSG:5179
- grid_size_m: 1000

## 3. Output Summary

- poles_5179_rows: 1387831
- active_grid_count: 9908
- total_pole_count_in_grid: 1387831
- pole_count_min: 1
- pole_count_max: 1289
- pole_count_mean: 140.0717601937828
- pole_count_median: 105.0

## 4. Top 20 Dense Grids

|   grid_id |   pole_count |   pole_density |   center_lon |   center_lat |
|----------:|-------------:|---------------:|-------------:|-------------:|
| 1020_1986 |         1289 |           1289 |      127.733 |      37.8781 |
| 1020_1985 |         1276 |           1276 |      127.733 |      37.8691 |
| 1021_1986 |         1170 |           1170 |      127.744 |      37.8781 |
| 1116_1987 |         1121 |           1121 |      128.825 |      37.8799 |
| 1116_1988 |         1054 |           1054 |      128.825 |      37.8889 |
| 1019_1985 |         1025 |           1025 |      127.722 |      37.8691 |
| 1115_1984 |          932 |            932 |      128.813 |      37.853  |
| 1019_1984 |          924 |            924 |      127.722 |      37.8601 |
| 1122_1973 |          920 |            920 |      128.891 |      37.7529 |
| 1033_1965 |          906 |            906 |      127.88  |      37.6884 |
| 1021_1984 |          892 |            892 |      127.744 |      37.86   |
| 1123_1974 |          891 |            891 |      128.902 |      37.7618 |
| 1019_1986 |          887 |            887 |      127.722 |      37.8781 |
| 1034_1966 |          871 |            871 |      127.891 |      37.6974 |
| 1020_1984 |          867 |            867 |      127.733 |      37.8601 |
| 1124_1975 |          854 |            854 |      128.914 |      37.7707 |
| 1022_1986 |          849 |            849 |      127.756 |      37.878  |
| 1022_1983 |          839 |            839 |      127.756 |      37.851  |
| 1123_1973 |          792 |            792 |      128.902 |      37.7528 |
| 1017_1992 |          790 |            790 |      127.699 |      37.9322 |

## 5. Output Files

- poles_5179: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\interim\poles_5179.parquet
- grid_1km_active: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\interim\grid_1km_active.parquet



---

<!-- Source: grid_station_mapping_report.md -->

# Grid Station Mapping Report

## 1. Summary

- grid_rows: 9908
- station_rows: 102
- aws_station_count: 88
- asos_station_count: 14
- output: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\interim\grid_station_mapping_202503.parquet
- output_rows: 9908

## 2. Distance Summary

| index   |   nearest_any_distance_m |   nearest_aws_distance_m |   nearest_asos_distance_m |
|:--------|-------------------------:|-------------------------:|--------------------------:|
| count   |                9908      |                9908      |                 9908      |
| mean    |                6136.69   |                6923.35   |                16110.2    |
| std     |                3103.24   |                3849.16   |                 8056.81   |
| min     |                  20.1547 |                  20.1547 |                   82.7907 |
| 10%     |                2219.28   |                2424.92   |                 5770.02   |
| 25%     |                3763.31   |                4096.77   |                 9956.23   |
| 50%     |                5893.62   |                6384.43   |                15623.1    |
| 75%     |                8194.89   |                9184.22   |                21258.2    |
| 90%     |               10440.1    |               12038.1    |                27538.4    |
| 95%     |               11685.6    |               13648.7    |                30954.2    |
| 99%     |               13709.3    |               19110.3    |                35550.2    |
| max     |               17256.9    |               25087.7    |                38950.2    |

## 3. Top AWS Station Coverage

|   nearest_aws_station_id | nearest_aws_station_name   |   grid_count |   pole_count |
|-------------------------:|:---------------------------|-------------:|-------------:|
|                      526 | 평창                         |          576 |        68722 |
|                      527 | 신동                         |          510 |        57714 |
|                      522 | 화촌                         |          433 |        65634 |
|                      563 | 북평                         |          366 |        38511 |
|                      878 | 도계                         |          356 |        37294 |
|                      535 | 서석                         |          294 |        35238 |
|                      978 | 춘천신북                       |          287 |        67457 |
|                      558 | 팔봉                         |          277 |        43299 |
|                      674 | 사북                         |          276 |        28785 |
|                      588 | 남산                         |          256 |        39509 |
|                      579 | 하장                         |          235 |        23117 |
|                      349 | 시동                         |          228 |        50068 |
|                      560 | 진부                         |          222 |        27952 |
|                      597 | 대화                         |          198 |        21764 |
|                      559 | 내면                         |          188 |        19555 |
|                      335 | 강림                         |          186 |        21989 |
|                      345 | 학성                         |          185 |        54684 |
|                      582 | 신림                         |          183 |        21524 |
|                      529 | 원덕                         |          172 |        18372 |
|                      537 | 임계                         |          167 |        19667 |

## 4. Top ASOS Station Coverage

|   nearest_asos_station_id | nearest_asos_station_name   |   grid_count |   pole_count |
|--------------------------:|:----------------------------|-------------:|-------------:|
|                       212 | 홍천                          |         1515 |       236954 |
|                       114 | 원주                          |         1349 |       224952 |
|                       217 | 정선군                         |         1215 |       132614 |
|                       100 | 대관령                         |         1100 |       122230 |
|                       216 | 태백                          |         1051 |       105269 |
|                       121 | 영월                          |          874 |       103614 |
|                       106 | 동해                          |          624 |        84468 |
|                       101 | 춘천                          |          550 |        99407 |
|                       104 | 북강릉                         |          461 |        86799 |
|                        93 | 북춘천                         |          342 |        44761 |
|                        90 | 속초                          |          335 |        64689 |
|                       105 | 강릉                          |          272 |        61146 |
|                       211 | 인제                          |          220 |        20928 |

## 5. Output Columns

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



---

<!-- Source: weather_daily_report.md -->

# Weather Daily Report

## 1. Input Encoding

- AWS hourly encoding: cp949
- ASOS hourly encoding: cp949
- ASOS daily encoding: cp949
- ASOS daily shape: (434, 62)

## 2. Output Summary

- output: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\interim\weather_daily_202503.parquet
- rows: 3124
- station_count: 102
- date_min: 2025-03-01 00:00:00
- date_max: 2025-03-31 00:00:00

## 3. By Source Type

| source_type   |   station_count |   rows | date_min            | date_max            |   mean_row_count |   min_row_count |   max_row_count |
|:--------------|----------------:|-------:|:--------------------|:--------------------|-----------------:|----------------:|----------------:|
| asos          |              14 |    434 | 2025-03-01 00:00:00 | 2025-03-31 00:00:00 |          24      |              24 |              24 |
| aws           |              88 |   2690 | 2025-03-01 00:00:00 | 2025-03-31 00:00:00 |          23.8803 |               1 |              24 |

## 4. Date Coverage Sample

| date                |   station_count |   rows |
|:--------------------|----------------:|-------:|
| 2025-03-01 00:00:00 |             102 |    102 |
| 2025-03-02 00:00:00 |             102 |    102 |
| 2025-03-03 00:00:00 |             102 |    102 |
| 2025-03-04 00:00:00 |             102 |    102 |
| 2025-03-05 00:00:00 |             101 |    101 |
| 2025-03-06 00:00:00 |             101 |    101 |
| 2025-03-07 00:00:00 |             102 |    102 |
| 2025-03-08 00:00:00 |             102 |    102 |
| 2025-03-09 00:00:00 |             101 |    101 |
| 2025-03-10 00:00:00 |             102 |    102 |

## 5. Columns

- station_id
- station_name
- date
- source_type
- temp_mean
- temp_max
- temp_min
- humidity_mean
- humidity_min
- rain_sum
- wind_mean
- wind_max
- wind_dir_mean
- pressure_mean
- row_count
- temp_obs_count
- humidity_obs_count
- wind_obs_count
- rain_obs_count



---

<!-- Source: grid_day_features_report.md -->

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



---

<!-- Source: grid_risk_scores_report.md -->

# Grid Risk Scores Report

## 1. Output Summary

- output: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\features\grid_risk_scores_202503.parquet
- rows: 307148
- grid_count: 9908
- date_count: 31
- date_min: 2025-03-01 00:00:00
- date_max: 2025-03-31 00:00:00

## 2. Risk Formula

`	ext
grid_risk_score = 0.40 * dry_weather_score
                + 0.25 * wind_score
                + 0.20 * asset_exposure_score
                + 0.15 * warning_score
`

## 3. Score Summary

| index   |   dry_weather_score |     wind_score |   asset_exposure_score |   warning_score |   distance_uncertainty_score |   grid_risk_score |   grid_risk_score_100 |
|:--------|--------------------:|---------------:|-----------------------:|----------------:|-----------------------------:|------------------:|----------------------:|
| count   |       307148        | 307148         |          307148        | 307148          |               307148         |    307148         |          307148       |
| mean    |            0.59209  |      0.323428  |               0.648448 |      0.0102716  |                    0.310765  |         0.448924  |              44.8924  |
| std     |            0.179623 |      0.177316  |               0.205835 |      0.0121674  |                    0.196036  |         0.0973294 |               9.73294 |
| min     |            0.112121 |      0         |               0        |      0          |                    0         |         0.0510991 |               5.11    |
| 1%      |            0.184091 |      0.0280244 |               0        |      0          |                    0         |         0.21744   |              21.744   |
| 5%      |            0.285606 |      0.100485  |               0.229535 |      0          |                    0.0470518 |         0.285941  |              28.594   |
| 10%     |            0.339394 |      0.137133  |               0.361682 |      0          |                    0.0832041 |         0.322106  |              32.211   |
| 25%     |            0.457576 |      0.202236  |               0.54748  |      0.00263158 |                    0.166782  |         0.381396  |              38.14    |
| 50%     |            0.604924 |      0.284182  |               0.679627 |      0.00526316 |                    0.281351  |         0.452331  |              45.233   |
| 75%     |            0.734848 |      0.408841  |               0.790887 |      0.0157895  |                    0.42261   |         0.517048  |              51.705   |
| 90%     |            0.825    |      0.573683  |               0.882364 |      0.0263158  |                    0.570917  |         0.571418  |              57.142   |
| 95%     |            0.871212 |      0.673623  |               0.932813 |      0.0394737  |                    0.658784  |         0.602627  |              60.2626  |
| 99%     |            0.916288 |      0.912621  |               1        |      0.05       |                    1         |         0.668152  |              66.815   |
| max     |            0.978409 |      1         |               1        |      0.05       |                    1         |         0.765707  |              76.571   |

## 4. Grade Summary

| grid_risk_grade   |   rows |   grid_count |   mean_score |   max_score |
|:------------------|-------:|-------------:|-------------:|------------:|
| high              |  16292 |         4705 |      63.8878 |      76.571 |
| medium            | 195743 |         9892 |      48.8083 |      60     |
| low               |  93308 |         9655 |      33.8977 |      40     |
| very_low          |   1805 |          718 |      17.1279 |      19.995 |

## 5. Date Summary

| date                |   rows |   mean_risk |   max_risk |   high_grid_count |   very_high_grid_count |   dry_warning_days |   strong_wind_warning_days |
|:--------------------|-------:|------------:|-----------:|------------------:|-----------------------:|-------------------:|---------------------------:|
| 2025-03-01 00:00:00 |   9908 |     39.578  |     61.545 |                 2 |                      0 |                  0 |                          0 |
| 2025-03-02 00:00:00 |   9908 |     39.0633 |     55.133 |                 0 |                      0 |                  0 |                          0 |
| 2025-03-03 00:00:00 |   9908 |     34.489  |     51.028 |                 0 |                      0 |                  0 |                          0 |
| 2025-03-04 00:00:00 |   9908 |     32.1914 |     48.33  |                 0 |                      0 |                  0 |                          0 |
| 2025-03-05 00:00:00 |   9908 |     30.815  |     45.015 |                 0 |                      0 |                  0 |                          0 |
| 2025-03-06 00:00:00 |   9908 |     33.9388 |     48.761 |                 0 |                      0 |                  0 |                          0 |
| 2025-03-07 00:00:00 |   9908 |     36.7117 |     50.721 |                 0 |                      0 |                  0 |                          0 |
| 2025-03-08 00:00:00 |   9908 |     38.4337 |     55.837 |                 0 |                      0 |                  0 |                          0 |
| 2025-03-09 00:00:00 |   9908 |     42.0526 |     56.703 |                 0 |                      0 |                  0 |                          0 |
| 2025-03-10 00:00:00 |   9908 |     45.0735 |     65.793 |                16 |                      0 |                  0 |                          0 |
| 2025-03-11 00:00:00 |   9908 |     48.1995 |     74.536 |               115 |                      0 |                  0 |                          0 |
| 2025-03-12 00:00:00 |   9908 |     49.2538 |     74.212 |               403 |                      0 |                  0 |                          0 |
| 2025-03-13 00:00:00 |   9908 |     53.023  |     71.903 |               700 |                      0 |                  0 |                          0 |
| 2025-03-14 00:00:00 |   9908 |     52.7578 |     69.295 |               627 |                      0 |                  0 |                          0 |
| 2025-03-15 00:00:00 |   9908 |     51.5182 |     67.762 |               558 |                      0 |                  0 |                          0 |
| 2025-03-16 00:00:00 |   9908 |     37.6678 |     52.811 |                 0 |                      0 |                  0 |                          0 |
| 2025-03-17 00:00:00 |   9908 |     42.4853 |     60.664 |                12 |                      0 |                  0 |                          0 |
| 2025-03-18 00:00:00 |   9908 |     36.9141 |     51.953 |                 0 |                      0 |                  0 |                          0 |
| 2025-03-19 00:00:00 |   9908 |     42.1908 |     54.89  |                 0 |                      0 |                  0 |                          0 |
| 2025-03-20 00:00:00 |   9908 |     43.8558 |     64.339 |                45 |                      0 |                  0 |                          0 |
| 2025-03-21 00:00:00 |   9908 |     49.296  |     69.576 |               921 |                      0 |                  0 |                          0 |
| 2025-03-22 00:00:00 |   9908 |     52.2197 |     71.203 |              1477 |                      0 |                  0 |                          0 |
| 2025-03-23 00:00:00 |   9908 |     51.1513 |     67.678 |               868 |                      0 |                  0 |                          0 |
| 2025-03-24 00:00:00 |   9908 |     53.8817 |     72.871 |              1868 |                      0 |                  0 |                          0 |
| 2025-03-25 00:00:00 |   9908 |     58.9597 |     76.571 |              4238 |                      0 |                  0 |                          0 |
| 2025-03-26 00:00:00 |   9908 |     56.8788 |     74.797 |              3051 |                      0 |                  0 |                          0 |
| 2025-03-27 00:00:00 |   9908 |     48.6215 |     74.214 |               547 |                      0 |                  0 |                          0 |
| 2025-03-28 00:00:00 |   9908 |     44.8436 |     70.92  |               288 |                      0 |                  0 |                          0 |
| 2025-03-29 00:00:00 |   9908 |     49.067  |     63.963 |               221 |                      0 |                  0 |                          0 |
| 2025-03-30 00:00:00 |   9908 |     48.4957 |     66.347 |               293 |                      0 |                  0 |                          0 |
| 2025-03-31 00:00:00 |   9908 |     48.0346 |     62.688 |                42 |                      0 |                  0 |                          0 |

## 6. Top 50 Risk Grid-Day Rows

| date                |   grid_id |   pole_count |   center_lon |   center_lat | primary_weather_source   |   primary_temp_max |   primary_humidity_min |   primary_rain_sum |   rain_sum_7d |   primary_wind_max |   wind_max_7d |   no_rain_days |   dry_warning_flag |   strong_wind_warning_flag |   grid_risk_score_100 | grid_risk_grade   |
|:--------------------|----------:|-------------:|-------------:|-------------:|:-------------------------|-------------------:|-----------------------:|-------------------:|--------------:|-------------------:|--------------:|---------------:|-------------------:|---------------------------:|----------------------:|:------------------|
| 2025-03-25 00:00:00 | 1085_1909 |          487 |      128.463 |      37.1804 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                76.571 | high              |
| 2025-03-25 00:00:00 | 1086_1910 |          485 |      128.475 |      37.1893 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                76.555 | high              |
| 2025-03-25 00:00:00 | 1095_1904 |          436 |      128.575 |      37.1343 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                76.15  | high              |
| 2025-03-25 00:00:00 | 1107_1925 |          419 |      128.713 |      37.3223 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.999 | high              |
| 2025-03-25 00:00:00 | 1086_1909 |          417 |      128.474 |      37.1803 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.98  | high              |
| 2025-03-25 00:00:00 | 1101_1913 |          404 |      128.644 |      37.2148 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.86  | high              |
| 2025-03-25 00:00:00 | 1106_1911 |          367 |      128.7   |      37.1962 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.495 | high              |
| 2025-03-25 00:00:00 | 1103_1932 |          492 |      128.669 |      37.3858 | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                75.457 | high              |
| 2025-03-25 00:00:00 | 1102_1902 |          351 |      128.654 |      37.1156 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.325 | high              |
| 2025-03-25 00:00:00 | 1084_1910 |          350 |      128.452 |      37.1895 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.314 | high              |
| 2025-03-25 00:00:00 | 1086_1908 |          347 |      128.474 |      37.1713 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.282 | high              |
| 2025-03-25 00:00:00 | 1128_1912 |          405 |      128.948 |      37.2025 | aws                      |               18.9 |                     26 |                  0 |             0 |               12.9 |          12.9 |              7 |                  0 |                          0 |                75.186 | high              |
| 2025-03-25 00:00:00 | 1102_1937 |          453 |      128.659 |      37.431  | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                75.143 | high              |
| 2025-03-25 00:00:00 | 1093_1910 |          329 |      128.553 |      37.1886 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.079 | high              |
| 2025-03-25 00:00:00 | 1099_1911 |          327 |      128.621 |      37.197  | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.056 | high              |
| 2025-03-25 00:00:00 | 1093_1903 |          327 |      128.553 |      37.1255 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.056 | high              |
| 2025-03-25 00:00:00 | 1089_1919 |          323 |      128.509 |      37.2701 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                75.009 | high              |
| 2025-03-25 00:00:00 | 1103_1939 |          434 |      128.67  |      37.4489 | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                74.98  | high              |
| 2025-03-25 00:00:00 | 1083_1909 |          319 |      128.441 |      37.1805 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.962 | high              |
| 2025-03-25 00:00:00 | 1089_1914 |          312 |      128.509 |      37.225  | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.877 | high              |
| 2025-03-25 00:00:00 | 1104_1905 |          311 |      128.677 |      37.1424 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.865 | high              |
| 2025-03-25 00:00:00 | 1107_1941 |          420 |      128.716 |      37.4665 | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                74.855 | high              |
| 2025-03-25 00:00:00 | 1106_1913 |          308 |      128.7   |      37.2143 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.828 | high              |
| 2025-03-25 00:00:00 | 1103_1907 |          306 |      128.666 |      37.1605 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.804 | high              |
| 2025-03-26 00:00:00 | 1128_1912 |          405 |      128.948 |      37.2025 | aws                      |               19.8 |                     11 |                  0 |             0 |                7.3 |          12.9 |              8 |                  0 |                          0 |                74.797 | high              |
| 2025-03-25 00:00:00 | 1103_1912 |          303 |      128.666 |      37.2056 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.766 | high              |
| 2025-03-25 00:00:00 | 1110_1941 |          407 |      128.75  |      37.4661 | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                74.735 | high              |
| 2025-03-25 00:00:00 | 1099_1924 |          298 |      128.623 |      37.3142 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.703 | high              |
| 2025-03-25 00:00:00 | 1116_1924 |          356 |      128.815 |      37.3122 | aws                      |               18.9 |                     26 |                  0 |             0 |               12.9 |          12.9 |              7 |                  0 |                          0 |                74.696 | high              |
| 2025-03-25 00:00:00 | 1105_1912 |          297 |      128.689 |      37.2054 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.69  | high              |
| 2025-03-25 00:00:00 | 1084_1909 |          290 |      128.452 |      37.1805 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.599 | high              |
| 2025-03-25 00:00:00 | 1097_1929 |          391 |      128.601 |      37.3594 | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                74.583 | high              |
| 2025-03-11 00:00:00 | 1080_2010 |           86 |      128.418 |      38.091  | aws                      |                7   |                     11 |                  0 |             0 |               14.7 |          14.7 |             11 |                  0 |                          0 |                74.536 | high              |
| 2025-03-25 00:00:00 | 1089_1912 |          285 |      128.509 |      37.207  | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.533 | high              |
| 2025-03-25 00:00:00 | 1109_1921 |          334 |      128.735 |      37.286  | aws                      |               18.9 |                     26 |                  0 |             0 |               12.9 |          12.9 |              7 |                  0 |                          0 |                74.453 | high              |
| 2025-03-25 00:00:00 | 1098_1911 |          276 |      128.61  |      37.1971 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.411 | high              |
| 2025-03-25 00:00:00 | 1104_1919 |          275 |      128.679 |      37.2685 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.398 | high              |
| 2025-03-25 00:00:00 | 1095_1911 |          275 |      128.576 |      37.1974 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.398 | high              |
| 2025-03-25 00:00:00 | 1085_1910 |          273 |      128.463 |      37.1894 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.37  | high              |
| 2025-03-25 00:00:00 | 1085_1907 |          273 |      128.463 |      37.1623 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.37  | high              |
| 2025-03-25 00:00:00 | 1097_1905 |          273 |      128.598 |      37.1431 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.37  | high              |
| 2025-03-11 00:00:00 | 1081_2010 |           82 |      128.429 |      38.091  | aws                      |                7   |                     11 |                  0 |             0 |               14.7 |          14.7 |             11 |                  0 |                          0 |                74.357 | high              |
| 2025-03-25 00:00:00 | 1096_1934 |          368 |      128.59  |      37.4046 | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                74.352 | high              |
| 2025-03-25 00:00:00 | 1103_1931 |          367 |      128.669 |      37.3768 | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                74.342 | high              |
| 2025-03-25 00:00:00 | 1100_1912 |          269 |      128.633 |      37.2059 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.314 | high              |
| 2025-03-26 00:00:00 | 1116_1924 |          356 |      128.815 |      37.3122 | aws                      |               19.8 |                     11 |                  0 |             0 |                7.3 |          12.9 |              8 |                  0 |                          0 |                74.306 | high              |
| 2025-03-25 00:00:00 | 1129_1911 |          318 |      128.959 |      37.1933 | aws                      |               18.9 |                     26 |                  0 |             0 |               12.9 |          12.9 |              7 |                  0 |                          0 |                74.267 | high              |
| 2025-03-25 00:00:00 | 1108_1942 |          359 |      128.727 |      37.4754 | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                74.258 | high              |
| 2025-03-25 00:00:00 | 1104_1940 |          359 |      128.682 |      37.4578 | aws                      |               22.1 |                     22 |                  0 |             0 |               10.5 |          10.5 |              7 |                  0 |                          0 |                74.258 | high              |
| 2025-03-25 00:00:00 | 1103_1923 |          264 |      128.668 |      37.3047 | aws                      |               22.5 |                     18 |                  0 |             0 |               11.5 |          11.5 |              7 |                  0 |                          0 |                74.243 | high              |

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
- dry_weather_score
- wind_score
- asset_exposure_score
- warning_score
- distance_uncertainty_score
- grid_risk_score
- grid_risk_score_100
- grid_risk_grade



---

<!-- Source: pole_risk_submission_report.md -->

# Pole Risk Submission Report

## 1. Input Summary

- grid_risk_rows: 307148
- grid_count: 9908
- date_count: 31
- pole_base_rows: 1387831

## 2. Output Files

- grid_summary: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\features\grid_risk_summary_202503.parquet
- pole_risk: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\features\pole_risk_scores_202503.parquet
- top_risk_poles_1000: C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\outputs\top_risk_poles_1000.csv

## 3. Grid Final Risk Formula

`	ext
grid_final_risk_score = 0.35 * risk_max
                      + 0.35 * risk_p95
                      + 0.20 * risk_mean
                      + 0.10 * high_day_ratio
`

## 4. Candidate Submission Files

| file                                                             |   top_pct |   decision_1_count |   decision_0_count |    rows |
|:-----------------------------------------------------------------|----------:|-------------------:|-------------------:|--------:|
| data\outputs\submission_candidates\baseline_submission_top1.csv  |      0.01 |              13879 |            1373952 | 1387831 |
| data\outputs\submission_candidates\baseline_submission_top3.csv  |      0.03 |              41635 |            1346196 | 1387831 |
| data\outputs\submission_candidates\baseline_submission_top5.csv  |      0.05 |              69392 |            1318439 | 1387831 |
| data\outputs\submission_candidates\baseline_submission_top10.csv |      0.1  |             138784 |            1249047 | 1387831 |

## 5. Grid Score Summary

| index   |   grid_final_risk_score_100 |    risk_mean |     risk_max |     risk_p95 |   high_day_count |   pole_count |
|:--------|----------------------------:|-------------:|-------------:|-------------:|-----------------:|-------------:|
| count   |                  9908       | 9908         | 9908         | 9908         |       9908       |     9908     |
| mean    |                    50.4076  |    0.448924  |    0.599766  |    0.568769  |          1.64433 |      140.072 |
| std     |                     5.92912 |    0.0516385 |    0.0672123 |    0.0592827 |          2.49555 |      126.722 |
| min     |                    31.211   |    0.244098  |    0.38779   |    0.364475  |          0       |        1     |
| 1%      |                    36.23    |    0.308741  |    0.434766  |    0.416823  |          0       |        2     |
| 5%      |                    40.7698  |    0.355319  |    0.490035  |    0.467665  |          0       |        9     |
| 10%     |                    43.221   |    0.380327  |    0.516161  |    0.494781  |          0       |       19     |
| 25%     |                    46.5545  |    0.417605  |    0.555133  |    0.531653  |          0       |       52     |
| 50%     |                    49.9555  |    0.452499  |    0.595691  |    0.568504  |          0       |      105     |
| 75%     |                    54.322   |    0.48627   |    0.649228  |    0.606941  |          2       |      189     |
| 90%     |                    58.5405  |    0.513644  |    0.693911  |    0.644425  |          6       |      305.3   |
| 95%     |                    60.7946  |    0.525896  |    0.711114  |    0.66997   |          7       |      399     |
| 99%     |                    63.8433  |    0.544929  |    0.734464  |    0.703067  |         10       |      568     |
| max     |                    67.733   |    0.570689  |    0.765707  |    0.745051  |         14       |     1289     |

## 6. Pole Score Summary

| index   |   pole_risk_score_100 |     pole_count |    risk_max |    risk_p95 |   high_day_count |
|:--------|----------------------:|---------------:|------------:|------------:|-----------------:|
| count   |           1.38783e+06 |    1.38783e+06 | 1.38783e+06 | 1.38783e+06 |      1.38783e+06 |
| mean    |          53.3423      |  254.705       | 0.627485    | 0.597624    |      2.70777     |
| std     |           5.30506     |  176.053       | 0.0585082   | 0.0498554   |      3.13084     |
| min     |          31.211       |    1           | 0.38779     | 0.364475    |      0           |
| 1%      |          42.511       |   24           | 0.505443    | 0.488558    |      0           |
| 5%      |          45.46        |   55           | 0.53793     | 0.519443    |      0           |
| 10%     |          46.873       |   76           | 0.554286    | 0.535232    |      0           |
| 25%     |          49.332       |  126           | 0.583932    | 0.562604    |      0           |
| 50%     |          52.885       |  213           | 0.622862    | 0.595882    |      2           |
| 75%     |          57.129       |  340           | 0.673674    | 0.63033     |      4           |
| 90%     |          60.802       |  482           | 0.70941     | 0.666043    |      8           |
| 95%     |          62.943       |  571           | 0.723932    | 0.687966    |      9           |
| 99%     |          64.838       |  871           | 0.743569    | 0.708824    |     12           |
| max     |          67.733       | 1289           | 0.765707    | 0.745051    |     14           |

## 7. Grade Summary

| grid_final_risk_grade   |   pole_count |   grid_count |   mean_score |   max_score |
|:------------------------|-------------:|-------------:|-------------:|------------:|
| high                    |       169319 |          646 |      62.5023 |      67.733 |
| medium                  |      1215402 |         8870 |      52.1047 |      59.998 |
| low                     |         3110 |          392 |      38.3151 |      39.989 |

## 8. Top 30 Risk Grids

|   grid_id |   pole_count |   center_lon |   center_lat |   grid_final_risk_score_100 | grid_final_risk_grade   |   risk_max |   risk_p95 |   high_day_count | peak_date           |   peak_grid_risk_score_100 |   peak_temp_max |   peak_humidity_min |   peak_wind_max |   peak_no_rain_days |
|----------:|-------------:|-------------:|-------------:|----------------------------:|:------------------------|-----------:|-----------:|-----------------:|:--------------------|---------------------------:|----------------:|--------------------:|----------------:|--------------------:|
| 1080_2010 |           86 |      128.418 |      38.091  |                      67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |                     74.536 |             7   |                  11 |            14.7 |                  11 |
| 1081_2010 |           82 |      128.429 |      38.091  |                      67.571 | high                    |   0.743569 |   0.732919 |               14 | 2025-03-11 00:00:00 |                     74.357 |             7   |                  11 |            14.7 |                  11 |
| 1128_1912 |          405 |      128.948 |      37.2025 |                      67.344 | high                    |   0.751863 |   0.745051 |               12 | 2025-03-25 00:00:00 |                     75.186 |            18.9 |                  26 |            12.9 |                   7 |
| 1116_1924 |          356 |      128.815 |      37.3122 |                      66.902 | high                    |   0.746959 |   0.740147 |               12 | 2025-03-25 00:00:00 |                     74.696 |            18.9 |                  26 |            12.9 |                   7 |
| 1085_1909 |          487 |      128.463 |      37.1804 |                      66.719 | high                    |   0.765707 |   0.705805 |               12 | 2025-03-25 00:00:00 |                     76.571 |            22.5 |                  18 |            11.5 |                   7 |
| 1086_1910 |          485 |      128.475 |      37.1893 |                      66.705 | high                    |   0.765551 |   0.705648 |               12 | 2025-03-25 00:00:00 |                     76.555 |            22.5 |                  18 |            11.5 |                   7 |
| 1109_1921 |          334 |      128.735 |      37.286  |                      66.684 | high                    |   0.744534 |   0.737722 |               12 | 2025-03-25 00:00:00 |                     74.453 |            18.9 |                  26 |            12.9 |                   7 |
| 1095_1904 |          436 |      128.575 |      37.1343 |                      66.34  | high                    |   0.761499 |   0.701596 |               12 | 2025-03-25 00:00:00 |                     76.15  |            22.5 |                  18 |            11.5 |                   7 |
| 1107_1925 |          419 |      128.713 |      37.3223 |                      66.204 | high                    |   0.759986 |   0.700083 |               12 | 2025-03-25 00:00:00 |                     75.999 |            22.5 |                  18 |            11.5 |                   7 |
| 1079_2010 |           70 |      128.407 |      38.0911 |                      66.198 | high                    |   0.737614 |   0.726964 |               12 | 2025-03-11 00:00:00 |                     73.761 |             7   |                  11 |            14.7 |                  11 |
| 1129_1911 |          318 |      128.959 |      37.1933 |                      66.194 | high                    |   0.742668 |   0.735856 |               11 | 2025-03-25 00:00:00 |                     74.267 |            18.9 |                  26 |            12.9 |                   7 |
| 1086_1909 |          417 |      128.474 |      37.1803 |                      66.188 | high                    |   0.759804 |   0.699901 |               12 | 2025-03-25 00:00:00 |                     75.98  |            22.5 |                  18 |            11.5 |                   7 |
| 1101_1913 |          404 |      128.644 |      37.2148 |                      66.079 | high                    |   0.758599 |   0.698697 |               12 | 2025-03-25 00:00:00 |                     75.86  |            22.5 |                  18 |            11.5 |                   7 |
| 1123_1972 |          689 |      128.902 |      37.7438 |                      65.832 | high                    |   0.729322 |   0.707938 |               14 | 2025-03-25 00:00:00 |                     72.932 |            20.3 |                  39 |            11.6 |                   7 |
| 1124_1967 |          621 |      128.912 |      37.6986 |                      65.832 | high                    |   0.729322 |   0.707938 |               14 | 2025-03-25 00:00:00 |                     72.932 |            20.3 |                  39 |            11.6 |                   7 |
| 1124_1968 |          571 |      128.912 |      37.7076 |                      65.832 | high                    |   0.729322 |   0.707938 |               14 | 2025-03-25 00:00:00 |                     72.932 |            20.3 |                  39 |            11.6 |                   7 |
| 1122_1972 |          592 |      128.89  |      37.7439 |                      65.832 | high                    |   0.729322 |   0.707938 |               14 | 2025-03-25 00:00:00 |                     72.932 |            20.3 |                  39 |            11.6 |                   7 |
| 1090_1999 |          450 |      128.531 |      37.991  |                      65.804 | high                    |   0.720207 |   0.708373 |               14 | 2025-03-24 00:00:00 |                     72.021 |            21.8 |                  22 |             9.1 |                   6 |
| 1128_1911 |          298 |      128.948 |      37.1935 |                      65.649 | high                    |   0.740199 |   0.733387 |               10 | 2025-03-25 00:00:00 |                     74.02  |            18.9 |                  26 |            12.9 |                   7 |
| 1113_1917 |          293 |      128.78  |      37.2495 |                      65.591 | high                    |   0.739556 |   0.732744 |               10 | 2025-03-25 00:00:00 |                     73.956 |            18.9 |                  26 |            12.9 |                   7 |
| 1121_1911 |          285 |      128.869 |      37.1944 |                      65.496 | high                    |   0.738504 |   0.731692 |               10 | 2025-03-25 00:00:00 |                     73.85  |            18.9 |                  26 |            12.9 |                   7 |
| 1120_1912 |          284 |      128.858 |      37.2035 |                      65.484 | high                    |   0.73837  |   0.731558 |               10 | 2025-03-25 00:00:00 |                     73.837 |            18.9 |                  26 |            12.9 |                   7 |
| 1125_1971 |          557 |      128.924 |      37.7345 |                      65.443 | high                    |   0.728577 |   0.707193 |               13 | 2025-03-25 00:00:00 |                     72.858 |            20.3 |                  39 |            11.6 |                   7 |
| 1106_1911 |          367 |      128.7   |      37.1962 |                      65.428 | high                    |   0.754946 |   0.695044 |               11 | 2025-03-25 00:00:00 |                     75.495 |            22.5 |                  18 |            11.5 |                   7 |
| 1113_1916 |          276 |      128.78  |      37.2405 |                      65.064 | high                    |   0.737285 |   0.730473 |                9 | 2025-03-25 00:00:00 |                     73.728 |            18.9 |                  26 |            12.9 |                   7 |
| 1120_1972 |          542 |      128.868 |      37.7442 |                      65.026 | high                    |   0.727538 |   0.706154 |               12 | 2025-03-25 00:00:00 |                     72.754 |            20.3 |                  39 |            11.6 |                   7 |
| 1116_1915 |          272 |      128.813 |      37.2311 |                      65.014 | high                    |   0.73673  |   0.729918 |                9 | 2025-03-25 00:00:00 |                     73.673 |            18.9 |                  26 |            12.9 |                   7 |
| 1124_1972 |          537 |      128.913 |      37.7437 |                      64.995 | high                    |   0.727186 |   0.705802 |               12 | 2025-03-25 00:00:00 |                     72.719 |            20.3 |                  39 |            11.6 |                   7 |
| 1102_1902 |          351 |      128.654 |      37.1156 |                      64.953 | high                    |   0.753251 |   0.693349 |               10 | 2025-03-25 00:00:00 |                     75.325 |            22.5 |                  18 |            11.5 |                   7 |
| 1121_1970 |          529 |      128.879 |      37.7261 |                      64.943 | high                    |   0.726614 |   0.70523  |               12 | 2025-03-25 00:00:00 |                     72.661 |            20.3 |                  39 |            11.6 |                   7 |

## 9. Notes

- This is a rule-based baseline submission generator.
- Final official submission should be selected after threshold sensitivity review.
- Since no public label is available, top-percentile submissions are generated as candidates.



---

<!-- Source: submission_candidate_review.md -->

# Submission Candidate Review

## 1. Candidate Validation

| candidate                 | file                                                             | exists   |    rows | columns_ok   | decision_values   |   decision_1_count |   decision_1_ratio |   lon_missing |   lat_missing |   pole_id_duplicate | name   |
|:--------------------------|:-----------------------------------------------------------------|:---------|--------:|:-------------|:------------------|-------------------:|-------------------:|--------------:|--------------:|--------------------:|:-------|
| baseline_submission_top1  | data\outputs\submission_candidates\baseline_submission_top1.csv  | True     | 1387831 | True         | [0, 1]            |              13879 |          0.0100005 |             0 |             0 |                   0 | top1   |
| baseline_submission_top3  | data\outputs\submission_candidates\baseline_submission_top3.csv  | True     | 1387831 | True         | [0, 1]            |              41635 |          0.0300001 |             0 |             0 |                   0 | top3   |
| baseline_submission_top5  | data\outputs\submission_candidates\baseline_submission_top5.csv  | True     | 1387831 | True         | [0, 1]            |              69392 |          0.0500003 |             0 |             0 |                   0 | top5   |
| baseline_submission_top10 | data\outputs\submission_candidates\baseline_submission_top10.csv | True     | 1387831 | True         | [0, 1]            |             138784 |          0.100001  |             0 |             0 |                   0 | top10  |

## 2. Selected Baseline

- selected_file: data/outputs/baseline_submission_final_top5.csv
- reason: top5 is selected as the default rule-based baseline because it balances conservative detection and sufficient high-risk coverage without labels.

## 3. Top 20 Risk Poles

|   pole_id |     lon |     lat |   grid_id |   pole_risk_score_100 | grid_final_risk_grade   |   risk_max |   risk_p95 |   high_day_count | peak_date           |   peak_temp_max |   peak_humidity_min |   peak_wind_max |   peak_no_rain_days |
|----------:|--------:|--------:|----------:|----------------------:|:------------------------|-----------:|-----------:|-----------------:|:--------------------|----------------:|--------------------:|----------------:|--------------------:|
|   1326212 | 128.423 | 38.0891 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326213 | 128.423 | 38.0891 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326214 | 128.422 | 38.0888 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326215 | 128.422 | 38.0887 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326377 | 128.412 | 38.0947 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326378 | 128.413 | 38.0951 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326379 | 128.413 | 38.095  | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326380 | 128.413 | 38.0946 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326381 | 128.414 | 38.0942 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326382 | 128.414 | 38.094  | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326383 | 128.415 | 38.094  | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326384 | 128.415 | 38.0939 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326385 | 128.416 | 38.0939 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326386 | 128.416 | 38.0937 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326387 | 128.416 | 38.0936 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326388 | 128.415 | 38.0937 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326389 | 128.414 | 38.0937 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326390 | 128.414 | 38.0936 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326391 | 128.413 | 38.0936 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |
|   1326392 | 128.413 | 38.0935 | 1080_2010 |                67.733 | high                    |   0.745363 |   0.734713 |               14 | 2025-03-11 00:00:00 |               7 |                  11 |            14.7 |                  11 |

## 4. Notes

- top1 is a conservative candidate.
- top3 is a backup conservative baseline.
- top5 is the default baseline candidate.
- top10 may be too broad without validation labels.



---

<!-- Source: risk_map_report.md -->

# Risk Map Report

## 1. Grid Risk Map

- grid_total: 9908
- grid_drawn: 5000
- top_grid_csv: data\outputs\top_risk_grids_500.csv
- grid_map: data\outputs\risk_map_grid_top5000.html
- risk_min: 49.89
- risk_max: 67.733

## 2. Top Pole Risk Map

- pole_total: 1387831
- pole_drawn: 500
- pole_map: data\outputs\risk_map_top_poles_500.html
- risk_min: 67.344
- risk_max: 67.733

## 3. Notes

- Grid map draws top 5000 grid cells by final risk score to avoid excessive HTML size.
- Pole map draws top 500 poles by pole risk score.
- These maps are for reporting and qualitative evaluation, not official submission format.

