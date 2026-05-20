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
