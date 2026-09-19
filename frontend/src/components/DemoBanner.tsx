import { AlertTriangle } from "lucide-react";
import { useHealth } from "../hooks/useHealth";

export function DemoBanner() {
  const { health, loading } = useHealth();
  if (loading || !health?.demo_mode) return null;
  return (
    <div
      role="status"
      className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-900"
    >
      <div className="mx-auto flex max-w-6xl items-center gap-2">
        <AlertTriangle className="h-4 w-4 shrink-0" aria-hidden />
        <span>
          <strong>Demo Mode</strong> – IBM Granite API is not connected. Responses use
          deterministic local samples.
        </span>
      </div>
    </div>
  );
}
