export function LoadingSpinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-eco-700" role="status">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-eco-600 border-t-transparent" />
      <span>{label}</span>
    </div>
  );
}
