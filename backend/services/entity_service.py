from backend.services.granite_service import granite_service
from backend.utils.validators import validate_entities


def extract_entities(text: str) -> tuple[dict, bool]:
    raw, demo = granite_service.extract_entities_structured(text)
    return validate_entities(raw), demo
