<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  API_BASE_URL,
  getHealth,
  queryRag,
  runMockOcr,
  runSelectedOcr,
  uploadDocument,
  type HealthResponse,
  type RagQueryResponse,
  type UploadResponse,
} from "./api/client";

type RequestState = "idle" | "loading" | "success" | "error";

type SourceSummary = {
  filename: string;
  chunkIds: string[];
};

const healthState = ref<RequestState>("idle");
const chatState = ref<RequestState>("idle");
const uploadState = ref<RequestState>("idle");
const health = ref<HealthResponse | null>(null);
const ragResult = ref<RagQueryResponse | null>(null);
const uploadResult = ref<UploadResponse | null>(null);
const selectedFile = ref<File | null>(null);
const uploadFallbackAvailable = ref(false);
const ragQuery = ref("");
const ragTopK = ref(3);
const healthError = ref("");
const ragError = ref("");
const uploadError = ref("");
const uploadMessage = ref("");

const suggestedQuestions = [
  "payment due date Net 15",
  "What is the SLA response target?",
  "When is the renewal date?",
];

const currentVersionLabel = computed(() => (health.value?.version ? `v${health.value.version}` : "v0.21.0"));

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

function sourceTone(source: string): "status-failed" | "status-ready" | "status-success" {
  if (source.includes("備援") || source.includes("不可用")) {
    return "status-failed";
  }

  if (source.includes("基準")) {
    return "status-ready";
  }

  return "status-success";
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
      return;
    }

    uploadMessage.value = "文件已完成 GPU OCR，並送入 demo 知識庫。";
    uploadState.value = "success";
  } catch (error) {
    uploadFallbackAvailable.value = true;
    uploadError.value = error instanceof Error ? `GPU OCR 未完成：${error.message}` : "GPU OCR 未完成";
    uploadState.value = "error";
  }
}

async function submitMockFallback(): Promise<void> {
  if (!uploadResult.value) {
    uploadError.value = "請先上傳文件。";
    return;
  }

  uploadState.value = "loading";
  uploadError.value = "";
  uploadMessage.value = "";

  try {
    await runMockOcr(uploadResult.value.document_id);
    uploadFallbackAvailable.value = false;
    uploadMessage.value = "已改用 mock OCR 完成 demo 備援處理。";
    uploadState.value = "success";
  } catch (error) {
    uploadError.value = error instanceof Error ? `Mock OCR 備援失敗：${error.message}` : "Mock OCR 備援失敗";
    uploadState.value = "error";
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
          <p class="hero-copy">
            前台只負責提問與上傳文件；其餘知識庫流程都由後端處理。
          </p>
        </div>

        <div class="hero-side">
          <span>服務狀態</span>
          <strong>{{ healthLabel }}</strong>
          <small>{{ health?.version ? `Backend ${health.version}` : API_BASE_URL }}</small>
        </div>
      </div>
    </header>

    <section class="minimal-grid" aria-label="文件客服入口">
      <article class="panel chat-surface">
        <div class="panel-heading">
          <div>
            <h2>問問題</h2>
            <p>詢問後端已建立的文件知識庫。</p>
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
            <p v-else class="muted">沒有引用來源。</p>
          </div>
        </section>

        <p v-else class="muted">請輸入問題。若尚未有資料，先在右側上傳公開 sample 文件。</p>
      </article>

      <article class="panel upload-surface">
        <div class="panel-heading">
          <div>
            <h2>上傳文件</h2>
            <p>文件送出後由後端 GPU OCR 建立 demo 知識庫。</p>
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

        <button
          type="button"
          class="button upload-button"
          :disabled="!selectedFile || uploadState === 'loading'"
          @click="submitUpload"
        >
          {{ uploadState === "loading" ? "後端處理中..." : "上傳並跑 GPU OCR" }}
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
          改用 mock OCR 備援
        </button>

        <dl v-if="uploadResult" class="upload-summary">
          <div>
            <dt>檔名</dt>
            <dd>{{ uploadResult.filename }}</dd>
          </div>
          <div>
            <dt>狀態</dt>
            <dd>{{ uploadFallbackAvailable ? "GPU OCR 待處理" : "已送入後端知識庫流程" }}</dd>
          </div>
        </dl>
      </article>
    </section>

    <p v-if="healthError" class="error footer-error">{{ healthError }}</p>
  </main>
</template>
