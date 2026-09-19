"""Deterministic demo responses for common test items."""

from backend.utils.validators import normalize_item_key

DEMO_WASTE: dict[str, dict] = {
    "plastic bottle": {
        "item": "plastic bottle",
        "category": "Recyclable",
        "material": "PET plastic",
        "recyclable": True,
        "disposal_method": "Empty, rinse lightly, remove cap if required locally, place in dry/recyclable bin.",
        "recycling_guidance": "Most curbside programs accept PET bottles; crush to save space.",
        "environmental_impact": "Recycling PET saves energy vs. virgin plastic production.",
        "safety_warning": "",
        "confidence": 0.92,
    },
    "banana peel": {
        "item": "banana peel",
        "category": "Organic Waste",
        "material": "Organic biomass",
        "recyclable": False,
        "disposal_method": "Compost or wet/organic waste bin; do not mix with dry recyclables.",
        "recycling_guidance": "Home composting or municipal organic collection if available.",
        "environmental_impact": "Composting returns nutrients to soil and reduces methane from landfills.",
        "safety_warning": "",
        "confidence": 0.95,
    },
    "potato peel": {
        "item": "potato peel",
        "category": "Organic Waste",
        "material": "Organic biomass",
        "recyclable": False,
        "disposal_method": "Compost or wet/organic waste bin; do not mix with dry recyclables.",
        "recycling_guidance": "Home composting or municipal organic collection if available.",
        "environmental_impact": "Composting returns nutrients to soil and reduces methane from landfills.",
        "safety_warning": "",
        "confidence": 0.94,
    },
    "old newspaper": {
        "item": "old newspaper",
        "category": "Dry Waste",
        "material": "Paper",
        "recyclable": True,
        "disposal_method": "Keep dry and flat; place in paper/cardboard recycling.",
        "recycling_guidance": "Remove plastic wrap or oily sections before recycling.",
        "environmental_impact": "Paper recycling reduces deforestation pressure.",
        "safety_warning": "",
        "confidence": 0.93,
    },
    "broken mobile phone": {
        "item": "broken mobile phone",
        "category": "E-Waste",
        "material": "Metals, plastics, electronic components",
        "recyclable": True,
        "disposal_method": "Take to authorized e-waste collection point or retailer take-back program.",
        "recycling_guidance": "Do not discard in household trash; recover valuable metals.",
        "environmental_impact": "Improper disposal leaches heavy metals into soil and water.",
        "safety_warning": "Damaged batteries may be hazardous—use certified e-waste handlers.",
        "confidence": 0.91,
    },
    "used battery": {
        "item": "used battery",
        "category": "Hazardous Waste",
        "material": "Electrochemical cells (alkaline/lithium)",
        "recyclable": True,
        "disposal_method": "Drop at battery recycling bins or hazardous waste collection—never in regular trash.",
        "recycling_guidance": "Tape lithium terminals if damaged; follow local HHW rules.",
        "environmental_impact": "Batteries contain metals and chemicals that contaminate landfills.",
        "safety_warning": "Risk of fire or leakage—do not puncture or incinerate.",
        "confidence": 0.96,
    },
    "glass bottle": {
        "item": "glass bottle",
        "category": "Recyclable",
        "material": "Glass",
        "recyclable": True,
        "disposal_method": "Rinse, remove non-glass parts if needed, place in glass recycling.",
        "recycling_guidance": "Glass is infinitely recyclable; separate by color if required locally.",
        "environmental_impact": "Recycling glass cuts raw material use and energy.",
        "safety_warning": "Handle broken glass with gloves; wrap sharp pieces before disposal.",
        "confidence": 0.94,
    },
    "food container": {
        "item": "food container",
        "category": "Dry Waste",
        "material": "Mixed plastic or foam (varies)",
        "recyclable": False,
        "disposal_method": "Scrape food residue; recycle only if labeled accepted locally, else dry waste.",
        "recycling_guidance": "Check resin code and municipal acceptance for plastic containers.",
        "environmental_impact": "Contaminated containers often reject entire recycling loads.",
        "safety_warning": "",
        "confidence": 0.78,
    },
}

DEMO_ENTITIES: dict[str, dict] = {
    "broken mobile phone": {
        "object": "mobile phone",
        "brand": "",
        "material": "electronic components",
        "hazard": "damaged battery",
        "waste_type": "E-Waste",
    },
}

CHAT_DEMO_REPLIES = {
    "plastic bottle": (
        "Rinse the bottle, keep the cap on or off per local rules, and place it in your "
        "recycling bin if PET is accepted. Local rules may differ—verify with your municipality."
    ),
    "wet waste": (
        "Wet waste is typically biodegradable kitchen and garden waste such as food scraps "
        "and peels. It should go to compost or organic bins, separate from dry recyclables."
    ),
    "batteries": (
        "Batteries should not go in normal garbage. Use store drop-off or hazardous waste "
        "collection. Lithium batteries need special handling—local rules may differ."
    ),
    "reduce household waste": (
        "Plan meals, reuse bags and containers, buy in bulk with less packaging, compost "
        "organics, and repair items before replacing them."
    ),
    "e-waste": (
        "E-waste includes phones, computers, and appliances with electronics. Take them to "
        "authorized e-waste recyclers to recover materials and avoid toxic leakage."
    ),
}


def lookup_demo_waste(text: str) -> dict | None:
    key = normalize_item_key(text)
    if key in DEMO_WASTE:
        return dict(DEMO_WASTE[key])
    for pattern, value in DEMO_WASTE.items():
        if pattern in key or key in pattern:
            result = dict(value)
            result["item"] = text.strip()
            return result
    return None


def demo_waste_fallback(text: str) -> dict:
    return {
        "item": text.strip(),
        "category": "Other",
        "material": "Unknown",
        "recyclable": False,
        "disposal_method": "Check local municipal segregation guidelines for this item.",
        "recycling_guidance": "When unsure, ask your local waste authority.",
        "environmental_impact": "Proper sorting reduces landfill and pollution.",
        "safety_warning": "",
        "confidence": 0.55,
    }


def demo_chat_reply(message: str) -> str:
    lower = message.lower()
    for keyword, reply in CHAT_DEMO_REPLIES.items():
        if keyword in lower:
            return reply
    return (
        "I'm EcoSort AI in demo mode. I can help with waste segregation, recycling, and "
        "disposal guidance. Try asking about plastic bottles, wet waste, batteries, or e-waste. "
        "Local regulations may differ—confirm with your municipality."
    )
