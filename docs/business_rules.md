# Business Rules & Disparity Detection Logic

## 1. Effective-Dated Band Lookup Logic
For an employee $E$ evaluated on effective date $T$:
1. Query `compensation_bands` matching `(role_id, level_id, location_id)`.
2. A band $B$ is **valid and active** if and only if:
   $$B.\text{effective\_start\_date} \le T \quad \text{AND} \quad (B.\text{effective\_end\_date} \text{ IS NULL} \;\lor\; B.\text{effective\_end\_date} \ge T)$$
3. If multiple versions exist, select the band with the highest `band_version`.
4. **Expired Band Policy**: If all matching bands have $B.\text{effective\_end\_date} < T$, the record is flagged as a `DATA_QUALITY_EXCEPTION` (`EXPIRED_BAND`, Rule `RULE-DQ-001`). The engine does not compute misleading parity metrics against an expired band.

---

## 2. Mathematical Normalization Formulas

### A. Annualized Base Salary
$$\text{annualized\_salary} = 
\begin{cases} 
\text{base\_salary} \times 12 & \text{if paid on monthly basis} \\ 
\text{base\_salary} & \text{if paid on annual basis} 
\end{cases}$$
*Constraint:* An already annualized salary is never multiplied by 12 again.

### B. Currency Normalization
All compensation is normalized to the reporting currency (USD) using the latest market rate on or before the salary effective date:
$$\text{normalized\_salary} = \text{source\_salary} \times \text{exchange\_rate\_to\_reporting\_currency}$$
*Convention:* The rate represents target currency per unit of source currency (e.g., 1 INR = 0.0115 USD).
*Constraint:* If no exchange rate exists for the required currency on date $T$, the calculation aborts and flags a `MISSING_EXCHANGE_RATE` data quality exception (`RULE-DQ-002`).

### C. FTE Normalization
Like-for-like full-time equivalent comparison:
$$\text{normalized\_fte\_salary} = \frac{\text{annualized\_salary}}{\text{fte}}$$
*Constraint:* FTE must satisfy $0.10 \le \text{fte} \le 1.00$. If FTE is ignored or missing for a part-time employee, a `NORMALIZATION_ERROR` exception is generated (`RULE-DQ-003`).

### D. Compa-Ratio
$$\text{compa\_ratio} = \frac{\text{normalized\_fte\_salary}}{\text{normalized\_band\_midpoint}}$$
*Healthy Range:* $0.85 \le \text{compa\_ratio} \le 1.15$. Values below 0.85 trigger `SEVERE_MIDPOINT_DISPARITY` (`RULE-DISP-003`).

### E. Within-Band Position Percentage
$$\text{band\_position} = \frac{\text{normalized\_fte\_salary} - \text{normalized\_band\_min}}{\text{normalized\_band\_max} - \text{normalized\_band\_min}} \times 100\%$$
*Outlier Retention Policy:* Values are **never clipped** at 0% or 100%. A position of -25% or 125% is retained verbatim so HR can observe the true magnitude of below-band or above-band disparities.

---

## 3. Disparity Detection Rules Matrix

| Rule ID | Name | Category | Condition | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `RULE-DQ-001` | Expired Compensation Band | Data Quality | Band expired prior to salary date | Refresh compensation bands |
| `RULE-DQ-002` | Missing Exchange Rate | Data Quality | Unknown currency or missing FX rate | Add market rate to table |
| `RULE-DQ-003` | FTE Normalization Error | Data Quality | FTE ignored or out of [0.1, 1.0] | Reconcile employee FTE record |
| `RULE-DQ-004` | Invalid Comparable Group | Data Quality | Disparate roles without approval | Document role equivalency |
| `RULE-DQ-005` | Unauthorized Adjustment | Data Quality | Application attempted without approval | Revert change and audit |
| `RULE-DISP-001` | Below Band Minimum | Review Candidate | `band_position < 0%` | Evaluate market adjustment |
| `RULE-DISP-002` | Above Band Maximum | Review Candidate | `band_position > 100%` | Review level or career promotion |
| `RULE-DISP-003` | Severe Midpoint Disparity | Review Candidate | `compa_ratio < 0.85` | Evaluate tenure and performance |
| `RULE-DISP-004` | Comparable Group Outlier | Review Candidate | Dev > 25% from peer median AND > 1.5 IQR | Peer group equity review |
| `RULE-DISP-005` | Promotion Inconsistency | Review Candidate | Promotion without salary adjustment | Verify promotional increase |

---

## 4. Human Review & Non-Adverse AI Safeguards
1. **Investigation Signals Only:** Statistical flags are classified as investigation signals, never proof of wrongdoing or discrimination.
2. **Protected Characteristics Prohibition:** Protected demographic attributes (gender, race, religion, ethnicity) are strictly excluded from analytical features and pay proposal calculations.
3. **No Automated Decisions:** The platform never automatically applies pay cuts, terminations, or adverse personnel actions.
4. **Separation of Duties:** Proposal creators cannot approve their own submissions; dual-custody approval is enforced at the database and API layers.
