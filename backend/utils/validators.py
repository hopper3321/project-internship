import json
import re
from typing import Any

ALLOWED_IMAGE = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_DOC_EXT = {".pdf", ".txt", ".docx"}
ALLOWED_DOC_MIME = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def normalize_item_key(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def require_non_empty(value: str | None, field: str) -> str:
    if not value or not str(value).strip():
        raise ValueError(f"{field} cannot be empty.")
    return str(value).strip()


def parse_json_from_llm(raw: str) -> dict[str, Any] | None:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None


def validate_waste_analysis(data: dict[str, Any], fallback_item: str) -> dict[str, Any]:
    categories = {
        "Wet Waste",
        "Dry Waste",
        "Recyclable",
        "Non-Recyclable",
        "E-Waste",
        "Hazardous Waste",
        "Organic Waste",
        "Other",
    }
    recyclable = data.get("recyclable")
    if isinstance(recyclable, str):
        recyclable = recyclable.lower() in ("true", "yes", "1")
    elif recyclable is None:
        recyclable = False
    else:
        recyclable = bool(recyclable)

    confidence = data.get("confidence", 0.7)
    try:
        confidence = float(confidence)
        confidence = max(0.0, min(1.0, confidence))
    except (TypeError, ValueError):
        confidence = 0.7

    category = str(data.get("category", "Other"))
    if category not in categories:
        category = "Other"

    return {
        "item": str(data.get("item") or fallback_item),
        "category": category,
        "material": str(data.get("material") or "Unknown"),
        "recyclable": recyclable,
        "disposal_method": str(data.get("disposal_method") or "Follow local municipal guidelines."),
        "recycling_guidance": str(
            data.get("recycling_guidance") or "Check local recycling rules."
        ),
        "environmental_impact": str(
            data.get("environmental_impact") or "Proper disposal reduces landfill burden."
        ),
        "safety_warning": str(data.get("safety_warning") or ""),
        "confidence": confidence,
    }


def validate_entities(data: dict[str, Any]) -> dict[str, str]:
    return {
        "object": str(data.get("object") or "unknown item"),
        "brand": str(data.get("brand") or ""),
        "material": str(data.get("material") or "unknown"),
        "hazard": str(data.get("hazard") or ""),
        "waste_type": str(data.get("waste_type") or "Other"),
    }
