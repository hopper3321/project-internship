import type { Entities, WasteAnalysis } from "../types";

export function AnalysisResultCard({
  analysis,
  entities,
}: {
  analysis: WasteAnalysis;
  entities?: Entities;
}) {
  return (
    <div className="space-y-4">
      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <header className="flex flex-wrap items-center justify-between gap-2 border-b pb-3">
          <h3 className="text-lg font-semibold capitalize">{analysis.item}</h3>
          <span className="rounded-full bg-eco-100 px-3 py-1 text-sm font-medium text-eco-800">
            {analysis.category}
          </span>
        </header>
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="font-medium text-slate-500">Material</dt>
            <dd>{analysis.material}</dd>
          </div>
          <div>
            <dt className="font-medium text-slate-500">Recyclable</dt>
            <dd>{analysis.recyclable ? "Yes" : "No"}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="font-medium text-slate-500">Disposal</dt>
            <dd>{analysis.disposal_method}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="font-medium text-slate-500">Recycling guidance</dt>
            <dd>{analysis.recycling_guidance}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="font-medium text-slate-500">Environmental impact</dt>
            <dd>{analysis.environmental_impact}</dd>
          </div>
          {analysis.safety_warning && (
            <div className="sm:col-span-2 rounded-lg bg-red-50 p-3 text-red-900">
              <dt className="font-medium">Safety warning</dt>
              <dd>{analysis.safety_warning}</dd>
            </div>
          )}
          <div>
            <dt className="font-medium text-slate-500">Confidence</dt>
            <dd>{(analysis.confidence * 100).toFixed(0)}%</dd>
          </div>
        </dl>
      </article>
      {entities && (
        <aside className="rounded-xl border border-dashed border-eco-300 bg-eco-50/50 p-4">
          <h4 className="text-sm font-semibold text-eco-900">Extracted entities</h4>
          <ul className="mt-2 grid gap-1 text-sm sm:grid-cols-2">
            <li>
              <span className="text-slate-500">Object:</span> {entities.object}
            </li>
            <li>
              <span className="text-slate-500">Brand:</span> {entities.brand || "—"}
            </li>
            <li>
              <span className="text-slate-500">Material:</span> {entities.material}
            </li>
            <li>
              <span className="text-slate-500">Hazard:</span> {entities.hazard || "—"}
            </li>
            <li>
              <span className="text-slate-500">Waste type:</span> {entities.waste_type}
            </li>
          </ul>
        </aside>
      )}
    </div>
  );
}
