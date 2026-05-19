# Data Inventory

## 1. Purpose

이 문서는 FIRE-GUARD 3.0 프로젝트에서 사용하는 데이터의 출처, 활용 목적, 현재 확보 상태를 추적하기 위한 문서입니다.

## 2. Confirmed Data

### 2.1 한전 전력설비 위치 데이터

- File: data/raw/contest/contest_data_1.zip
- Source: 대회 제공 / 한국전력공사
- Expected columns:
  - pole_id
  - lon
  - lat
- Usage:
  - 전력설비 위치 확인
  - grid별 설비 밀도 계산
  - 고위험 pole_id 점검 우선순위 산출

## 3. Data To Download

### 3.1 AWS 시간자료

- Source: 기상자료개방포털
- Usage:
  - 기온, 습도, 강수량, 풍속, 풍향 feature 생성
  - grid별 대표 기상값 산정

### 3.2 ASOS 시간/일자료

- Source: 기상자료개방포털
- Usage:
  - 기준 관측값
  - AWS 결측 보정
  - 일 단위 기상 집계 검증

### 3.3 관측소 메타데이터

- Source: 기상자료개방포털
- Usage:
  - grid 중심점과 관측소 거리 계산
  - nearest_station_distance feature 생성

### 3.4 건조·강풍 특보

- Source: 기상자료개방포털
- Usage:
  - dry_warning_flag
  - strong_wind_warning_flag
  - warning_overlap_flag

## 4. Rule

사용한 모든 데이터는 최종 보고서와 README에 출처를 명시합니다.

## 5. Next Step

1. contest_data_1.zip 압축 내부 구조 확인
2. gangwon_poles_4326.csv 프로파일링
3. poles_clean.parquet 생성
4. 1km grid 생성
