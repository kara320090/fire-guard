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
