"""Local RAG with ChromaDB."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings
from docx import Document as DocxDocument
from pypdf import PdfReader

from backend import config

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


class RAGService:
    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=str(config.CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name="ecosort_documents",
            metadata={"hnsw:space": "cosine"},
        )

    @staticmethod
    def extract_text(file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".txt":
            return file_path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".pdf":
            reader = PdfReader(str(file_path))
            parts = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
            return "\n".join(parts)
        if suffix == ".docx":
            doc = DocxDocument(str(file_path))
            return "\n".join(p.text for p in doc.paragraphs)
        raise ValueError("Unsupported document type.")

    @staticmethod
    def chunk_text(text: str) -> list[str]:
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start = end - CHUNK_OVERLAP
        return chunks

    def ingest(self, file_path: Path, original_name: str) -> dict:
        text = self.extract_text(file_path)
        chunks = self.chunk_text(text)
        if not chunks:
            raise ValueError("No text could be extracted from the document.")

        doc_id = str(uuid.uuid4())
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [
            {"source": original_name, "chunk_index": i, "document_id": doc_id}
            for i in range(len(chunks))
        ]
        self._collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        return {
            "document_id": doc_id,
            "filename": original_name,
            "chunks": len(chunks),
            "characters": len(text),
        }

    def search(self, query: str, n_results: int = 4) -> tuple[list[str], list[str]]:
        if self._collection.count() == 0:
            return [], []
        try:
            result = self._collection.query(query_texts=[query], n_results=min(n_results, 8))
        except Exception as exc:
            raise RuntimeError("RAG database error during search.") from exc

        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        sources: list[str] = []
        for meta in metas:
            name = meta.get("source", "unknown")
            idx = meta.get("chunk_index", "")
            sources.append(f"{name}, section ~{idx}")
        return docs, sources

    def get_document_text_sample(self, filename: str, max_chars: int = 12000) -> str:
        if self._collection.count() == 0:
            return ""
        try:
            result = self._collection.get(where={"source": filename})
        except Exception:
            return ""
        docs = result.get("documents") or []
        combined = "\n".join(docs)
        return combined[:max_chars]


rag_service = RAGService()
