"""
Disparity Detection & Explainable Pay Equity Analysis Engine.
Rule-based, explainable, transparent calculations.
Distinguishes Data Quality Exceptions from Statistical Compensation Review Candidates.
"""

from datetime import date
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from sqlalchemy.orm import Session

from app.models import (
    Employee, SalaryRecord, CompensationBand, ExchangeRate,
    ComparableGroup, ComparableGroupMember, Promotion, AdjustmentProposal,
    AdjustmentApplicationEvent, DataQualityIssue
)
from app.analytics.normalization import (
    annualize_salary, convert_currency, normalize_fte,
    calculate_compa_ratio, calculate_band_position,
    NormalizationError, MissingExchangeRateException
)
from app.analytics.rules import RULES
from app.config import settings

class DisparityAnalysisEngine:
    def __init__(self, db: Session, reporting_currency: str = "USD"):
        self.db = db
        self.reporting_currency = reporting_currency
        self._rate_cache = {}
        self._band_cache = {}
        self._active_proposal_set = None

    def get_effective_exchange_rate(self, from_curr: str, to_curr: str, as_of: date) -> Optional[float]:
        """Lookup latest effective exchange rate on or before as_of date."""
        if from_curr == to_curr:
            return 1.0
        cache_key = (from_curr, to_curr, as_of)
        if cache_key in self._rate_cache:
            return self._rate_cache[cache_key]

        rate_record = (
            self.db.query(ExchangeRate)
            .filter(
                ExchangeRate.from_currency == from_curr,
                ExchangeRate.to_currency == to_curr,
                ExchangeRate.effective_date <= as_of
            )
            .order_by(ExchangeRate.effective_date.desc())
            .first()
        )
        val = rate_record.rate if rate_record else None
        self._rate_cache[cache_key] = val
        return val

    def get_applicable_band(
        self, role_id: str, level_id: str, location_id: str, as_of: date
    ) -> Tuple[Optional[CompensationBand], Optional[str]]:
        """
        Lookup applicable compensation band on as_of date.
        Returns (band, error_reason).
        Distinguishes active bands from expired bands.
        """
        cache_key = (role_id, level_id, location_id, as_of)
        if cache_key in self._band_cache:
            return self._band_cache[cache_key]

        # First check if any band matches exactly on the date
        valid_band = (
            self.db.query(CompensationBand)
            .filter(
                CompensationBand.role_id == role_id,
                CompensationBand.level_id == level_id,
                CompensationBand.location_id == location_id,
                CompensationBand.effective_start_date <= as_of,
                (CompensationBand.effective_end_date.is_(None) | (CompensationBand.effective_end_date >= as_of))
            )
            .order_by(CompensationBand.band_version.desc())
            .first()
        )
        if valid_band:
            res = (valid_band, None)
            self._band_cache[cache_key] = res
            return res

        # Check if an expired band exists (Scenario A)
        expired_band = (
            self.db.query(CompensationBand)
            .filter(
                CompensationBand.role_id == role_id,
                CompensationBand.level_id == level_id,
                CompensationBand.location_id == location_id,
                CompensationBand.effective_end_date < as_of
            )
            .order_by(CompensationBand.effective_end_date.desc())
            .first()
        )
        if expired_band:
            res = (expired_band, "EXPIRED_BAND")
            self._band_cache[cache_key] = res
            return res

        res = (None, "MISSING_BAND")
        self._band_cache[cache_key] = res
        return res

    def analyze_employee(
        self, employee: Employee, as_of_date: date = date(2026, 1, 1)
    ) -> Dict[str, Any]:
        """
        Analyze a single employee record on the given effective date.
        Returns comprehensive analytical result with full math provenance.
        """
        # 1. Fetch latest active salary record on or before as_of_date
        salary = (
            self.db.query(SalaryRecord)
            .filter(
                SalaryRecord.employee_id == employee.employee_id,
                SalaryRecord.effective_date <= as_of_date
            )
            .order_by(SalaryRecord.effective_date.desc())
            .first()
        )

        result: Dict[str, Any] = {
            "employee_id": employee.employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "role_id": employee.role_id,
            "role_name": employee.role.role_name if employee.role else employee.role_id,
            "level_id": employee.level_id,
            "level_name": employee.level.level_name if employee.level else employee.level_id,
            "location_id": employee.location_id,
            "location_name": f"{employee.location.city}, {employee.location.country}" if employee.location else employee.location_id,
            "currency": employee.location.currency_code if employee.location else "USD",
            "actual_base_salary": 0.0,
            "fte": employee.fte,
            "annualized_salary": 0.0,
            "reporting_currency": self.reporting_currency,
            "exchange_rate": 1.0,
            "normalized_fte_salary": 0.0,
            "applicable_band_id": None,
            "band_min": None,
            "band_mid": None,
            "band_max": None,
            "compa_ratio": None,
            "band_position": None,
            "is_below_band": False,
            "is_above_band": False,
            "is_underpaid_midpoint": False,
            "comparable_group_id": None,
            "comparable_group_size": None,
            "group_median_salary": None,
            "is_group_outlier": False,
            "status": "VALID",
            "exception_reasons": [],
            "exceptions_detail": [],
            "has_active_proposal": False
        }

        if not salary:
            result["status"] = "DATA_QUALITY_EXCEPTION"
            result["exception_reasons"].append("NO_SALARY_RECORD")
            return result

        result["actual_base_salary"] = salary.base_salary
        result["currency"] = salary.currency_code
        result["annualized_salary"] = salary.annualized_salary

        # 2. Check FTE validity and normalization consistency (Scenario B check)
        if employee.fte is None or employee.fte < 0.1 or employee.fte > 1.0:
            result["status"] = "DATA_QUALITY_EXCEPTION"
            result["exception_reasons"].append("NORMALIZATION_ERROR: Invalid FTE value")
            result["exceptions_detail"].append(RULES["RULE-DQ-003"])
        elif employee.employment_type == "part_time" and salary.fte_at_record == 1.0 and employee.fte < 1.0:
            result["status"] = "DATA_QUALITY_EXCEPTION"
            result["exception_reasons"].append(f"NORMALIZATION_ERROR: FTE ignored in analysis (employee FTE is {employee.fte}, record evaluated without FTE adjustment)")
            result["exceptions_detail"].append(RULES["RULE-DQ-003"])

        # 3. Currency Normalization (Scenario C check)
        rate = self.get_effective_exchange_rate(salary.currency_code, self.reporting_currency, salary.effective_date)
        if rate is None:
            result["status"] = "DATA_QUALITY_EXCEPTION"
            result["exception_reasons"].append(f"MISSING_EXCHANGE_RATE: No rate for {salary.currency_code} to {self.reporting_currency}")
            result["exceptions_detail"].append(RULES["RULE-DQ-002"])
            return result

        result["exchange_rate"] = rate

        # Calculate normalized FTE salary
        try:
            norm_curr = convert_currency(salary.annualized_salary, salary.currency_code, self.reporting_currency, rate)
            norm_fte = normalize_fte(norm_curr, employee.fte if 0.1 <= employee.fte <= 1.0 else 1.0)
            result["normalized_fte_salary"] = norm_fte
        except NormalizationError as e:
            result["status"] = "DATA_QUALITY_EXCEPTION"
            result["exception_reasons"].append(f"NORMALIZATION_ERROR: {str(e)}")
            result["exceptions_detail"].append(RULES["RULE-DQ-003"])
            return result

        # 4. Resolve Effective-Dated Band (Scenario A check)
        band, band_err = self.get_applicable_band(
            employee.role_id, employee.level_id, employee.location_id, salary.effective_date
        )

        if band_err == "EXPIRED_BAND":
            result["status"] = "DATA_QUALITY_EXCEPTION"
            result["applicable_band_id"] = band.band_id if band else None
            result["exception_reasons"].append(f"EXPIRED_BAND: Band {band.band_id if band else ''} expired before salary date {salary.effective_date}")
            result["exceptions_detail"].append(RULES["RULE-DQ-001"])
            return result
        elif band_err == "MISSING_BAND" or not band:
            result["status"] = "DATA_QUALITY_EXCEPTION"
            result["exception_reasons"].append("MISSING_BAND: No compensation band configured")
            return result

        result["applicable_band_id"] = band.band_id

        # Normalize band values to reporting currency
        band_rate = self.get_effective_exchange_rate(band.currency_code, self.reporting_currency, salary.effective_date)
        if band_rate is None:
            result["status"] = "DATA_QUALITY_EXCEPTION"
            result["exception_reasons"].append(f"MISSING_EXCHANGE_RATE for band currency {band.currency_code}")
            result["exceptions_detail"].append(RULES["RULE-DQ-002"])
            return result

        band_min_norm = convert_currency(band.minimum_salary, band.currency_code, self.reporting_currency, band_rate)
        band_mid_norm = convert_currency(band.midpoint_salary, band.currency_code, self.reporting_currency, band_rate)
        band_max_norm = convert_currency(band.maximum_salary, band.currency_code, self.reporting_currency, band_rate)

        result["band_min"] = band_min_norm
        result["band_mid"] = band_mid_norm
        result["band_max"] = band_max_norm

        # 5. Compa-ratio and Band Position
        try:
            cr = calculate_compa_ratio(result["normalized_fte_salary"], band_mid_norm)
            bp = calculate_band_position(result["normalized_fte_salary"], band_min_norm, band_max_norm)
            result["compa_ratio"] = cr
            result["band_position"] = bp

            # Evaluate Disparity Rules
            if bp < settings.BAND_POSITION_LOW_THRESHOLD:  # < 0%
                result["is_below_band"] = True
                result["status"] = "REVIEW_CANDIDATE" if result["status"] == "VALID" else result["status"]
                result["exception_reasons"].append(f"OUTLIER_BELOW_BAND: Position is {bp}% (< 0%)")
                result["exceptions_detail"].append(RULES["RULE-DISP-001"])

            elif bp > settings.BAND_POSITION_HIGH_THRESHOLD * 100.0:  # > 100%
                result["is_above_band"] = True
                result["status"] = "REVIEW_CANDIDATE" if result["status"] == "VALID" else result["status"]
                result["exception_reasons"].append(f"OUTLIER_ABOVE_BAND: Position is {bp}% (> 100%)")
                result["exceptions_detail"].append(RULES["RULE-DISP-002"])

            if cr < settings.COMPA_RATIO_LOW_THRESHOLD:  # < 0.85
                result["is_underpaid_midpoint"] = True
                result["status"] = "REVIEW_CANDIDATE" if result["status"] == "VALID" else result["status"]
                result["exception_reasons"].append(f"SEVERE_MIDPOINT_DISPARITY: Compa-ratio is {cr} (< {settings.COMPA_RATIO_LOW_THRESHOLD})")
                result["exceptions_detail"].append(RULES["RULE-DISP-003"])

        except NormalizationError as e:
            result["status"] = "DATA_QUALITY_EXCEPTION"
            result["exception_reasons"].append(f"METRIC_CALC_ERROR: {str(e)}")

        # 6. Check Active Proposal
        if self._active_proposal_set is None:
            active_prop = (
                self.db.query(AdjustmentProposal)
                .filter(
                    AdjustmentProposal.employee_id == employee.employee_id,
                    AdjustmentProposal.proposal_status.in_(["draft", "pending_review", "approved"])
                )
                .first()
            )
            if active_prop:
                result["has_active_proposal"] = True
        else:
            result["has_active_proposal"] = employee.employee_id in self._active_proposal_set

        return result

    def analyze_all(self, as_of_date: date = date(2026, 1, 1)) -> List[Dict[str, Any]]:
        """
        Run compensation analysis across all active employees.
        Includes comparable group aggregation and group outlier detection.
        Optimized with batch pre-fetching.
        """
        # Pre-load active proposals
        active_props = (
            self.db.query(AdjustmentProposal.employee_id)
            .filter(AdjustmentProposal.proposal_status.in_(["draft", "pending_review", "approved"]))
            .all()
        )
        self._active_proposal_set = {p[0] for p in active_props}

        employees = self.db.query(Employee).filter(Employee.employment_status == "active").all()
        results = []

        for emp in employees:
            res = self.analyze_employee(emp, as_of_date)
            results.append(res)

        # Comparable Group Statistics & Outlier Check
        # Group valid results by role_id and level_id
        valid_by_group: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for r in results:
            if r["status"] in ["VALID", "REVIEW_CANDIDATE"]:
                key = (r["role_id"], r["level_id"])
                valid_by_group.setdefault(key, []).append(r)

        for key, members in valid_by_group.items():
            count = len(members)
            if count >= settings.GROUP_MIN_SIZE:
                salaries = [m["normalized_fte_salary"] for m in members]
                med = float(np.median(salaries))
                q25, q75 = float(np.percentile(salaries, 25)), float(np.percentile(salaries, 75))
                iqr = q75 - q25

                for m in members:
                    m["comparable_group_id"] = f"GRP-{key[0]}-{key[1]}"
                    m["comparable_group_size"] = count
                    m["group_median_salary"] = round(med, 2)

                    # Deviation check: > 25% from median AND 1.5 IQR
                    dev_pct = abs(m["normalized_fte_salary"] - med) / med if med > 0 else 0
                    if dev_pct > settings.GROUP_MAX_DEVIATION_PCT and (iqr > 0 and (m["normalized_fte_salary"] < q25 - 1.5 * iqr or m["normalized_fte_salary"] > q75 + 1.5 * iqr)):
                        m["is_group_outlier"] = True
                        if m["status"] == "VALID":
                            m["status"] = "REVIEW_CANDIDATE"
                        reason = f"GROUP_OUTLIER: Deviation of {round(dev_pct*100, 1)}% from group median ({round(med, 2)})"
                        if reason not in m["exception_reasons"]:
                            m["exception_reasons"].append(reason)
                            m["exceptions_detail"].append(RULES["RULE-DISP-004"])

        return results
