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
