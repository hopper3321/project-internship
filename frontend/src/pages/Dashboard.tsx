import { Camera, FileText, MessageCircle, Search } from "lucide-react";
import { Link } from "react-router-dom";
import { useMemo } from "react";
import { StatCard } from "../components/StatCard";
import { historyStats, loadHistory } from "../utils/historyStorage";

const actions = [
  { to: "/analyzer", label: "Analyze Waste", icon: Search, desc: "Type an item name" },
  { to: "/image", label: "Upload Image", icon: Camera, desc: "Photo-based analysis" },
  { to: "/chat", label: "Ask AI", icon: MessageCircle, desc: "Chat assistant" },
  { to: "/documents", label: "Upload Document", icon: FileText, desc: "RAG knowledge base" },
];

export function Dashboard() {
  const history = useMemo(() => loadHistory(), []);
  const stats = historyStats(history);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-600 mt-1">
          Overview of your waste analyses (stored locally in this browser).
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total analyses" value={stats.total} icon={Search} />
        <StatCard title="Recyclable items" value={stats.recyclable} icon={Search} accent="bg-green-50" />
        <StatCard title="Non-recyclable" value={stats.nonRecyclable} icon={Search} />
        <StatCard title="Hazardous / E-waste" value={stats.hazardous} icon={Search} accent="bg-amber-50" />
      </div>
      <section>
        <h2 className="text-lg font-semibold mb-3">Quick actions</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {actions.map((a) => (
            <Link
              key={a.to}
              to={a.to}
              className="rounded-xl border bg-white p-5 shadow-sm transition hover:border-eco-400 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-eco-500"
            >
              <a.icon className="h-8 w-8 text-eco-600 mb-2" aria-hidden />
              <h3 className="font-semibold">{a.label}</h3>
              <p className="text-sm text-slate-500 mt-1">{a.desc}</p>
            </Link>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-lg font-semibold mb-3">Recent analyses</h2>
        {history.length === 0 ? (
          <p className="rounded-xl border border-dashed p-8 text-center text-slate-500">
            No analyses yet. Use Waste Analyzer or Image Analyzer to get started.
          </p>
        ) : (
          <ul className="divide-y rounded-xl border bg-white">
            {history.slice(0, 8).map((h) => (
              <li key={h.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm">
                <span className="font-medium capitalize">{h.input}</span>
                <span className="text-slate-500">{new Date(h.date).toLocaleString()}</span>
                <span className="rounded bg-slate-100 px-2 py-0.5">{h.category}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
