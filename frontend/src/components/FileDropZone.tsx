import { Upload } from "lucide-react";
import { useCallback, useState } from "react";

export function FileDropZone({
  accept,
  label,
  onFile,
  disabled,
}: {
  accept: string;
  label: string;
  onFile: (file: File) => void;
  disabled?: boolean;
}) {
  const [drag, setDrag] = useState(false);

  const handle = useCallback(
    (file: File | undefined) => {
      if (file && !disabled) onFile(file);
    },
    [disabled, onFile],
  );

  return (
    <label
      className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition ${
        drag ? "border-eco-500 bg-eco-50" : "border-slate-300 bg-white hover:border-eco-400"
      } ${disabled ? "pointer-events-none opacity-50" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        handle(e.dataTransfer.files[0]);
      }}
    >
      <Upload className="mb-2 h-10 w-10 text-eco-600" aria-hidden />
      <span className="font-medium text-slate-700">{label}</span>
      <span className="mt-1 text-xs text-slate-500">Drag and drop or click to browse</span>
      <input
        type="file"
        className="sr-only"
        accept={accept}
        disabled={disabled}
        onChange={(e) => handle(e.target.files?.[0])}
      />
    </label>
  );
}
