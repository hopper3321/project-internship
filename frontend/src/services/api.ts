import type {
  DocSummary,
  DocumentMeta,
  Entities,
  HealthStatus,
  WasteAnalysis,
} from "../types";

async function parseJson<T>(res: Response): Promise<T> {
  const data = await res.json();
  if (!res.ok) {
    throw new Error((data as { error?: string }).error || "Request failed");
  }
  return data as T;
}

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch("/api/health");
  return parseJson(res);
}

export async function analyzeText(item: string): Promise<{
  analysis: WasteAnalysis;
  entities: Entities;
  demo_mode: boolean;
  demo_message?: string;
}> {
  const res = await fetch("/api/analyze-text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item }),
  });
  return parseJson(res);
}

export async function analyzeImage(file: File): Promise<{
  result: Record<string, unknown>;
  demo_mode: boolean;
  demo_message?: string;
}> {
  const form = new FormData();
  form.append("image", file);
  const res = await fetch("/api/analyze-image", { method: "POST", body: form });
  return parseJson(res);
}

export async function chat(message: string, history: { role: string; content: string }[]) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  return parseJson<{
    reply: string;
    agent_action: string;
    agent_tool: string;
    demo_mode: boolean;
    demo_message?: string;
  }>(res);
}

export async function uploadDocument(file: File): Promise<{ document: DocumentMeta }> {
  const form = new FormData();
  form.append("document", file);
  const res = await fetch("/api/upload-document", { method: "POST", body: form });
  return parseJson(res);
}

export async function searchDocument(query: string) {
  const res = await fetch("/api/search-document", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  return parseJson<{ answer: string; sources: string[]; demo_mode: boolean; demo_message?: string }>(
    res,
  );
}

export async function summarizeDocument(filename: string) {
  const res = await fetch("/api/summarize-document", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename }),
  });
  return parseJson<{ summary: DocSummary; filename: string; demo_mode: boolean; demo_message?: string }>(
    res,
  );
}

export async function extractEntities(text: string) {
  const res = await fetch("/api/extract-entities", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return parseJson<{ entities: Entities; demo_mode: boolean }>(res);
}

export async function agentRoute(message: string) {
  const res = await fetch("/api/agent-route", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  return parseJson<{ tool: string; label: string }>(res);
}
