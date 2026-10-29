# Detection Performance & Model Evaluation Report

## 1. Overview
The evaluation framework benchmarks the rule-based detection engine (`DisparityAnalysisEngine`) against isolated ground-truth labels (`data/ground_truth/ground_truth.json`). 

Ground truth labels were synthesized during a separate scenario-injection phase after generating baseline records, and are strictly isolated from analytical feature inputs.

---

## 2. Global Detection Metrics

| Metric | Measured Value | Benchmark Target | Result |
| :--- | :--- | :--- | :--- |
| **Precision** | **1.0000 (100.0%)** | &ge; 0.95 | **PASSED** |
| **Recall** | **1.0000 (100.0%)** | &ge; 0.95 | **PASSED** |
| **F1 Score** | **1.0000** | &ge; 0.95 | **PASSED** |
| **Total Scenarios Evaluated** | 10 | 10 | Complete Coverage |
| **True Positives (TP)** | 7 | - | Detected anomalies |
| **False Positives (FP)** | 0 | - | Zero false alarms |
| **True Negatives (TN)** | 3 | - | Correct boundary cases |
| **False Negatives (FN)** | 0 | - | Zero missed anomalies |

---

## 3. Confusion Matrix

```
                      Actual Positive (Anomaly)    Actual Negative (Valid)
Predicted Positive                7                            0
Predicted Negative                0                            3
```

---

## 4. Per-Scenario Detection Results

| Scenario ID | Category | Expected Outcome | Observed Outcome | Associated Rule | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SCENARIO_A` | Expired Compensation Band | `DATA_QUALITY_EXCEPTION` | `DATA_QUALITY_EXCEPTION` | `RULE-DQ-001` | **DETECTED** |
| `SCENARIO_B` | FTE Ignored in Analysis | `DATA_QUALITY_EXCEPTION` | `DATA_QUALITY_EXCEPTION` | `RULE-DQ-003` | **DETECTED** |
| `SCENARIO_C` | Missing Currency FX Rate | `DATA_QUALITY_EXCEPTION` | `DATA_QUALITY_EXCEPTION` | `RULE-DQ-002` | **DETECTED** |
| `SCENARIO_D` | Unauthorized Adjustment | `DATA_QUALITY_EXCEPTION` | `DATA_QUALITY_EXCEPTION` | `RULE-DQ-005` | **DETECTED** |
| `SCENARIO_E` | Invalid Comparable Group | `DATA_QUALITY_EXCEPTION` | `DATA_QUALITY_EXCEPTION` | `RULE-DQ-004` | **DETECTED** |
| `OUTLIER_BELOW_BAND` | Outlier Below Band Min (< 0%) | `REVIEW_CANDIDATE` | `REVIEW_CANDIDATE` | `RULE-DISP-001` | **DETECTED** |
| `OUTLIER_ABOVE_BAND` | Outlier Above Band Max (> 100%)| `REVIEW_CANDIDATE` | `REVIEW_CANDIDATE` | `RULE-DISP-002` | **DETECTED** |
| `BOUNDARY_EXACT_MIN` | Salary at Exact Band Minimum | `VALID` | `VALID` | None | **CORRECT_NEGATIVE** |
| `BOUNDARY_EXACT_MID` | Salary at Exact Band Midpoint | `VALID` | `VALID` | None | **CORRECT_NEGATIVE** |
| `BOUNDARY_EXACT_MAX` | Salary at Exact Band Maximum | `VALID` | `VALID` | None | **CORRECT_NEGATIVE** |

---

## 5. Dataset Determinism & Reproducibility
- **Fixed Seed:** `20261022`
- **Verification Script:** `scripts/check_reproducibility.py`
- **Methodology:** Generated full datasets twice in isolated temporary directories.
- **Results:**
  - Entity row counts: 100% identical.
  - Primary and foreign keys: 100% identical.
  - Bitwise SHA-256 file hashes across all 16 generated CSV files: **100% BITWISE MATCH**.
