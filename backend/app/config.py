import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_NAME: str = os.getenv("APP_NAME", "Compensation Disparity Analysis & Explainable Pay Equity System")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'compensation_equity.db'}")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-insecure-secret-key-change-in-production-20261022")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    # Analytics Config
    DEFAULT_REPORTING_CURRENCY: str = os.getenv("DEFAULT_REPORTING_CURRENCY", "USD")
    COMPA_RATIO_LOW_THRESHOLD: float = float(os.getenv("COMPA_RATIO_LOW_THRESHOLD", "0.80"))
    COMPA_RATIO_HIGH_THRESHOLD: float = float(os.getenv("COMPA_RATIO_HIGH_THRESHOLD", "1.20"))
    BAND_POSITION_LOW_THRESHOLD: float = float(os.getenv("BAND_POSITION_LOW_THRESHOLD", "0.0"))
    BAND_POSITION_HIGH_THRESHOLD: float = float(os.getenv("BAND_POSITION_HIGH_THRESHOLD", "1.0"))
    GROUP_MIN_SIZE: int = int(os.getenv("GROUP_MIN_SIZE", "5"))
    GROUP_OUTLIER_IQR_MULTIPLIER: float = float(os.getenv("GROUP_OUTLIER_IQR_MULTIPLIER", "1.5"))
    GROUP_MAX_DEVIATION_PCT: float = float(os.getenv("GROUP_MAX_DEVIATION_PCT", "0.25"))

    # Seed
    RANDOM_SEED: int = int(os.getenv("RANDOM_SEED", "20261022"))
    DATASET_PROFILE: str = os.getenv("DATASET_PROFILE", "full")

settings = Settings()
