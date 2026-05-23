<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  API_BASE_URL,
  getDocument,
  getHealth,
  getOcrResult,
  listDocuments,
  queryRag,
  runMockOcr,
  runSelectedOcr,
  uploadDocument,
  type BoundingBox,
  type DocumentListResponse,
  type DocumentMetadata,
  type HealthResponse,
  type OcrResultResponse,
  type RagQueryResponse,
  type RetrievedChunk,
  type UploadResponse,
} from "./api/client";

type RequestState = "idle" | "loading" | "success" | "error";

type TraceFact = {
  label: string;
  value: string;
  tone?: "default" | "failed" | "ready" | "success";
};

type TraceCandidateRow = {
  rank: number;
  score: string;
  documentId: string;
  chunkId: string;
  filename: string;
  preview: string;
  traceSummary: string[];
};

type DemoStat = {
  label: string;
  value: string;
  detail: string;
  tone?: "default" | "failed" | "ready" | "success";
};

type WorkflowStep = {
  label: string;
  detail: string;
  state: "idle" | "loading" | "ready" | "success" | "failed";
};

const healthState = ref<RequestState>("idle");
const documentsState = ref<RequestState>("idle");
const detailState = ref<RequestState>("idle");
const ocrState = ref<RequestState>("idle");
const chatState = ref<RequestState>("idle");
const uploadState = ref<RequestState>("idle");
const health = ref<HealthResponse | null>(null);
const documents = ref<DocumentMetadata[]>([]);
const selectedDocument = ref<DocumentMetadata | null>(null);
const uploadResult = ref<UploadResponse | null>(null);
const ragResult = ref<RagQueryResponse | null>(null);
const selectedFile = ref<File | null>(null);
const ragQuery = ref("");
const ragTopK = ref(3);
const healthError = ref("");
const documentsError = ref("");
const detailError = ref("");
const ocrError = ref("");
const ragError = ref("");
const uploadError = ref("");
const latestResponse = ref<
  | DocumentListResponse
  | DocumentMetadata
  | HealthResponse
  | OcrResultResponse
  | RagQueryResponse
  | UploadResponse
  | null
>(null);

const requestStateLabels: Record<RequestState, string> = {
  idle: "待命",
  loading: "處理中",
  success: "成功",
  error: "錯誤",
};

const statusLabels: Record<string, string> = {
  idle: "待命",
  loading: "處理中",
  success: "成功",
  error: "錯誤",
  uploaded: "已上傳",
  pending: "待處理",
  processing: "處理中",
  running: "執行中",
  completed: "已完成",
  ready: "可查詢",
  failed: "失敗",
  disabled: "停用",
  local_indexing: "本機索引",
  vector_indexing: "向量索引",
  ocr: "OCR",
  ocr_mock: "模擬 OCR",
  upload: "上傳",
  keyword: "關鍵字",
  vector: "向量",
  hybrid: "混合檢索",
  vector_rerank: "向量重排",
  hybrid_rerank: "混合重排",
};

const currentVersionLabel = computed(() => (health.value?.version ? `v${health.value.version}` : "v0.20.0"));

const readyDocumentCount = computed(() => documents.value.filter((document) => document.processing.ready).length);

const completedOcrCount = computed(
  () => documents.value.filter((document) => document.ocr.status === "completed").length,
);

const selectedDocumentLabel = computed(() => selectedDocument.value?.filename ?? "尚未選擇文件");

const latestJobLabel = computed(() => {
  if (!selectedDocument.value?.latest_job) {
    return "尚無處理工作";
  }

  return formatProcessingJob(selectedDocument.value.latest_job);
});

const demoStats = computed<DemoStat[]>(() => [
  {
    label: "後端",
    value: healthLabel.value,
    detail: health.value?.version ? `版本 ${health.value.version}` : API_BASE_URL,
    tone: healthState.value === "error" ? "failed" : healthState.value === "success" ? "success" : "ready",
  },
  {
    label: "文件",
    value: String(documents.value.length),
    detail: `${completedOcrCount.value} 份 OCR 已完成 / ${readyDocumentCount.value} 份可查詢`,
    tone: documents.value.length > 0 ? "success" : "ready",
  },
  {
    label: "已選文件",
    value: selectedDocument.value ? displayStatus(selectedDocument.value.status) : "無",
    detail: selectedDocumentLabel.value,
    tone: selectedDocument.value?.processing.ready ? "success" : selectedDocument.value ? "ready" : "default",
  },
  {
    label: "回答",
    value: ragResult.value ? ragAnswerSource.value : "待提問",
    detail: ragResult.value ? ragRetrievalSource.value : "OCR 後可提問",
    tone: ragResult.value ? sourceTone(ragAnswerSource.value) : "default",
  },
]);

const healthLabel = computed(() => {
  if (healthState.value === "success" && health.value?.status === "ok") {
    return "後端在線";
  }

  if (healthState.value === "loading") {
    return "檢查中";
  }

  if (healthState.value === "error") {
    return "無法連線";
  }

  return "尚未檢查";
});

const workflowSteps = computed<WorkflowStep[]>(() => [
  {
    label: "上傳",
    detail: selectedDocument.value ? selectedDocument.value.filename : "本機 JSON 儲存",
    state:
      uploadState.value === "loading"
        ? "loading"
        : selectedDocument.value
          ? "success"
          : uploadState.value === "error"
            ? "failed"
            : "idle",
  },
  {
    label: "OCR",
    detail: selectedDocument.value?.ocr.status ? displayStatus(selectedDocument.value.ocr.status) : "依 OCR 供應器執行",
    state:
      ocrState.value === "loading"
        ? "loading"
        : selectedDocument.value?.ocr.status === "completed"
          ? "success"
          : selectedDocument.value?.ocr.status === "failed"
            ? "failed"
            : selectedDocument.value
              ? "ready"
              : "idle",
  },
  {
    label: "索引",
    detail: selectedDocument.value?.processing.indexing ? displayStatus(selectedDocument.value.processing.indexing) : "本機片段",
    state:
      selectedDocument.value?.processing.indexing === "completed"
        ? "success"
        : selectedDocument.value?.processing.indexing === "failed"
          ? "failed"
          : selectedDocument.value
            ? "ready"
            : "idle",
  },
  {
    label: "追蹤",
    detail: ragResult.value ? `${ragResult.value.retrieved_chunks.length} 個候選片段` : "引用中繼資料",
    state:
      chatState.value === "loading"
        ? "loading"
        : ragResult.value
          ? "success"
          : chatState.value === "error"
            ? "failed"
            : "idle",
  },
]);

const latestResponseJson = computed(() =>
  latestResponse.value ? JSON.stringify(latestResponse.value, null, 2) : "尚未取得 API 回應。",
);

const selectedDocumentJson = computed(() =>
  selectedDocument.value
    ? JSON.stringify(selectedDocument.value, null, 2)
    : "尚未選擇文件。",
);

const selectedOcrEntries = computed(() =>
  selectedDocument.value ? Object.entries(selectedDocument.value.ocr.extracted_fields) : [],
);

const selectedOcrText = computed(() =>
  selectedDocument.value?.ocr.text ? selectedDocument.value.ocr.text : "尚未執行 OCR。",
);

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

  if (trace?.llm_generation_status === "completed") {
    return `${trace.llm_provider ?? "ollama"}/${trace.llm_model ?? "qwen3.5:4b"}`;
  }

  if (trace?.llm_generation_status === "failed") {
    return "LLM 不可用，改用備援";
  }

  return "確定性基準回答";
});

const ragAnswerSourceClass = computed(() => {
  if (sourceTone(ragAnswerSource.value) === "failed") {
    return "status-failed";
  }

  if (sourceTone(ragAnswerSource.value) === "ready") {
    return "status-ready";
  }

  return "status-success";
});

const ragRetrievalSource = computed(() => {
  const trace = ragTraceMetadata.value;

  if (trace?.vector_retrieval_status === "completed") {
    return `${trace.retrieval_provider ?? "vector"}/${trace.vector_store ?? "qdrant"}`;
  }

  if (trace?.vector_retrieval_status === "failed") {
    return "向量檢索不可用，改用備援";
  }

  return "關鍵字基準檢索";
});

const ragRetrievalSourceClass = computed(() => {
  if (sourceTone(ragRetrievalSource.value) === "failed") {
    return "status-failed";
  }

  if (sourceTone(ragRetrievalSource.value) === "ready") {
    return "status-ready";
  }

  return "status-success";
});

const ragStrategyLabel = computed(() => {
  const metadata = ragTraceMetadata.value;

  if (metadata.strategy_label) {
    return displayStatus(metadata.strategy_label);
  }

  if (metadata.vector_retrieval_status === "completed") {
    return "向量";
  }

  if (metadata.vector_retrieval_status === "failed") {
    return "關鍵字備援";
  }

  return "關鍵字";
});

const ragTraceFacts = computed<TraceFact[]>(() => {
  if (!ragResult.value) {
    return [];
  }

  const metadata = ragTraceMetadata.value;
  const facts: TraceFact[] = [
    { label: "策略", value: ragStrategyLabel.value, tone: "ready" },
    { label: "回答來源", value: ragAnswerSource.value, tone: sourceTone(ragAnswerSource.value) },
    { label: "檢索來源", value: ragRetrievalSource.value, tone: sourceTone(ragRetrievalSource.value) },
    { label: "候選片段", value: String(ragResult.value.retrieved_chunks.length) },
  ];

  const vectorStatus = metadata.vector_retrieval_status;
  if (vectorStatus) {
    facts.push({ label: "向量狀態", value: displayStatus(vectorStatus), tone: vectorStatus === "failed" ? "failed" : "success" });
  }

  const rerankStatus = metadata.rerank_status;
  if (rerankStatus) {
    facts.push({
      label: "重排",
      value: [metadata.rerank_provider, displayStatus(rerankStatus)].filter(Boolean).join(" / "),
      tone: rerankStatus === "failed" || rerankStatus === "disabled" ? "failed" : "success",
    });
  }

  if (metadata.merge_policy) {
    facts.push({ label: "合併策略", value: metadata.merge_policy });
  }

  const latency = firstMetadataValue(metadata, ["rerank_latency_ms", "llm_generation_latency_ms"]);
  if (latency) {
    facts.push({ label: "延遲", value: `${latency} ms` });
  }

  const fallback = firstMetadataValue(metadata, [
    "fallback_reason",
    "rerank_fallback_reason",
    "vector_retrieval_error",
    "llm_error",
  ]);
  facts.push({
    label: "備援",
    value: fallback ?? "無",
    tone: fallback ? "failed" : "ready",
  });

  return facts;
});

const ragTraceRows = computed<TraceCandidateRow[]>(() =>
  ragResult.value
    ? ragResult.value.retrieved_chunks.map((chunk, index) => ({
        rank: index + 1,
        score: formatScore(chunk.score),
        documentId: chunk.document_id,
        chunkId: chunk.chunk_id,
        filename: chunk.filename,
        preview: previewText(chunk.text),
        traceSummary: candidateTraceSummary(chunk),
      }))
    : [],
);

function formatBytes(size: number): string {
  return `${size.toLocaleString()} 位元組`;
}

function statusClass(status: string): string {
  return `status-${status.replace(/_/g, "-")}`;
}

function displayStatus(status: string): string {
  return statusLabels[status] ?? status.replace(/_/g, " ");
}

function displayRequestState(state: RequestState): string {
  return requestStateLabels[state];
}

function formatProcessingJob(job: { job_type: string; status: string }): string {
  return `${displayStatus(job.job_type)} / ${displayStatus(job.status)}`;
}

function formatBbox(bbox: BoundingBox): string {
  return `座標 ${bbox.x_min},${bbox.y_min},${bbox.x_max},${bbox.y_max}`;
}

function metadataEntries(metadata: Record<string, string>): [string, string][] {
  return Object.entries(metadata);
}

function firstMetadataValue(metadata: Record<string, string>, keys: string[]): string | null {
  for (const key of keys) {
    const value = metadata[key];

    if (value) {
      return value;
    }
  }

  return null;
}

function sourceTone(source: string): TraceFact["tone"] {
  if (
    source.toLowerCase().includes("fallback") ||
    source.toLowerCase().includes("unavailable") ||
    source.includes("備援") ||
    source.includes("不可用")
  ) {
    return "failed";
  }

  if (source.toLowerCase().includes("baseline") || source.includes("基準")) {
    return "ready";
  }

  return "success";
}

function formatScore(score: number | string): string {
  const numericScore = typeof score === "number" ? score : Number(score);

  return Number.isFinite(numericScore) ? numericScore.toFixed(4) : String(score);
}

function previewText(text: string): string {
  return text.length > 180 ? `${text.slice(0, 180)}...` : text;
}

function candidateTraceSummary(chunk: RetrievedChunk): string[] {
  const metadata = chunk.metadata;
  const summary = [
    chunk.source_type ? `來源 ${chunk.source_type}` : `來源 ${chunk.source}`,
    metadata.strategy_label ? `策略 ${displayStatus(metadata.strategy_label)}` : "",
    metadata.retrieval_provider ? `供應器 ${metadata.retrieval_provider}` : "",
    metadata.branches ? `分支 ${metadata.branches}` : "",
    metadata.final_rank ? `最終排名 ${metadata.final_rank}` : "",
    metadata.keyword_rank ? `關鍵字排名 ${metadata.keyword_rank}` : "",
    metadata.vector_rank ? `向量排名 ${metadata.vector_rank}` : "",
    metadata.merged_score ? `合併分數 ${formatScore(metadata.merged_score)}` : "",
    metadata.rerank_status ? `重排 ${displayStatus(metadata.rerank_status)}` : "",
    metadata.rerank_rank ? `重排排名 ${metadata.rerank_rank}` : "",
    metadata.rerank_score ? `重排分數 ${formatScore(metadata.rerank_score)}` : "",
    firstMetadataValue(metadata, ["fallback_reason", "rerank_fallback_reason", "vector_retrieval_error"])
      ? `備援 ${firstMetadataValue(metadata, ["fallback_reason", "rerank_fallback_reason", "vector_retrieval_error"])}`
      : "",
  ].filter(Boolean);

  return summary.length ? summary : ["無中繼資料"];
}

async function checkHealth(): Promise<void> {
  healthState.value = "loading";
  healthError.value = "";

  try {
    const response = await getHealth();
    health.value = response;
    latestResponse.value = response;
    healthState.value = "success";
  } catch (error) {
    health.value = null;
    healthError.value = error instanceof Error ? error.message : "後端健康檢查失敗";
    healthState.value = "error";
  }
}

async function refreshDocuments(): Promise<void> {
  documentsState.value = "loading";
  documentsError.value = "";

  try {
    const response = await listDocuments();
    documents.value = response.documents;
    latestResponse.value = response;
    documentsState.value = "success";
  } catch (error) {
    documents.value = [];
    documentsError.value = error instanceof Error ? error.message : "載入文件列表失敗";
    documentsState.value = "error";
  }
}

async function selectDocument(documentId: string): Promise<void> {
  detailState.value = "loading";
  detailError.value = "";

  try {
    const response = await getDocument(documentId);
    const ocrResponse = await getOcrResult(documentId);
    selectedDocument.value = {
      ...response,
      ocr: ocrResponse,
    };
    latestResponse.value = ocrResponse;
    detailState.value = "success";
    ocrState.value = "idle";
    ocrError.value = "";
  } catch (error) {
    selectedDocument.value = null;
    detailError.value = error instanceof Error ? error.message : "載入文件失敗";
    detailState.value = "error";
  }
}

async function runOcrForSelectedDocument(): Promise<void> {
  if (!selectedDocument.value) {
    ocrError.value = "請先選擇文件。";
    return;
  }

  const documentId = selectedDocument.value.document_id;
  ocrState.value = "loading";
  ocrError.value = "";

  try {
    const response = await runMockOcr(documentId);
    const updatedDocument = await getDocument(documentId);
    selectedDocument.value = updatedDocument;
    documents.value = documents.value.map((document) =>
      document.document_id === documentId ? updatedDocument : document,
    );
    latestResponse.value = response;
    ocrState.value = "success";
  } catch (error) {
    ocrError.value = error instanceof Error ? error.message : "執行 OCR 失敗";
    ocrState.value = "error";
  }
}

async function runSelectedOcrForSelectedDocument(): Promise<void> {
  if (!selectedDocument.value) {
    ocrError.value = "請先選擇文件。";
    return;
  }

  const documentId = selectedDocument.value.document_id;
  ocrState.value = "loading";
  ocrError.value = "";

  try {
    const response = await runSelectedOcr(documentId);
    const updatedDocument = await getDocument(documentId);
    selectedDocument.value = updatedDocument;
    documents.value = documents.value.map((document) =>
      document.document_id === documentId ? updatedDocument : document,
    );
    latestResponse.value = response;
    ocrState.value = "success";
  } catch (error) {
    try {
      const updatedDocument = await getDocument(documentId);
      selectedDocument.value = updatedDocument;
      documents.value = documents.value.map((document) =>
        document.document_id === documentId ? updatedDocument : document,
      );
    } catch {
      // 無法刷新失敗 metadata 時，保留原始 API 錯誤。
    }

    ocrError.value = error instanceof Error ? error.message : "執行預設 OCR 失敗";
    ocrState.value = "error";
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
    const response = await queryRag(query, ragTopK.value);
    ragResult.value = response;
    latestResponse.value = response;
    chatState.value = "success";
  } catch (error) {
    ragResult.value = null;
    ragError.value = error instanceof Error ? error.message : "RAG 查詢失敗";
    chatState.value = "error";
  }
}

function handleFileChange(event: Event): void {
  const input = event.target as HTMLInputElement;
  selectedFile.value = input.files?.[0] ?? null;
  uploadResult.value = null;
  uploadError.value = "";
}

async function submitUpload(): Promise<void> {
  if (!selectedFile.value) {
    uploadError.value = "請先選擇檔案。";
    return;
  }

  uploadState.value = "loading";
  uploadError.value = "";

  try {
    const response = await uploadDocument(selectedFile.value);
    uploadResult.value = response;
    latestResponse.value = response;
    uploadState.value = "success";
    await refreshDocuments();
    await selectDocument(response.document_id);
  } catch (error) {
    uploadResult.value = null;
    uploadError.value = error instanceof Error ? error.message : "上傳失敗";
    uploadState.value = "error";
  }
}

onMounted(() => {
  void checkHealth();
  void refreshDocuments();
});
</script>

<template>
  <main class="page">
    <header class="hero">
      <div class="hero-shell">
        <div class="hero-main">
          <div class="hero-kicker">
            <span class="eyebrow">{{ currentVersionLabel }}</span>
            <span class="status-pill" :class="`status-${healthState}`">{{ healthLabel }}</span>
          </div>
          <h1>DocuRAG AgentOps</h1>
          <p class="hero-copy">
            本機文件智能展示，整合 OCR、具引用來源的 RAG、檢索追蹤與可評估的中繼資料。
          </p>
        </div>

        <div class="hero-side">
          <span>目前選取文件</span>
          <strong>{{ selectedDocumentLabel }}</strong>
          <small>{{ latestJobLabel }}</small>
        </div>
      </div>

      <section class="metric-strip" aria-label="MVP 狀態總覽">
        <article v-for="stat in demoStats" :key="stat.label" class="metric-card" :class="stat.tone ? `metric-${stat.tone}` : ''">
          <span>{{ stat.label }}</span>
          <strong>{{ stat.value }}</strong>
          <small>{{ stat.detail }}</small>
        </article>
      </section>

      <ol class="workflow-strip" aria-label="文件流程狀態">
        <li v-for="step in workflowSteps" :key="step.label" :class="`workflow-${step.state}`">
          <span>{{ step.label }}</span>
          <strong>{{ step.detail }}</strong>
        </li>
      </ol>
    </header>

    <section class="layout" aria-label="展示操作區">
      <article class="panel">
        <div class="panel-heading">
          <div>
            <h2>後端健康狀態</h2>
            <p>GET /health</p>
          </div>
          <span class="status-pill" :class="`status-${healthState}`">{{ healthLabel }}</span>
        </div>

        <dl v-if="health" class="facts">
          <div>
            <dt>服務</dt>
            <dd>{{ health.service }}</dd>
          </div>
          <div>
            <dt>狀態</dt>
            <dd>{{ displayStatus(health.status) }}</dd>
          </div>
          <div>
            <dt>版本</dt>
            <dd>{{ health.version }}</dd>
          </div>
        </dl>

        <p v-if="healthError" class="error">{{ healthError }}</p>
        <p class="api-base">API 基底 URL：{{ API_BASE_URL }}</p>

        <button type="button" class="button" :disabled="healthState === 'loading'" @click="checkHealth">
          {{ healthState === "loading" ? "檢查中..." : "重新檢查後端" }}
        </button>
      </article>

      <article class="panel">
        <div class="panel-heading">
          <div>
            <h2>上傳文件</h2>
            <p>POST /documents/upload</p>
          </div>
        </div>

        <label class="file-picker">
          <span>選擇檔案</span>
          <input type="file" @change="handleFileChange" />
        </label>

        <p v-if="selectedFile" class="selected-file">
          {{ selectedFile.name }} - {{ formatBytes(selectedFile.size) }}
        </p>
        <p v-else class="muted">尚未選擇檔案。</p>

        <p v-if="uploadError" class="error">{{ uploadError }}</p>

        <button
          type="button"
          class="button"
          :disabled="!selectedFile || uploadState === 'loading'"
          @click="submitUpload"
        >
          {{ uploadState === "loading" ? "上傳中..." : "上傳到後端" }}
        </button>
      </article>

      <article class="panel">
        <div class="panel-heading">
          <div>
            <h2>上傳結果</h2>
            <p>最新保存的中繼資料</p>
          </div>
          <span v-if="uploadResult" class="status-pill status-success">{{ displayStatus(uploadResult.status) }}</span>
        </div>

        <dl v-if="uploadResult" class="facts">
          <div>
            <dt>文件 ID</dt>
            <dd>{{ uploadResult.document_id }}</dd>
          </div>
          <div>
            <dt>檔名</dt>
            <dd>{{ uploadResult.filename }}</dd>
          </div>
          <div>
            <dt>內容類型</dt>
            <dd>{{ uploadResult.content_type }}</dd>
          </div>
          <div>
            <dt>大小</dt>
            <dd>{{ formatBytes(uploadResult.size) }}</dd>
          </div>
        </dl>

        <p v-else class="muted">尚未上傳檔案。</p>
      </article>

      <article class="panel documents-panel">
        <div class="panel-heading">
          <div>
            <h2>文件列表</h2>
            <p>GET /documents</p>
          </div>
          <button
            type="button"
            class="button secondary-button"
            :disabled="documentsState === 'loading'"
            @click="refreshDocuments"
          >
            {{ documentsState === "loading" ? "載入中..." : "重新整理列表" }}
          </button>
        </div>

        <p v-if="documentsError" class="error">{{ documentsError }}</p>

        <div v-if="documents.length" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>檔名</th>
                <th>狀態</th>
                <th>OCR</th>
                <th>索引</th>
                <th>最新工作</th>
                <th>大小</th>
                <th>建立時間</th>
                <th>內容類型</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="document in documents"
                :key="document.document_id"
                :class="{ selected: selectedDocument?.document_id === document.document_id }"
              >
                <td>
                  <button
                    type="button"
                    class="link-button"
                    :disabled="detailState === 'loading'"
                    @click="selectDocument(document.document_id)"
                  >
                    {{ document.filename }}
                  </button>
                </td>
                <td><span class="status-pill" :class="statusClass(document.status)">{{ displayStatus(document.status) }}</span></td>
                <td><span class="status-pill" :class="statusClass(document.ocr.status)">{{ displayStatus(document.ocr.status) }}</span></td>
                <td>
                  <span class="status-pill" :class="statusClass(document.processing.indexing)">
                    {{ displayStatus(document.processing.indexing) }}
                  </span>
                </td>
                <td>
                  <span v-if="document.latest_job" class="status-pill" :class="statusClass(document.latest_job.status)">
                    {{ formatProcessingJob(document.latest_job) }}
                  </span>
                  <span v-else class="muted">無</span>
                </td>
                <td>{{ formatBytes(document.size) }}</td>
                <td>{{ document.created_at }}</td>
                <td>{{ document.content_type }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-else class="muted">目前沒有文件。</p>
      </article>

      <article class="panel ocr-panel">
        <div class="panel-heading">
          <div>
            <h2>OCR 結果</h2>
            <p>預設 /ocr 供應器：GPU-only PaddleOCR PP-OCRv4；模擬覆寫：/ocr/mock</p>
          </div>
          <div class="button-row">
            <button
              type="button"
              class="button secondary-button"
              :disabled="!selectedDocument || ocrState === 'loading'"
              @click="runOcrForSelectedDocument"
            >
              {{ ocrState === "loading" ? "執行中..." : "執行模擬 OCR" }}
            </button>
            <button
              type="button"
              class="button"
              :disabled="!selectedDocument || ocrState === 'loading'"
              @click="runSelectedOcrForSelectedDocument"
            >
              {{ ocrState === "loading" ? "執行中..." : "執行預設 OCR" }}
            </button>
          </div>
        </div>

        <p v-if="ocrError" class="error">{{ ocrError }}</p>

        <dl v-if="selectedDocument" class="facts">
          <div>
            <dt>文件狀態</dt>
            <dd>
              <span class="status-pill" :class="statusClass(selectedDocument.status)">
                {{ displayStatus(selectedDocument.status) }}
              </span>
            </dd>
          </div>
          <div>
            <dt>OCR 狀態</dt>
            <dd>
              <span class="status-pill" :class="statusClass(selectedDocument.ocr.status)">
                {{ displayStatus(selectedDocument.ocr.status) }}
              </span>
            </dd>
          </div>
          <div>
            <dt>索引狀態</dt>
            <dd>
              <span class="status-pill" :class="statusClass(selectedDocument.processing.indexing)">
                {{ displayStatus(selectedDocument.processing.indexing) }}
              </span>
            </dd>
          </div>
          <div>
            <dt>可查詢</dt>
            <dd>{{ selectedDocument.processing.ready ? "是" : "否" }}</dd>
          </div>
          <div v-if="selectedDocument.processing.failed_reason">
            <dt>失敗原因</dt>
            <dd>{{ selectedDocument.processing.failed_reason }}</dd>
          </div>
          <div v-if="selectedDocument.latest_job">
            <dt>最新工作</dt>
            <dd>
              {{ formatProcessingJob(selectedDocument.latest_job) }}
            </dd>
          </div>
          <div>
            <dt>更新時間</dt>
            <dd>{{ selectedDocument.processing.updated_at ?? selectedDocument.ocr.updated_at ?? "尚未執行" }}</dd>
          </div>
        </dl>

        <div v-if="selectedDocument" class="ocr-grid">
          <section>
            <h3>OCR 文字</h3>
            <pre class="ocr-text">{{ selectedOcrText }}</pre>
          </section>

          <section>
            <h3>擷取欄位</h3>
            <dl v-if="selectedOcrEntries.length" class="field-list">
              <div v-for="[field, value] in selectedOcrEntries" :key="field">
                <dt>{{ field }}</dt>
                <dd>{{ value }}</dd>
              </div>
            </dl>
            <p v-else class="muted">尚未擷取欄位。</p>
          </section>
        </div>

        <p v-else class="muted">尚未選擇文件。</p>
      </article>

      <article class="panel chat-panel">
        <div class="panel-heading">
          <div>
            <h2>RAG 問答</h2>
            <p>POST /rag/query</p>
          </div>
          <span class="status-pill" :class="`status-${chatState}`">{{ displayRequestState(chatState) }}</span>
        </div>

        <form class="chat-form" @submit.prevent="submitRagQuery">
          <label>
            <span>問題</span>
            <textarea v-model="ragQuery" rows="3" placeholder="例如：付款期限是 Net 15 嗎？" />
          </label>

          <label>
            <span>候選數 Top K</span>
            <input v-model.number="ragTopK" type="number" min="1" max="10" />
          </label>

          <button type="submit" class="button" :disabled="chatState === 'loading'">
            {{ chatState === "loading" ? "查詢中..." : "詢問 RAG" }}
          </button>
        </form>

        <p v-if="ragError" class="error">{{ ragError }}</p>

        <section v-if="ragResult" class="rag-result">
          <div class="answer-heading">
            <h3>回答</h3>
            <div class="answer-badges">
              <span class="status-pill" :class="ragAnswerSourceClass">{{ ragAnswerSource }}</span>
              <span class="status-pill" :class="ragRetrievalSourceClass">{{ ragRetrievalSource }}</span>
            </div>
          </div>
          <pre class="answer-text">{{ ragResult.answer }}</pre>

          <section class="trace-panel" aria-label="檢索追蹤">
            <h3>檢索追蹤</h3>
            <dl class="trace-facts">
              <div v-for="fact in ragTraceFacts" :key="fact.label">
                <dt>{{ fact.label }}</dt>
                <dd :class="fact.tone ? `trace-${fact.tone}` : ''">{{ fact.value }}</dd>
              </div>
            </dl>

            <div v-if="ragTraceRows.length" class="trace-table-wrap">
              <table class="trace-table">
                <thead>
                  <tr>
                    <th>排名</th>
                    <th>分數</th>
                    <th>來源</th>
                    <th>候選內容</th>
                    <th>追蹤</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in ragTraceRows" :key="`${row.documentId}-${row.chunkId}`">
                    <td>{{ row.rank }}</td>
                    <td>{{ row.score }}</td>
                    <td>
                      <strong>{{ row.filename }}</strong>
                      <code>{{ row.documentId }}</code>
                      <code>{{ row.chunkId }}</code>
                    </td>
                    <td class="trace-preview">{{ row.preview }}</td>
                    <td>
                      <div class="trace-summary">
                        <code v-for="item in row.traceSummary" :key="`${row.chunkId}-${item}`">{{ item }}</code>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="muted">無中繼資料</p>
          </section>

          <h3>引用來源</h3>
          <ul v-if="ragResult.citations.length" class="citation-list">
            <li v-for="citation in ragResult.citations" :key="`${citation.document_id}-${citation.chunk_id}`">
              <span>{{ citation.filename }}</span>
              <code>{{ citation.document_id }}</code>
              <code>{{ citation.chunk_id }}</code>
              <code v-if="citation.source_type">{{ citation.source_type }}</code>
              <code v-if="citation.page_number">頁 {{ citation.page_number }}</code>
              <code v-if="citation.confidence != null">信心 {{ citation.confidence }}</code>
              <code v-if="citation.bbox">{{ formatBbox(citation.bbox) }}</code>
              <code v-for="[key, value] in metadataEntries(citation.trace_metadata)" :key="`${citation.chunk_id}-${key}`">
                {{ key }}={{ value }}
              </code>
            </li>
          </ul>
          <p v-else class="muted">沒有引用來源。</p>

          <h3>檢索片段</h3>
          <div v-if="ragResult.retrieved_chunks.length" class="chunk-list">
            <article v-for="chunk in ragResult.retrieved_chunks" :key="chunk.chunk_id" class="chunk-item">
              <div class="chunk-meta">
                <span>{{ chunk.filename }}</span>
                <code>{{ chunk.chunk_id }}</code>
                <span v-if="chunk.source_type">{{ chunk.source_type }}</span>
                <span v-if="chunk.page_number">頁 {{ chunk.page_number }}</span>
                <span v-if="chunk.confidence != null">信心 {{ chunk.confidence }}</span>
                <span v-if="chunk.bbox">{{ formatBbox(chunk.bbox) }}</span>
                <span>分數 {{ chunk.score }}</span>
              </div>
              <div v-if="metadataEntries(chunk.metadata).length" class="chunk-meta trace-meta">
                <code v-for="[key, value] in metadataEntries(chunk.metadata)" :key="`${chunk.chunk_id}-${key}`">
                  {{ key }}={{ value }}
                </code>
              </div>
              <pre>{{ chunk.text }}</pre>
            </article>
          </div>
          <p v-else class="muted">沒有檢索片段。</p>
        </section>

        <p v-else class="muted">請先上傳文件並執行 OCR，再輸入問題。</p>
      </article>

      <article class="panel response-panel">
        <div class="panel-heading">
          <div>
            <h2>文件中繼資料 JSON</h2>
            <p>GET /documents/{{ "{document_id}" }}</p>
          </div>
        </div>
        <p v-if="detailError" class="error">{{ detailError }}</p>
        <pre>{{ selectedDocumentJson }}</pre>
      </article>

      <article class="panel response-panel">
        <div class="panel-heading">
          <div>
            <h2>API 回應 JSON</h2>
            <p>最新 API 回應</p>
          </div>
        </div>
        <pre>{{ latestResponseJson }}</pre>
      </article>
    </section>
  </main>
</template>
