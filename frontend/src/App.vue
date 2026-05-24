<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  API_BASE_URL,
  getHealth,
  listDocuments,
  parseDocumentFields,
  queryRag,
  runAgent,
  runMockOcr,
  runSelectedOcr,
  uploadDocument,
  type AgentRun,
  type DocumentMetadata,
  type DocumentFields,
  type ExtractedField,
  type HealthResponse,
  type ParserResult,
  type RagQueryResponse,
  type UploadResponse,
} from "./api/client";

type RequestState = "idle" | "loading" | "success" | "error";
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
const chatState = ref<RequestState>("idle");
const documentsState = ref<RequestState>("idle");
const uploadState = ref<RequestState>("idle");
const viewMode = ref<ViewMode>("viewer");
const health = ref<HealthResponse | null>(null);
const ragResult = ref<RagQueryResponse | null>(null);
const documents = ref<DocumentMetadata[]>([]);
const uploadResult = ref<UploadResponse | null>(null);
const selectedFile = ref<File | null>(null);
const uploadFallbackAvailable = ref(false);
const ragQuery = ref("");
const ragTopK = ref(3);
const healthError = ref("");
const ragError = ref("");
const documentsError = ref("");
const uploadError = ref("");
const uploadMessage = ref("");
const parseStates = ref<Record<string, RequestState>>({});
const parseErrors = ref<Record<string, string>>({});
const agentState = ref<RequestState>("idle");
const agentRun = ref<AgentRun | null>(null);
const agentTask = ref("Summarize invoice fields and cite payment terms.");
const agentDocumentId = ref("");
const agentQuery = ref("payment terms");
const agentTopK = ref(3);
const agentError = ref("");

const suggestedQuestions = [
  "payment due date Net 15",
  "What is the SLA response target?",
  "When is the renewal date?",
];

const currentVersionLabel = computed(() => (health.value?.version ? `v${health.value.version}` : "v0.24.0"));

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

const invoiceFieldLabels: Array<[InvoiceFieldKey, string]> = [
  ["document_type", "文件類型"],
  ["invoice_number", "發票號碼"],
  ["vendor_name", "供應商"],
  ["issue_date", "日期"],
  ["total_amount", "總金額"],
  ["tax_amount", "稅額"],
  ["currency", "幣別"],
];

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
  viewMode.value = "admin";
  if (documentsState.value === "idle") {
    void refreshDocuments();
  }
}

function formatBytes(size: number): string {
  return `${size.toLocaleString()} 位元組`;
}

function handleFileChange(event: Event): void {
  const input = event.target as HTMLInputElement;
  selectedFile.value = input.files?.[0] ?? null;
  uploadResult.value = null;
  uploadFallbackAvailable.value = false;
  uploadMessage.value = "";
  uploadError.value = "";
}

function chunkReadiness(document: DocumentMetadata): string {
  if (document.chunks.length > 0) {
    return `local chunks ready (${document.chunks.length})`;
  }

  return "local chunks not ready";
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
  return document.ocr.status === "completed" || document.processing.ocr === "completed";
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

function parserFieldDisplay(result: ParserResult, fieldName: InvoiceFieldKey): string {
  if (fieldName === "total_amount") {
    return formatAmount(result.fields);
  }

  return formatFieldValue(result.fields[fieldName]);
}

function fieldMeta(field: ExtractedField): string {
  const confidence = field.confidence === null ? "confidence n/a" : `confidence ${Math.round(field.confidence * 100)}%`;
  const source = field.source_text ? `source: ${field.source_text}` : field.fallback_reason ? `reason: ${field.fallback_reason}` : "source unavailable";

  return `${confidence}; ${source}`;
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

async function submitUpload(): Promise<void> {
  if (!selectedFile.value) {
    uploadError.value = "請先選擇檔案。";
    return;
  }

  uploadState.value = "loading";
  uploadError.value = "";
  uploadMessage.value = "";
  uploadFallbackAvailable.value = false;

  let uploadedDocumentId = "";

  try {
    const response = await uploadDocument(selectedFile.value);
    uploadResult.value = response;
    uploadedDocumentId = response.document_id;
    await refreshDocuments();
    syncAgentDocumentSelection();
  } catch (error) {
    uploadResult.value = null;
    uploadError.value = error instanceof Error ? error.message : "文件上傳失敗";
    uploadState.value = "error";
    return;
  }

  try {
    const ocrResult = await runSelectedOcr(uploadedDocumentId);
    const selectedProvider = ocrResult.extracted_fields.provider ?? "";

    if (selectedProvider !== "paddleocr") {
      uploadFallbackAvailable.value = true;
      uploadError.value = selectedProvider
        ? `GPU OCR 未完成：目前後端 selected OCR provider 是 ${selectedProvider}。`
        : "GPU OCR 未完成：目前後端 selected OCR provider 不是 paddleocr。";
      uploadState.value = "error";
      await refreshDocuments();
      return;
    }

    uploadMessage.value = "文件已完成 provider-selected OCR，並產生 local chunks。";
    uploadState.value = "success";
    await refreshDocuments();
  } catch (error) {
    uploadFallbackAvailable.value = true;
    uploadError.value = error instanceof Error ? `GPU OCR 未完成：${error.message}` : "GPU OCR 未完成";
    uploadState.value = "error";
    await refreshDocuments();
  }
}

async function submitMockFallback(): Promise<void> {
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
    uploadMessage.value = "已改用 mock OCR 完成後台 ingestion 備援處理。";
    uploadState.value = "success";
    await refreshDocuments();
  } catch (error) {
    uploadError.value = error instanceof Error ? `Mock OCR 備援失敗：${error.message}` : "Mock OCR 備援失敗";
    uploadState.value = "error";
  }
}

async function submitFieldParse(document: DocumentMetadata): Promise<void> {
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
  const task = agentTask.value.trim();
  const documentId = agentDocumentId.value.trim();
  const query = agentQuery.value.trim();

  if (!task) {
    agentError.value = "Agent task is required.";
    return;
  }

  if (!documentId) {
    agentError.value = "Select an ingested document for this Agent demo run.";
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
    agentError.value = error instanceof Error ? error.message : "Agent run failed.";
    agentState.value = "error";
  }
}

onMounted(() => {
  void checkHealth();
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
              @click="openAdminSurface"
            >
              後台知識庫管理
            </button>
          </div>
        </div>
      </div>
    </header>

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

          <button type="submit" class="button" :disabled="chatState === 'loading'">
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

        <div class="surface-note">
          <strong>目前階段</strong>
          <span>backend upload + provider-selected OCR + local chunking。real OCR 失敗時保留文件並提供 mock OCR fallback；尚未完成 VLM parser、worker pipeline、DB 或 production indexing。</span>
        </div>

        <label class="file-picker">
          <span>選擇文件</span>
          <input type="file" @change="handleFileChange" />
        </label>

        <p v-if="selectedFile" class="selected-file">
          {{ selectedFile.name }} - {{ formatBytes(selectedFile.size) }}
        </p>
        <p v-else class="muted">尚未選擇文件。</p>

        <button
          type="button"
          class="button upload-button"
          :disabled="!selectedFile || uploadState === 'loading'"
          @click="submitUpload"
        >
          {{ uploadState === "loading" ? "後台處理中..." : "建立 demo 知識庫資料" }}
        </button>

        <p v-if="uploadMessage" class="success-message">{{ uploadMessage }}</p>
        <p v-if="uploadError" class="error">{{ uploadError }}</p>
        <button
          v-if="uploadFallbackAvailable"
          type="button"
          class="button secondary-button upload-button"
          :disabled="uploadState === 'loading'"
          @click="submitMockFallback"
        >
          使用 mock OCR fallback
        </button>
      </article>

      <article class="panel ingestion-status">
        <div class="panel-heading">
          <div>
            <h2>Ingestion 狀態</h2>
            <p>只呈現 local MVP 處理狀態，不代表正式 production indexing。</p>
          </div>
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
                document {{ document.status }}
              </span>
              <span class="status-pill" :class="documentStatusTone(document.processing.ocr)">
                OCR {{ document.processing.ocr }}
              </span>
              <span class="status-pill" :class="documentStatusTone(parserStatus(document))">
                Parser {{ parserStatus(document) }}
              </span>
              <span class="status-pill" :class="document.processing.ready ? 'status-success' : 'status-ready'">
                {{ chunkReadiness(document) }}
              </span>
            </div>
            <div class="parser-actions">
              <button
                type="button"
                class="button secondary-button compact-button"
                :disabled="!canParseDocument(document) || parseStates[document.document_id] === 'loading'"
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
              <small v-if="!canParseDocument(document)">OCR 完成後才能解析欄位。</small>
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
                  <span>Parser</span>
                  <strong>{{ document.parser_result.parser_source }}</strong>
                </div>
                <small v-if="document.parser_result.fallback_reason">
                  {{ document.parser_result.fallback_reason }}
                </small>
              </div>
              <div class="fields-grid">
                <div v-for="field in invoiceFieldLabels" :key="field[0]" class="field-cell">
                  <span>{{ field[1] }}</span>
                  <strong>{{ parserFieldDisplay(document.parser_result, field[0]) }}</strong>
                  <small>{{ fieldMeta(document.parser_result.fields[field[0]]) }}</small>
                </div>
              </div>
              <p v-if="missingFieldLabels(document.parser_result).length" class="muted compact-note">
                缺少欄位：{{ missingFieldLabels(document.parser_result).join("、") }}
              </p>
              <p v-if="document.parser_result.fields.line_items.length" class="muted compact-note">
                line items：{{ document.parser_result.fields.line_items.length }}
              </p>
            </section>
            <section
              v-else-if="document.parser_result?.status === 'failed'"
              class="fields-summary fields-summary-failed"
              aria-label="欄位解析失敗"
            >
              <strong>{{ document.parser_result.fallback_reason ?? "parser_failed" }}</strong>
              <span>{{ document.parser_result.error_message ?? "欄位解析未完成。" }}</span>
            </section>
            <p v-else class="muted compact-note">尚未執行欄位解析。</p>
            <p v-if="document.processing.failed_reason" class="error">{{ document.processing.failed_reason }}</p>
          </li>
        </ul>
      </article>

      <article class="panel agent-surface" aria-label="Agent trace surface">
        <div class="panel-heading">
          <div>
            <h2>Agent trace</h2>
            <p>Admin / Analyst demo surface for deterministic tool-use runs.</p>
          </div>
          <span class="status-pill" :class="documentStatusTone(agentRun?.status ?? 'pending')">
            {{ agentRun?.status ?? "pending" }}
          </span>
        </div>

        <form class="agent-form" @submit.prevent="submitAgentRun">
          <label class="agent-task-field">
            <span>Agent task</span>
            <textarea v-model="agentTask" rows="3" />
          </label>

          <label>
            <span>Document</span>
            <select v-model="agentDocumentId">
              <option value="" disabled>Select document</option>
              <option v-for="document in agentDocumentOptions" :key="document.document_id" :value="document.document_id">
                {{ document.filename }}
              </option>
            </select>
          </label>

          <label>
            <span>Query</span>
            <input v-model="agentQuery" type="text" placeholder="payment terms" />
          </label>

          <label>
            <span>Top K</span>
            <input v-model.number="agentTopK" type="number" min="1" max="10" />
          </label>

          <button type="submit" class="button" :disabled="agentState === 'loading'">
            {{ agentState === "loading" ? "Running..." : "Run Agent" }}
          </button>
        </form>

        <p v-if="agentError" class="error">{{ agentError }}</p>
        <p v-if="!agentRun" class="muted compact-note">
          Agent trace runs stay inside the Phase 25 read-only tool allowlist.
        </p>

        <section v-if="agentRun" class="agent-result" aria-label="Agent run result">
          <div class="trace-facts">
            <div>
              <dt>Run</dt>
              <dd>{{ agentRun.run_id }}</dd>
            </div>
            <div>
              <dt>Planner</dt>
              <dd>{{ agentRun.trace.planner }}</dd>
            </div>
            <div>
              <dt>Tool policy</dt>
              <dd>{{ agentRun.trace.tool_policy }}</dd>
            </div>
            <div>
              <dt>Fallbacks</dt>
              <dd>{{ agentRun.trace.fallback_count }}</dd>
            </div>
          </div>

          <section class="agent-section">
            <h3>Plan</h3>
            <ol class="agent-step-list">
              <li v-for="step in agentRun.plan_steps" :key="step.step_id">
                <div>
                  <strong>{{ step.title }}</strong>
                  <small>{{ step.tool_name ?? "no tool" }}</small>
                </div>
                <span class="status-pill" :class="documentStatusTone(step.status)">{{ step.status }}</span>
                <p>{{ step.observation_summary ?? "observation unavailable" }}</p>
                <small v-if="step.fallback_reason" class="fallback-note">{{ step.fallback_reason }}</small>
              </li>
            </ol>
          </section>

          <section class="agent-section">
            <h3>Tool calls</h3>
            <div class="agent-tool-list">
              <article v-for="toolCall in agentRun.tool_calls" :key="`${agentRun.run_id}-${toolCall.tool_name}`">
                <div class="agent-tool-heading">
                  <strong>{{ toolCall.tool_name }}</strong>
                  <span class="status-pill" :class="documentStatusTone(toolCall.status)">{{ toolCall.status }}</span>
                </div>
                <dl class="agent-tool-details">
                  <div>
                    <dt>Input</dt>
                    <dd>{{ toolCall.input_summary }}</dd>
                  </div>
                  <div>
                    <dt>Observation</dt>
                    <dd>{{ toolCall.observation.message }}</dd>
                  </div>
                  <div v-if="toolCall.output_summary">
                    <dt>Output</dt>
                    <dd>{{ toolCall.output_summary }}</dd>
                  </div>
                  <div v-if="toolCall.observation.fallback_reason">
                    <dt>Fallback</dt>
                    <dd>{{ toolCall.observation.fallback_reason }}</dd>
                  </div>
                </dl>
                <p v-if="toolCall.observation.missing_fields.length" class="muted compact-note">
                  Missing fields: {{ toolCall.observation.missing_fields.join(", ") }}
                </p>
              </article>
            </div>
          </section>

          <section class="agent-section">
            <h3>Final answer</h3>
            <pre class="answer-text">{{ agentRun.final_answer.text }}</pre>
          </section>

          <section class="agent-section">
            <h3>Citations</h3>
            <ul v-if="agentRun.citations.length" class="citation-list">
              <li v-for="citation in agentRun.citations" :key="`${citation.document_id}-${citation.chunk_id}`">
                <span>{{ citation.filename }}</span>
                <code>{{ citation.chunk_id }}</code>
              </li>
            </ul>
            <p v-else class="muted compact-note">No citations returned for this Agent run.</p>
          </section>
        </section>
      </article>
    </section>

    <p v-if="healthError" class="error footer-error">{{ healthError }}</p>
  </main>
</template>
