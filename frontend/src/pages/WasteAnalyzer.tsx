import { FormEvent, useState } from "react";
import { AnalysisResultCard } from "../components/AnalysisResultCard";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { useToast } from "../hooks/useToast";
import { analyzeText } from "../services/api";
import type { Entities, WasteAnalysis } from "../types";
import { addHistory } from "../utils/historyStorage";

const samples = [
  "plastic bottle",
  "banana peel",
  "old newspaper",
  "glass bottle",
  "used battery",
  "broken mobile phone",
  "food container",
];

export function WasteAnalyzer() {
  const [item, setItem] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<WasteAnalysis | null>(null);
  const [entities, setEntities] = useState<Entities | null>(null);
  const { push } = useToast();

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!item.trim()) {
      push("Please enter an item to analyze.", "error");
      return;
    }
    setLoading(true);
    setAnalysis(null);
    try {
      const res = await analyzeText(item.trim());
      setAnalysis(res.analysis);
      setEntities(res.entities);
      addHistory({
        input: res.analysis.item,
        category: res.analysis.category,
        recyclable: res.analysis.recyclable,
        disposal: res.analysis.disposal_method,
        type: "text",
      });
      push("Analysis complete.", "success");
    } catch (err) {
      push(err instanceof Error ? err.message : "Analysis failed.", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">Waste Analyzer</h1>
        <p className="text-slate-600 mt-1">Describe a waste item to get segregation guidance.</p>
      </div>
      <form onSubmit={submit} className="space-y-3">
        <label className="block text-sm font-medium" htmlFor="item">
          Item description
        </label>
        <input
          id="item"
          className="w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-eco-500 focus:ring-2 focus:ring-eco-200"
          value={item}
          onChange={(e) => setItem(e.target.value)}
          placeholder="e.g. plastic bottle"
        />
        <div className="flex flex-wrap gap-2">
          {samples.map((s) => (
            <button
              key={s}
              type="button"
              className="rounded-full bg-slate-100 px-3 py-1 text-xs hover:bg-eco-100"
              onClick={() => setItem(s)}
            >
              {s}
            </button>
          ))}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-eco-600 px-5 py-2 font-medium text-white hover:bg-eco-700 disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </form>
      {loading && <LoadingSpinner label="Analyzing waste item…" />}
      {analysis && entities && <AnalysisResultCard analysis={analysis} entities={entities} />}
    </div>
  );
}
