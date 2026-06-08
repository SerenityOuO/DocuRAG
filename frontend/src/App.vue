<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  API_BASE_URL,
  clearAuthToken,
  createEvalDataset,
  createEvalItem,
  deleteEvalDataset,
  deleteEvalItem,
  getEvalRunItems,
  getHealth,
  getMe,
  listEvalDatasets,
  listEvalItems,
  indexDocumentVector,
  listDocuments,
  login as loginDemo,
  logout as logoutDemo,
  parseDocumentFields,
  queryRag,
  runAgent,
  runBuiltInRagEval,
  runEvalStrategyComparison,
  runMockOcr,
  runSelectedOcr,
  updateEvalDataset,
  updateEvalItem,
  uploadDocument,
  type AgentRun,
  type AuthRole,
  type AuthUser,
  type BuiltInRagEvalCaseResult,
  type BuiltInRagEvalResponse,
  type BoundingBox,
  type DocumentMetadata,
  type DocumentFields,
  type EvalDataset,
  type EvalItem,
  type EvalRerankAnalysisRow,
  type EvalRunCaseResult,
  type EvalRunItemsResponse,
  type EvalRunResponse,
  type EvalStrategy,
  type ExtractedField,
  type HealthResponse,
  type ParserResult,
  type RagQueryResponse,
  type UploadResponse,
  setAuthToken,
} from "./api/client";

type RequestState = "idle" | "loading" | "success" | "error";
type AuthRequestState = RequestState | "checking";
type ViewMode = "viewer" | "admin";

type SourceSummary = {
  filename: string;
  chunkIds: string[];
};

type InvoiceFieldKey =
  | "document_type"
  | "vendor_name"
  | "invoice_number"
  | "issue_date"
  | "total_amount"
  | "tax_amount"
  | "currency";

const healthState = ref<RequestState>("idle");
const authState = ref<AuthRequestState>("checking");
const chatState = ref<RequestState>("idle");
const documentsState = ref<RequestState>("idle");
const uploadState = ref<RequestState>("idle");
const viewMode = ref<ViewMode>("admin");
const authMode = ref("disabled");
const authUser = ref<AuthUser | null>(null);
const health = ref<HealthResponse | null>(null);
const ragResult = ref<RagQueryResponse | null>(null);
const documents = ref<DocumentMetadata[]>([]);
const uploadResult = ref<UploadResponse | null>(null);
const selectedFiles = ref<File[]>([]);
const uploadFallbackAvailable = ref(false);
const ragQuery = ref("");
const ragTopK = ref(3);
const healthError = ref("");
const authError = ref("");
const ragError = ref("");
const documentsError = ref("");
const uploadError = ref("");
const uploadMessage = ref("");
const parseStates = ref<Record<string, RequestState>>({});
const parseErrors = ref<Record<string, string>>({});
const agentState = ref<RequestState>("idle");
const agentRun = ref<AgentRun | null>(null);
const agentTask = ref("整理這份 invoice 欄位，並補充付款期限來源。");
const agentDocumentId = ref("");
const agentQuery = ref("付款期限 / payment terms");
const agentTopK = ref(3);
const agentError = ref("");
const ragEvalState = ref<RequestState>("idle");
const ragEvalResult = ref<BuiltInRagEvalResponse | null>(null);
const ragEvalError = ref("");
const evalDatasetState = ref<RequestState>("idle");
const evalItemState = ref<RequestState>("idle");
const evalDatasets = ref<EvalDataset[]>([]);
const evalItems = ref<EvalItem[]>([]);
const selectedEvalDatasetId = ref("");
const editingEvalItemId = ref("");
const evalDatasetName = ref("Invoice retrieval quality");
const evalDatasetDescription = ref("Demo-safe RAG evaluation dataset");
const evalDatasetError = ref("");
const evalDatasetMessage = ref("");
const evalItemQuery = ref("付款期限是什麼？");
const evalItemExpectedTerms = ref("Net 15, payment terms");
const evalItemExpectedDocumentIds = ref("");
const evalItemExpectedChunkIds = ref("");
const evalItemTags = ref("invoice");
const evalItemNotes = ref("");
const evalItemError = ref("");
const evalItemMessage = ref("");
const strategyEvalState = ref<RequestState>("idle");
const strategyEvalResult = ref<EvalRunResponse | null>(null);
const strategyEvalItems = ref<EvalRunItemsResponse | null>(null);
const strategyEvalTopK = ref(5);
const strategyEvalStrategies = ref<EvalStrategy[]>(["keyword", "hybrid_rerank", "vector"]);
const strategyEvalError = ref("");
const loginUsername = ref("admin");
const loginPassword = ref("demo-admin-pass");

const suggestedQuestions = [
  "payment due date Net 15",
  "What is the SLA response target?",
  "When is the renewal date?",
];

const currentVersionLabel = computed(() => (health.value?.version ? `v${health.value.version}` : "v0.43.0"));

const demoAuthRequired = computed(() => authMode.value === "demo" && authUser.value === null);
const formalAuthRequired = computed(() => authMode.value === "formal" && authUser.value === null);
const roleGuardEnabled = computed(() => authMode.value === "demo" || authMode.value === "formal");
const canUseReadSurface = computed(() => !roleGuardEnabled.value || authUser.value !== null);
const canUseIngestion = computed(() => {
  if (!roleGuardEnabled.value) {
    return true;
  }

  return authUser.value?.role === "admin" || authUser.value?.role === "analyst";
});
const authSurfaceLabel = computed(() => {
  if (authMode.value === "formal") {
    return "Formal Auth";
  }

  if (authMode.value === "demo") {
    return "Demo Auth";
  }

  return "Auth Mode";
});
const currentRoleLabel = computed(() => {
  if (!authUser.value) {
    return authMode.value;
  }

  const roleLabel = roleLabels[authUser.value.role] ?? authUser.value.role;
  return `${authUser.value.display_name} / ${roleLabel}`;
});

const heroCopy = computed(() =>
  viewMode.value === "admin"
    ? "後台知識庫管理入口，讓 Admin / Analyst 建立可供前台查詢的文件資料。"
    : "前台查詢入口，只回答後端已建立的文件知識庫；資料建立由後台知識庫管理流程處理。",
);

const healthLabel = computed(() => {
  if (healthState.value === "success" && health.value?.status === "ok") {
    return "後端在線";
  }

  if (healthState.value === "loading") {
    return "連線檢查中";
  }

  if (healthState.value === "error") {
    return "後端未連線";
  }

  return "尚未檢查";
});

const ragTraceMetadata = computed(() => {
  const citationTrace = ragResult.value?.citations[0]?.trace_metadata ?? {};
  const chunkMetadata = ragResult.value?.retrieved_chunks[0]?.metadata ?? {};

  return {
    ...chunkMetadata,
    ...citationTrace,
  };
});

const ragAnswerSource = computed(() => {
  const trace = ragTraceMetadata.value;

  if (trace.llm_generation_status === "completed") {
    return `${trace.llm_provider ?? "ollama"}/${trace.llm_model ?? "qwen3.5:4b"}`;
  }

  if (trace.llm_generation_status === "failed") {
    return "LLM 不可用，改用後端備援";
  }

  return "確定性基準回答";
});

const ragRetrievalSource = computed(() => {
  const trace = ragTraceMetadata.value;

  if (trace.strategy_label === "hybrid_rerank") {
    if (trace.fallback_state && trace.fallback_state !== "none") {
      return `hybrid_rerank 備援：${trace.fallback_state}`;
    }

    return "hybrid_rerank";
  }

  if (trace.strategy_label === "hybrid") {
    return "hybrid";
  }

  if (trace.strategy_label === "vector_rerank") {
    if (trace.rerank_status && trace.rerank_status !== "completed") {
      return `vector_rerank 備援：${trace.rerank_status}`;
    }

    return "vector_rerank";
  }

  if (trace.vector_retrieval_status === "completed") {
    return `${trace.retrieval_provider ?? "vector"}/${trace.vector_store ?? "qdrant"}`;
  }

  if (trace.vector_retrieval_status === "failed") {
    return "向量檢索不可用，改用後端備援";
  }

  return "關鍵字基準檢索";
});

const citedSources = computed<SourceSummary[]>(() => {
  const summaries = new Map<string, Set<string>>();

  for (const citation of ragResult.value?.citations ?? []) {
    const chunkIds = summaries.get(citation.filename) ?? new Set<string>();
    chunkIds.add(citation.chunk_id);
    summaries.set(citation.filename, chunkIds);
  }

  return Array.from(summaries.entries()).map(([filename, chunkIds]) => ({
    filename,
    chunkIds: Array.from(chunkIds),
  }));
});

const latestDocuments = computed(() => documents.value.slice(0, 5));
const agentDocumentOptions = computed(() => latestDocuments.value);
const selectedFileSummary = computed(() => {
  if (selectedFiles.value.length === 0) {
    return "";
  }

  if (selectedFiles.value.length === 1) {
    const [file] = selectedFiles.value;
    return `${file.name} - ${formatBytes(file.size)}`;
  }

  return `已選擇 ${selectedFiles.value.length} 個檔案：${selectedFiles.value.map((file) => file.name).join("、")}`;
});
const uploadButtonLabel = computed(() => {
  if (uploadState.value === "loading") {
    return selectedFiles.value.length > 1 ? "後台依序處理中..." : "後台處理中...";
  }

  if (selectedFiles.value.length > 1) {
    return "依序建立多檔知識庫資料";
  }

  const [file] = selectedFiles.value;
  if (file && isTextUploadFile(file)) {
    return "建立 direct text 知識庫資料";
  }

  if (file && isPdfUploadFile(file)) {
    return "建立 text-native PDF 知識庫資料";
  }

  return "建立進階 demo 知識庫資料";
});

const ragEvalStatusLabel = computed(() => {
  if (ragEvalState.value === "loading") {
    return "測試中";
  }

  if (ragEvalResult.value) {
    return `完成 ${ragEvalResult.value.summary.case_count} cases`;
  }

  return "尚未執行";
});
const selectedEvalDataset = computed(
  () => evalDatasets.value.find((dataset) => dataset.dataset_id === selectedEvalDatasetId.value) ?? null,
);
const evalDatasetStatusLabel = computed(() => {
  if (evalDatasetState.value === "loading") {
    return "同步中";
  }

  if (selectedEvalDataset.value) {
    return `${selectedEvalDataset.value.item_count} items`;
  }

  if (evalDatasets.value.length > 0) {
    return `${evalDatasets.value.length} datasets`;
  }

  return "尚未建立";
});
const evalItemFormModeLabel = computed(() => (editingEvalItemId.value ? "更新 item" : "新增 item"));

const strategyEvalStatusLabel = computed(() => {
  if (strategyEvalState.value === "loading") {
    return "Running";
  }

  if (strategyEvalResult.value) {
    return `${strategyEvalResult.value.strategy_summaries.length} strategies`;
  }

  if (selectedEvalDataset.value) {
    return "Ready";
  }

  return "Select dataset";
});

const demoUsers: Array<{ role: AuthRole; label: string; username: string; password: string }> = [
  {
    role: "admin",
    label: "Admin",
    username: "admin",
    password: "demo-admin-pass",
  },
  {
    role: "analyst",
    label: "Analyst",
    username: "analyst",
    password: "demo-analyst-pass",
  },
  {
    role: "viewer",
    label: "Viewer",
    username: "viewer",
    password: "demo-viewer-pass",
  },
];

const roleLabels: Record<AuthRole, string> = {
  admin: "Admin",
  analyst: "Analyst",
  viewer: "Viewer",
};

const invoiceFieldLabels: Array<[InvoiceFieldKey, string]> = [
  ["document_type", "文件類型"],
  ["invoice_number", "發票號碼"],
  ["vendor_name", "供應商"],
  ["issue_date", "日期"],
  ["total_amount", "總金額"],
  ["tax_amount", "稅額"],
  ["currency", "幣別"],
];

const statusLabels: Record<string, string> = {
  idle: "待命",
  loading: "處理中",
  pending: "待處理",
  running: "執行中",
  success: "成功",
  uploaded: "已上傳",
  ready: "已就緒",
  completed: "已完成",
  parsed: "已解析",
  parsing: "解析中",
  failed: "失敗",
  error: "錯誤",
};

const toolLabels: Record<string, string> = {
  get_document_fields: "讀取結構化欄位",
  search_documents: "搜尋文件內容",
  summarize_invoice_fields: "彙整發票欄位",
};

const stepTitleLabels: Record<string, string> = {
  "Read structured invoice fields": "讀取結構化欄位",
  "Search supporting document chunks": "搜尋相關文件片段",
  "Summarize invoice fields": "彙整發票欄位",
  "Reject unsupported demo task": "拒絕不支援的 demo 任務",
};

const traceValueLabels: Record<string, string> = {
  deterministic: "確定性規劃器",
  allowlisted_read_only: "唯讀 allowlist 工具",
  tiered_read_only_guarded: "分級唯讀工具檢查",
  allowed: "允許",
  forbidden: "禁止",
  "read-only": "唯讀",
  no_side_effects: "不修改資料",
  not_required: "不需要",
  auth_disabled_or_local: "本地未啟用權限模式",
  role_allowed: "角色允許",
  tool_permission_forbidden: "工具權限不足",
};

const agentMessageLabels: Record<string, string> = {
  "Parser result was available.": "已取得欄位解析結果。",
  "Parser result is not available for this document.": "這份文件還沒有可用的欄位解析結果。",
  "Document not found.": "找不到文件。",
  "Document not found for search.": "搜尋時找不到指定文件。",
  "Document search failed.": "文件搜尋失敗。",
  "No document chunks matched the query.": "沒有找到符合查詢的文件片段。",
  "Document search returned matching chunks.": "已找到符合查詢的文件片段。",
  "Cannot summarize invoice fields before parser result is available.": "欄位解析結果尚不可用，無法彙整發票欄位。",
  "Invoice fields were summarized with deterministic formatting.": "已用確定性格式彙整發票欄位。",
  "No document_id or query was provided for the demo-safe planner.": "尚未提供文件或查詢內容，demo-safe 規劃器無法執行。",
  "Tool execution was blocked by permission guard.": "工具執行已被權限檢查阻擋。",
};

const fallbackReasonLabels: Record<string, string> = {
  document_not_found: "找不到文件",
  evidence_unavailable: "沒有可用 evidence",
  evidence_unmatched: "欄位值未對回 OCR evidence",
  field_not_found: "欄位未找到",
  missing_fields: "欄位不完整",
  no_retrieved_chunks: "沒有找到可引用片段",
  parser_result_missing: "缺少欄位解析結果",
  summary_failed: "欄位彙整失敗",
  tool_error: "工具執行錯誤",
  tool_failed: "工具執行失敗",
  unsupported_task: "不支援的任務",
  unsupported_file: "檔案格式不支援 VLM，已使用備援解析",
  tool_permission_forbidden: "工具權限不足",
};

const agentFieldLabels: Record<string, string> = {
  document_type: "文件類型",
  vendor_name: "供應商",
  invoice_number: "發票號碼",
  issue_date: "日期",
  total_amount: "總金額",
  tax_amount: "稅額",
  currency: "幣別",
  line_items: "品項明細",
};

function sourceTone(source: string): "status-failed" | "status-ready" | "status-success" {
  if (source.includes("備援") || source.includes("不可用")) {
    return "status-failed";
  }

  if (source.includes("基準")) {
    return "status-ready";
  }

  return "status-success";
}

function openViewerSurface(): void {
  viewMode.value = "viewer";
}

function openAdminSurface(): void {
  if (!canUseIngestion.value) {
    viewMode.value = "viewer";
    return;
  }

  viewMode.value = "admin";
  if (documentsState.value === "idle") {
    void refreshDocuments();
  }
  if (evalDatasetState.value === "idle") {
    void refreshEvalDatasets();
  }
}

function formatBytes(size: number): string {
  return `${size.toLocaleString()} 位元組`;
}

function statusLabel(status: string | null | undefined): string {
  if (!status) {
    return "待處理";
  }

  return statusLabels[status] ?? status;
}

function toolLabel(toolName: string | null | undefined): string {
  if (!toolName) {
    return "不呼叫工具";
  }

  return toolLabels[toolName] ?? toolName;
}

function handleFileChange(event: Event): void {
  const input = event.target as HTMLInputElement;
  selectedFiles.value = Array.from(input.files ?? []);
  uploadResult.value = null;
  uploadFallbackAvailable.value = false;
  uploadMessage.value = "";
  uploadError.value = "";
}

function isTextUploadFile(file: File): boolean {
  return file.name.toLowerCase().endsWith(".txt");
}

function isPdfUploadFile(file: File): boolean {
  return file.name.toLowerCase().endsWith(".pdf");
}

function hasDirectTextChunks(document: DocumentMetadata): boolean {
  return document.chunks.some((chunk) => ["text_upload", "pdf_text"].includes(chunk.source_type));
}

function processingReason(document: DocumentMetadata): string {
  return document.processing.failed_reason ?? "";
}

function chunkReadiness(document: DocumentMetadata): string {
  if (document.chunks.length > 0) {
    const sourceType = document.chunks[0]?.source_type;
    if (sourceType === "text_upload") {
      return `文字 chunks 已建立 (${document.chunks.length})`;
    }

    if (sourceType === "pdf_text") {
      return `PDF 文字 chunks 已建立 (${document.chunks.length})`;
    }

    return `local chunks 已建立 (${document.chunks.length})`;
  }

  if (processingReason(document).includes("pdf_scanned_pending_ocr")) {
    return "掃描 PDF 待 OCR";
  }

  if (processingReason(document).includes("pdf_text_extraction_failed")) {
    return "PDF 文字抽取失敗";
  }

  return "local chunks 尚未建立";
}

function documentSourceLabel(document: DocumentMetadata): string {
  const sourceType = document.chunks[0]?.source_type;
  if (sourceType === "text_upload") {
    return "直接文字匯入";
  }

  if (sourceType === "pdf_text") {
    return "text-native PDF";
  }

  if (sourceType) {
    return sourceType;
  }

  if (processingReason(document).includes("pdf_scanned_pending_ocr")) {
    return "掃描 PDF 待 OCR";
  }

  if (processingReason(document).includes("pdf_text_extraction_failed")) {
    return "PDF 文字抽取失敗";
  }

  if (document.file_type === "txt") {
    return "文字待匯入";
  }

  if (document.file_type === "pdf") {
    return "PDF 文字待抽取";
  }

  return "圖片 OCR";
}

function documentStatusTone(status: string): string {
  if (["ready", "completed", "success"].includes(status)) {
    return "status-success";
  }

  if (["failed", "error"].includes(status)) {
    return "status-failed";
  }

  return "status-ready";
}

function parserStatus(document: DocumentMetadata): string {
  if (document.parser_result?.status) {
    return document.parser_result.status;
  }

  return document.processing.parser ?? "pending";
}

function canParseDocument(document: DocumentMetadata): boolean {
  return (
    canUseIngestion.value &&
    (
      document.ocr.status === "completed" ||
      document.processing.ocr === "completed" ||
      hasDirectTextChunks(document)
    )
  );
}

function formatFieldValue(field: ExtractedField): string {
  if (field.value === null || field.value === undefined || field.value === "") {
    return "missing";
  }

  return String(field.value);
}

function formatAmount(fields: DocumentFields): string {
  const amount = formatFieldValue(fields.total_amount);

  if (amount === "missing") {
    return amount;
  }

  const currency = fields.currency.value ? ` ${fields.currency.value}` : "";
  return `${amount}${currency}`;
}

function formatPercent(value: number): string {
  return `${Math.round(value * 1000) / 10}%`;
}

function formatLatency(value: number): string {
  return `${value.toLocaleString(undefined, { maximumFractionDigits: 1 })} ms`;
}

function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "n/a";
  }

  return value.toFixed(4);
}

function strategyCaseRank(caseResult: EvalRunCaseResult): string {
  if (!caseResult.hit || caseResult.first_relevant_rank === null) {
    return "No hit";
  }

  return `Rank ${caseResult.first_relevant_rank}`;
}

function strategyFallbackReasons(caseResult: EvalRunCaseResult): string {
  if (caseResult.fallback_reasons.length === 0) {
    return caseResult.error ?? "No fallback reason";
  }

  return caseResult.fallback_reasons.join(", ");
}

function strategySummaryFallbackReasons(summary: { fallback_reasons: Array<{ reason: string; count: number }> }): string {
  if (summary.fallback_reasons.length === 0) {
    return "none";
  }

  return summary.fallback_reasons.map((reason) => `${reason.reason} (${reason.count})`).join(", ");
}

function rerankRowLabel(row: EvalRerankAnalysisRow): string {
  const beforeRank = row.pre_rerank_rank ?? "-";
  const afterRank = row.post_rerank_rank ?? row.rank;
  return `${beforeRank} -> ${afterRank}`;
}

function ragEvalCaseRank(caseResult: BuiltInRagEvalCaseResult): string {
  if (!caseResult.hit || caseResult.first_relevant_rank === null) {
    return "未命中";
  }

  return `Rank ${caseResult.first_relevant_rank}`;
}

function splitInputList(value: string): string[] {
  return value
    .split(/[,\n]/)
    .map((item) => item.trim())
    .filter((item, index, items) => item.length > 0 && items.indexOf(item) === index);
}

function evalDatasetUpdatedLabel(dataset: EvalDataset): string {
  return new Date(dataset.updated_at).toLocaleString(undefined, {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function resetEvalDatasetForm(): void {
  selectedEvalDatasetId.value = "";
  evalItems.value = [];
  evalDatasetName.value = "Invoice retrieval quality";
  evalDatasetDescription.value = "Demo-safe RAG evaluation dataset";
  evalDatasetError.value = "";
  evalDatasetMessage.value = "";
  resetEvalItemForm();
}

function fillEvalDatasetForm(dataset: EvalDataset): void {
  selectedEvalDatasetId.value = dataset.dataset_id;
  evalDatasetName.value = dataset.name;
  evalDatasetDescription.value = dataset.description ?? "";
  evalDatasetError.value = "";
  evalDatasetMessage.value = "";
  resetEvalItemForm();
}

function resetEvalItemForm(): void {
  editingEvalItemId.value = "";
  evalItemQuery.value = "付款期限是什麼？";
  evalItemExpectedTerms.value = "Net 15, payment terms";
  evalItemExpectedDocumentIds.value = "";
  evalItemExpectedChunkIds.value = "";
  evalItemTags.value = "invoice";
  evalItemNotes.value = "";
  evalItemError.value = "";
  evalItemMessage.value = "";
}

function fillEvalItemForm(item: EvalItem): void {
  editingEvalItemId.value = item.item_id;
  evalItemQuery.value = item.query;
  evalItemExpectedTerms.value = item.expected_terms.join(", ");
  evalItemExpectedDocumentIds.value = item.expected_document_ids.join(", ");
  evalItemExpectedChunkIds.value = item.expected_chunk_ids.join(", ");
  evalItemTags.value = item.tags.join(", ");
  evalItemNotes.value = item.notes ?? "";
  evalItemError.value = "";
  evalItemMessage.value = "";
}

function clearEvalDatasetState(): void {
  evalDatasets.value = [];
  evalItems.value = [];
  selectedEvalDatasetId.value = "";
  editingEvalItemId.value = "";
  evalDatasetState.value = "idle";
  evalItemState.value = "idle";
  evalDatasetError.value = "";
  evalDatasetMessage.value = "";
  evalItemError.value = "";
  evalItemMessage.value = "";
}

async function refreshEvalDatasets(preferredDatasetId = selectedEvalDatasetId.value): Promise<void> {
  if (!canUseIngestion.value) {
    clearEvalDatasetState();
    return;
  }

  evalDatasetState.value = "loading";
  evalDatasetError.value = "";

  try {
    const response = await listEvalDatasets();
    evalDatasets.value = response.datasets;
    const nextDataset =
      response.datasets.find((dataset) => dataset.dataset_id === preferredDatasetId) ?? response.datasets[0] ?? null;

    if (nextDataset) {
      fillEvalDatasetForm(nextDataset);
      const itemsResponse = await listEvalItems(nextDataset.dataset_id);
      evalItems.value = itemsResponse.items;
    } else {
      resetEvalDatasetForm();
    }

    evalDatasetState.value = "success";
  } catch (error) {
    clearEvalDatasetState();
    evalDatasetError.value = error instanceof Error ? error.message : "Eval dataset 讀取失敗";
    evalDatasetState.value = "error";
  }
}

async function selectEvalDataset(dataset: EvalDataset): Promise<void> {
  fillEvalDatasetForm(dataset);
  evalItemState.value = "loading";
  evalItemError.value = "";

  try {
    const response = await listEvalItems(dataset.dataset_id);
    evalItems.value = response.items;
    evalItemState.value = "success";
  } catch (error) {
    evalItems.value = [];
    evalItemError.value = error instanceof Error ? error.message : "Eval item 讀取失敗";
    evalItemState.value = "error";
  }
}

async function submitEvalDataset(): Promise<void> {
  if (!canUseIngestion.value) {
    evalDatasetError.value = "Viewer 角色不能管理 eval dataset。";
    return;
  }

  const name = evalDatasetName.value.trim();
  if (!name) {
    evalDatasetError.value = "請先輸入 dataset 名稱。";
    return;
  }

  evalDatasetState.value = "loading";
  evalDatasetError.value = "";
  evalDatasetMessage.value = "";

  try {
    const payload = {
      name,
      description: evalDatasetDescription.value.trim() || null,
    };
    const wasEditing = Boolean(selectedEvalDatasetId.value);
    const dataset = selectedEvalDatasetId.value
      ? await updateEvalDataset(selectedEvalDatasetId.value, payload)
      : await createEvalDataset(payload);
    await refreshEvalDatasets(dataset.dataset_id);
    evalDatasetMessage.value = wasEditing ? "Eval dataset 已更新。" : "Eval dataset 已建立。";
  } catch (error) {
    evalDatasetError.value = error instanceof Error ? error.message : "Eval dataset 儲存失敗";
    evalDatasetState.value = "error";
  }
}

async function removeSelectedEvalDataset(): Promise<void> {
  if (!canUseIngestion.value || !selectedEvalDataset.value) {
    return;
  }

  evalDatasetState.value = "loading";
  evalDatasetError.value = "";
  evalDatasetMessage.value = "";

  try {
    await deleteEvalDataset(selectedEvalDataset.value.dataset_id);
    await refreshEvalDatasets("");
    evalDatasetMessage.value = "Eval dataset 已刪除。";
  } catch (error) {
    evalDatasetError.value = error instanceof Error ? error.message : "Eval dataset 刪除失敗";
    evalDatasetState.value = "error";
  }
}

async function submitEvalItem(): Promise<void> {
  if (!canUseIngestion.value) {
    evalItemError.value = "Viewer 角色不能管理 eval item。";
    return;
  }

  if (!selectedEvalDataset.value) {
    evalItemError.value = "請先選擇 eval dataset。";
    return;
  }

  const query = evalItemQuery.value.trim();
  const expectedTerms = splitInputList(evalItemExpectedTerms.value);
  if (!query || expectedTerms.length === 0) {
    evalItemError.value = "請輸入 query 與至少一個 expected term。";
    return;
  }

  evalItemState.value = "loading";
  evalItemError.value = "";
  evalItemMessage.value = "";

  const payload = {
    query,
    expected_terms: expectedTerms,
    expected_document_ids: splitInputList(evalItemExpectedDocumentIds.value),
    expected_chunk_ids: splitInputList(evalItemExpectedChunkIds.value),
    tags: splitInputList(evalItemTags.value),
    notes: evalItemNotes.value.trim() || null,
  };

  try {
    const wasEditing = Boolean(editingEvalItemId.value);
    if (editingEvalItemId.value) {
      await updateEvalItem(selectedEvalDataset.value.dataset_id, editingEvalItemId.value, payload);
    } else {
      await createEvalItem(selectedEvalDataset.value.dataset_id, payload);
    }

    resetEvalItemForm();
    await refreshEvalDatasets(selectedEvalDataset.value.dataset_id);
    evalItemMessage.value = wasEditing ? "Eval item 已更新。" : "Eval item 已新增。";
    evalItemState.value = "success";
  } catch (error) {
    evalItemError.value = error instanceof Error ? error.message : "Eval item 儲存失敗";
    evalItemState.value = "error";
  }
}

async function removeEvalItem(item: EvalItem): Promise<void> {
  if (!canUseIngestion.value || !selectedEvalDataset.value) {
    return;
  }

  evalItemState.value = "loading";
  evalItemError.value = "";
  evalItemMessage.value = "";

  try {
    await deleteEvalItem(selectedEvalDataset.value.dataset_id, item.item_id);
    resetEvalItemForm();
    await refreshEvalDatasets(selectedEvalDataset.value.dataset_id);
    evalItemMessage.value = "Eval item 已刪除。";
    evalItemState.value = "success";
  } catch (error) {
    evalItemError.value = error instanceof Error ? error.message : "Eval item 刪除失敗";
    evalItemState.value = "error";
  }
}

function parserFieldDisplay(result: ParserResult, fieldName: InvoiceFieldKey): string {
  if (fieldName === "total_amount") {
    return formatAmount(result.fields);
  }

  return formatFieldValue(result.fields[fieldName]);
}

function fieldConfidence(field: ExtractedField): string {
  return field.confidence === null ? "信心值 n/a" : `信心值 ${Math.round(field.confidence * 100)}%`;
}

function fieldEvidenceStatus(field: ExtractedField): string {
  if (field.fallback_reason === "evidence_unmatched") {
    return "evidence unmatched";
  }

  if (field.fallback_reason === "evidence_unavailable") {
    return "evidence unavailable";
  }

  if (field.source_text || field.source_page !== null || field.source_bbox) {
    return "evidence linked";
  }

  if (field.fallback_reason) {
    return "fallback";
  }

  return "evidence missing";
}

function fieldEvidenceTone(field: ExtractedField): string {
  if (field.fallback_reason === "evidence_unmatched" || field.fallback_reason === "evidence_unavailable") {
    return "evidence-warning";
  }

  if (field.source_text || field.source_page !== null || field.source_bbox) {
    return "evidence-linked";
  }

  return "evidence-neutral";
}

function fieldSourceText(field: ExtractedField): string {
  if (field.source_text) {
    return field.source_text;
  }

  if (field.fallback_reason) {
    return fallbackReasonLabel(field.fallback_reason) || field.fallback_reason;
  }

  return "來源未提供";
}

function fieldSourceLocation(field: ExtractedField): string {
  const page = field.source_page === null ? "page n/a" : `page ${field.source_page}`;
  const bbox = formatBoundingBox(field.source_bbox);
  return bbox ? `${page}; ${bbox}` : page;
}

function formatBoundingBox(bbox: BoundingBox | null): string {
  if (!bbox) {
    return "";
  }

  const values = [bbox.x_min, bbox.y_min, bbox.x_max, bbox.y_max].map((value) => Math.round(value));
  return `bbox ${values.join(", ")}`;
}

function agentStepTitle(title: string): string {
  return stepTitleLabels[title] ?? title;
}

function agentTraceValue(value: string | undefined): string {
  if (!value) {
    return "未提供";
  }

  return traceValueLabels[value] ?? value;
}

function fallbackReasonLabel(reason: string | null | undefined): string {
  if (!reason) {
    return "";
  }

  return fallbackReasonLabels[reason] ?? reason;
}

function agentMessage(message: string | null | undefined): string {
  if (!message) {
    return "沒有可用觀察結果。";
  }

  return agentMessageLabels[message] ?? message;
}

function agentSummary(summary: string | null | undefined): string {
  if (!summary) {
    return "沒有輸出摘要。";
  }

  const retrievedMatch = summary.match(/^Retrieved (\d+) chunk\(s\)\.$/);
  if (retrievedMatch) {
    return `已找回 ${retrievedMatch[1]} 個文件片段。`;
  }

  if (summary.startsWith("Parser result status is ")) {
    return `欄位解析狀態：${statusLabel(summary.replace("Parser result status is ", "").replace(".", ""))}。`;
  }

  return summary
    .replace(/invoice_number=/g, "發票號碼=")
    .replace(/vendor=/g, "供應商=")
    .replace(/total=/g, "總金額=");
}

function agentInputSummary(summary: string | null | undefined): string {
  if (!summary) {
    return "沒有輸入摘要。";
  }

  return summary
    .replace(/query=/g, "查詢=")
    .replace(/document_id=/g, "文件 ID=")
    .replace(/top_k=/g, "Top K=")
    .replace(/\bany\b/g, "不限文件");
}

function missingFieldText(fields: string[]): string {
  return fields.map((field) => agentFieldLabels[field] ?? field).join("、");
}

function agentAnswerText(text: string): string {
  return text
    .replace(/Tool trace:/g, "工具流程：")
    .replace(/Citations: none available\./g, "引用來源：目前沒有可用引用。")
    .replace(/Citations:/g, "引用來源：")
    .replace(/get_document_fields=completed/g, "讀取結構化欄位=已完成")
    .replace(/search_documents=completed/g, "搜尋文件內容=已完成")
    .replace(/summarize_invoice_fields=completed/g, "彙整發票欄位=已完成")
    .replace(/get_document_fields=failed/g, "讀取結構化欄位=失敗")
    .replace(/search_documents=failed/g, "搜尋文件內容=失敗")
    .replace(/summarize_invoice_fields=failed/g, "彙整發票欄位=失敗")
    .replace(/Invoice /g, "發票 ")
    .replace(/ is from /g, " 來自 ")
    .replace(/Issue date:/g, "開立日期：")
    .replace(/Total amount:/g, "總金額：")
    .replace(/Tax amount:/g, "稅額：")
    .replace(/Source chunks:/g, "來源片段：")
    .replace(/Missing fields:/g, "缺少欄位：")
    .replace(/unknown invoice number/g, "未知發票號碼")
    .replace(/unknown vendor/g, "未知供應商")
    .replace(/Agent run failed at/g, "Agent 執行失敗於")
    .replace(/Fallback reason:/g, "備援原因：");
}

function missingFieldLabels(result: ParserResult): string[] {
  return invoiceFieldLabels
    .filter(([fieldName]) => result.fields[fieldName].value === null)
    .map(([, label]) => label);
}

function updateDocumentParserResult(documentId: string, parserResult: ParserResult): void {
  documents.value = documents.value.map((document) =>
    document.document_id === documentId
      ? {
          ...document,
          parser_result: parserResult,
          processing: {
            ...document.processing,
            parser: parserResult.status === "parsed" ? "completed" : parserResult.status,
          },
        }
      : document,
  );
}

function syncAgentDocumentSelection(): void {
  const hasSelectedDocument = documents.value.some((document) => document.document_id === agentDocumentId.value);

  if (!hasSelectedDocument) {
    agentDocumentId.value = latestDocuments.value[0]?.document_id ?? "";
  }
}

function useSuggestedQuestion(question: string): void {
  ragQuery.value = question;
}

function selectDemoUser(role: AuthRole): void {
  const demoUser = demoUsers.find((user) => user.role === role);
  if (!demoUser) {
    return;
  }

  loginUsername.value = demoUser.username;
  loginPassword.value = demoUser.password;
}

function syncViewModeToRole(): void {
  if (roleGuardEnabled.value && authUser.value === null) {
    viewMode.value = "viewer";
    return;
  }

  if (roleGuardEnabled.value && authUser.value?.role === "viewer") {
    viewMode.value = "viewer";
    return;
  }

  if (canUseIngestion.value) {
    viewMode.value = "admin";
  }
}

async function checkAuth(): Promise<void> {
  authState.value = "checking";
  authError.value = "";

  try {
    const response = await getMe();
    authMode.value = response.auth_mode;
    authUser.value = response.authenticated ? response.user : null;
    syncViewModeToRole();
    authState.value = "success";
  } catch (error) {
    clearAuthToken();
    authMode.value = "demo";
    authUser.value = null;
    authError.value = error instanceof Error ? error.message : "Demo auth 狀態讀取失敗";
    authState.value = "error";
  }
}

async function submitLogin(): Promise<void> {
  authState.value = "loading";
  authError.value = "";

  try {
    const response = await loginDemo(loginUsername.value, loginPassword.value);
    setAuthToken(response.access_token);
    authMode.value = response.auth_mode;
    authUser.value = response.user;
    syncViewModeToRole();
    authState.value = "success";
    await refreshDocuments();
    await refreshEvalDatasets();
  } catch (error) {
    clearAuthToken();
    authUser.value = null;
    authError.value = error instanceof Error ? error.message : "Demo login failed";
    authState.value = "error";
  }
}

async function submitLogout(): Promise<void> {
  authState.value = "loading";
  authError.value = "";

  try {
    await logoutDemo();
  } catch {
    // Logout is stateless in demo mode; clearing the local token is the important part.
  }

  clearAuthToken();
  authUser.value = null;
  viewMode.value = "viewer";
  uploadResult.value = null;
  uploadFallbackAvailable.value = false;
  clearEvalDatasetState();
  authState.value = "success";
}

async function checkHealth(): Promise<void> {
  healthState.value = "loading";
  healthError.value = "";

  try {
    health.value = await getHealth();
    healthState.value = "success";
  } catch (error) {
    health.value = null;
    healthError.value = error instanceof Error ? error.message : "後端健康檢查失敗";
    healthState.value = "error";
  }
}

async function submitRagQuery(): Promise<void> {
  const query = ragQuery.value.trim();

  if (!canUseReadSurface.value) {
    ragError.value = "請先完成登入，才能查詢可存取的 project 文件。";
    return;
  }

  if (!query) {
    ragError.value = "請先輸入問題。";
    return;
  }

  chatState.value = "loading";
  ragError.value = "";

  try {
    ragResult.value = await queryRag(query, ragTopK.value);
    chatState.value = "success";
  } catch (error) {
    ragResult.value = null;
    ragError.value = error instanceof Error ? error.message : "RAG 查詢失敗";
    chatState.value = "error";
  }
}

async function refreshDocuments(): Promise<void> {
  if (!canUseReadSurface.value) {
    documents.value = [];
    documentsState.value = "idle";
    return;
  }

  documentsState.value = "loading";
  documentsError.value = "";

  try {
    const response = await listDocuments();
    documents.value = response.documents;
    syncAgentDocumentSelection();
    documentsState.value = "success";
  } catch (error) {
    documents.value = [];
    documentsError.value = error instanceof Error ? error.message : "文件狀態讀取失敗";
    documentsState.value = "error";
  }
}

async function runAggressivePostOcr(documentId: string, baseMessage: string): Promise<string> {
  const messages = [baseMessage];

  try {
    const parserResult = await parseDocumentFields(documentId);
    updateDocumentParserResult(documentId, parserResult);
    messages.push(`VLM-first 欄位解析完成（${parserResult.parser_source}）。`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "欄位解析暫時不可用";
    messages.push(`欄位解析暫時不可用，已保留後端備援：${message}`);
  }

  try {
    const vectorResult = await indexDocumentVector(documentId);
    messages.push(`Qdrant 向量索引完成（${vectorResult.indexed_chunk_count} chunks）。`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "向量索引暫時不可用";
    messages.push(`向量索引暫時不可用，查詢會使用後端備援：${message}`);
  }

  return messages.join(" ");
}

async function processIngestionFile(file: File, allowMockFallback: boolean): Promise<string> {
  let uploadedDocumentId = "";

  try {
    const response = await uploadDocument(file);
    uploadResult.value = response;
    uploadedDocumentId = response.document_id;
    await refreshDocuments();
    syncAgentDocumentSelection();

    if (isTextUploadFile(file)) {
      return await runAggressivePostOcr(
        uploadedDocumentId,
        "文件已完成直接文字匯入，並產生 text_upload local chunks。",
      );
    }

    if (isPdfUploadFile(file)) {
      if (response.chunks.some((chunk) => chunk.source_type === "pdf_text")) {
        return await runAggressivePostOcr(
          uploadedDocumentId,
          "文件已完成 text-native PDF 文字抽取，並產生 pdf_text local chunks。",
        );
      }

      const failedReason = response.processing.failed_reason ?? "";
      if (failedReason.includes("pdf_scanned_pending_ocr")) {
        return "PDF 未偵測到可抽取文字層，已標示為 pdf_scanned_pending_ocr；需要後續 PDF rendering / OCR pipeline。";
      }

      throw new Error(failedReason ? `PDF 文字抽取失敗：${failedReason}` : "PDF 文字抽取失敗。");
    }
  } catch (error) {
    uploadResult.value = null;
    throw new Error(error instanceof Error ? error.message : "文件上傳失敗");
  }

  try {
    const ocrResult = await runSelectedOcr(uploadedDocumentId);
    const selectedProvider = ocrResult.extracted_fields.provider ?? "";

    if (selectedProvider !== "paddleocr") {
      uploadFallbackAvailable.value = allowMockFallback;
      throw new Error(selectedProvider
        ? `目前後端 selected OCR provider 是 ${selectedProvider}。`
        : "目前後端 selected OCR provider 不是 paddleocr。");
    }

    return await runAggressivePostOcr(
      uploadedDocumentId,
      "文件已完成 provider-selected OCR，並產生 local chunks。",
    );
  } catch (error) {
    uploadFallbackAvailable.value = allowMockFallback;
    throw new Error(error instanceof Error ? `GPU OCR 未完成：${error.message}` : "GPU OCR 未完成");
  }
}

async function submitUpload(): Promise<void> {
  if (!canUseIngestion.value) {
    uploadError.value = "Viewer 角色不能執行 ingestion 操作。";
    return;
  }

  if (selectedFiles.value.length === 0) {
    uploadError.value = "請先選擇檔案。";
    return;
  }

  uploadState.value = "loading";
  uploadError.value = "";
  uploadMessage.value = "";
  uploadFallbackAvailable.value = false;

  const successMessages: string[] = [];
  const failureMessages: string[] = [];
  const singleFileMode = selectedFiles.value.length === 1;

  for (const [fileIndex, file] of selectedFiles.value.entries()) {
    uploadMessage.value =
      selectedFiles.value.length > 1 ? `處理中 ${fileIndex + 1}/${selectedFiles.value.length}：${file.name}` : "";

    try {
      const message = await processIngestionFile(file, singleFileMode);
      successMessages.push(`${file.name}：${message}`);
      await refreshDocuments();
    } catch (error) {
      const message = error instanceof Error ? error.message : "處理失敗";
      failureMessages.push(`${file.name}：${message}`);
      await refreshDocuments();
    }
  }

  if (successMessages.length > 0) {
    uploadMessage.value =
      selectedFiles.value.length > 1
        ? `已完成 ${successMessages.length}/${selectedFiles.value.length} 個檔案。${successMessages.join(" ")}`
        : successMessages[0];
  } else {
    uploadMessage.value = "";
  }

  if (failureMessages.length > 0) {
    uploadError.value =
      selectedFiles.value.length > 1
        ? `部分檔案處理失敗：${failureMessages.join(" ")}`
        : failureMessages[0];
    uploadState.value = "error";
    return;
  }

  uploadState.value = "success";
}

async function submitMockFallback(): Promise<void> {
  if (!canUseIngestion.value) {
    uploadError.value = "Viewer 角色不能執行 OCR fallback。";
    return;
  }

  if (!uploadResult.value) {
    uploadError.value = "請先完成文件上傳。";
    return;
  }

  uploadState.value = "loading";
  uploadError.value = "";
  uploadMessage.value = "";

  try {
    await runMockOcr(uploadResult.value.document_id);
    uploadFallbackAvailable.value = false;
    uploadMessage.value = await runAggressivePostOcr(
      uploadResult.value.document_id,
      "已改用 mock OCR 完成後台 ingestion 備援處理。",
    );
    uploadState.value = "success";
    await refreshDocuments();
  } catch (error) {
    uploadError.value = error instanceof Error ? `Mock OCR 備援失敗：${error.message}` : "Mock OCR 備援失敗";
    uploadState.value = "error";
  }
}

async function submitFieldParse(document: DocumentMetadata): Promise<void> {
  if (!canUseIngestion.value) {
    parseErrors.value = {
      ...parseErrors.value,
      [document.document_id]: "Viewer 角色不能執行欄位解析。",
    };
    return;
  }

  parseStates.value = {
    ...parseStates.value,
    [document.document_id]: "loading",
  };
  parseErrors.value = {
    ...parseErrors.value,
    [document.document_id]: "",
  };

  try {
    const parserResult = await parseDocumentFields(document.document_id);
    updateDocumentParserResult(document.document_id, parserResult);
    parseStates.value = {
      ...parseStates.value,
      [document.document_id]: "success",
    };
    await refreshDocuments();
  } catch (error) {
    parseErrors.value = {
      ...parseErrors.value,
      [document.document_id]: error instanceof Error ? error.message : "欄位解析失敗",
    };
    parseStates.value = {
      ...parseStates.value,
      [document.document_id]: "error",
    };
    await refreshDocuments();
  }
}

async function submitAgentRun(): Promise<void> {
  if (!canUseIngestion.value) {
    agentError.value = "Viewer 角色不能執行 Agent write 操作。";
    return;
  }

  const task = agentTask.value.trim();
  const documentId = agentDocumentId.value.trim();
  const query = agentQuery.value.trim();

  if (!task) {
    agentError.value = "請先輸入 Agent 任務。";
    return;
  }

  if (!documentId) {
    agentError.value = "請先選擇已匯入的文件。";
    return;
  }

  agentState.value = "loading";
  agentError.value = "";

  try {
    agentRun.value = await runAgent({
      task,
      document_id: documentId,
      query: query || undefined,
      top_k: agentTopK.value,
    });
    agentState.value = agentRun.value.status === "failed" ? "error" : "success";
  } catch (error) {
    agentRun.value = null;
    agentError.value = error instanceof Error ? error.message : "Agent 執行失敗。";
    agentState.value = "error";
  }
}

async function submitBuiltInRagEval(): Promise<void> {
  if (!canUseIngestion.value) {
    ragEvalError.value = "Viewer 角色不能執行測試RAG。";
    return;
  }

  ragEvalState.value = "loading";
  ragEvalError.value = "";

  try {
    ragEvalResult.value = await runBuiltInRagEval();
    ragEvalState.value = "success";
  } catch (error) {
    ragEvalResult.value = null;
    ragEvalError.value = error instanceof Error ? error.message : "測試RAG 執行失敗";
    ragEvalState.value = "error";
  }
}

async function submitStrategyComparisonEval(): Promise<void> {
  if (!canUseIngestion.value) {
    strategyEvalError.value = "Viewer cannot run strategy comparison.";
    return;
  }

  if (!selectedEvalDataset.value) {
    strategyEvalError.value = "Select an eval dataset before running strategy comparison.";
    return;
  }

  strategyEvalState.value = "loading";
  strategyEvalError.value = "";

  try {
    const result = await runEvalStrategyComparison({
      dataset_id: selectedEvalDataset.value.dataset_id,
      strategies: strategyEvalStrategies.value,
      top_k: strategyEvalTopK.value,
    });
    strategyEvalResult.value = result;
    strategyEvalItems.value = await getEvalRunItems(result.run_id);
    strategyEvalState.value = "success";
  } catch (error) {
    strategyEvalResult.value = null;
    strategyEvalItems.value = null;
    strategyEvalError.value = error instanceof Error ? error.message : "Strategy comparison failed.";
    strategyEvalState.value = "error";
  }
}

onMounted(async () => {
  void checkHealth();
  await checkAuth();
  if (canUseReadSurface.value) {
    void refreshDocuments();
  }
  if (canUseIngestion.value) {
    void refreshEvalDatasets();
  }
});
</script>

<template>
  <main class="page product-page">
    <header class="hero product-hero">
      <div class="hero-shell">
        <div class="hero-main">
          <div class="hero-kicker">
            <span class="eyebrow">{{ currentVersionLabel }}</span>
            <span class="status-pill" :class="`status-${healthState}`">{{ healthLabel }}</span>
          </div>
          <h1>文件客服助理</h1>
          <p class="hero-copy">{{ heroCopy }}</p>
        </div>

        <div class="hero-side">
          <span>服務狀態</span>
          <strong>{{ healthLabel }}</strong>
          <small>{{ health?.version ? `Backend ${health.version}` : API_BASE_URL }}</small>
          <span>{{ authSurfaceLabel }}</span>
          <strong>{{ currentRoleLabel }}</strong>
          <button
            v-if="roleGuardEnabled && authUser"
            type="button"
            class="button secondary-button compact-button"
            :disabled="authState === 'loading'"
            @click="submitLogout"
          >
            登出
          </button>
          <div class="mode-switch" aria-label="產品入口">
            <button
              type="button"
              class="mode-button"
              :class="{ 'mode-button-active': viewMode === 'viewer' }"
              @click="openViewerSurface"
            >
              前台查詢
            </button>
            <button
              type="button"
              class="mode-button"
              :class="{ 'mode-button-active': viewMode === 'admin' }"
              :disabled="!canUseIngestion"
              @click="openAdminSurface"
            >
              後台知識庫管理
            </button>
          </div>
        </div>
      </div>
    </header>

    <section v-if="authState === 'checking'" class="minimal-grid viewer-grid" aria-label="demo auth loading">
      <article class="panel auth-surface">
        <div class="panel-heading">
          <div>
            <h2>Demo Auth</h2>
            <p>讀取登入狀態中...</p>
          </div>
        </div>
      </article>
    </section>

    <section v-else-if="demoAuthRequired" class="minimal-grid viewer-grid" aria-label="demo login">
      <article class="panel auth-surface">
        <div class="panel-heading">
          <div>
            <h2>Demo Login</h2>
            <p>選擇一個 demo role 進入對應 surface。</p>
          </div>
          <span class="status-pill status-ready">demo auth</span>
        </div>

        <div class="role-picker" aria-label="demo roles">
          <button
            v-for="demoUser in demoUsers"
            :key="demoUser.role"
            type="button"
            class="mode-button"
            :class="{ 'mode-button-active': loginUsername === demoUser.username }"
            @click="selectDemoUser(demoUser.role)"
          >
            {{ demoUser.label }}
          </button>
        </div>

        <form class="auth-form" @submit.prevent="submitLogin">
          <label>
            <span>Username</span>
            <input v-model="loginUsername" type="text" autocomplete="username" />
          </label>
          <label>
            <span>Password</span>
            <input v-model="loginPassword" type="password" autocomplete="current-password" />
          </label>
          <button type="submit" class="button" :disabled="authState === 'loading'">
            {{ authState === "loading" ? "登入中..." : "登入" }}
          </button>
        </form>

        <p v-if="authError" class="error">{{ authError }}</p>
      </article>
    </section>

    <section v-else-if="formalAuthRequired" class="minimal-grid viewer-grid" aria-label="formal auth required">
      <article class="panel auth-surface">
        <div class="panel-heading">
          <div>
            <h2>Formal Auth</h2>
            <p>正式 Auth / RBAC 已啟用；請使用 signed bearer token 後重新載入。</p>
          </div>
          <span class="status-pill status-failed">locked</span>
        </div>

        <p class="muted compact-note">
          Production login runtime 仍未實作；未登入時不顯示 ingestion、測試RAG 或 Agent write 入口。
        </p>
      </article>
    </section>

    <template v-else>
    <section v-if="viewMode === 'viewer'" class="minimal-grid viewer-grid" aria-label="前台文件客服查詢入口">
      <article class="panel chat-surface">
        <div class="panel-heading">
          <div>
            <h2>前台查詢</h2>
            <p>Viewer 只詢問後端已建立的文件知識庫，並查看回答與引用來源。</p>
          </div>
        </div>

        <div class="suggestion-row" aria-label="建議問題">
          <button
            v-for="question in suggestedQuestions"
            :key="question"
            type="button"
            class="suggestion-button"
            @click="useSuggestedQuestion(question)"
          >
            {{ question }}
          </button>
        </div>

        <form class="chat-form minimal-chat-form" @submit.prevent="submitRagQuery">
          <label>
            <span>問題</span>
            <textarea v-model="ragQuery" rows="4" placeholder="例如：付款期限是什麼？" />
          </label>

          <label>
            <span>Top K</span>
            <input v-model.number="ragTopK" type="number" min="1" max="10" />
          </label>

          <button type="submit" class="button" :disabled="chatState === 'loading' || !canUseReadSurface">
            {{ chatState === "loading" ? "查詢中..." : "送出問題" }}
          </button>
        </form>

        <p v-if="ragError" class="error">{{ ragError }}</p>

        <section v-if="ragResult" class="answer-card" aria-label="RAG 回答">
          <div class="answer-heading">
            <h3>回答</h3>
            <div class="answer-badges">
              <span class="status-pill" :class="sourceTone(ragAnswerSource)">{{ ragAnswerSource }}</span>
              <span class="status-pill" :class="sourceTone(ragRetrievalSource)">{{ ragRetrievalSource }}</span>
            </div>
          </div>
          <pre class="answer-text">{{ ragResult.answer }}</pre>

          <div class="source-block">
            <h3>引用來源</h3>
            <ul v-if="citedSources.length" class="source-list">
              <li v-for="source in citedSources" :key="source.filename">
                <span>{{ source.filename }}</span>
                <small>{{ source.chunkIds.length }} 個引用片段</small>
              </li>
            </ul>
            <p v-else class="muted">沒有引用來源；請確認後端知識庫資料是否已建立。</p>
          </div>
        </section>

        <p v-else class="muted">請輸入問題。若尚未有資料，請先由後台知識庫管理流程建立資料。</p>
      </article>
    </section>

    <section v-else class="minimal-grid admin-grid" aria-label="後台知識庫管理入口">
      <article class="panel ingestion-surface">
        <div class="panel-heading">
          <div>
            <h2>後台知識庫管理</h2>
            <p>Admin / Analyst 在這裡建立前台可查詢的 demo knowledge base。</p>
          </div>
        </div>

        <label class="file-picker">
          <span>選擇文件</span>
          <input type="file" multiple :disabled="!canUseIngestion" @change="handleFileChange" />
        </label>

        <p v-if="selectedFiles.length" class="selected-file">
          {{ selectedFileSummary }}
        </p>
        <p v-else class="muted">尚未選擇文件。</p>

        <button
          type="button"
          class="button upload-button"
          :disabled="!canUseIngestion || selectedFiles.length === 0 || uploadState === 'loading'"
          @click="submitUpload"
        >
          {{ uploadButtonLabel }}
        </button>

        <p v-if="uploadMessage" class="success-message">{{ uploadMessage }}</p>
        <p v-if="uploadError" class="error">{{ uploadError }}</p>
        <button
          v-if="uploadFallbackAvailable"
          type="button"
          class="button secondary-button upload-button"
          :disabled="!canUseIngestion || uploadState === 'loading'"
          @click="submitMockFallback"
        >
          使用 mock OCR fallback
        </button>
      </article>

      <article class="panel ingestion-status">
        <details class="collapsible-status">
          <summary>
            <div>
              <h2>資料匯入狀態</h2>
              <p>{{ latestDocuments.length }} 筆文件紀錄，點開後才顯示處理細節。</p>
            </div>
          </summary>

          <div class="collapsible-body">
            <div class="status-toolbar">
              <button type="button" class="button secondary-button compact-button" @click="refreshDocuments">
                重新整理
              </button>
            </div>

            <p v-if="documentsError" class="error">{{ documentsError }}</p>
            <p v-if="documentsState === 'loading'" class="muted">讀取文件狀態中...</p>
            <p v-else-if="latestDocuments.length === 0" class="muted">目前沒有後台文件紀錄。</p>

            <ul v-else class="document-status-list">
              <li v-for="document in latestDocuments" :key="document.document_id">
                <div>
                  <strong>{{ document.filename }}</strong>
                  <small>{{ document.document_id }}</small>
                </div>
                <div class="document-status-row">
                  <span class="status-pill" :class="documentStatusTone(document.status)">
                    文件 {{ statusLabel(document.status) }}
                  </span>
                  <span class="status-pill status-ready">
                    {{ documentSourceLabel(document) }}
                  </span>
                  <span class="status-pill" :class="documentStatusTone(document.processing.ocr)">
                    OCR {{ statusLabel(document.processing.ocr) }}
                  </span>
                  <span class="status-pill" :class="documentStatusTone(parserStatus(document))">
                    欄位解析 {{ statusLabel(parserStatus(document)) }}
                  </span>
                  <span class="status-pill" :class="document.processing.ready ? 'status-success' : 'status-ready'">
                    {{ chunkReadiness(document) }}
                  </span>
                </div>
                <div class="parser-actions">
                  <button
                    type="button"
                    class="button secondary-button compact-button"
                    :disabled="!canUseIngestion || !canParseDocument(document) || parseStates[document.document_id] === 'loading'"
                    @click="submitFieldParse(document)"
                  >
                    {{
                      parseStates[document.document_id] === "loading"
                        ? "解析中..."
                        : document.parser_result?.status === "parsed"
                          ? "重新解析欄位"
                          : "解析欄位"
                    }}
                  </button>
                  <small v-if="!canParseDocument(document)">OCR 完成、直接文字匯入或 text-native PDF 後才能解析欄位。</small>
                </div>
                <p v-if="parseErrors[document.document_id]" class="error">
                  {{ parseErrors[document.document_id] }}
                </p>
                <section
                  v-if="document.parser_result?.status === 'parsed'"
                  class="fields-summary"
                  aria-label="欄位解析摘要"
                >
                  <div class="fields-summary-header">
                    <div>
                      <span>欄位解析器</span>
                      <strong>{{ document.parser_result.parser_source }}</strong>
                    </div>
                    <small v-if="document.parser_result.fallback_reason">
                      {{ fallbackReasonLabel(document.parser_result.fallback_reason) }}
                    </small>
                  </div>
                  <div class="fields-grid">
                    <div v-for="field in invoiceFieldLabels" :key="field[0]" class="field-cell">
                      <span>{{ field[1] }}</span>
                      <strong>{{ parserFieldDisplay(document.parser_result, field[0]) }}</strong>
                      <div class="field-evidence-row">
                        <span class="field-confidence">{{ fieldConfidence(document.parser_result.fields[field[0]]) }}</span>
                        <span class="field-evidence-pill" :class="fieldEvidenceTone(document.parser_result.fields[field[0]])">
                          {{ fieldEvidenceStatus(document.parser_result.fields[field[0]]) }}
                        </span>
                      </div>
                      <dl class="field-evidence-list">
                        <div>
                          <dt>來源</dt>
                          <dd>{{ fieldSourceText(document.parser_result.fields[field[0]]) }}</dd>
                        </div>
                        <div>
                          <dt>位置</dt>
                          <dd>{{ fieldSourceLocation(document.parser_result.fields[field[0]]) }}</dd>
                        </div>
                        <div v-if="document.parser_result.fields[field[0]].fallback_reason">
                          <dt>原因</dt>
                          <dd>{{ fallbackReasonLabel(document.parser_result.fields[field[0]].fallback_reason) }}</dd>
                        </div>
                      </dl>
                    </div>
                  </div>
                  <p v-if="missingFieldLabels(document.parser_result).length" class="muted compact-note">
                    缺少欄位：{{ missingFieldLabels(document.parser_result).join("、") }}
                  </p>
                  <p v-if="document.parser_result.fields.line_items.length" class="muted compact-note">
                    品項明細：{{ document.parser_result.fields.line_items.length }}
                  </p>
                </section>
                <section
                  v-else-if="document.parser_result?.status === 'failed'"
                  class="fields-summary fields-summary-failed"
                  aria-label="欄位解析失敗"
                >
                  <strong>{{ fallbackReasonLabel(document.parser_result.fallback_reason) || "欄位解析失敗" }}</strong>
                  <span>{{ document.parser_result.error_message ?? "欄位解析未完成。" }}</span>
                </section>
                <p v-else class="muted compact-note">尚未執行欄位解析。</p>
                <p v-if="document.processing.failed_reason" class="error">{{ document.processing.failed_reason }}</p>
              </li>
            </ul>
          </div>
        </details>
      </article>

      <article class="panel eval-dataset-surface" aria-label="Eval dataset 管理">
        <div class="panel-heading">
          <div>
            <h2>Eval Dataset</h2>
            <p>Admin / Analyst 管理 RAG evaluation dataset 與 eval items。</p>
          </div>
          <span class="status-pill" :class="`status-${evalDatasetState}`">{{ evalDatasetStatusLabel }}</span>
        </div>

        <form class="eval-dataset-form" @submit.prevent="submitEvalDataset">
          <label>
            <span>Dataset name</span>
            <input v-model="evalDatasetName" type="text" :disabled="!canUseIngestion || evalDatasetState === 'loading'" />
          </label>
          <label>
            <span>Description</span>
            <input
              v-model="evalDatasetDescription"
              type="text"
              :disabled="!canUseIngestion || evalDatasetState === 'loading'"
            />
          </label>
          <div class="eval-form-actions">
            <button type="submit" class="button" :disabled="!canUseIngestion || evalDatasetState === 'loading'">
              {{ selectedEvalDataset ? "更新 dataset" : "建立 dataset" }}
            </button>
            <button type="button" class="button secondary-button" :disabled="evalDatasetState === 'loading'" @click="resetEvalDatasetForm">
              新增
            </button>
            <button
              type="button"
              class="button danger-button"
              :disabled="!canUseIngestion || !selectedEvalDataset || evalDatasetState === 'loading'"
              @click="removeSelectedEvalDataset"
            >
              刪除
            </button>
          </div>
        </form>

        <p v-if="evalDatasetMessage" class="success-message">{{ evalDatasetMessage }}</p>
        <p v-if="evalDatasetError" class="error">{{ evalDatasetError }}</p>

        <div class="eval-management-grid">
          <section class="eval-dataset-list-panel" aria-label="Eval dataset list">
            <div class="status-toolbar">
              <button type="button" class="button secondary-button compact-button" :disabled="evalDatasetState === 'loading'" @click="refreshEvalDatasets()">
                重新整理
              </button>
            </div>

            <p v-if="evalDatasetState === 'loading'" class="muted compact-note">讀取 eval datasets 中...</p>
            <p v-else-if="evalDatasets.length === 0" class="muted compact-note">尚未建立 eval dataset。</p>

            <ul v-else class="eval-dataset-list">
              <li
                v-for="dataset in evalDatasets"
                :key="dataset.dataset_id"
                :class="{ selected: selectedEvalDatasetId === dataset.dataset_id }"
              >
                <button type="button" class="link-button" @click="selectEvalDataset(dataset)">
                  {{ dataset.name }}
                </button>
                <small>{{ dataset.dataset_id }}</small>
                <div class="eval-dataset-badges">
                  <span class="status-pill status-success">{{ dataset.item_count }} items</span>
                  <span class="status-pill status-ready">{{ dataset.schema_version }}</span>
                  <span class="status-pill status-idle">{{ evalDatasetUpdatedLabel(dataset) }}</span>
                </div>
              </li>
            </ul>
          </section>

          <section class="eval-item-panel" aria-label="Eval item management">
            <form class="eval-item-form" @submit.prevent="submitEvalItem">
              <label class="eval-item-query">
                <span>Query</span>
                <textarea
                  v-model="evalItemQuery"
                  rows="3"
                  :disabled="!canUseIngestion || !selectedEvalDataset || evalItemState === 'loading'"
                />
              </label>
              <label>
                <span>Expected terms</span>
                <textarea
                  v-model="evalItemExpectedTerms"
                  rows="2"
                  :disabled="!canUseIngestion || !selectedEvalDataset || evalItemState === 'loading'"
                />
              </label>
              <label>
                <span>Document IDs</span>
                <input
                  v-model="evalItemExpectedDocumentIds"
                  type="text"
                  :disabled="!canUseIngestion || !selectedEvalDataset || evalItemState === 'loading'"
                />
              </label>
              <label>
                <span>Chunk IDs</span>
                <input
                  v-model="evalItemExpectedChunkIds"
                  type="text"
                  :disabled="!canUseIngestion || !selectedEvalDataset || evalItemState === 'loading'"
                />
              </label>
              <label>
                <span>Tags</span>
                <input
                  v-model="evalItemTags"
                  type="text"
                  :disabled="!canUseIngestion || !selectedEvalDataset || evalItemState === 'loading'"
                />
              </label>
              <label>
                <span>Notes</span>
                <input
                  v-model="evalItemNotes"
                  type="text"
                  :disabled="!canUseIngestion || !selectedEvalDataset || evalItemState === 'loading'"
                />
              </label>
              <div class="eval-form-actions">
                <button
                  type="submit"
                  class="button"
                  :disabled="!canUseIngestion || !selectedEvalDataset || evalItemState === 'loading'"
                >
                  {{ evalItemFormModeLabel }}
                </button>
                <button type="button" class="button secondary-button" :disabled="evalItemState === 'loading'" @click="resetEvalItemForm">
                  清空
                </button>
              </div>
            </form>

            <p v-if="evalItemMessage" class="success-message">{{ evalItemMessage }}</p>
            <p v-if="evalItemError" class="error">{{ evalItemError }}</p>
            <p v-if="!selectedEvalDataset" class="muted compact-note">請先選擇或建立 dataset。</p>
            <p v-else-if="evalItemState === 'loading'" class="muted compact-note">同步 eval items 中...</p>
            <p v-else-if="evalItems.length === 0" class="muted compact-note">目前沒有 eval item。</p>

            <ul v-else class="eval-item-list">
              <li v-for="item in evalItems" :key="item.item_id">
                <div>
                  <strong>{{ item.query }}</strong>
                  <small>{{ item.item_id }}</small>
                </div>
                <div class="eval-dataset-badges">
                  <span v-for="term in item.expected_terms" :key="`${item.item_id}-${term}`" class="status-pill status-ready">
                    {{ term }}
                  </span>
                  <span v-for="tag in item.tags" :key="`${item.item_id}-${tag}`" class="status-pill status-idle">
                    {{ tag }}
                  </span>
                </div>
                <p v-if="item.notes" class="muted compact-note">{{ item.notes }}</p>
                <div class="eval-form-actions">
                  <button type="button" class="button secondary-button compact-button" @click="fillEvalItemForm(item)">
                    編輯
                  </button>
                  <button type="button" class="button danger-button compact-button" @click="removeEvalItem(item)">
                    刪除
                  </button>
                </div>
              </li>
            </ul>
          </section>
        </div>
      </article>

      <article class="panel strategy-comparison-panel" aria-label="strategy comparison eval dashboard">
          <div class="strategy-run-heading">
            <div>
              <h3>Strategy comparison</h3>
              <p>Compare keyword, hybrid_rerank and optional vector-backed strategy on the selected eval dataset.</p>
            </div>
            <span class="status-pill" :class="`status-${strategyEvalState}`">{{ strategyEvalStatusLabel }}</span>
          </div>

          <div class="eval-toolbar">
            <label class="strategy-topk-label">
              <span>Top K</span>
              <input
                v-model.number="strategyEvalTopK"
                type="number"
                min="1"
                max="10"
                :disabled="!canUseIngestion || strategyEvalState === 'loading'"
              />
            </label>
            <button
              type="button"
              class="button"
              :disabled="!canUseIngestion || !selectedEvalDataset || strategyEvalState === 'loading'"
              @click="submitStrategyComparisonEval"
            >
              {{ strategyEvalState === "loading" ? "Running comparison..." : "Run strategy comparison" }}
            </button>
            <span class="status-pill status-ready">{{ strategyEvalStrategies.join(" / ") }}</span>
          </div>

          <p v-if="strategyEvalError" class="error">{{ strategyEvalError }}</p>
          <p v-if="!strategyEvalResult" class="muted compact-note">
            Run strategy comparison to inspect Hit Rate@K, MRR@K, Recall@K, failure cases, fallback cases and rerank score changes.
          </p>

          <section v-if="strategyEvalResult" class="strategy-eval-result" aria-label="strategy comparison result">
            <div class="eval-dataset-row">
              <span class="status-pill status-ready">{{ strategyEvalResult.dataset_name }}</span>
              <span class="status-pill status-success">Top {{ strategyEvalResult.top_k }}</span>
              <span class="status-pill status-idle">{{ strategyEvalResult.run_id }}</span>
            </div>

            <div class="table-wrap strategy-table-wrap">
              <table class="strategy-metrics-table">
                <thead>
                  <tr>
                    <th>Strategy</th>
                    <th>Hit Rate@K</th>
                    <th>MRR@K</th>
                    <th>Recall@K</th>
                    <th>Latency</th>
                    <th>Failure / Fallback</th>
                    <th>Trace metadata</th>
                    <th>Fallback reasons</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="summary in strategyEvalResult.strategy_summaries" :key="summary.strategy">
                    <td><strong>{{ summary.strategy }}</strong></td>
                    <td>{{ formatPercent(summary.hit_rate_at_k) }}</td>
                    <td>{{ summary.mrr_at_k.toFixed(2) }}</td>
                    <td>{{ formatPercent(summary.recall_at_k) }}</td>
                    <td>{{ formatLatency(summary.average_latency_ms) }}</td>
                    <td>{{ summary.failure_count }} / {{ summary.fallback_count }}</td>
                    <td>{{ summary.trace_metadata_count }}</td>
                    <td>{{ strategySummaryFallbackReasons(summary) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="strategy-detail-grid">
              <details class="collapsible-status eval-case-details" :open="Boolean(strategyEvalItems?.fallback_cases.length)">
                <summary>
                  <div>
                    <h3>Fallback cases</h3>
                    <p>{{ strategyEvalItems?.fallback_cases.length ?? 0 }} fallback cases from this strategy comparison.</p>
                  </div>
                </summary>
                <ul v-if="strategyEvalItems?.fallback_cases.length" class="eval-case-list">
                  <li v-for="caseResult in strategyEvalItems.fallback_cases" :key="`${caseResult.strategy}-${caseResult.case_id}`">
                    <div>
                      <strong>{{ caseResult.strategy }} / {{ caseResult.case_id }}</strong>
                      <small>{{ strategyCaseRank(caseResult) }} / Top {{ caseResult.top_k }}</small>
                    </div>
                    <p>{{ caseResult.query }}</p>
                    <small>{{ strategyFallbackReasons(caseResult) }}</small>
                  </li>
                </ul>
                <p v-else class="muted compact-note">No fallback cases.</p>
              </details>

              <details class="collapsible-status eval-case-details" :open="Boolean(strategyEvalItems?.failed_cases.length)">
                <summary>
                  <div>
                    <h3>Failure cases</h3>
                    <p>{{ strategyEvalItems?.failed_cases.length ?? 0 }} failure cases from this strategy comparison.</p>
                  </div>
                </summary>
                <ul v-if="strategyEvalItems?.failed_cases.length" class="eval-case-list">
                  <li v-for="caseResult in strategyEvalItems.failed_cases" :key="`${caseResult.strategy}-${caseResult.case_id}`">
                    <div>
                      <strong>{{ caseResult.strategy }} / {{ caseResult.case_id }}</strong>
                      <small>{{ strategyCaseRank(caseResult) }} / Top {{ caseResult.top_k }}</small>
                    </div>
                    <p>{{ caseResult.query }}</p>
                    <small>{{ caseResult.error ?? caseResult.matched_expected_terms.join(", ") }}</small>
                  </li>
                </ul>
                <p v-else class="muted compact-note">No failure cases.</p>
              </details>
            </div>

            <section class="rerank-analysis-panel" aria-label="rerank analysis">
              <div class="strategy-run-heading">
                <div>
                  <h3>Rerank analysis</h3>
                  <p>Before / after ranking and rerank score for vector_rerank or hybrid_rerank candidates.</p>
                </div>
                <span class="status-pill status-ready">{{ strategyEvalItems?.rerank_analysis.length ?? 0 }} rows</span>
              </div>

              <div v-if="strategyEvalItems?.rerank_analysis.length" class="table-wrap strategy-table-wrap">
                <table class="strategy-metrics-table rerank-table">
                  <thead>
                    <tr>
                      <th>Case</th>
                      <th>Strategy</th>
                      <th>Rank change</th>
                      <th>Pre score</th>
                      <th>Rerank score</th>
                      <th>Status</th>
                      <th>Chunk</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in strategyEvalItems.rerank_analysis" :key="`${row.case_id}-${row.strategy}-${row.chunk_id}-${row.rank}`">
                      <td>{{ row.case_id }}</td>
                      <td><strong>{{ row.strategy }}</strong></td>
                      <td>{{ rerankRowLabel(row) }}</td>
                      <td>{{ formatScore(row.pre_rerank_score) }}</td>
                      <td>{{ formatScore(row.rerank_score) }}</td>
                      <td>{{ row.rerank_status ?? row.fallback_state ?? "n/a" }}</td>
                      <td>
                        <strong>{{ row.filename || row.document_id }}</strong>
                        <small>{{ row.chunk_id }}</small>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p v-else class="muted compact-note">No rerank analysis rows yet.</p>
            </section>
          </section>
      </article>

      <article class="panel eval-surface" aria-label="測試RAG">
        <div class="panel-heading">
          <div>
            <h2>測試RAG</h2>
            <p>內建中文發票基準測試，固定使用 hybrid_rerank。</p>
          </div>
          <span class="status-pill status-ready">hybrid_rerank</span>
        </div>

        <div class="eval-toolbar">
          <button
            type="button"
            class="button"
            :disabled="!canUseIngestion || ragEvalState === 'loading'"
            @click="submitBuiltInRagEval"
          >
            {{ ragEvalState === "loading" ? "測試中..." : "執行測試" }}
          </button>
          <span class="status-pill" :class="`status-${ragEvalState}`">{{ ragEvalStatusLabel }}</span>
        </div>

        <p v-if="ragEvalError" class="error">{{ ragEvalError }}</p>
        <p v-if="!ragEvalResult" class="muted compact-note">
          使用 10 張 demo-safe 中文發票 fixture，顯示 retrieval benchmark 第一版核心指標。
        </p>

        <section v-if="ragEvalResult" class="eval-result" aria-label="測試RAG 結果">
          <div class="eval-metric-grid">
            <div class="eval-metric-cell">
              <span>Hit Rate@K</span>
              <strong>{{ formatPercent(ragEvalResult.summary.hit_rate_at_k) }}</strong>
            </div>
            <div class="eval-metric-cell">
              <span>MRR@K</span>
              <strong>{{ ragEvalResult.summary.mrr_at_k.toFixed(2) }}</strong>
            </div>
            <div class="eval-metric-cell">
              <span>平均延遲</span>
              <strong>{{ formatLatency(ragEvalResult.summary.average_latency_ms) }}</strong>
            </div>
            <div class="eval-metric-cell">
              <span>Failure / Fallback</span>
              <strong>{{ ragEvalResult.summary.failure_count }} / {{ ragEvalResult.summary.fallback_count }}</strong>
            </div>
          </div>

          <div class="eval-dataset-row">
            <span class="status-pill status-ready">{{ ragEvalResult.dataset_name }}</span>
            <span class="status-pill status-success">{{ ragEvalResult.case_count }} cases</span>
            <span
              v-if="ragEvalResult.environment.vector_preflight_status"
              class="status-pill"
              :class="ragEvalResult.environment.vector_preflight_status === 'completed' ? 'status-success' : 'status-failed'"
            >
              vector {{ ragEvalResult.environment.vector_preflight_status }}
            </span>
            <span
              v-if="ragEvalResult.environment.rerank_provider"
              class="status-pill"
              :class="ragEvalResult.summary.fallback_count ? 'status-ready' : 'status-success'"
            >
              rerank {{ ragEvalResult.environment.rerank_provider }}
            </span>
          </div>

          <details v-if="ragEvalResult.fallback_cases.length" class="collapsible-status eval-case-details">
            <summary>
              <div>
                <h3>Fallback cases</h3>
                <p>{{ ragEvalResult.fallback_cases.length }} 筆 case 使用 fallback。</p>
              </div>
            </summary>
            <ul class="eval-case-list">
              <li v-for="caseResult in ragEvalResult.fallback_cases" :key="caseResult.case_id">
                <div>
                  <strong>{{ caseResult.case_id }}</strong>
                  <small>{{ ragEvalCaseRank(caseResult) }} / Top {{ caseResult.top_k }}</small>
                </div>
                <p>{{ caseResult.query }}</p>
                <small>{{ caseResult.fallback_reasons.join("；") }}</small>
              </li>
            </ul>
          </details>

          <details v-if="ragEvalResult.failed_cases.length" class="collapsible-status eval-case-details">
            <summary>
              <div>
                <h3>Failed cases</h3>
                <p>{{ ragEvalResult.failed_cases.length }} 筆 case 未命中或發生錯誤。</p>
              </div>
            </summary>
            <ul class="eval-case-list">
              <li v-for="caseResult in ragEvalResult.failed_cases" :key="caseResult.case_id">
                <div>
                  <strong>{{ caseResult.case_id }}</strong>
                  <small>{{ ragEvalCaseRank(caseResult) }} / Top {{ caseResult.top_k }}</small>
                </div>
                <p>{{ caseResult.query }}</p>
                <small>{{ caseResult.error ?? caseResult.matched_expected_terms.join("、") }}</small>
              </li>
            </ul>
          </details>
        </section>
      </article>

      <article class="panel agent-surface" aria-label="Agent 執行紀錄">
        <details class="collapsible-status agent-collapsible">
          <summary>
            <div>
              <h2>Agent 執行紀錄</h2>
              <p>Admin / Analyst 可在這裡查看受控工具流程、權限 trace、觀察結果與引用來源。</p>
            </div>
            <span class="status-pill" :class="documentStatusTone(agentRun?.status ?? 'pending')">
              {{ statusLabel(agentRun?.status ?? "pending") }}
            </span>
          </summary>

          <div class="collapsible-body">
            <form class="agent-form" @submit.prevent="submitAgentRun">
              <label class="agent-task-field">
                <span>任務</span>
                <textarea v-model="agentTask" rows="3" />
              </label>

              <label>
                <span>文件</span>
                <select v-model="agentDocumentId">
                  <option value="" disabled>選擇文件</option>
                  <option v-for="document in agentDocumentOptions" :key="document.document_id" :value="document.document_id">
                    {{ document.filename }}
                  </option>
                </select>
              </label>

              <label>
                <span>查詢關鍵字</span>
                <input v-model="agentQuery" type="text" placeholder="payment terms" />
              </label>

              <label>
                <span>Top K</span>
                <input v-model.number="agentTopK" type="number" min="1" max="10" />
              </label>

              <button type="submit" class="button" :disabled="!canUseIngestion || agentState === 'loading'">
                {{ agentState === "loading" ? "執行中..." : "執行 Agent" }}
              </button>
            </form>

            <p v-if="agentError" class="error">{{ agentError }}</p>
            <p v-if="!agentRun" class="muted compact-note">
              Agent 只會使用 Phase 38 已受權限檢查的唯讀工具，不會執行任意外部操作。
            </p>

            <section v-if="agentRun" class="agent-result" aria-label="Agent 執行結果">
              <div class="trace-facts">
                <div>
                  <dt>執行 ID</dt>
                  <dd>{{ agentRun.run_id }}</dd>
                </div>
                <div>
                  <dt>規劃器</dt>
                  <dd>{{ agentTraceValue(agentRun.trace.planner) }}</dd>
                </div>
                <div>
                  <dt>工具政策</dt>
                  <dd>{{ agentTraceValue(agentRun.trace.tool_policy) }}</dd>
                </div>
                <div>
                  <dt>權限判斷</dt>
                  <dd>{{ agentTraceValue(agentRun.trace.permission_decision) }}</dd>
                </div>
                <div v-if="agentRun.trace.permission_denied_tool">
                  <dt>阻擋工具</dt>
                  <dd>{{ toolLabel(agentRun.trace.permission_denied_tool) }}</dd>
                </div>
                <div>
                  <dt>備援次數</dt>
                  <dd>{{ agentRun.trace.fallback_count }}</dd>
                </div>
              </div>

              <section class="agent-section">
                <h3>執行計畫</h3>
                <ol class="agent-step-list">
                  <li v-for="step in agentRun.plan_steps" :key="step.step_id">
                    <div>
                      <strong>{{ agentStepTitle(step.title) }}</strong>
                      <small>{{ toolLabel(step.tool_name) }}</small>
                    </div>
                    <span class="status-pill" :class="documentStatusTone(step.status)">{{ statusLabel(step.status) }}</span>
                    <p>{{ agentMessage(step.observation_summary) }}</p>
                    <small v-if="step.fallback_reason" class="fallback-note">{{ fallbackReasonLabel(step.fallback_reason) }}</small>
                  </li>
                </ol>
              </section>

              <section class="agent-section">
                <h3>工具呼叫</h3>
                <div class="agent-tool-list">
                  <article v-for="toolCall in agentRun.tool_calls" :key="`${agentRun.run_id}-${toolCall.tool_name}`">
                    <div class="agent-tool-heading">
                      <strong>{{ toolLabel(toolCall.tool_name) }}</strong>
                      <span class="status-pill" :class="documentStatusTone(toolCall.status)">{{ statusLabel(toolCall.status) }}</span>
                    </div>
                    <dl class="agent-tool-details">
                      <div>
                        <dt>輸入摘要</dt>
                        <dd>{{ agentInputSummary(toolCall.input_summary) }}</dd>
                      </div>
                      <div>
                        <dt>觀察結果</dt>
                        <dd>{{ agentMessage(toolCall.observation.message) }}</dd>
                      </div>
                      <div v-if="toolCall.trace_metadata.tool_tier">
                        <dt>工具分級</dt>
                        <dd>{{ agentTraceValue(toolCall.trace_metadata.tool_tier) }}</dd>
                      </div>
                      <div v-if="toolCall.trace_metadata.permission_decision">
                        <dt>權限判斷</dt>
                        <dd>{{ agentTraceValue(toolCall.trace_metadata.permission_decision) }}</dd>
                      </div>
                      <div v-if="toolCall.trace_metadata.side_effect_policy">
                        <dt>副作用政策</dt>
                        <dd>{{ agentTraceValue(toolCall.trace_metadata.side_effect_policy) }}</dd>
                      </div>
                      <div v-if="toolCall.output_summary">
                        <dt>輸出摘要</dt>
                        <dd>{{ agentSummary(toolCall.output_summary) }}</dd>
                      </div>
                      <div v-if="toolCall.observation.fallback_reason">
                        <dt>備援原因</dt>
                        <dd>{{ fallbackReasonLabel(toolCall.observation.fallback_reason) }}</dd>
                      </div>
                    </dl>
                    <p v-if="toolCall.observation.missing_fields.length" class="muted compact-note">
                      缺少欄位：{{ missingFieldText(toolCall.observation.missing_fields) }}
                    </p>
                  </article>
                </div>
              </section>

              <section class="agent-section">
                <h3>最終回答</h3>
                <pre class="answer-text">{{ agentAnswerText(agentRun.final_answer.text) }}</pre>
              </section>

              <section class="agent-section">
                <h3>引用來源</h3>
                <ul v-if="agentRun.citations.length" class="citation-list">
                  <li v-for="citation in agentRun.citations" :key="`${citation.document_id}-${citation.chunk_id}`">
                    <span>{{ citation.filename }}</span>
                    <code>{{ citation.chunk_id }}</code>
                  </li>
                </ul>
                <p v-else class="muted compact-note">這次 Agent 執行沒有回傳引用來源。</p>
              </section>
            </section>
          </div>
        </details>
      </article>
    </section>

    <p v-if="healthError" class="error footer-error">{{ healthError }}</p>
    </template>
  </main>
</template>
