# Phase 02 - Document Demo Workflow

## Goal

建立文件平台主流程的 thin slice，但先使用 sample / fixture，不接完整 OCR、RAG、Qdrant、Redis、NATS。

## Completion Criteria

- 可以在 UI 看到 document list。
- 可以建立 document metadata 或上傳 placeholder file。
- Document detail 可以顯示 sample OCR text、extracted fields、chunks。
- Chat 頁可以回傳 demo answer + citation + trace。
- Eval 頁可以顯示 sample metrics。

## Tickets

### P02-T01 - Document metadata API

- Goal：建立文件列表能力。
- Scope：document model、list、create metadata。
- Out of Scope：真 OCR、真 storage。
- Files likely to change：`backend/app/api/documents.py`、`backend/app/services/document_service.py`、`backend/app/schemas/*`。
- Acceptance Criteria：可建立 uploaded document。
- Validation：API test。

### P02-T02 - Document frontend list

- Goal：顯示文件工作流入口。
- Scope：Documents page、status badge、project filter。
- Out of Scope：真檔案預覽。
- Files likely to change：`frontend/src/pages/Documents.vue`、`frontend/src/api/documents.ts`。
- Acceptance Criteria：文件列表顯示狀態。
- Validation：Manual browser check。

### P02-T03 - Sample document detail API

- Goal：用 fixture 展示 OCR / fields / chunks。
- Scope：detail、pages、fields、chunks demo data。
- Out of Scope：parser、Qdrant。
- Files likely to change：`backend/app/api/documents.py`、`sample-data/documents/*`。
- Acceptance Criteria：API 回傳 sample OCR 與 fields。
- Validation：API test。

### P02-T04 - Document detail page

- Goal：展示文件解析結果。
- Scope：OCR text、fields、chunks 三區塊。
- Out of Scope：人工修正儲存。
- Files likely to change：`frontend/src/pages/DocumentDetail.vue`、`frontend/src/api/documents.ts`。
- Acceptance Criteria：可看 sample OCR / fields / chunks。
- Validation：Manual browser check。

### P02-T05 - Demo chat API with citation

- Goal：建立 RAG 展示介面。
- Scope：chat endpoint 回傳 fixture answer / citation / trace。
- Out of Scope：embedding、rerank、LLM。
- Files likely to change：`backend/app/api/chat.py`、`backend/app/services/chat_service.py`。
- Acceptance Criteria：回答必含 citation 與 trace。
- Validation：API test。

### P02-T06 - Chat page

- Goal：展示問答與引用。
- Scope：Chat UI、citation cards、trace panel。
- Out of Scope：streaming。
- Files likely to change：`frontend/src/pages/Chat.vue`、`frontend/src/api/chat.ts`。
- Acceptance Criteria：可送問題並顯示 citation。
- Validation：Manual browser check。

### P02-T07 - Sample eval metrics API

- Goal：展示 RAG 評估能力。
- Scope：eval dataset fixture、metrics response。
- Out of Scope：真 retrieval eval。
- Files likely to change：`backend/app/api/eval.py`、`backend/app/services/eval_service.py`、`sample-data/eval/*`。
- Acceptance Criteria：回傳 Hit Rate / MRR / Recall / Latency。
- Validation：API test。

### P02-T08 - Eval page

- Goal：展示策略比較。
- Scope：metrics table、failure cases。
- Out of Scope：batch runner。
- Files likely to change：`frontend/src/pages/Eval.vue`、`frontend/src/api/eval.ts`。
- Acceptance Criteria：UI 可看策略比較表。
- Validation：Manual browser check。
