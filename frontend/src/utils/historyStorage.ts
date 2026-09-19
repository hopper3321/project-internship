import type { HistoryEntry } from "../types";

const KEY = "ecosort_history";

export function loadHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    return JSON.parse(raw) as HistoryEntry[];
  } catch {
    return [];
  }
}

export function saveHistory(entries: HistoryEntry[]): void {
  localStorage.setItem(KEY, JSON.stringify(entries));
}

export function addHistory(entry: Omit<HistoryEntry, "id" | "date">): HistoryEntry[] {
  const full: HistoryEntry = {
    ...entry,
    id: crypto.randomUUID(),
    date: new Date().toISOString(),
  };
  const next = [full, ...loadHistory()].slice(0, 200);
  saveHistory(next);
  return next;
}

export function deleteHistoryItem(id: string): HistoryEntry[] {
  const next = loadHistory().filter((e) => e.id !== id);
  saveHistory(next);
  return next;
}

export function clearHistory(): void {
  localStorage.removeItem(KEY);
}

export function historyStats(entries: HistoryEntry[]) {
  return {
    total: entries.length,
    recyclable: entries.filter((e) => e.recyclable).length,
    nonRecyclable: entries.filter((e) => !e.recyclable).length,
    hazardous: entries.filter((e) =>
      /hazard|e-waste|battery/i.test(e.category),
    ).length,
  };
}
