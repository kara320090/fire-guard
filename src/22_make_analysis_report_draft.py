from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

REPORT_PATH = ROOT / "reports" / "FIRE_GUARD_analysis_report_draft.md"

SECTIONS = [
    ROOT / "reports" / "poles_profile_report.md",
    ROOT / "reports" / "grid_1km_profile_report.md",
    ROOT / "reports" / "grid_station_mapping_report.md",
    ROOT / "reports" / "weather_daily_report.md",
    ROOT / "reports" / "grid_day_features_report.md",
    ROOT / "reports" / "grid_risk_scores_report.md",
    ROOT / "reports" / "pole_risk_submission_report.md",
    ROOT / "reports" / "submission_candidate_review.md",
    ROOT / "reports" / "risk_map_report.md",
]

def read_section(path: Path) -> str:
    if not path.exists():
        return f"## Missing Section: {path.name}\n\n- file not found: {path}\n\n"

    text = path.read_text(encoding="utf-8-sig", errors="replace")
    return f"\n\n---\n\n<!-- Source: {path.name} -->\n\n{text}\n"

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    header = f"""# FIRE-GUARD 3.0 분석 보고서 초안

생성일: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

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

"""

    body = ""
    for path in SECTIONS:
        body += read_section(path)

    REPORT_PATH.write_text(header + body, encoding="utf-8-sig")

    print("Saved:", REPORT_PATH)

if __name__ == "__main__":
    main()
