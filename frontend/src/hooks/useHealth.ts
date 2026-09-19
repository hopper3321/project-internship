import { useEffect, useState } from "react";
import { fetchHealth } from "../services/api";
import type { HealthStatus } from "../types";

export function useHealth() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() =>
        setHealth({
          status: "error",
          demo_mode: true,
          ibm_configured: false,
          message: "Backend unreachable. Start the Flask server.",
        }),
      )
      .finally(() => setLoading(false));
  }, []);

  return { health, loading };
}
