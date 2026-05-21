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
  ocr: OcrResult;
};

export type DocumentMetadata = UploadResponse;

export type DocumentListResponse = {
  documents: DocumentMetadata[];
};

export type OcrResult = {
  status: string;
  text: string;
  extracted_fields: Record<string, string>;
  updated_at: string | null;
};

export type OcrResultResponse = OcrResult & {
  document_id: string;
};

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export const API_BASE_URL = configuredBaseUrl.replace(/\/$/, "");

async function readJson<T>(response: Response): Promise<T> {
  const body = (await response.json()) as T;

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return body;
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

export async function getOcrResult(documentId: string): Promise<OcrResultResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/ocr`);
  return readJson<OcrResultResponse>(response);
}
