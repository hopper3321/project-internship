import { useToast } from "../hooks/useToast";

export function ToastContainer() {
  const { toasts, dismiss } = useToast();
  return (
    <div
      className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm"
      aria-live="polite"
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`rounded-lg border px-4 py-3 text-sm shadow-lg ${
            t.type === "error"
              ? "border-red-200 bg-red-50 text-red-900"
              : t.type === "success"
                ? "border-green-200 bg-green-50 text-green-900"
                : "border-slate-200 bg-white text-slate-800"
          }`}
        >
          <div className="flex justify-between gap-2">
            <span>{t.message}</span>
            <button
              type="button"
              className="text-xs underline shrink-0"
              onClick={() => dismiss(t.id)}
            >
              Dismiss
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
