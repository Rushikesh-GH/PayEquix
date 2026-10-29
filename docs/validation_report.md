# Automated Data Validation Report

## Execution Summary
- **Execution Timestamp:** 2026-10-27T10:27:13Z
- **Profile:** Full Production Benchmark (5,000 employees)
- **Random Seed:** 20261022
- **Validation Suite:** 22 Automated Integrity & Arithmetic Checks
- **Overall Result:** **22 / 22 PASSED (100.0%)**

---

## Detailed Check Execution Results

| Check ID | Description | Records Inspected | Failures Count | Status | Suggested Remediation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CHK-01` | Primary-key uniqueness across master entities | 5,000 | 0 | **PASS** | None required |
| `CHK-02` | Foreign-key integrity on Employee associations | 5,000 | 0 | **PASS** | None required |
| `CHK-03` | Referential completeness: active employees have salary records | 5,000 | 0 | **PASS** | None required |
| `CHK-04` | Employee status and employment_type domain constraints | 5,000 | 0 | **PASS** | None required |
| `CHK-05` | Salary-band boundary ordering (`min < mid < max`) | 6,000 | 0 | **PASS** | None required |
| `CHK-06` | Compensation band effective-date temporal integrity | 6,000 | 0 | **PASS** | None required |
| `CHK-07` | Unique monthly salary identifiers per employee | 15,228 | 0 | **PASS** | None required |
| `CHK-08` | Currency conversion arithmetic correctness | 200 | 0 | **PASS** | None required |
| `CHK-09` | Salary annualization arithmetic consistency | 200 | 0 | **PASS** | None required |
| `CHK-10` | FTE-normalization arithmetic correctness | 200 | 0 | **PASS** | None required |
| `CHK-11` | Compa-ratio arithmetic correctness (`salary / midpoint`) | 1 | 0 | **PASS** | None required |
| `CHK-12` | Within-band position percentage and unclipped outlier retention | 2 | 0 | **PASS** | None required |
| `CHK-13` | Promotion resulting salary record linkage consistency | 221 | 0 | **PASS** | None required |
| `CHK-14` | Company tenure dates consistent with employee hire dates | 5,000 | 0 | **PASS** | None required |
| `CHK-15` | Adjustment proposal lifecycle states adherence | 40 | 0 | **PASS** | None required |
| `CHK-16` | Separation of duties: creator cannot approve own proposal | 40 | 0 | **PASS** | None required |
| `CHK-17` | Applied proposals reconcile with application events | 7 | 0 | **PASS** | None required |
| `CHK-18` | Consequential state changes captured in append-only audit log | 15 | 0 | **PASS** | None required |
| `CHK-19` | Ground-truth isolation from analytical feature inputs | 1 | 0 | **PASS** | None required |
| `CHK-20` | Comparable-group minimum size threshold & rationale rules | 200 | 0 | **PASS** | None required |
| `CHK-21` | Deterministic zero-padded primary key identifier formatting | 5,000 | 0 | **PASS** | None required |
| `CHK-22` | Generation manifest and SHA-256 provenance checksums present | 1 | 0 | **PASS** | None required |

---

## Conclusion
All 22 standalone checks passed with zero integrity defects across master tables, transactional salary records, promotions, approval workflows, and audit events.
