# FIRE-GUARD 3.0

## Project Title

FIRE-GUARD:
2-Stage 기상·공간 융합 앙상블 기반 전력설비 화재위험 예측 및 예방점검 우선순위 시스템

## Definition

ASOS/AWS 관측자료, 건조·강풍 특보, 전력설비 위치 데이터를 결합해 전력설비 인근 화재위험을 단계적으로 탐지하고, 고위험 설비의 예방점검 우선순위를 제시하는 의사결정 시스템입니다.

## Main Outputs

1. Grid별 화재위험도 지도
2. 고위험 grid Top-N
3. 고위험 pole_id Top-N
4. 점검 우선순위표
5. 위험 원인 설명 카드
6. Streamlit 또는 HTML 기반 결과 시각화

## Data Policy

사용한 모든 데이터는 출처를 명확히 기록합니다.
기상청 회신에 따라 ASOS/AWS 관측자료, 관측소 메타데이터, 건조·강풍 특보 자료는 feature 생성, 공간 매칭, 보조 분석 및 검증 용도로 활용합니다.

## Current Status

- contest_data_1.zip 확보
- 한전 전력설비 위치 데이터 프로파일링 예정
- AWS/ASOS/특보 데이터 다운로드 예정
