"""
Single reusable compensation-normalization service.
Strictly implements the documented mathematical definitions:
1. Annualized Salary: monthly * 12 or annual amount directly.
2. Currency Normalization: amount * exchange_rate_to_reporting_currency.
3. FTE Normalization: annualized_salary / fte.
4. Compa-Ratio: normalized_fte_salary / normalized_band_midpoint.
5. Within-Band Position: (normalized_fte_salary - normalized_band_min) / (normalized_band_max - normalized_band_min) * 100%.
"""

from typing import Optional, Tuple

class NormalizationError(ValueError):
    """Exception raised for errors in normalization calculation."""
    pass

class MissingExchangeRateException(NormalizationError):
    """Exception raised when effective exchange rate is unavailable."""
    pass

def annualize_salary(base_salary: float, is_monthly: bool = False) -> float:
    """
    Annualize base salary.
    If monthly: base_salary * 12.
    If annual: base_salary directly.
    Never multiply an already annualized salary.
    """
    if base_salary <= 0:
        raise NormalizationError(f"Base salary must be positive, got {base_salary}")
    
    if is_monthly:
        return round(base_salary * 12.0, 2)
    return round(float(base_salary), 2)


def convert_currency(
    amount: float,
    source_currency: str,
    reporting_currency: str,
    exchange_rate: Optional[float]
) -> float:
    """
    Convert salary to reporting currency using effective-dated exchange rate.
    Convention: normalized_salary = source_salary * exchange_rate_to_reporting_currency.
    If source == reporting, rate must be 1.0.
    A missing or invalid exchange rate raises an explicit exception.
    Never silently substitute an unknown rate.
    """
    if source_currency == reporting_currency:
        return round(float(amount), 2)
    
    if exchange_rate is None or exchange_rate <= 0:
        raise MissingExchangeRateException(
            f"Missing or invalid exchange rate from {source_currency} to {reporting_currency}"
        )
    
    return round(amount * exchange_rate, 2)


def normalize_fte(annualized_salary: float, fte: float) -> float:
    """
    Normalize annualized salary to Full-Time-Equivalent (FTE) basis.
    fte_normalized_salary = annualized_salary / fte.
    FTE must be strictly between 0.1 and 1.0.
    """
    if fte is None or fte < 0.1 or fte > 1.0:
        raise NormalizationError(f"FTE must be between 0.1 and 1.0, got {fte}")
    
    return round(annualized_salary / fte, 2)


def calculate_compa_ratio(normalized_fte_salary: float, normalized_band_midpoint: float) -> float:
    """
    Compa-ratio = normalized_fte_salary / normalized_band_midpoint.
    Returns ratio rounded to 4 decimal places (e.g., 0.9520).
    """
    if normalized_band_midpoint <= 0:
        raise NormalizationError(f"Band midpoint must be positive, got {normalized_band_midpoint}")
    
    return round(normalized_fte_salary / normalized_band_midpoint, 4)


def calculate_band_position(
    normalized_fte_salary: float,
    normalized_band_minimum: float,
    normalized_band_maximum: float
) -> float:
    """
    Within-band position:
    band_position = (normalized_fte_salary - normalized_band_minimum) / (normalized_band_maximum - normalized_band_minimum)
    Displayed as percentage (e.g. 50.0 for midpoint, -10.0 for below min, 115.0 for above max).
    Values are NOT clipped to preserve true outlier signals.
    """
    spread = normalized_band_maximum - normalized_band_minimum
    if spread <= 0:
        raise NormalizationError(
            f"Invalid band spread: max ({normalized_band_maximum}) <= min ({normalized_band_minimum})"
        )
    
    position_pct = ((normalized_fte_salary - normalized_band_minimum) / spread) * 100.0
    return round(position_pct, 2)
