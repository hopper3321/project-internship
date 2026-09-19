"""Sample test cases for deterministic demo waste analysis."""

import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.services.demo_data import lookup_demo_waste
from backend.services.image_service import DemoVisionProvider
from backend.utils.validators import validate_waste_analysis

CASES = [
    "plastic bottle",
    "banana peel",
    "potato peel",
    "old newspaper",
    "broken mobile phone",
    "used battery",
    "glass bottle",
    "food container",
]


def test_demo_cases_exist_and_validate():
    for item in CASES:
        raw = lookup_demo_waste(item)
        assert raw is not None, f"Missing demo case: {item}"
        validated = validate_waste_analysis(raw, item)
        assert validated["item"]
        assert validated["category"]
        assert 0 <= validated["confidence"] <= 1


def test_demo_image_uses_potato_peel_hint():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "potato_peel.png"
        Image.new("RGB", (100, 100), (200, 180, 80)).save(path)
        result = DemoVisionProvider().analyze(str(path))
        assert result["waste_category"] == "Organic Waste"
        assert result["detected_item"] == "potato peel"


def test_demo_image_uses_plastic_bottle_hint():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "plastic_bottle.png"
        Image.new("RGB", (100, 100), (200, 180, 80)).save(path)
        result = DemoVisionProvider().analyze(str(path))
        assert result["waste_category"] == "Recyclable"
        assert result["detected_item"] == "plastic bottle"


if __name__ == "__main__":
    test_demo_cases_exist_and_validate()
    test_demo_image_uses_potato_peel_hint()
    test_demo_image_uses_plastic_bottle_hint()
    print("All demo test cases passed.")
