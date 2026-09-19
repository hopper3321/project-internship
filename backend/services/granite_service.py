"""IBM watsonx.ai Granite integration with demo fallback."""

from __future__ import annotations

import logging
from typing import Any

import requests

from backend import config
from backend.services import demo_data
from backend.utils.validators import parse_json_from_llm

logger = logging.getLogger(__name__)

SYSTEM_WASTE_ANALYST = """You are a waste classification expert. Respond ONLY with valid JSON, no markdown.
Schema:
{"item":"","category":"","material":"","recyclable":true,"disposal_method":"","recycling_guidance":"","environmental_impact":"","safety_warning":"","confidence":0.0}
Categories: Wet Waste, Dry Waste, Recyclable, Non-Recyclable, E-Waste, Hazardous Waste, Organic Waste, Other.
For hazardous items, give safe high-level disposal guidance only—no dangerous instructions."""


class GraniteService:
    def __init__(self) -> None:
        self._token: str | None = None

    @property
    def demo_mode(self) -> bool:
        return config.is_demo_mode()

    def _get_iam_token(self) -> str:
        if self._token:
            return self._token
        url = "https://iam.cloud.ibm.com/identity/token"
        resp = requests.post(
            url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": config.IBM_WATSONX_API_KEY,
            },
            timeout=30,
        )
        if resp.status_code != 200:
            raise RuntimeError("Invalid IBM API key or IAM authentication failed.")
        self._token = resp.json()["access_token"]
        return self._token

    def generate(self, prompt: str, system: str | None = None, max_tokens: int = 1024) -> str:
        if self.demo_mode:
            raise RuntimeError("DEMO_MODE")

        token = self._get_iam_token()
        url = f"{config.IBM_WATSONX_URL}/ml/v1/text/generation?version=2023-05-29"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload: dict[str, Any] = {
            "model_id": config.IBM_GRANITE_MODEL,
            "project_id": config.IBM_WATSONX_PROJECT_ID,
            "input": prompt if not system else f"{system}\n\nUser: {prompt}",
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": max_tokens,
                "temperature": 0.2,
            },
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=90)
        except requests.RequestException as exc:
            raise RuntimeError("Network failure contacting IBM watsonx.ai.") from exc

        if resp.status_code == 401:
            self._token = None
            raise RuntimeError("Invalid IBM API credentials.")
        if resp.status_code >= 400:
            logger.error("Granite error %s: %s", resp.status_code, resp.text[:500])
            raise RuntimeError("IBM Granite request failed.")

        data = resp.json()
        results = data.get("results") or []
        if not results:
            raise RuntimeError("Empty response from IBM Granite.")
        return (results[0].get("generated_text") or "").strip()

    def analyze_waste_text(self, item: str) -> tuple[dict[str, Any], bool]:
        demo = self.demo_mode
        if demo:
            found = demo_data.lookup_demo_waste(item)
            return found or demo_data.demo_waste_fallback(item), True

        prompt = (
            f'Classify this waste item for disposal guidance: "{item}". '
            f"Return JSON only with the required schema."
        )
        raw = self.generate(prompt, system=SYSTEM_WASTE_ANALYST)
        parsed = parse_json_from_llm(raw)
        if not parsed:
            found = demo_data.lookup_demo_waste(item)
            return found or demo_data.demo_waste_fallback(item), True
        return parsed, False

    def chat(self, message: str, history: list[dict] | None = None) -> tuple[str, bool]:
        if self.demo_mode:
            return demo_data.demo_chat_reply(message), True

        system = """You are EcoSort AI, an environmental waste-management assistant.
Explain waste segregation simply. Provide practical disposal guidance. Warn about hazardous waste.
Never invent municipal rules—say local rules may differ. Be concise. Stay on waste topics."""
        hist = history or []
        context = "\n".join(
            f"{m.get('role','user').capitalize()}: {m.get('content','')}" for m in hist[-6:]
        )
        prompt = f"{context}\nUser: {message}\nAssistant:"
        try:
            text = self.generate(prompt, system=system, max_tokens=512)
        except RuntimeError:
            return demo_data.demo_chat_reply(message), True
        return text, False

    def extract_entities_structured(self, text: str) -> tuple[dict[str, Any], bool]:
        if self.demo_mode:
            lower = text.lower()
            if "samsung" in lower and ("phone" in lower or "mobile" in lower):
                return {
                    "object": "mobile phone",
                    "brand": "Samsung",
                    "material": "electronic components",
                    "hazard": "lithium battery",
                    "waste_type": "E-Waste",
                }, True
            found = demo_data.lookup_demo_waste(text)
            wt = found["category"] if found else "Other"
            return {
                "object": text.split()[0] if text else "item",
                "brand": "",
                "material": found["material"] if found else "unknown",
                "hazard": found.get("safety_warning", "") if found else "",
                "waste_type": wt,
            }, True

        prompt = (
            f'Extract waste entities from: "{text}". Return JSON only: '
            '{"object":"","brand":"","material":"","hazard":"","waste_type":""}'
        )
        raw = self.generate(prompt, system=SYSTEM_WASTE_ANALYST, max_tokens=256)
        parsed = parse_json_from_llm(raw) or {}
        return parsed, False

    def rag_answer(self, question: str, context_chunks: list[str], sources: list[str]) -> tuple[str, bool]:
        if not context_chunks:
            return "I could not find this information in the uploaded documents.", False

        if self.demo_mode:
            joined = " ".join(context_chunks)[:800]
            return (
                f"Based on uploaded documents (demo mode):\n{joined[:600]}...\n\n"
                f"Sources: {', '.join(sources)}"
            ), True

        context = "\n---\n".join(context_chunks)
        prompt = (
            f"Answer ONLY using the context below. If the answer is not in the context, "
            f'reply exactly: "I could not find this information in the uploaded documents."\n\n'
            f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        )
        system = "You cite facts only from provided context. Do not invent sources."
        try:
            answer = self.generate(prompt, system=system, max_tokens=512)
        except RuntimeError:
            return "I could not find this information in the uploaded documents.", False
        if "could not find" in answer.lower() and len(answer) < 120:
            return "I could not find this information in the uploaded documents.", False
        return answer, False

    def summarize_document(self, text: str, filename: str) -> tuple[dict[str, Any], bool]:
        excerpt = text[:12000]
        if self.demo_mode:
            return {
                "main_topic": f"Waste management guidance from {filename}",
                "key_points": [
                    "Segregate wet and dry waste at source.",
                    "Recycle paper, metal, and clean plastics where accepted.",
                    "E-waste and batteries need special collection.",
                ],
                "waste_management_rules": [
                    "Use color-coded bins where provided by municipality.",
                    "Keep recyclables clean and dry.",
                ],
                "important_warnings": [
                    "Do not mix hazardous waste with household trash.",
                    "Local rules may differ—verify with local authority.",
                ],
                "actionable_recommendations": [
                    "Label bins at home for family members.",
                    "Schedule periodic e-waste drop-offs.",
                ],
            }, True

        prompt = (
            f"Summarize this document ({filename}) for waste management. Return JSON only:\n"
            '{"main_topic":"","key_points":[],"waste_management_rules":[],"important_warnings":[],'
            '"actionable_recommendations":[]}\n\nDocument:\n'
            f"{excerpt}"
        )
        raw = self.generate(prompt, system=SYSTEM_WASTE_ANALYST, max_tokens=1024)
        parsed = parse_json_from_llm(raw) or {}
        return {
            "main_topic": str(parsed.get("main_topic") or filename),
            "key_points": list(parsed.get("key_points") or []),
            "waste_management_rules": list(parsed.get("waste_management_rules") or []),
            "important_warnings": list(parsed.get("important_warnings") or []),
            "actionable_recommendations": list(
                parsed.get("actionable_recommendations") or []
            ),
        }, False


granite_service = GraniteService()
