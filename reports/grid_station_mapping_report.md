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
