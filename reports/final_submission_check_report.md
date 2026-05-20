# Final Submission Check Report

## 1. Validation Result

| item                  | value                                                                                              |
|:----------------------|:---------------------------------------------------------------------------------------------------|
| input_path            | C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\data\outputs\baseline_submission_final_top5.csv |
| rows                  | 1387831                                                                                            |
| expected_rows         | 1387831                                                                                            |
| row_count_ok          | True                                                                                               |
| columns               | ['pole_id', 'lon', 'lat', 'decision']                                                              |
| columns_ok            | True                                                                                               |
| pole_id_missing       | 0                                                                                                  |
| pole_id_duplicates    | 0                                                                                                  |
| lon_missing           | 0                                                                                                  |
| lat_missing           | 0                                                                                                  |
| decision_values       | [0, 1]                                                                                             |
| decision_values_ok    | True                                                                                               |
| decision_1_count      | 69392                                                                                              |
| decision_0_count      | 1318439                                                                                            |
| decision_1_ratio      | 0.050000324246972434                                                                               |
| lon_min               | 127.50888371330925                                                                                 |
| lon_max               | 129.36334879138315                                                                                 |
| lat_min               | 37.03725721266511                                                                                  |
| lat_max               | 38.2304451198568                                                                                   |
| final_submission_path | C:\Users\soma\Desktop\대회파일\날씨 빅데이터 콘테스트\fire-guard\submission\FIRE_GUARD_submission_top5.csv       |
| final_file_size_mb    | 62.231                                                                                             |
| sha256                | 2dcbb19b1f8a21d53720513c3121066b8c63ab4db8798fa4dc962bb948fa5019                                   |
| hard_fail_count       | 0                                                                                                  |
| hard_fail             | []                                                                                                 |

## 2. Final Judgment

- PASS: final submission file passed structural validation.
