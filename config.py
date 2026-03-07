"""
Configurações do gravador (variáveis de ambiente + defaults).
Use .env para sobrescrever; nunca commite .env.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_env_str(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default


def _get_env_int(
    name: str,
    default: int,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    raw = os.getenv(name)
    try:
        value = int(raw) if raw not in (None, "") else default
    except (TypeError, ValueError):
        value = default

    if min_value is not None:
        value = max(min_value, value)
    if max_value is not None:
        value = min(max_value, value)

    return value


BASE_DIR = Path(__file__).resolve().parent

GRAVACOES_DIR = Path(_get_env_str("GRAVACOES_DIR", str(BASE_DIR / "gravacoes")))
GRAVACOES_DIR.mkdir(parents=True, exist_ok=True)

GDRIVE_PASTA_LOCAL = _get_env_str("GDRIVE_PASTA_LOCAL") or None
GDRIVE_PASTA_ID = _get_env_str("GDRIVE_PASTA_ID") or None

CODEC = _get_env_str("CODEC", "av1").lower()
VALID_CODECS = {"av1", "hevc_nvenc", "hevc", "h264"}
if CODEC not in VALID_CODECS:
    CODEC = "h264"

CRF = _get_env_int("CRF", default=30, min_value=18, max_value=40)
FPS = _get_env_int("FPS", default=30, min_value=10, max_value=60)
AV1_PRESET = _get_env_int("AV1_PRESET", default=10, min_value=0, max_value=13)

TEAMS_WINDOW_TITLE = _get_env_str("TEAMS_WINDOW_TITLE", "Teams")
TEAMS_SCREEN_SHARE_KEYWORDS = _get_env_str(
    "TEAMS_SCREEN_SHARE_KEYWORDS",
    "Compartilhando|Sharing|Screen|Partage",
)

AUDIO_DEVICE_DSHOW = _get_env_str("AUDIO_DEVICE_DSHOW") or None

HEALTH_CHECK_INTERVAL_SEC = _get_env_int(
    "HEALTH_CHECK_INTERVAL_SEC",
    default=10,
    min_value=5,
    max_value=60,
)
HEALTH_CHECK_STALL_SECONDS = _get_env_int(
    "HEALTH_CHECK_STALL_SECONDS",
    default=30,
    min_value=15,
    max_value=300,
)

CRF_OFFSET_SCREEN_SHARE = _get_env_int(
    "CRF_OFFSET_SCREEN_SHARE",
    default=3,
    min_value=0,
    max_value=10,
)

LOG_LEVEL = _get_env_str("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path(_get_env_str("LOG_DIR", str(BASE_DIR / "logs")))
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG_FILE = LOG_DIR / "audit.log"

FFMPEG_LOGLEVEL = _get_env_str("FFMPEG_LOGLEVEL", "warning")
