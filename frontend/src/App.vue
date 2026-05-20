<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  API_BASE_URL,
  getHealth,
  uploadDocument,
  type HealthResponse,
  type UploadResponse,
} from "./api/client";

type RequestState = "idle" | "loading" | "success" | "error";

const healthState = ref<RequestState>("idle");
const uploadState = ref<RequestState>("idle");
const health = ref<HealthResponse | null>(null);
const uploadResult = ref<UploadResponse | null>(null);
const selectedFile = ref<File | null>(null);
const healthError = ref("");
const uploadError = ref("");
const latestResponse = ref<HealthResponse | UploadResponse | null>(null);

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
  } catch (error) {
    uploadResult.value = null;
    uploadError.value = error instanceof Error ? error.message : "Upload failed";
    uploadState.value = "error";
  }
}

onMounted(() => {
  void checkHealth();
});
</script>

<template>
  <main class="page">
    <header class="hero">
      <p class="eyebrow">v0.2.0 Demo UI</p>
      <h1>DocuRAG AgentOps</h1>
      <p class="hero-copy">Backend health 與 document upload stub 驗證。</p>
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
            <p>Backend stub metadata</p>
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
            <dd>{{ uploadResult.size }} bytes</dd>
          </div>
        </dl>

        <p v-else class="muted">尚未上傳檔案。</p>
      </article>

      <article class="panel response-panel">
        <div class="panel-heading">
          <div>
            <h2>API response JSON</h2>
            <p>GET /health 或 POST /documents/upload</p>
          </div>
        </div>
        <pre>{{ latestResponseJson }}</pre>
      </article>
    </section>
  </main>
</template>
