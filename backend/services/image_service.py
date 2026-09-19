"""Vision provider interface — IBM vision when available, demo fallback otherwise."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Protocol

from PIL import Image

from backend import config
from backend.services.demo_data import lookup_demo_waste
from backend.services.granite_service import granite_service


class VisionProvider(Protocol):
    def analyze(self, image_path: str) -> dict[str, Any]: ...


class DemoVisionProvider:
    """Deterministic demo results from image metadata (no fake API calls)."""

    SCENARIOS = [
        "plastic bottle",
        "banana peel",
        "potato peel",
        "glass bottle",
        "used battery",
    ]

    @staticmethod
    def _infer_item_key(image_path: str) -> str | None:
        name = Path(image_path).name.lower()
        if "battery" in name:
            return "used battery"
        if "phone" in name or "mobile" in name:
            return "broken mobile phone"
        if "plastic" in name or "pet" in name or "cup" in name:
            return "plastic bottle"
        if "glass" in name or "jar" in name:
            return "glass bottle"
        if "potato" in name or ("peel" in name and "banana" not in name):
            return "potato peel"
        if "banana" in name or "fruit" in name or "organic" in name:
            return "banana peel"
        if "bottle" in name:
            return "glass bottle"
        return None

    def analyze(self, image_path: str) -> dict[str, Any]:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            w, h = img.size
            digest = hashlib.md5(open(image_path, "rb").read()).hexdigest()
        item_key = self._infer_item_key(image_path) or self.SCENARIOS[int(digest[:2], 16) % len(self.SCENARIOS)]
        base = lookup_demo_waste(item_key) or {}
        return {
            "detected_item": base.get("item", item_key),
            "waste_category": base.get("category", "Other"),
            "material": base.get("material", "Unknown"),
            "recyclable": base.get("recyclable", False),
            "disposal_recommendation": base.get("disposal_method", ""),
            "safety_warning": base.get("safety_warning", ""),
            "explanation": (
                f"Demo mode: vision API not connected. Inferred sample scenario '{item_key}' "
                f"from deterministic demo mapping (image {w}x{h}). Upload IBM vision-capable "
                "model credentials to enable real image analysis."
            ),
            "demo_mode": True,
        }


class GraniteVisionProvider:
    """Placeholder for watsonx vision/multimodal — falls back with clear error."""

    def analyze(self, image_path: str) -> dict[str, Any]:
        # IBM Granite text models typically do not accept raw images via same endpoint.
        # When multimodal is configured, extend here without changing routes.
        raise RuntimeError(
            "Image analysis requires a vision-capable model. Configure a vision provider "
            "or use demo mode."
        )


def get_vision_provider() -> VisionProvider:
    if config.is_demo_mode():
        return DemoVisionProvider()
    return GraniteVisionProvider()


def analyze_image_file(image_path: str) -> tuple[dict[str, Any], bool]:
    provider = get_vision_provider()
    try:
        result = provider.analyze(image_path)
        return result, bool(result.get("demo_mode", config.is_demo_mode()))
    except RuntimeError as exc:
        if config.is_demo_mode():
            return DemoVisionProvider().analyze(image_path), True
        return {
            "error": str(exc),
            "detected_item": "",
            "waste_category": "",
            "material": "",
            "recyclable": False,
            "disposal_recommendation": "",
            "safety_warning": "",
            "explanation": str(exc),
        }, False
    except Exception:
        if config.is_demo_mode():
            return DemoVisionProvider().analyze(image_path), True
        raise
