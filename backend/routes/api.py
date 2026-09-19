import logging
import uuid
from pathlib import Path

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from backend import config
from backend.services.agent_service import route_agent
from backend.services.entity_service import extract_entities
from backend.services.granite_service import granite_service
from backend.services.image_service import analyze_image_file
from backend.services.rag_service import rag_service
from backend.utils.validators import (
    ALLOWED_DOC_EXT,
    ALLOWED_IMAGE_EXT,
    require_non_empty,
    validate_waste_analysis,
)

logger = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__)


def _demo_flag() -> bool:
    return config.is_demo_mode()


def _error(message: str, status: int = 400):
    return jsonify({"error": message, "demo_mode": _demo_flag()}), status


@api_bp.get("/health")
def health():
    return jsonify(config.health_payload())


@api_bp.post("/analyze-text")
def analyze_text():
    data = request.get_json(silent=True) or {}
    try:
        item = require_non_empty(data.get("item") or data.get("text"), "Item")
    except ValueError as exc:
        return _error(str(exc), 400)

    try:
        raw, used_demo = granite_service.analyze_waste_text(item)
        analysis = validate_waste_analysis(raw, item)
        entities, ent_demo = extract_entities(item)
    except RuntimeError as exc:
        return _error(str(exc), 503)
    except Exception:
        logger.exception("analyze-text failed")
        return _error("Unable to analyze item. Please try again.", 500)

    demo = _demo_flag() or used_demo or ent_demo
    return jsonify(
        {
            "analysis": analysis,
            "entities": entities,
            "demo_mode": demo,
            "demo_message": (
                "Demo Mode – IBM Granite API is not connected." if demo else None
            ),
        }
    )


@api_bp.post("/analyze-image")
def analyze_image():
    if "image" not in request.files:
        return _error("No image file provided.", 400)
    file = request.files["image"]
    if not file.filename:
        return _error("Empty filename.", 400)

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXT:
        return _error("Unsupported image format. Use JPG, JPEG, PNG, or WEBP.", 400)

    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > config.MAX_UPLOAD_BYTES:
        return _error("File too large.", 413)
    if size == 0:
        return _error("Empty file.", 400)

    safe_name = secure_filename(file.filename)
    dest = config.UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_name}"
    file.save(dest)

    try:
        result, demo = analyze_image_file(str(dest))
    except Exception:
        logger.exception("Image analysis failed")
        return _error("Image analysis failed.", 500)
    finally:
        try:
            dest.unlink(missing_ok=True)
        except OSError:
            pass

    if result.get("error") and not demo:
        return jsonify({"error": result["error"], "demo_mode": False}), 503

    return jsonify(
        {
            "result": result,
            "demo_mode": demo or _demo_flag(),
            "demo_message": (
                "Demo Mode – IBM Granite API is not connected."
                if (demo or _demo_flag())
                else None
            ),
        }
    )


@api_bp.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    try:
        message = require_non_empty(data.get("message"), "Message")
    except ValueError as exc:
        return _error(str(exc), 400)

    history = data.get("history") or []
    has_docs = rag_service._collection.count() > 0
    tool, tool_label = route_agent(message, has_documents=has_docs)

    try:
        if tool == "analyze_text_waste":
            raw, used_demo = granite_service.analyze_waste_text(message)
            analysis = validate_waste_analysis(raw, message)
            reply = (
                f"Category: {analysis['category']}. "
                f"Disposal: {analysis['disposal_method']} "
                f"Recycling: {analysis['recycling_guidance']}"
            )
            demo = used_demo or _demo_flag()
        elif tool == "search_documents":
            chunks, sources = rag_service.search(message)
            reply, used_demo = granite_service.rag_answer(message, chunks, sources)
            demo = used_demo or _demo_flag()
        elif tool == "extract_entities":
            entities, used_demo = extract_entities(message)
            reply = (
                f"Extracted: object={entities['object']}, brand={entities['brand'] or '—'}, "
                f"material={entities['material']}, hazard={entities['hazard'] or '—'}, "
                f"waste_type={entities['waste_type']}."
            )
            demo = used_demo or _demo_flag()
        elif tool == "summarize_document":
            reply = (
                "Use the Document / RAG page: upload a file, select it, and click "
                '"Summarize document" for a full summary.'
            )
            demo = _demo_flag()
        elif tool == "analyze_image":
            reply = (
                "Open the Image Analyzer page to upload JPG, PNG, or WEBP for analysis."
            )
            demo = _demo_flag()
        else:
            reply, used_demo = granite_service.chat(message, history)
            demo = used_demo or _demo_flag()
    except RuntimeError as exc:
        return _error(str(exc), 503)
    except Exception:
        logger.exception("chat failed")
        return _error("Chat request failed.", 500)

    return jsonify(
        {
            "reply": reply,
            "agent_action": tool_label,
            "agent_tool": tool,
            "demo_mode": demo,
            "demo_message": (
                "Demo Mode – IBM Granite API is not connected." if demo else None
            ),
        }
    )


@api_bp.post("/upload-document")
def upload_document():
    if "document" not in request.files:
        return _error("No document provided.", 400)
    file = request.files["document"]
    if not file.filename:
        return _error("Empty filename.", 400)

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_DOC_EXT:
        return _error("Unsupported format. Use PDF, TXT, or DOCX.", 400)

    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > config.MAX_UPLOAD_BYTES:
        return _error("File too large.", 413)

    original = secure_filename(file.filename)
    dest = config.UPLOAD_DIR / f"{uuid.uuid4().hex}_{original}"
    file.save(dest)

    try:
        meta = rag_service.ingest(dest, original)
    except ValueError as exc:
        dest.unlink(missing_ok=True)
        return _error(str(exc), 400)
    except RuntimeError as exc:
        dest.unlink(missing_ok=True)
        return _error(str(exc), 500)
    except Exception:
        logger.exception("Document ingest failed")
        dest.unlink(missing_ok=True)
        return _error("Failed to process document.", 500)

    return jsonify({"success": True, "document": meta, "demo_mode": _demo_flag()})


@api_bp.post("/search-document")
def search_document():
    data = request.get_json(silent=True) or {}
    try:
        query = require_non_empty(data.get("query"), "Query")
    except ValueError as exc:
        return _error(str(exc), 400)

    try:
        chunks, sources = rag_service.search(query)
        if not chunks:
            return jsonify(
                {
                    "answer": "I could not find this information in the uploaded documents.",
                    "sources": [],
                    "demo_mode": _demo_flag(),
                }
            )
        answer, used_demo = granite_service.rag_answer(query, chunks, sources)
    except RuntimeError as exc:
        return _error(str(exc), 503)
    except Exception:
        logger.exception("search-document failed")
        return _error("Document search failed.", 500)

    demo = used_demo or _demo_flag()
    return jsonify(
        {
            "answer": answer,
            "sources": sources,
            "demo_mode": demo,
            "demo_message": (
                "Demo Mode – IBM Granite API is not connected." if demo else None
            ),
        }
    )


@api_bp.post("/summarize-document")
def summarize_document():
    data = request.get_json(silent=True) or {}
    filename = (data.get("filename") or "").strip()
    if not filename:
        return _error("filename is required.", 400)

    text = rag_service.get_document_text_sample(filename)
    if not text:
        return _error("Document not found in knowledge base. Upload it first.", 404)

    try:
        summary, used_demo = granite_service.summarize_document(text, filename)
    except RuntimeError as exc:
        return _error(str(exc), 503)
    except Exception:
        logger.exception("summarize failed")
        return _error("Summarization failed.", 500)

    demo = used_demo or _demo_flag()
    return jsonify(
        {
            "summary": summary,
            "filename": filename,
            "demo_mode": demo,
            "demo_message": (
                "Demo Mode – IBM Granite API is not connected." if demo else None
            ),
        }
    )


@api_bp.post("/extract-entities")
def extract_entities_route():
    data = request.get_json(silent=True) or {}
    try:
        text = require_non_empty(data.get("text"), "Text")
    except ValueError as exc:
        return _error(str(exc), 400)

    try:
        entities, used_demo = extract_entities(text)
    except RuntimeError as exc:
        return _error(str(exc), 503)
    except Exception:
        logger.exception("entity extraction failed")
        return _error("Entity extraction failed.", 500)

    demo = used_demo or _demo_flag()
    return jsonify(
        {
            "entities": entities,
            "demo_mode": demo,
            "demo_message": (
                "Demo Mode – IBM Granite API is not connected." if demo else None
            ),
        }
    )


@api_bp.post("/agent-route")
def agent_route():
    data = request.get_json(silent=True) or {}
    try:
        message = require_non_empty(data.get("message"), "Message")
    except ValueError as exc:
        return _error(str(exc), 400)
    has_docs = rag_service._collection.count() > 0
    tool, label = route_agent(message, has_documents=has_docs)
    return jsonify({"tool": tool, "label": label})
