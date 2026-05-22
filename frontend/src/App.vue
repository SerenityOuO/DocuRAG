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
  type UploadResponse,
} from "./api/client";

type RequestState = "idle" | "loading" | "success" | "error";

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

const currentVersionLabel = computed(() => (health.value?.version ? `v${health.value.version}` : "v0.8.0"));

const healthLabel = computed(() => {
  if (healthState.value === "success" && health.value?.status === "ok") {
    return "Backend online";
  }

  if (healthState.value === "loading") {
    return "Checking";
  }

  if (healthState.value === "error") {
    return "Unavailable";
  }

  return "Not checked";
});

const latestResponseJson = computed(() =>
  latestResponse.value ? JSON.stringify(latestResponse.value, null, 2) : "尚未取得 API response。",
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

function formatBytes(size: number): string {
  return `${size.toLocaleString()} bytes`;
}

function statusClass(status: string): string {
  return `status-${status.replace(/_/g, "-")}`;
}

function formatBbox(bbox: BoundingBox): string {
  return `bbox ${bbox.x_min},${bbox.y_min},${bbox.x_max},${bbox.y_max}`;
}

function metadataEntries(metadata: Record<string, string>): [string, string][] {
  return Object.entries(metadata);
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
    healthError.value = error instanceof Error ? error.message : "Health check failed";
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
    documentsError.value = error instanceof Error ? error.message : "Load documents failed";
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
    detailError.value = error instanceof Error ? error.message : "Load document failed";
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
    ocrError.value = error instanceof Error ? error.message : "Run OCR failed";
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
      // Keep the original API error visible when refreshing failed metadata is unavailable.
    }

    ocrError.value = error instanceof Error ? error.message : "Run selected OCR failed";
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
    ragError.value = error instanceof Error ? error.message : "RAG query failed";
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
    uploadError.value = error instanceof Error ? error.message : "Upload failed";
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
      <p class="eyebrow">{{ currentVersionLabel }}</p>
      <h1>DocuRAG AgentOps</h1>
      <p class="hero-copy">
        Backend health、本機文件上傳、metadata 保存、PaddleOCR default provider、mock override、local keyword RAG
        與 citation trace 驗證。
      </p>
    </header>

    <section class="layout" aria-label="Demo controls">
      <article class="panel">
        <div class="panel-heading">
          <div>
            <h2>Backend health</h2>
            <p>GET /health</p>
          </div>
          <span class="status-pill" :class="`status-${healthState}`">{{ healthLabel }}</span>
        </div>

        <dl v-if="health" class="facts">
          <div>
            <dt>Service</dt>
            <dd>{{ health.service }}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{{ health.status }}</dd>
          </div>
          <div>
            <dt>Version</dt>
            <dd>{{ health.version }}</dd>
          </div>
        </dl>

        <p v-if="healthError" class="error">{{ healthError }}</p>
        <p class="api-base">API base URL: {{ API_BASE_URL }}</p>

        <button type="button" class="button" :disabled="healthState === 'loading'" @click="checkHealth">
          {{ healthState === "loading" ? "Checking..." : "Refresh health" }}
        </button>
      </article>

      <article class="panel">
        <div class="panel-heading">
          <div>
            <h2>Upload document</h2>
            <p>POST /documents/upload</p>
          </div>
        </div>

        <label class="file-picker">
          <span>Select file</span>
          <input type="file" @change="handleFileChange" />
        </label>

        <p v-if="selectedFile" class="selected-file">
          {{ selectedFile.name }} - {{ selectedFile.size }} bytes
        </p>
        <p v-else class="muted">尚未選擇檔案。</p>

        <p v-if="uploadError" class="error">{{ uploadError }}</p>

        <button
          type="button"
          class="button"
          :disabled="!selectedFile || uploadState === 'loading'"
          @click="submitUpload"
        >
          {{ uploadState === "loading" ? "Uploading..." : "Upload to backend" }}
        </button>
      </article>

      <article class="panel">
        <div class="panel-heading">
          <div>
            <h2>Upload result</h2>
            <p>Latest saved metadata</p>
          </div>
          <span v-if="uploadResult" class="status-pill status-success">{{ uploadResult.status }}</span>
        </div>

        <dl v-if="uploadResult" class="facts">
          <div>
            <dt>Document ID</dt>
            <dd>{{ uploadResult.document_id }}</dd>
          </div>
          <div>
            <dt>Filename</dt>
            <dd>{{ uploadResult.filename }}</dd>
          </div>
          <div>
            <dt>Content type</dt>
            <dd>{{ uploadResult.content_type }}</dd>
          </div>
          <div>
            <dt>Size</dt>
            <dd>{{ formatBytes(uploadResult.size) }}</dd>
          </div>
        </dl>

        <p v-else class="muted">尚未上傳檔案。</p>
      </article>

      <article class="panel documents-panel">
        <div class="panel-heading">
          <div>
            <h2>Documents</h2>
            <p>GET /documents</p>
          </div>
          <button
            type="button"
            class="button secondary-button"
            :disabled="documentsState === 'loading'"
            @click="refreshDocuments"
          >
            {{ documentsState === "loading" ? "Loading..." : "Refresh list" }}
          </button>
        </div>

        <p v-if="documentsError" class="error">{{ documentsError }}</p>

        <div v-if="documents.length" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Filename</th>
                <th>Status</th>
                <th>OCR</th>
                <th>Indexing</th>
                <th>Latest job</th>
                <th>Size</th>
                <th>Created at</th>
                <th>Content type</th>
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
                <td><span class="status-pill" :class="statusClass(document.status)">{{ document.status }}</span></td>
                <td><span class="status-pill" :class="statusClass(document.ocr.status)">{{ document.ocr.status }}</span></td>
                <td>
                  <span class="status-pill" :class="statusClass(document.processing.indexing)">
                    {{ document.processing.indexing }}
                  </span>
                </td>
                <td>
                  <span v-if="document.latest_job" class="status-pill" :class="statusClass(document.latest_job.status)">
                    {{ document.latest_job.job_type }} / {{ document.latest_job.status }}
                  </span>
                  <span v-else class="muted">none</span>
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
            <h2>OCR result</h2>
            <p>Default /ocr provider: PaddleOCR；mock override: /ocr/mock</p>
          </div>
          <div class="button-row">
            <button
              type="button"
              class="button secondary-button"
              :disabled="!selectedDocument || ocrState === 'loading'"
              @click="runOcrForSelectedDocument"
            >
              {{ ocrState === "loading" ? "Running..." : "Run Mock Override" }}
            </button>
            <button
              type="button"
              class="button"
              :disabled="!selectedDocument || ocrState === 'loading'"
              @click="runSelectedOcrForSelectedDocument"
            >
              {{ ocrState === "loading" ? "Running..." : "Run Selected OCR" }}
            </button>
          </div>
        </div>

        <p v-if="ocrError" class="error">{{ ocrError }}</p>

        <dl v-if="selectedDocument" class="facts">
          <div>
            <dt>Document status</dt>
            <dd>
              <span class="status-pill" :class="statusClass(selectedDocument.status)">
                {{ selectedDocument.status }}
              </span>
            </dd>
          </div>
          <div>
            <dt>OCR status</dt>
            <dd>
              <span class="status-pill" :class="statusClass(selectedDocument.ocr.status)">
                {{ selectedDocument.ocr.status }}
              </span>
            </dd>
          </div>
          <div>
            <dt>Indexing status</dt>
            <dd>
              <span class="status-pill" :class="statusClass(selectedDocument.processing.indexing)">
                {{ selectedDocument.processing.indexing }}
              </span>
            </dd>
          </div>
          <div>
            <dt>Ready</dt>
            <dd>{{ selectedDocument.processing.ready ? "yes" : "no" }}</dd>
          </div>
          <div v-if="selectedDocument.processing.failed_reason">
            <dt>Failed reason</dt>
            <dd>{{ selectedDocument.processing.failed_reason }}</dd>
          </div>
          <div v-if="selectedDocument.latest_job">
            <dt>Latest job</dt>
            <dd>
              {{ selectedDocument.latest_job.job_type }} / {{ selectedDocument.latest_job.status }}
            </dd>
          </div>
          <div>
            <dt>Updated at</dt>
            <dd>{{ selectedDocument.processing.updated_at ?? selectedDocument.ocr.updated_at ?? "Not run" }}</dd>
          </div>
        </dl>

        <div v-if="selectedDocument" class="ocr-grid">
          <section>
            <h3>OCR text</h3>
            <pre class="ocr-text">{{ selectedOcrText }}</pre>
          </section>

          <section>
            <h3>Extracted fields</h3>
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
            <h2>RAG chat</h2>
            <p>POST /rag/query</p>
          </div>
          <span class="status-pill" :class="`status-${chatState}`">{{ chatState }}</span>
        </div>

        <form class="chat-form" @submit.prevent="submitRagQuery">
          <label>
            <span>Query</span>
            <textarea v-model="ragQuery" rows="3" placeholder="例如：payment due date Net 15" />
          </label>

          <label>
            <span>Top K</span>
            <input v-model.number="ragTopK" type="number" min="1" max="10" />
          </label>

          <button type="submit" class="button" :disabled="chatState === 'loading'">
            {{ chatState === "loading" ? "Querying..." : "Ask RAG" }}
          </button>
        </form>

        <p v-if="ragError" class="error">{{ ragError }}</p>

        <section v-if="ragResult" class="rag-result">
          <h3>Answer</h3>
          <pre class="answer-text">{{ ragResult.answer }}</pre>

          <h3>Citations</h3>
          <ul v-if="ragResult.citations.length" class="citation-list">
            <li v-for="citation in ragResult.citations" :key="`${citation.document_id}-${citation.chunk_id}`">
              <span>{{ citation.filename }}</span>
              <code>{{ citation.document_id }}</code>
              <code>{{ citation.chunk_id }}</code>
              <code v-if="citation.source_type">{{ citation.source_type }}</code>
              <code v-if="citation.page_number">page {{ citation.page_number }}</code>
              <code v-if="citation.confidence != null">conf {{ citation.confidence }}</code>
              <code v-if="citation.bbox">{{ formatBbox(citation.bbox) }}</code>
              <code v-for="[key, value] in metadataEntries(citation.trace_metadata)" :key="`${citation.chunk_id}-${key}`">
                {{ key }}={{ value }}
              </code>
            </li>
          </ul>
          <p v-else class="muted">沒有 citation。</p>

          <h3>Retrieved chunks</h3>
          <div v-if="ragResult.retrieved_chunks.length" class="chunk-list">
            <article v-for="chunk in ragResult.retrieved_chunks" :key="chunk.chunk_id" class="chunk-item">
              <div class="chunk-meta">
                <span>{{ chunk.filename }}</span>
                <code>{{ chunk.chunk_id }}</code>
                <span v-if="chunk.source_type">{{ chunk.source_type }}</span>
                <span v-if="chunk.page_number">page {{ chunk.page_number }}</span>
                <span v-if="chunk.confidence != null">confidence {{ chunk.confidence }}</span>
                <span v-if="chunk.bbox">{{ formatBbox(chunk.bbox) }}</span>
                <span>score {{ chunk.score }}</span>
              </div>
              <div v-if="metadataEntries(chunk.metadata).length" class="chunk-meta trace-meta">
                <code v-for="[key, value] in metadataEntries(chunk.metadata)" :key="`${chunk.chunk_id}-${key}`">
                  {{ key }}={{ value }}
                </code>
              </div>
              <pre>{{ chunk.text }}</pre>
            </article>
          </div>
          <p v-else class="muted">沒有 retrieved chunk。</p>
        </section>

        <p v-else class="muted">請先上傳文件並執行 OCR，再輸入問題。</p>
      </article>

      <article class="panel response-panel">
        <div class="panel-heading">
          <div>
            <h2>Document metadata JSON</h2>
            <p>GET /documents/{{ "{document_id}" }}</p>
          </div>
        </div>
        <p v-if="detailError" class="error">{{ detailError }}</p>
        <pre>{{ selectedDocumentJson }}</pre>
      </article>

      <article class="panel response-panel">
        <div class="panel-heading">
          <div>
            <h2>API response JSON</h2>
            <p>Latest API response</p>
          </div>
        </div>
        <pre>{{ latestResponseJson }}</pre>
      </article>
    </section>
  </main>
</template>
