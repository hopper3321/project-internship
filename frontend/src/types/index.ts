export interface WasteAnalysis {
  item: string;
  category: string;
  material: string;
  recyclable: boolean;
  disposal_method: string;
  recycling_guidance: string;
  environmental_impact: string;
  safety_warning: string;
  confidence: number;
}

export interface Entities {
  object: string;
  brand: string;
  material: string;
  hazard: string;
  waste_type: string;
}

export interface HistoryEntry {
  id: string;
  date: string;
  input: string;
  category: string;
  recyclable: boolean;
  disposal: string;
  type: "text" | "image";
}

export interface DocumentMeta {
  document_id: string;
  filename: string;
  chunks: number;
  characters: number;
}

export interface DocSummary {
  main_topic: string;
  key_points: string[];
  waste_management_rules: string[];
  important_warnings: string[];
  actionable_recommendations: string[];
}

export interface HealthStatus {
  status: string;
  demo_mode: boolean;
  ibm_configured: boolean;
  message: string;
}

export interface ApiError {
  error: string;
  demo_mode?: boolean;
}
