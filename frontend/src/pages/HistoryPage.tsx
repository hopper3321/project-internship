import { useState } from "react";
import { useToast } from "../hooks/useToast";
import type { HistoryEntry } from "../types";
import { clearHistory, deleteHistoryItem, loadHistory } from "../utils/historyStorage";

export function HistoryPage() {
  const [entries, setEntries] = useState<HistoryEntry[]>(() => loadHistory());
  const { push } = useToast();

  function remove(id: string) {
    setEntries(deleteHistoryItem(id));
    push("Entry deleted.", "info");
  }

  function clearAll() {
    clearHistory();
    setEntries([]);
    push("History cleared.", "success");
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold">History</h1>
          <p className="text-slate-600 text-sm">Stored in localStorage on this device only.</p>
        </div>
        {entries.length > 0 && (
          <button
            type="button"
            onClick={clearAll}
            className="rounded-lg border border-red-200 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50"
          >
            Clear all
          </button>
        )}
      </div>
      {entries.length === 0 ? (
        <p className="rounded-xl border border-dashed p-8 text-center text-slate-500">
          No history yet.
        </p>
      ) : (
        <ul className="space-y-3">
          {entries.map((e) => (
            <li key={e.id} className="rounded-xl border bg-white p-4 text-sm">
              <div className="flex flex-wrap justify-between gap-2">
                <span className="font-medium capitalize">{e.input}</span>
                <span className="text-slate-500">{new Date(e.date).toLocaleString()}</span>
              </div>
              <p className="mt-2 text-slate-600">
                {e.category} · {e.recyclable ? "Recyclable" : "Not recyclable"} · {e.type}
              </p>
              <p className="mt-1">{e.disposal}</p>
              <button
                type="button"
                className="mt-2 text-xs text-red-600 underline"
                onClick={() => remove(e.id)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
