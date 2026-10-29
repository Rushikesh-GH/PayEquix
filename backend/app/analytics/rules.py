"""
Disparity Detection Rules & Data Quality Definitions.
Separates data-quality exceptions from statistical compensation review candidates.
"""

from typing import Dict, Any, List

# Rule Definitions
RULES = {
    # Data Quality Rules
    "RULE-DQ-001": {
        "id": "RULE-DQ-001",
        "name": "Expired Compensation Band",
        "category": "DATA_QUALITY",
        "severity": "CRITICAL",
        "issue_type": "EXPIRED_BAND",
        "description": "Salary record compared against a compensation band that expired before the salary effective date.",
        "recommended_action": "Investigate and update compensation band effective dates or reassign to valid current band."
    },
    "RULE-DQ-002": {
        "id": "RULE-DQ-002",
        "name": "Missing Exchange Rate",
        "category": "DATA_QUALITY",
        "severity": "CRITICAL",
        "issue_type": "MISSING_EXCHANGE_RATE",
        "description": "Salary record uses a foreign currency with no effective-dated conversion rate to reporting currency.",
        "recommended_action": "Provide verified market exchange rate for the required effective date in exchange_rates table."
    },
    "RULE-DQ-003": {
        "id": "RULE-DQ-003",
        "name": "FTE Normalization Error",
        "category": "DATA_QUALITY",
        "severity": "HIGH",
        "issue_type": "NORMALIZATION_ERROR",
        "description": "FTE is missing, zero, negative, or exceeds 1.0, or part-time salary was left unadjusted.",
        "recommended_action": "Correct employee FTE record to a valid value between 0.1 and 1.0."
    },
    "RULE-DQ-004": {
        "id": "RULE-DQ-004",
        "name": "Invalid Comparable Group Membership",
        "category": "DATA_QUALITY",
        "severity": "HIGH",
        "issue_type": "INVALID_COMPARABLE_GROUP",
        "description": "Employee assigned to comparable group with materially incompatible role without approved equivalency rationale.",
        "recommended_action": "Exclude from group statistics or document and approve formal role-equivalency justification."
    },
    "RULE-DQ-005": {
        "id": "RULE-DQ-005",
        "name": "Unauthorized Adjustment Application",
        "category": "DATA_QUALITY",
        "severity": "CRITICAL",
        "issue_type": "UNAUTHORIZED_ADJUSTMENT",
        "description": "Salary adjustment was marked as applied without required approvals or self-approved.",
        "recommended_action": "Revert unapproved salary change, conduct audit investigation, and re-submit through proper approval chain."
    },

    # Compensation Disparity Rules (Review Candidates)
    "RULE-DISP-001": {
        "id": "RULE-DISP-001",
        "name": "Compensation Below Band Minimum",
        "category": "COMPENSATION_REVIEW",
        "severity": "HIGH",
        "issue_type": "OUTLIER_BELOW_BAND",
        "description": "FTE-normalized salary falls below the minimum boundary of the applicable compensation band (< 0%).",
        "recommended_action": "Evaluate for immediate salary adjustment proposal to bring employee to at least band minimum."
    },
    "RULE-DISP-002": {
        "id": "RULE-DISP-002",
        "name": "Compensation Above Band Maximum",
        "category": "COMPENSATION_REVIEW",
        "severity": "MEDIUM",
        "issue_type": "OUTLIER_ABOVE_BAND",
        "description": "FTE-normalized salary exceeds the maximum boundary of the applicable compensation band (> 100%).",
        "recommended_action": "Review employee career level, consider promotion to next band or lump-sum merit policy."
    },
    "RULE-DISP-003": {
        "id": "RULE-DISP-003",
        "name": "Severe Midpoint Disparity",
        "category": "COMPENSATION_REVIEW",
        "severity": "MEDIUM",
        "issue_type": "SEVERE_MIDPOINT_DISPARITY",
        "description": "Compa-ratio is significantly below benchmark midpoint (compa_ratio < 0.85).",
        "recommended_action": "Examine tenure, recent performance reviews, and market parity to determine if adjustment is warranted."
    },
    "RULE-DISP-004": {
        "id": "RULE-DISP-004",
        "name": "Comparable Group Median Outlier",
        "category": "COMPENSATION_REVIEW",
        "severity": "MEDIUM",
        "issue_type": "GROUP_OUTLIER",
        "description": "FTE-normalized salary deviates materially (> 20% or 1.5x IQR) from the comparable peer group median.",
        "recommended_action": "Conduct peer group equity review factoring in experience and performance ratings."
    },
    "RULE-DISP-005": {
        "id": "RULE-DISP-005",
        "name": "Promotion Salary Inconsistency",
        "category": "COMPENSATION_REVIEW",
        "severity": "HIGH",
        "issue_type": "PROMOTION_INCONSISTENCY",
        "description": "Recent promotion to a higher level without an accompanying salary adjustment, resulting in low band position.",
        "recommended_action": "Verify if promotional increase was omitted or delayed; submit promotional salary adjustment."
    }
}
