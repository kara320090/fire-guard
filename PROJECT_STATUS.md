# FIRE-GUARD 3.0 Project Status

## 1. Project Definition

FIRE-GUARD 3.0은 ASOS/AWS 관측자료, 건조·강풍 특보, 전력설비 위치 데이터를 결합하여 전력설비 주변 화재위험도를 산정하고, 고위험 설비의 예방점검 우선순위를 제시하는 기상·공간 융합 위험도 분석 시스템입니다.

## 2. Current Pipeline Status

| Step | Status | Output |
|---|---:|---|
| 전력설비 원본 프로파일링 | Done | reports/poles_profile_report.md |
| 1km grid 생성 | Done | data/interim/grid_1km_active.parquet |
| grid 밀도 분석 | Done | data/outputs/grid_density_summary.csv |
| pole base 생성 | Done | data/interim/pole_base.parquet |
| AWS/ASOS/특보 원자료 표준화 | Done | reports/raw_standardization_report.md |
| 필요 관측소 102개 추출 | Done | data/interim/station_list_needed.csv |
| 관측소 좌표 102개 매칭 | Done | data/interim/station_meta_active_202503.csv |
| weather daily feature 생성 | Done | data/interim/weather_daily_202503.parquet |
| grid-station 거리 매칭 | Done | data/interim/grid_station_mapping_202503.parquet |
| grid-day feature 생성 | Done | data/features/grid_day_features_202503.parquet |
| warning daily feature 생성 | Done | data/interim/warning_daily_202503.parquet |
| grid risk score 생성 | Done | data/features/grid_risk_scores_202503.parquet |
| pole risk score 생성 | Done | data/features/pole_risk_scores_202503.parquet |
| 제출 후보 생성 | Done | data/outputs/submission_candidates |
| 최종 top5 baseline 선택 | Done | data/outputs/baseline_submission_final_top5.csv |
| 위험지도 생성 | Done | data/outputs/risk_map_grid_top5000.html |
| 최종 제출 파일 검수 | Done | reports/final_submission_check_report.md |

## 3. Final Submission Candidate

| Item | Value |
|---|---:|
| selected baseline | top5 |
| rows | 1,387,831 |
| columns | pole_id, lon, lat, decision |
| decision=1 | 69,392 |
| decision=0 | 1,318,439 |
| decision=1 ratio | 5.000032% |
| file size | 62.231 MB |
| SHA256 | 2dcbb19b1f8a21d53720513c3121066b8c63ab4db8798fa4dc962bb948fa5019 |

## 4. Main Method

1. 전력설비 좌표를 정제하고 1km grid로 공간 집계했습니다.
2. AWS/ASOS 관측자료를 일 단위 기상 feature로 변환했습니다.
3. 관측소 좌표와 grid 중심점 간 거리 기반 nearest station 매칭을 수행했습니다.
4. 건조도, 무강수 지속일, 풍속, 전력설비 밀도, 특보 여부를 결합해 grid risk score를 계산했습니다.
5. grid 위험도를 pole 단위로 확장하고, 상위 percentile 기반 제출 후보를 생성했습니다.
6. threshold sensitivity 후보 중 top5를 1차 최종 baseline으로 선택했습니다.

## 5. Important Artifacts

| Artifact | Path |
|---|---|
| Final submission manifest | submission/submission_manifest.md |
| Final validation report | reports/final_submission_check_report.md |
| Risk map report | reports/risk_map_report.md |
| Pole risk report | reports/pole_risk_submission_report.md |
| Grid risk report | reports/grid_risk_scores_report.md |
| Grid map HTML | data/outputs/risk_map_grid_top5000.html |
| Top pole map HTML | data/outputs/risk_map_top_poles_500.html |

## 6. Notes

- 최종 제출 CSV는 구조 검수를 통과했습니다.
- 대용량 CSV는 GitHub 권장 용량을 초과할 수 있으므로 중복 커밋을 피합니다.
- 현재 제출 후보는 rule-based baseline이며, 추후 label 또는 평가 피드백이 확보되면 threshold와 scoring weight를 재조정할 수 있습니다.
