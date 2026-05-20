# FIRE-GUARD Progress Log

## 현재 완료 상태

### 1. 전력설비 데이터 프로파일링 완료

- 원본 파일: data/raw/contest/contest_data_1.zip
- 내부 CSV: hanjeon/gangwon_poles_4326.csv
- 원본 행 수: 1,387,831
- 필수 컬럼: pole_id, lon, lat
- pole_id 결측: 0
- lon/lat 결측 또는 invalid: 0
- pole_id 중복: 0
- 대한민국 범위 밖 좌표: 0
- 정제 후 행 수: 1,387,831

### 2. 1km Grid 생성 완료

- 분석 좌표계: EPSG:5179
- Grid 크기: 1km x 1km
- 전력설비가 포함된 active grid 수: 9,908
- grid당 평균 설비 수: 약 140.07
- grid당 중앙값 설비 수: 105
- 최대 설비 밀도 grid: 1,289개/km²

### 3. 생성된 주요 파일

- data/interim/poles_clean.parquet
- data/interim/poles_5179.parquet
- data/interim/grid_1km_active.parquet
- data/outputs/grid_pole_density_map.html
- data/outputs/top_dense_grids_100.csv
- data/outputs/grid_density_summary.csv
- reports/poles_profile_report.md
- reports/grid_1km_profile_report.md
- reports/grid_density_summary.md

## 다음 작업

1. AWS 시간자료 샘플 다운로드
2. ASOS 시간/일자료 샘플 다운로드
3. 관측소 메타데이터 확보
4. 건조·강풍 특보 샘플 확보
5. 관측소-grid 공간 매칭
