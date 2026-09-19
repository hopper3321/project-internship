import { useState } from "react";
import { FileDropZone } from "../components/FileDropZone";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { useToast } from "../hooks/useToast";
import { analyzeImage } from "../services/api";
import { addHistory } from "../utils/historyStorage";

const ALLOWED = ["image/jpeg", "image/png", "image/webp"];

export function ImageAnalyzer() {
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const { push } = useToast();

  async function onFile(file: File) {
    if (!ALLOWED.includes(file.type) && !file.name.match(/\.(jpe?g|png|webp)$/i)) {
      push("Unsupported format. Use JPG, PNG, or WEBP.", "error");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      push("File too large (max 10 MB).", "error");
      return;
    }
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setLoading(true);
    try {
      const res = await analyzeImage(file);
      if (res.result.error && !res.demo_mode) {
        push(String(res.result.error), "error");
        setResult(null);
        return;
      }
      setResult(res.result);
      const cat = String(res.result.waste_category || "Other");
      addHistory({
        input: String(res.result.detected_item || "image"),
        category: cat,
        recyclable: Boolean(res.result.recyclable),
        disposal: String(res.result.disposal_recommendation || ""),
        type: "image",
      });
      push("Image analysis complete.", "success");
    } catch (err) {
      push(err instanceof Error ? err.message : "Image analysis failed.", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">Image Analyzer</h1>
        <p className="text-slate-600 mt-1">
          Upload a photo of waste for category and disposal recommendations.
        </p>
      </div>
      <FileDropZone
        accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
        label="Upload waste image (JPG, PNG, WEBP)"
        onFile={onFile}
        disabled={loading}
      />
      {preview && (
        <img
          src={preview}
          alt="Uploaded waste preview"
          className="max-h-64 rounded-lg border object-contain"
        />
      )}
      {loading && <LoadingSpinner label="Processing image…" />}
      {result && !result.error && (
        <article className="rounded-xl border bg-white p-6 shadow-sm space-y-3 text-sm">
          <h3 className="text-lg font-semibold capitalize">{String(result.detected_item)}</h3>
          <p>
            <span className="text-slate-500">Category:</span> {String(result.waste_category)}
          </p>
          <p>
            <span className="text-slate-500">Material:</span> {String(result.material)}
          </p>
          <p>
            <span className="text-slate-500">Recyclable:</span>{" "}
            {result.recyclable ? "Yes" : "No"}
          </p>
          <p>
            <span className="text-slate-500">Disposal:</span>{" "}
            {String(result.disposal_recommendation)}
          </p>
          {Boolean(result.safety_warning) && (
            <p className="rounded bg-red-50 p-2 text-red-900">
              {String(result.safety_warning)}
            </p>
          )}
          <p className="text-slate-600">{String(result.explanation)}</p>
        </article>
      )}
    </div>
  );
}
