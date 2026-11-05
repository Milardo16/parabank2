"""Параметры окружения. Значения берутся из переменных окружения / файла .env."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("BASE_URL", "https://parabank.parasoft.com/parabank").rstrip("/")
    register_path: str = os.getenv("REGISTER_PATH", "/register.htm")
    browser: str = os.getenv("BROWSER", "chrome")
    headless: bool = _bool(os.getenv("HEADLESS", "false"))
    explicit_timeout: int = int(os.getenv("EXPLICIT_TIMEOUT", "10"))
    window_width: int = int(os.getenv("WINDOW_WIDTH", "1366"))
    window_height: int = int(os.getenv("WINDOW_HEIGHT", "900"))
    reports_dir: Path = ROOT / os.getenv("REPORTS_DIR", "reports")


settings = Settings()
