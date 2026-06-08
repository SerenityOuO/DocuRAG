export type HealthResponse = {
  service: string;
  status: string;
  version: string;
};

export type AuthRole = "admin" | "analyst" | "viewer";

export type AuthUser = {
  username: string;
  display_name: string;
  role: AuthRole;
};

export type LoginResponse = {
  auth_mode: string;
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type MeResponse = {
  auth_mode: string;
  authenticated: boolean;
  user: AuthUser | null;
};

export type LogoutResponse = {
  auth_mode: string;
  status: string;
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
  parser_result: ParserResult | null;
  field_corrections: FieldCorrection[];
  chunks: DocumentChunk[];
  processing_jobs: ProcessingJob[];
  latest_job: ProcessingJob | null;
};

export type DocumentMetadata = UploadResponse;

export type DocumentListResponse = {
  documents: DocumentMetadata[];
};

export type DocumentDeleteResponse = {
  document_id: string;
  filename: string;
  status: "deleted";
  deleted_file_count: number;
  missing_file_count: number;
  skipped_file_count: number;
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
  parser: string;
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

export type ExtractedField = {
  value: string | number | boolean | null;
  confidence: number | null;
  source_text: string | null;
  source_page: number | null;
  source_bbox: BoundingBox | null;
  parser_source: string;
  fallback_reason: string | null;
};

export type FieldCorrection = {
  correction_id: string;
  document_id: string;
  field_name: string;
  corrected_value: string | number | boolean | null;
  reviewer: string;
  reason: string | null;
  version: number;
  source_parser_value: string | number | boolean | null;
  created_at: string;
  updated_at: string;
};

export type FieldCorrectionRequest = {
  field_name: string;
  corrected_value: string | number | boolean | null;
  reason?: string | null;
};

export type FieldCorrectionResponse = {
  document_id: string;
  corrections: FieldCorrection[];
};

export type GoldenLabel = {
  document_id: string;
  filename: string;
  project_id: string | null;
  field_name: string;
  corrected_value: string | number | boolean | null;
  reviewer: string;
  reason: string | null;
  version: number;
  source_parser_value: string | number | boolean | null;
  updated_at: string;
};

export type GoldenLabelsResponse = {
  schema_version: "parser_golden_labels_v1";
  exported_at: string;
  labels: GoldenLabel[];
};

export type InvoiceLineItem = {
  description: ExtractedField;
  quantity: ExtractedField;
  unit_price: ExtractedField;
  amount: ExtractedField;
};

export type DocumentFields = {
  document_type: ExtractedField;
  vendor_name: ExtractedField;
  invoice_number: ExtractedField;
  issue_date: ExtractedField;
  total_amount: ExtractedField;
  tax_amount: ExtractedField;
  currency: ExtractedField;
  line_items: InvoiceLineItem[];
};

export type ParserResult = {
  document_id: string;
  status: string;
  parser_source: string;
  schema_version: string;
  fields: DocumentFields;
  fallback_reason: string | null;
  error_message: string | null;
  source_ocr_status: string | null;
  source_ocr_updated_at: string | null;
  updated_at: string | null;
  trace_metadata: Record<string, string>;
};

export type VectorIndexingResponse = {
  document_id: string;
  status: string;
  indexed_chunk_count: number;
  skipped_chunk_count: number;
  point_ids: string[];
  collection_name: string | null;
  vector_size: number | null;
  embedding_provider: string | null;
  embedding_model: string | null;
  reason: string | null;
  error: string | null;
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

export type BuiltInRagEvalSummary = {
  case_count: number;
  hit_rate_at_k: number;
  mrr_at_k: number;
  average_latency_ms: number;
  failure_count: number;
  fallback_count: number;
};

export type BuiltInRagEvalCaseResult = {
  case_id: string;
  query: string;
  top_k: number;
  hit: boolean;
  first_relevant_rank: number | null;
  matched_expected_terms: string[];
  error: string | null;
  fallback_reasons: string[];
};

export type BuiltInRagEvalResponse = {
  run_id: string;
  created_at: string;
  strategy: "hybrid_rerank";
  dataset_name: string;
  dataset_path: string;
  case_count: number;
  summary: BuiltInRagEvalSummary;
  environment: Record<string, string | number | boolean | null>;
  failed_cases: BuiltInRagEvalCaseResult[];
  fallback_cases: BuiltInRagEvalCaseResult[];
};

export type EvalDataset = {
  dataset_id: string;
  project_id: string | null;
  name: string;
  description: string | null;
  schema_version: "eval_dataset_v1";
  item_count: number;
  created_at: string;
  updated_at: string;
};

export type EvalItem = {
  item_id: string;
  dataset_id: string;
  project_id: string | null;
  query: string;
  expected_terms: string[];
  expected_document_ids: string[];
  expected_chunk_ids: string[];
  tags: string[];
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type EvalDatasetListResponse = {
  datasets: EvalDataset[];
};

export type EvalDatasetDetailResponse = {
  dataset: EvalDataset;
  items: EvalItem[];
};

export type EvalItemListResponse = {
  items: EvalItem[];
};

export type EvalDatasetPayload = {
  name: string;
  description?: string | null;
};

export type EvalItemPayload = {
  query: string;
  expected_terms: string[];
  expected_document_ids?: string[];
  expected_chunk_ids?: string[];
  tags?: string[];
  notes?: string | null;
};

export type EvalStrategy = "keyword" | "vector" | "vector_rerank" | "hybrid" | "hybrid_rerank";

export type EvalFallbackReason = {
  reason: string;
  count: number;
};

export type EvalRunStrategySummary = {
  strategy: EvalStrategy;
  case_count: number;
  hit_rate_at_k: number;
  mrr_at_k: number;
  recall_at_k: number;
  average_latency_ms: number;
  failure_count: number;
  fallback_count: number;
  trace_metadata_count: number;
  result_strategy_counts: Record<string, number>;
  fallback_reasons: EvalFallbackReason[];
  environment: Record<string, unknown>;
};

export type EvalRunCaseResult = {
  case_id: string;
  item_id: string;
  strategy: string;
  query: string;
  top_k: number;
  hit: boolean;
  first_relevant_rank: number | null;
  matched_expected_terms: string[];
  error: string | null;
  fallback_reasons: string[];
};

export type EvalRerankAnalysisRow = {
  case_id: string;
  item_id: string;
  strategy: string;
  rank: number;
  document_id: string;
  filename: string;
  chunk_id: string;
  text: string;
  pre_rerank_rank: number | null;
  post_rerank_rank: number | null;
  pre_rerank_score: number | null;
  rerank_score: number | null;
  rerank_status: string | null;
  fallback_state: string | null;
};

export type EvalRunResponse = {
  run_id: string;
  dataset_id: string;
  dataset_name: string;
  project_id: string | null;
  created_at: string;
  top_k: number;
  strategies: EvalStrategy[];
  strategy_summaries: EvalRunStrategySummary[];
};

export type EvalRunItemsResponse = {
  run_id: string;
  failed_cases: EvalRunCaseResult[];
  fallback_cases: EvalRunCaseResult[];
  rerank_analysis: EvalRerankAnalysisRow[];
};

export type EvalRunPayload = {
  dataset_id: string;
  strategies?: EvalStrategy[];
  top_k?: number;
};

export type AgentToolStatus = "completed" | "failed";

export type AgentRunStatus = "pending" | "running" | "completed" | "failed";

export type AgentToolName = "get_document_fields" | "search_documents" | "summarize_invoice_fields";

export type AgentToolObservation = {
  status: AgentToolStatus;
  message: string;
  missing_fields: string[];
  fallback_reason: string | null;
};

export type AgentToolCall = {
  tool_name: AgentToolName;
  status: AgentToolStatus;
  input_summary: string;
  output_summary: string | null;
  observation: AgentToolObservation;
  output: Record<string, unknown>;
  citations: RagCitation[];
  retrieved_chunks: RetrievedChunk[];
  trace_metadata: Record<string, string>;
  error_message: string | null;
};

export type AgentStep = {
  step_id: string;
  order: number;
  title: string;
  tool_name: AgentToolName | null;
  status: AgentRunStatus;
  input_summary: string | null;
  observation_summary: string | null;
  fallback_reason: string | null;
};

export type AgentFinalAnswer = {
  text: string;
  status: AgentRunStatus;
  fallback_reason: string | null;
};

export type AgentRun = {
  run_id: string;
  status: AgentRunStatus;
  task: string;
  document_id: string | null;
  query: string | null;
  plan_steps: AgentStep[];
  tool_calls: AgentToolCall[];
  final_answer: AgentFinalAnswer;
  citations: RagCitation[];
  trace: Record<string, string>;
  created_at: string;
  updated_at: string;
};

export type AgentRunRequest = {
  task: string;
  document_id?: string;
  query?: string;
  top_k?: number;
};

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const authTokenStorageKey = "docurag_demo_auth_token";
let authToken =
  typeof window === "undefined" ? "" : window.localStorage.getItem(authTokenStorageKey) ?? "";

export const API_BASE_URL = configuredBaseUrl.replace(/\/$/, "");

export function setAuthToken(token: string): void {
  authToken = token;
  window.localStorage.setItem(authTokenStorageKey, token);
}

export function clearAuthToken(): void {
  authToken = "";
  window.localStorage.removeItem(authTokenStorageKey);
}

function authHeaders(): Record<string, string> {
  if (!authToken) {
    return {};
  }

  return {
    Authorization: `Bearer ${authToken}`,
  };
}

function jsonHeaders(): Record<string, string> {
  return {
    "Content-Type": "application/json",
    ...authHeaders(),
  };
}

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

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      password,
    }),
  });

  return readJson<LoginResponse>(response);
}

export async function logout(): Promise<LogoutResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
    headers: authHeaders(),
  });

  return readJson<LogoutResponse>(response);
}

export async function getMe(): Promise<MeResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: authHeaders(),
  });

  return readJson<MeResponse>(response);
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  return readJson<UploadResponse>(response);
}

export async function listDocuments(): Promise<DocumentListResponse> {
  const response = await fetch(`${API_BASE_URL}/documents`, {
    headers: authHeaders(),
  });
  return readJson<DocumentListResponse>(response);
}

export async function getDocument(documentId: string): Promise<DocumentMetadata> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    headers: authHeaders(),
  });
  return readJson<DocumentMetadata>(response);
}

export async function deleteDocument(documentId: string): Promise<DocumentDeleteResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  return readJson<DocumentDeleteResponse>(response);
}

export async function runMockOcr(documentId: string): Promise<OcrResultResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/ocr/mock`, {
    method: "POST",
    headers: authHeaders(),
  });

  return readJson<OcrResultResponse>(response);
}

export async function runSelectedOcr(documentId: string): Promise<OcrResultResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/ocr`, {
    method: "POST",
    headers: authHeaders(),
  });

  return readJson<OcrResultResponse>(response);
}

export async function getOcrResult(documentId: string): Promise<OcrResultResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/ocr`, {
    headers: authHeaders(),
  });
  return readJson<OcrResultResponse>(response);
}

export async function parseDocumentFields(documentId: string): Promise<ParserResult> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/parse`, {
    method: "POST",
    headers: authHeaders(),
  });

  return readJson<ParserResult>(response);
}

export async function getDocumentFields(documentId: string): Promise<ParserResult> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/fields`, {
    headers: authHeaders(),
  });
  return readJson<ParserResult>(response);
}

export async function saveDocumentCorrections(
  documentId: string,
  corrections: FieldCorrectionRequest[],
): Promise<FieldCorrectionResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/corrections`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify({
      corrections,
    }),
  });

  return readJson<FieldCorrectionResponse>(response);
}

export async function exportGoldenLabels(): Promise<GoldenLabelsResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/golden-labels`, {
    headers: authHeaders(),
  });

  return readJson<GoldenLabelsResponse>(response);
}

export async function indexDocumentVector(documentId: string): Promise<VectorIndexingResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/index/vector`, {
    method: "POST",
    headers: authHeaders(),
  });

  return readJson<VectorIndexingResponse>(response);
}

export async function queryRag(query: string, topK: number): Promise<RagQueryResponse> {
  const response = await fetch(`${API_BASE_URL}/rag/query`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify({
      query,
      top_k: topK,
    }),
  });

  return readJson<RagQueryResponse>(response);
}

export async function runBuiltInRagEval(): Promise<BuiltInRagEvalResponse> {
  const response = await fetch(`${API_BASE_URL}/eval/rag/built-in`, {
    method: "POST",
    headers: jsonHeaders(),
  });

  return readJson<BuiltInRagEvalResponse>(response);
}

export async function listEvalDatasets(): Promise<EvalDatasetListResponse> {
  const response = await fetch(`${API_BASE_URL}/eval/datasets`, {
    headers: authHeaders(),
  });

  return readJson<EvalDatasetListResponse>(response);
}

export async function createEvalDataset(payload: EvalDatasetPayload): Promise<EvalDataset> {
  const response = await fetch(`${API_BASE_URL}/eval/datasets`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify(payload),
  });

  return readJson<EvalDataset>(response);
}

export async function updateEvalDataset(datasetId: string, payload: EvalDatasetPayload): Promise<EvalDataset> {
  const response = await fetch(`${API_BASE_URL}/eval/datasets/${datasetId}`, {
    method: "PATCH",
    headers: jsonHeaders(),
    body: JSON.stringify(payload),
  });

  return readJson<EvalDataset>(response);
}

export async function deleteEvalDataset(datasetId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/eval/datasets/${datasetId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  await readJson<unknown>(response);
}

export async function getEvalDataset(datasetId: string): Promise<EvalDatasetDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/eval/datasets/${datasetId}`, {
    headers: authHeaders(),
  });

  return readJson<EvalDatasetDetailResponse>(response);
}

export async function listEvalItems(datasetId: string): Promise<EvalItemListResponse> {
  const response = await fetch(`${API_BASE_URL}/eval/datasets/${datasetId}/items`, {
    headers: authHeaders(),
  });

  return readJson<EvalItemListResponse>(response);
}

export async function createEvalItem(datasetId: string, payload: EvalItemPayload): Promise<EvalItem> {
  const response = await fetch(`${API_BASE_URL}/eval/datasets/${datasetId}/items`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify(payload),
  });

  return readJson<EvalItem>(response);
}

export async function updateEvalItem(datasetId: string, itemId: string, payload: EvalItemPayload): Promise<EvalItem> {
  const response = await fetch(`${API_BASE_URL}/eval/datasets/${datasetId}/items/${itemId}`, {
    method: "PATCH",
    headers: jsonHeaders(),
    body: JSON.stringify(payload),
  });

  return readJson<EvalItem>(response);
}

export async function deleteEvalItem(datasetId: string, itemId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/eval/datasets/${datasetId}/items/${itemId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  await readJson<unknown>(response);
}

export async function runEvalStrategyComparison(payload: EvalRunPayload): Promise<EvalRunResponse> {
  const response = await fetch(`${API_BASE_URL}/eval/runs`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify(payload),
  });

  return readJson<EvalRunResponse>(response);
}

export async function getEvalRunItems(runId: string): Promise<EvalRunItemsResponse> {
  const response = await fetch(`${API_BASE_URL}/eval/runs/${runId}/items`, {
    headers: authHeaders(),
  });

  return readJson<EvalRunItemsResponse>(response);
}

export async function runAgent(request: AgentRunRequest): Promise<AgentRun> {
  const response = await fetch(`${API_BASE_URL}/agent/run`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify(request),
  });

  return readJson<AgentRun>(response);
}
