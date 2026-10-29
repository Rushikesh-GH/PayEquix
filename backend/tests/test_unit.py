import pytest
from app.analytics.normalization import (
    annualize_salary, convert_currency, normalize_fte,
    calculate_compa_ratio, calculate_band_position,
    NormalizationError, MissingExchangeRateException
)

def test_annualize_salary():
    # Annual salary remains identical
    assert annualize_salary(120000.0, is_monthly=False) == 120000.0
    # Monthly salary multiplies by 12
    assert annualize_salary(10000.0, is_monthly=True) == 120000.0
    # Negative salary raises NormalizationError
    with pytest.raises(NormalizationError):
        annualize_salary(-5000.0)

def test_convert_currency():
    # Same currency has rate 1.0
    assert convert_currency(100000.0, "USD", "USD", 1.0) == 100000.0
    # INR to USD conversion (1 INR = 0.012 USD)
    assert convert_currency(1000000.0, "INR", "USD", 0.012) == 12000.0
    # Missing exchange rate raises explicit exception
    with pytest.raises(MissingExchangeRateException):
        convert_currency(1000000.0, "XYZ", "USD", None)
    # Zero/negative rate raises exception
    with pytest.raises(MissingExchangeRateException):
        convert_currency(1000000.0, "EUR", "USD", 0.0)

def test_normalize_fte():
    # Full-time 1.0
    assert normalize_fte(100000.0, 1.0) == 100000.0
    # Half-time 0.5 (salary / 0.5 = 200,000)
    assert normalize_fte(50000.0, 0.5) == 100000.0
    # FTE out of bounds raises error
    with pytest.raises(NormalizationError):
        normalize_fte(50000.0, 0.05)  # < 0.10
    with pytest.raises(NormalizationError):
        normalize_fte(50000.0, 1.20)  # > 1.00

def test_calculate_compa_ratio():
    # Exactly at midpoint
    assert calculate_compa_ratio(100000.0, 100000.0) == 1.0
    # Below midpoint (90k / 100k = 0.90)
    assert calculate_compa_ratio(90000.0, 100000.0) == 0.9000
    # Above midpoint (115k / 100k = 1.15)
    assert calculate_compa_ratio(115000.0, 100000.0) == 1.1500
    # Invalid midpoint raises error
    with pytest.raises(NormalizationError):
        calculate_compa_ratio(100000.0, 0.0)

def test_calculate_band_position_unclipped():
    # Exactly at minimum (0%)
    assert calculate_band_position(80000.0, 80000.0, 120000.0) == 0.0
    # Exactly at midpoint (50%)
    assert calculate_band_position(100000.0, 80000.0, 120000.0) == 50.0
    # Exactly at maximum (100%)
    assert calculate_band_position(120000.0, 80000.0, 120000.0) == 100.0
    # Below minimum (-25.0% - unclipped!)
    assert calculate_band_position(70000.0, 80000.0, 120000.0) == -25.0
    # Above maximum (125.0% - unclipped!)
    assert calculate_band_position(130000.0, 80000.0, 120000.0) == 125.0
    # Inverted min/max raises error
    with pytest.raises(NormalizationError):
        calculate_band_position(100000.0, 120000.0, 80000.0)
