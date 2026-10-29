"""
Evaluation Metrics Pipeline.
Compares analytical detector outputs against isolated ground-truth labels.
Computes:
  - Precision, Recall, F1-Score
  - Confusion Matrix (TP, FP, TN, FN)
  - Per-Rule Precision and Recall
  - Per-Scenario Detection Rates (Scenario A, B, C, D, E, Boundary cases)
Produces evaluation_summary.json, evaluation_summary.csv, confusion_matrix.csv, per_rule_metrics.csv.
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.database import SessionLocal
from app.models import Employee, SalaryRecord, DataQualityIssue, AdjustmentProposal
from app.analytics.engine import DisparityAnalysisEngine

DATA_DIR = ROOT_DIR / "data"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"
MANIFESTS_DIR = DATA_DIR / "manifests"

def run_evaluation():
    db = SessionLocal()
    gt_file = GROUND_TRUTH_DIR / "ground_truth.json"
    if not gt_file.exists():
        print(f"Error: Ground truth file {gt_file} not found.")
        sys.exit(1)

    with open(gt_file, "r", encoding="utf-8") as f:
        ground_truth_records = json.load(f)

    print("\n========================================================")
    print("RUNNING EVALUATION METRICS PIPELINE AGAINST GROUND TRUTH")
    print("========================================================\n")

    engine = DisparityAnalysisEngine(db)
    analysis_results = {r["employee_id"]: r for r in engine.analyze_all()}

    # Also check proposal-level anomalies (Scenario D) and comparable-group anomalies (Scenario E)
    dq_issues = {d.entity_id: d for d in db.query(DataQualityIssue).all()}

    tp = 0
    fp = 0
    tn = 0
    fn = 0

    per_rule_stats = {}
    per_scenario_results = {}

    for gt in ground_truth_records:
        scen_id = gt["scenario_id"]
        entity_id = gt["entity_id"]
        expected_dec = gt["expected_decision"]
        expected_rule = gt["expected_detection_rule"]

        # Check observed decision
        observed_dec = "VALID"
        observed_rules = []

        if gt["entity_type"] == "EMPLOYEE":
            res = analysis_results.get(entity_id)
            if res:
                observed_dec = res["status"]
                observed_rules = [ex.get("id") for ex in res.get("exceptions_detail", [])]
        elif gt["entity_type"] == "SALARY_RECORD":
            # Find employee for this salary record
            sr = db.query(SalaryRecord).filter(SalaryRecord.salary_record_id == entity_id).first()
            if sr:
                res = analysis_results.get(sr.employee_id)
                if res:
                    observed_dec = res["status"]
                    observed_rules = [ex.get("id") for ex in res.get("exceptions_detail", [])]
        elif gt["entity_type"] in ["ADJUSTMENT_PROPOSAL", "COMPARABLE_GROUP"]:
            # Check data quality table
            dqi = dq_issues.get(entity_id)
            if dqi:
                observed_dec = "DATA_QUALITY_EXCEPTION"
                observed_rules = [dqi.detection_rule]

        # Initialize per-rule stats
        if expected_rule != "NONE":
            per_rule_stats.setdefault(expected_rule, {"tp": 0, "fp": 0, "fn": 0})

        # Evaluate against expectation
        is_anomaly_expected = (expected_dec in ["DATA_QUALITY_EXCEPTION", "REVIEW_CANDIDATE"])
        is_anomaly_observed = (observed_dec in ["DATA_QUALITY_EXCEPTION", "REVIEW_CANDIDATE"])

        matched_rule = (expected_rule in observed_rules) or (expected_rule == "NONE" and not observed_rules)

        if is_anomaly_expected:
            if is_anomaly_observed and (matched_rule or expected_dec == observed_dec):
                tp += 1
                if expected_rule in per_rule_stats:
                    per_rule_stats[expected_rule]["tp"] += 1
                per_scenario_results[scen_id] = {
                    "status": "DETECTED",
                    "expected": expected_dec,
                    "observed": observed_dec,
                    "rule": expected_rule
                }
            else:
                fn += 1
                if expected_rule in per_rule_stats:
                    per_rule_stats[expected_rule]["fn"] += 1
                per_scenario_results[scen_id] = {
                    "status": "MISSED",
                    "expected": expected_dec,
                    "observed": observed_dec,
                    "rule": expected_rule
                }
        else:
            if not is_anomaly_observed:
                tn += 1
                per_scenario_results[scen_id] = {
                    "status": "CORRECT_NEGATIVE",
                    "expected": expected_dec,
                    "observed": observed_dec,
                    "rule": "NONE"
                }
            else:
                fp += 1
                per_scenario_results[scen_id] = {
                    "status": "FALSE_POSITIVE",
                    "expected": expected_dec,
                    "observed": observed_dec,
                    "rule": observed_rules[0] if observed_rules else "UNKNOWN"
                }

    db.close()

    # Calculate metrics with zero-denominator safety
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print(f"Total Evaluated Ground Truth Cases: {len(ground_truth_records)}")
    print(f"True Positives (TP):  {tp}")
    print(f"False Positives (FP): {fp}")
    print(f"True Negatives (TN):  {tn}")
    print(f"False Negatives (FN): {fn}")
    print(f"Precision:            {precision:.4f} ({precision*100:.1f}%)")
    print(f"Recall:               {recall:.4f} ({recall*100:.1f}%)")
    print(f"F1 Score:             {f1_score:.4f}")

    print("\nPer-Scenario Detection Rates:")
    for sc, det in per_scenario_results.items():
        print(f"  - {sc:25s}: {det['status']} (Expected: {det['expected']}, Observed: {det['observed']})")

    # Format output manifest
    summary = {
        "status": "COMPLETED",
        "total_scenarios": len(ground_truth_records),
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1_score, 4),
        "per_scenario_results": per_scenario_results,
        "per_rule_metrics": {
            r: {
                "tp": s["tp"],
                "fp": s["fp"],
                "fn": s["fn"],
                "precision": round(s["tp"] / (s["tp"] + s["fp"]), 4) if (s["tp"] + s["fp"]) > 0 else 1.0,
                "recall": round(s["tp"] / (s["tp"] + s["fn"]), 4) if (s["tp"] + s["fn"]) > 0 else 1.0
            }
            for r, s in per_rule_stats.items()
        }
    }

    # Write JSON summary
    with open(MANIFESTS_DIR / "evaluation_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Write evaluation_summary.csv
    with open(MANIFESTS_DIR / "evaluation_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Scenarios", len(ground_truth_records)])
        writer.writerow(["True Positives", tp])
        writer.writerow(["False Positives", fp])
        writer.writerow(["True Negatives", tn])
        writer.writerow(["False Negatives", fn])
        writer.writerow(["Precision", round(precision, 4)])
        writer.writerow(["Recall", round(recall, 4)])
        writer.writerow(["F1 Score", round(f1_score, 4)])

    # Write confusion_matrix.csv
    with open(MANIFESTS_DIR / "confusion_matrix.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Predicted / Actual", "Actual Positive (Anomaly)", "Actual Negative (Valid)"])
        writer.writerow(["Predicted Positive (Anomaly)", tp, fp])
        writer.writerow(["Predicted Negative (Valid)", fn, tn])

    # Write per_rule_metrics.csv
    with open(MANIFESTS_DIR / "per_rule_metrics.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Rule ID", "TP", "FP", "FN", "Precision", "Recall"])
        for r, m in summary["per_rule_metrics"].items():
            writer.writerow([r, m["tp"], m["fp"], m["fn"], m["precision"], m["recall"]])

    print("\n========================================================")
    print("EVALUATION ARTIFACTS WRITTEN TO:")
    print(f"  - {MANIFESTS_DIR / 'evaluation_summary.json'}")
    print(f"  - {MANIFESTS_DIR / 'evaluation_summary.csv'}")
    print(f"  - {MANIFESTS_DIR / 'confusion_matrix.csv'}")
    print(f"  - {MANIFESTS_DIR / 'per_rule_metrics.csv'}")
    print("========================================================\n")

    return summary

if __name__ == "__main__":
    run_evaluation()
