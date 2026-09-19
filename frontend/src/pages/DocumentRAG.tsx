import { FormEvent, useState } from "react";
import { FileDropZone } from "../components/FileDropZone";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { useToast } from "../hooks/useToast";
import { searchDocument, summarizeDocument, uploadDocument } from "../services/api";
import type { DocSummary, DocumentMeta } from "../types";

export function DocumentRAG() {
  const [docs, setDocs] = useState<DocumentMeta[]>([]);
  const [uploading, setUploading] = useState(false);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [searching, setSearching] = useState(false);
  const [summary, setSummary] = useState<DocSummary | null>(null);
  const [summarizeTarget, setSummarizeTarget] = useState("");
  const { push } = useToast();

  async function onUpload(file: File) {
    setUploading(true);
    try {
      const res = await uploadDocument(file);
      setDocs((d) => [...d, res.document]);
      push(`Uploaded ${res.document.filename}`, "success");
    } catch (err) {
      push(err instanceof Error ? err.message : "Upload failed.", "error");
    } finally {
      setUploading(false);
    }
  }

  async function onSearch(e: FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    setAnswer("");
    setSources([]);
    try {
      const res = await searchDocument(query.trim());
      setAnswer(res.answer);
      setSources(res.sources);
    } catch (err) {
      push(err instanceof Error ? err.message : "Search failed.", "error");
    } finally {
      setSearching(false);
    }
  }

  async function onSummarize() {
    if (!summarizeTarget) {
      push("Select a document to summarize.", "error");
      return;
    }
    setSearching(true);
    try {
      const res = await summarizeDocument(summarizeTarget);
      setSummary(res.summary);
    } catch (err) {
      push(err instanceof Error ? err.message : "Summarize failed.", "error");
    } finally {
      setSearching(false);
    }
  }

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">Document / RAG</h1>
        <p className="text-slate-600 mt-1">
          Upload municipal or campus guidelines (PDF, TXT, DOCX) and query them with retrieval-augmented
          generation.
        </p>
      </div>
      <FileDropZone
        accept=".pdf,.txt,.docx"
        label="Upload PDF, TXT, or DOCX"
        onFile={onUpload}
        disabled={uploading}
      />
      {uploading && <LoadingSpinner label="Extracting and indexing document…" />}
      {docs.length > 0 && (
        <ul className="rounded-lg border bg-white divide-y text-sm">
          {docs.map((d) => (
            <li key={d.document_id} className="px-4 py-2 flex justify-between">
              <span>{d.filename}</span>
              <span className="text-slate-500">{d.chunks} chunks</span>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={onSearch} className="space-y-2">
        <label htmlFor="rag-query" className="font-medium text-sm">
          Ask about uploaded documents
        </label>
        <input
          id="rag-query"
          className="w-full rounded-lg border px-3 py-2"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What does the document say about plastic waste?"
        />
        <button
          type="submit"
          disabled={searching || docs.length === 0}
          className="rounded-lg bg-eco-600 px-4 py-2 text-white disabled:opacity-50"
        >
          Search documents
        </button>
      </form>
      {searching && <LoadingSpinner />}
      {answer && (
        <article className="rounded-xl border bg-white p-5 space-y-2">
          <h3 className="font-semibold">Answer</h3>
          <p className="text-sm whitespace-pre-wrap">{answer}</p>
          {sources.length > 0 && (
            <div className="text-xs text-slate-600">
              <p className="font-medium">Sources:</p>
              <ul className="list-disc pl-4">
                {sources.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </article>
      )}
      <section className="border-t pt-6 space-y-3">
        <h2 className="font-semibold">Summarize document</h2>
        <select
          className="w-full rounded-lg border px-3 py-2"
          value={summarizeTarget}
          onChange={(e) => setSummarizeTarget(e.target.value)}
        >
          <option value="">Select uploaded document</option>
          {docs.map((d) => (
            <option key={d.document_id} value={d.filename}>
              {d.filename}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={onSummarize}
          disabled={!summarizeTarget || searching}
          className="rounded-lg border border-eco-600 px-4 py-2 text-eco-700 hover:bg-eco-50"
        >
          Summarize document
        </button>
        {summary && (
          <article className="rounded-xl bg-eco-50/50 border p-5 text-sm space-y-3">
            <p>
              <strong>Main topic:</strong> {summary.main_topic}
            </p>
            <SectionList title="Key points" items={summary.key_points} />
            <SectionList title="Waste-management rules" items={summary.waste_management_rules} />
            <SectionList title="Important warnings" items={summary.important_warnings} />
            <SectionList title="Recommendations" items={summary.actionable_recommendations} />
          </article>
        )}
      </section>
    </div>
  );
}

function SectionList({ title, items }: { title: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <div>
      <p className="font-medium">{title}</p>
      <ul className="list-disc pl-5">
        {items.map((x, i) => (
          <li key={i}>{x}</li>
        ))}
      </ul>
    </div>
  );
}
