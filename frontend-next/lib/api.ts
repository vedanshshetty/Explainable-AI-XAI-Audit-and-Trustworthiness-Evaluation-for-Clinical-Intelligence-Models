import type { AnalysisResponse, AnalyzeRequest } from "./types";

/**
 * Requests go through the Next.js rewrite defined in next.config.mjs
 * (/api/backend/* -> http://localhost:8000/*) so the browser makes a same-origin
 * call. That avoids CORS entirely and leaves the FastAPI backend untouched.
 */
const BASE = "/api/backend";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function analyze(payload: AnalyzeRequest): Promise<AnalysisResponse> {
  let response: Response;
  try {
    response = await fetch(`${BASE}/api/v1/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      "Could not reach the backend. Start it with `python run.py` (or `python run_backend.py`) and confirm http://localhost:8000 responds.",
      0,
    );
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body && typeof body.detail === "string") detail = body.detail;
    } catch {
      /* keep the generic message */
    }
    throw new ApiError(detail, response.status);
  }

  try {
    return (await response.json()) as AnalysisResponse;
  } catch {
    throw new ApiError("Backend returned a response that could not be parsed as JSON.", response.status);
  }
}

export async function fetchStatus(): Promise<{
  status: string;
  model: string;
  k_retrieve: number;
  k_rerank: number;
  corpus_docs: number;
  indexed_docs: number;
  index_in_sync: boolean;
} | null> {
  try {
    const response = await fetch(`${BASE}/api/v1/status`, { cache: "no-store" });
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}