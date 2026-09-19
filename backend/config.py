import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

UPLOAD_DIR = BASE_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_data"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]

IBM_WATSONX_API_KEY = os.getenv("IBM_WATSONX_API_KEY", "").strip()
IBM_WATSONX_PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID", "").strip()
IBM_WATSONX_URL = os.getenv(
    "IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com"
).strip().rstrip("/")
IBM_GRANITE_MODEL = os.getenv(
    "IBM_GRANITE_MODEL", "ibm/granite-3-8b-instruct"
).strip()

_force_demo = os.getenv("DEMO_MODE", "true").lower() in ("1", "true", "yes")


def ibm_credentials_configured() -> bool:
    return bool(IBM_WATSONX_API_KEY and IBM_WATSONX_PROJECT_ID and IBM_WATSONX_URL)


def is_demo_mode() -> bool:
    if _force_demo:
        return True
    return not ibm_credentials_configured()


def health_payload() -> dict:
    demo = is_demo_mode()
    return {
        "status": "ok",
        "demo_mode": demo,
        "ibm_configured": ibm_credentials_configured() and not _force_demo,
        "message": (
            "Demo Mode – IBM Granite API is not connected."
            if demo
            else "IBM Granite API is configured."
        ),
    }
