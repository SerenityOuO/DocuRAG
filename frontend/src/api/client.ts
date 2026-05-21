export type HealthResponse = {
  service: string;
  status: string;
  version: string;
};

export type UploadResponse = {
  document_id: string;
  project_id: string | null;
  filename: string;
  stored_filename: string;
  file_type: string;
  content_type: string;
  size: number;
  status: string;
  created_at: string;
  processing: DocumentProcessingStatus;
  ocr: OcrResult;
  chunks: DocumentChunk[];
  processing_jobs: ProcessingJob[];
  latest_job: ProcessingJob | null;
};

export type DocumentMetadata = UploadResponse;

export type DocumentListResponse = {
  documents: DocumentMetadata[];
};

export type OcrResult = {
  status: string;
  text: string;
  extracted_fields: Record<string, string>;
  lines: OcrTextLine[];
  updated_at: string | null;
};

export type DocumentProcessingStatus = {
  upload: string;
  ocr: string;
  indexing: string;
  ready: boolean;
  failed_reason: string | null;
  updated_at: string | null;
};

export type ProcessingJob = {
  job_id: string;
  document_id: string;
  job_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  error_message: string | null;
};

export type OcrResultResponse = OcrResult & {
  document_id: string;
};

export type BoundingBox = {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
};

export type OcrTextLine = {
  text: string;
  page_number: number | null;
  bbox: BoundingBox | null;
  confidence: number | null;
  metadata: Record<string, string>;
};

export type DocumentChunk = {
  chunk_id: string;
  document_id: string;
  text: string;
  source: string;
  created_at: string;
  page_number: number | null;
  bbox: BoundingBox | null;
  confidence: number | null;
  source_type: string;
  metadata: Record<string, string>;
};

export type RagCitation = {
  document_id: string;
  filename: string;
  chunk_id: string;
  page_number: number | null;
  bbox: BoundingBox | null;
  confidence: number | null;
  source_type: string | null;
  trace_metadata: Record<string, string>;
};

export type RetrievedChunk = DocumentChunk & {
  filename: string;
  score: number;
};

export type RagQueryResponse = {
  answer: string;
  citations: RagCitation[];
  retrieved_chunks: RetrievedChunk[];
};

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export const API_BASE_URL = configuredBaseUrl.replace(/\/$/, "");

async function readJson<T>(response: Response): Promise<T> {
  const body = (await response.json()) as unknown;

  if (!response.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body
        ? (body as { detail?: unknown }).detail
        : null;
    const message =
      typeof detail === "string"
        ? detail
        : detail && typeof detail === "object"
          ? JSON.stringify(detail)
          : `API request failed: ${response.status}`;

    throw new Error(message);
  }

  return body as T;
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return readJson<HealthResponse>(response);
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  return readJson<UploadResponse>(response);
}

export async function listDocuments(): Promise<DocumentListResponse> {
  const response = await fetch(`${API_BASE_URL}/documents`);
  return readJson<DocumentListResponse>(response);
}

export async function getDocument(documentId: string): Promise<DocumentMetadata> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`);
  return readJson<DocumentMetadata>(response);
}

export async function runMockOcr(documentId: string): Promise<OcrResultResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/ocr/mock`, {
    method: "POST",
  });

  return readJson<OcrResultResponse>(response);
}

export async function runSelectedOcr(documentId: string): Promise<OcrResultResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/ocr`, {
    method: "POST",
  });

  return readJson<OcrResultResponse>(response);
}

export async function getOcrResult(documentId: string): Promise<OcrResultResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/ocr`);
  return readJson<OcrResultResponse>(response);
}

export async function queryRag(query: string, topK: number): Promise<RagQueryResponse> {
  const response = await fetch(`${API_BASE_URL}/rag/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      top_k: topK,
    }),
  });

  return readJson<RagQueryResponse>(response);
}
