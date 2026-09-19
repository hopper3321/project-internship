"""Simple agent routing to the appropriate tool."""

from __future__ import annotations

import re

TOOLS = {
    "analyze_text_waste": "Waste Analysis",
    "analyze_image": "Image Analysis",
    "search_documents": "Document Search",
    "summarize_document": "Document Summarization",
    "extract_entities": "Entity Extraction",
    "chat": "General Chat",
}


def route_agent(message: str, has_documents: bool = False) -> tuple[str, str]:
    lower = message.lower().strip()

    if re.search(r"\b(summarize|summary)\b.*\b(pdf|document|doc|file)\b", lower):
        return "summarize_document", TOOLS["summarize_document"]
    if re.search(r"\b(summarize|summary)\b", lower) and has_documents:
        return "summarize_document", TOOLS["summarize_document"]
    if has_documents and re.search(
        r"\b(uploaded|municipal|document|pdf)\b", lower
    ) and re.search(r"\b(say|about|mention|rule|guideline|plastic)\b", lower):
        return "search_documents", TOOLS["search_documents"]
    if re.search(r"\b(search|find in document|uploaded document)\b", lower) and has_documents:
        return "search_documents", TOOLS["search_documents"]
    if re.search(r"\b(image|photo|picture|uploaded image)\b", lower):
        return "analyze_image", TOOLS["analyze_image"]
    if re.search(r"\b(extract|entities|brand|hazard)\b", lower):
        return "extract_entities", TOOLS["extract_entities"]

    # Educational / general questions → chat (before item keyword matching)
    if re.search(
        r"\b(what is|what's|explain|define|how can i reduce|can .+ be put|tell me about)\b",
        lower,
    ):
        return "chat", TOOLS["chat"]

    if re.search(r"\b(how should i dispose|what should i do with|throw away|get rid of)\b", lower):
        return "analyze_text_waste", TOOLS["analyze_text_waste"]

    # Short item-like inputs (e.g. "plastic bottle" on analyzer-style phrasing)
    if re.search(
        r"\b(plastic bottle|banana peel|newspaper|glass bottle|used battery|mobile phone|food container)\b",
        lower,
    ) and not re.search(r"\?", lower):
        return "analyze_text_waste", TOOLS["analyze_text_waste"]

    return "chat", TOOLS["chat"]
