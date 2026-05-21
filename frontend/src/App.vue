<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  API_BASE_URL,
  getDocument,
  getHealth,
  getOcrResult,
  listDocuments,
  runMockOcr,
  uploadDocument,
  type DocumentListResponse,
  type DocumentMetadata,
  type HealthResponse,
  type OcrResultResponse,
  type UploadResponse,
} from "./api/client";

type RequestState = "idle" | "loading" | "success" | "error";

const healthState = ref<RequestState>("idle");
const documentsState = ref<RequestState>("idle");
const detailState = ref<RequestState>("idle");
const ocrState = ref<RequestState>("idle");
const uploadState = ref<RequestState>("idle");
const health = ref<HealthResponse | null>(null);
const documents = ref<DocumentMetadata[]>([]);
const selectedDocument = ref<DocumentMetadata | null>(null);
const uploadResult = ref<UploadResponse | null>(null);
const selectedFile = ref<File | null>(null);
const healthError = ref("");
const documentsError = ref("");
const detailError = ref("");
const ocrError = ref("");
const uploadError = ref("");
const latestResponse = ref<
  DocumentListResponse | DocumentMetadata | HealthResponse | OcrResultResponse | UploadResponse | null
>(null);

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
    selectedDocument.value = {
      ...selectedDocument.value,
      status: "ready",
      ocr: response,
    };
    documents.value = documents.value.map((document) =>
      document.document_id === documentId
        ? { ...document, status: "ready", ocr: response }
        : document,
    );
    latestResponse.value = response;
    ocrState.value = "success";
  } catch (error) {
    ocrError.value = error instanceof Error ? error.message : "Run OCR failed";
    ocrState.value = "error";
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
      <p class="eyebrow">v0.4.0 OCR Mock Pipeline</p>
      <h1>DocuRAG AgentOps</h1>
      <p class="hero-copy">Backend health、本機文件上傳、metadata 保存、文件列表與 mock OCR 驗證。</p>
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
            <p>POST /documents/{{ "{document_id}" }}/ocr/mock</p>
          </div>
          <button
            type="button"
            class="button secondary-button"
            :disabled="!selectedDocument || ocrState === 'loading'"
            @click="runOcrForSelectedDocument"
          >
            {{ ocrState === "loading" ? "Running..." : "Run Mock OCR" }}
          </button>
        </div>

        <p v-if="ocrError" class="error">{{ ocrError }}</p>

        <dl v-if="selectedDocument" class="facts">
          <div>
            <dt>OCR status</dt>
            <dd>
              <span class="status-pill" :class="statusClass(selectedDocument.ocr.status)">
                {{ selectedDocument.ocr.status }}
              </span>
            </dd>
          </div>
          <div>
            <dt>Updated at</dt>
            <dd>{{ selectedDocument.ocr.updated_at ?? "Not run" }}</dd>
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
