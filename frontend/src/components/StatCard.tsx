import type { LucideIcon } from "lucide-react";

export function StatCard({
  title,
  value,
  icon: Icon,
  accent = "bg-white",
}: {
  title: string;
  value: number | string;
  icon: LucideIcon;
  accent?: string;
}) {
  return (
    <div className={`rounded-xl border border-slate-200 p-5 shadow-sm ${accent}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
        </div>
        <Icon className="h-8 w-8 text-eco-600 opacity-80" aria-hidden />
      </div>
    </div>
  );
}
