# goal.md — DocuRAG AgentOps PRD 規格說明書

## 0. 文件資訊

| 欄位 | 內容 |
|---|---|
| 專案名稱 | DocuRAG AgentOps |
| 文件類型 | PRD / Product Requirement Document |
| 目標用途 | 面試展示用 Side Project，可放置於 GitHub |
| 主要定位 | 企業級文件解析、RAG 評估與 AI Agent 平台 |
| 目標職能 | AI Software Engineer / AI Application Engineer / RAG Engineer / LLMOps Engineer |
| 技術主軸 | RAG、OCR/VLM、Rerank、Agent、FastAPI、Vue3、Qdrant、Redis、NATS、vLLM、Docker/K8s |
| MVP 版本 | v0.1 |
| 文件狀態 | Draft |

---

## 1. 專案背景

企業內部常有大量非結構化或半結構化文件，例如發票、報價單、合約、檢測報告、規格書、SOP、財務表單與掃描 PDF。這些文件通常存在以下問題：

1. 內容分散於 PDF、圖片、掃描檔與表格中，難以直接查詢。
2. OCR 後的文字缺少結構化欄位，無法直接進入資料庫分析。
3. 一般 RAG Chatbot 只能回答問題，缺乏檢索品質評估與錯誤分析。
4. 企業應用需要多使用者、權限控管、日誌、非同步任務與部署維運能力。
5. 實務上需要知道 RAG 為什麼答對、為什麼答錯，以及不同 chunking / indexing / rerank 策略的量化差異。

因此本專案設計為一套可展示完整 AI 工程能力的文件智能平台，從文件上傳、OCR/VLM 解析、向量索引、RAG 問答、Rerank 評估、Agent 工具調用，到 Docker 部署與系統監控，形成一個可展示、可驗證、可擴充的 Side Project。

---

## 2. 專案願景

DocuRAG AgentOps 的目標不是建立一個單純的 RAG Chatbot，而是建立一個接近企業實務情境的 AI 文件平台。

使用者可以上傳文件或單據，系統會自動解析內容、抽取欄位、建立檢索索引，並提供具來源引用的問答服務。開發者與管理者可以透過評估模組比較不同 RAG 策略的效果，例如 Dense Search、Hybrid Search、Rerank 前後差異，以及不同 chunking 策略對 Hit Rate 與 MRR 的影響。

---

## 3. 專案目標

### 3.1 產品目標

1. 支援文件上傳、OCR 解析與 VLM 結構化欄位抽取。
2. 建立可追蹤來源的 RAG 問答系統。
3. 支援 Qdrant 向量資料庫與 metadata filtering。
4. 實作 Dense Search、Hybrid Search 與 Rerank 流程。
5. 建立 RAG 評估模組，量化 Hit Rate、MRR、Recall@K、Latency。
6. 建立 AI Agent，可根據任務自動選擇工具。
7. 支援多使用者與 RBAC 權限管理。
8. 使用 Redis 處理 session、cache 與 rate limit。
9. 使用 NATS 建立非同步任務架構。
10. 支援 vLLM / Ollama / OpenAI-compatible endpoint 作為推論後端。
11. 採用可替換的 LLM / VLM / Embedding / Reranker / OCR 模型組合，不綁定單一模型供應商。
12. 提供 Docker Compose 一鍵啟動與基本 K8s 部署範例。
13. 產出完整 GitHub README、架構圖、API 文件、評估報告與 Demo 資料。

### 3.2 面試展示目標

本專案應讓面試官在 5 至 10 分鐘內看出以下能力：

| 能力 | 展示方式 |
|---|---|
| RAG 架構能力 | 文件切分、Embedding、Qdrant indexing、RAG trace |
| RAG 評估能力 | Hit Rate、MRR、Recall@K、策略比較表 |
| OCR / VLM 能力 | 單據解析成 JSON schema |
| Agent 能力 | Tool-use、Task Planning、任務 trace |
| 後端工程能力 | FastAPI、RESTful API、async worker |
| 系統設計能力 | Multi-user、RBAC、PostgreSQL schema |
| 分散式通訊能力 | NATS event-driven worker |
| 快取與高併發概念 | Redis session / cache / rate limit |
| 推論維運能力 | vLLM / Ollama、KV Cache 估算、latency log |
| 部署能力 | Docker Compose、K8s manifests |

---

## 4. 目標使用者

### 4.1 Admin

系統管理者，負責組織、使用者、角色、模型與系統狀態管理。

主要需求：

- 管理使用者與角色。
- 查看所有專案狀態。
- 查看任務佇列與錯誤日誌。
- 設定模型 endpoint。
- 監控系統查詢量與延遲。

### 4.2 Manager

專案管理者，負責文件專案、評估結果與資料品質。

主要需求：

- 建立專案。
- 管理文件。
- 查看 OCR / RAG 評估結果。
- 比較不同檢索策略。
- 匯出報告。

### 4.3 Analyst

一般分析人員，負責上傳文件、查詢資料與修正解析結果。

主要需求：

- 上傳 PDF / 圖片。
- 查看 OCR 與 VLM 抽取結果。
- 人工修正欄位。
- 使用 RAG Chat 查詢文件內容。
- 查看回答引用來源。

### 4.4 Viewer

只讀使用者，只能查詢與查看文件。

主要需求：

- 使用 RAG Chat。
- 查看文件與引用來源。
- 不可上傳、刪除、修改資料。

---

## 5. 使用情境

### 5.1 單據解析情境

使用者上傳發票或報價單後，系統自動解析：

- 供應商名稱
- 發票號碼
- 日期
- 總金額
- 稅額
- 幣別
- 品項列表
- 數量
- 單價
- 小計

使用者可在 UI 查看原始圖片、OCR 文字、VLM JSON 結果與欄位信心分數，並可人工修正錯誤欄位。

### 5.2 合約問答情境

使用者上傳合約 PDF 後詢問：

> 這份合約的付款條件、違約金與保密義務是什麼？

系統會檢索相關條文、使用 Reranker 排序、產生回答，並附上來源頁碼與原文片段。

### 5.3 財務文件查詢情境

使用者詢問：

> 找出 2025 年 12 月金額超過 50,000 元的單據，並列出供應商、發票號碼與總金額。

Agent 會選擇 SQL 查詢工具與文件檢索工具，產生表格化答案，並附上來源文件。

### 5.4 RAG 評估情境

開發者建立評估資料集，針對不同策略執行測試：

- Dense Search
- Hybrid Search
- Dense + Rerank
- Hybrid + Rerank
- Fixed-size Chunking
- Semantic Chunking
- Parent-child Chunking

系統輸出 Hit Rate@K、MRR@K、Recall@K、平均延遲與失敗案例。

---

## 6. 功能範圍

## 6.1 MVP 必做功能

### F-001 使用者登入與 RBAC 權限

系統需支援帳號登入與角色權限控管。

角色定義：

| 角色 | 權限 |
|---|---|
| Admin | 所有管理權限 |
| Manager | 管理專案、文件與評估結果 |
| Analyst | 上傳文件、查詢、修正欄位 |
| Viewer | 查詢與只讀 |

驗收標準：

- 使用者可以登入與登出。
- 不同角色看到不同功能入口。
- Viewer 無法上傳、刪除或重新索引文件。
- API 層需檢查使用者角色與 project access。

---

### F-002 專案管理

系統需支援多專案管理。

功能：

- 建立 project。
- 查看 project list。
- 切換 project。
- 每個 project 對應獨立文件、chunks、eval dataset。
- API 查詢需依 `organization_id` 與 `project_id` 過濾資料。

驗收標準：

- 使用者只能看到自己 organization 下的 projects。
- 不同 project 的文件不可互相查詢。
- 向量搜尋需支援 metadata filtering。

---

### F-003 文件上傳

系統需支援以下格式：

- PDF
- JPG
- PNG
- TXT

功能：

- 上傳文件。
- 儲存原始檔案。
- 建立 document record。
- 顯示文件處理狀態。
- 發送非同步 OCR 任務。
- TXT / text-native 文件可直接進入文字切分與索引流程，不需 OCR。
- PDF 需區分 text-native PDF 與 scanned PDF；scanned PDF 需先完成 PDF rendering / OCR pipeline。

文件狀態：

| 狀態 | 說明 |
|---|---|
| uploaded | 已上傳 |
| ocr_processing | OCR 處理中 |
| ocr_completed | OCR 完成 |
| parsing | VLM / Parser 處理中 |
| parsed | 欄位解析完成 |
| indexing | 建立索引中 |
| indexed | 可查詢 |
| failed | 處理失敗 |

驗收標準：

- 上傳成功後可在文件列表看到該文件。
- 系統會自動建立 OCR 任務。
- UI 顯示當前處理狀態。
- 失敗時需顯示錯誤原因。

---

### F-004 OCR 文字解析

系統需將文件圖片或 PDF 轉成可檢索文字。

功能：

- text-native PDF 文字抽取。
- PDF 轉頁面圖片。
- 圖片 OCR。
- 儲存每頁 OCR 文字。
- 儲存文字區塊座標。
- UI 顯示 OCR 原文。

建議工具：

- PaddleOCR
- Tesseract
- EasyOCR

驗收標準：

- 可對至少 5 份 sample documents 產生 OCR 文字。
- OCR 結果可在 UI 查看。
- OCR 結果需寫入資料庫。
- OCR 完成後自動觸發解析任務。

---

### F-005 VLM / Parser 結構化抽取

系統需將 OCR 原文或圖片內容轉成結構化 JSON。

第一版支援三種文件類型：

| 類型 | 說明 |
|---|---|
| invoice | 發票 / 收據 / 單據 |
| contract | 合約 |
| report | 報告 / 規格書 |

invoice schema：

```json
{
  "document_type": "invoice",
  "vendor_name": "string",
  "invoice_number": "string",
  "issue_date": "date",
  "total_amount": "number",
  "tax_amount": "number",
  "currency": "string",
  "line_items": [
    {
      "name": "string",
      "quantity": "number",
      "unit_price": "number",
      "subtotal": "number"
    }
  ]
}
```

contract schema：

```json
{
  "document_type": "contract",
  "parties": ["string"],
  "effective_date": "date",
  "payment_terms": "string",
  "termination_clause": "string",
  "confidentiality_clause": "string",
  "penalty_clause": "string"
}
```

驗收標準：

- 上傳 invoice sample 後可產生 JSON 欄位。
- UI 可顯示欄位、信心分數與來源頁碼。
- 使用者可人工修正欄位。
- 修正後的資料需保留 version 或 audit log。

---

### F-006 Chunking 與 Indexing

系統需將文件內容切分後建立向量索引。

支援策略：

| 策略 | 說明 |
|---|---|
| fixed_size | 固定 token 長度切分 |
| semantic | 依段落、標題、條文或表格語意切分 |
| parent_child | child chunk 用於檢索，parent chunk 用於回答 |

chunk metadata：

```json
{
  "tenant_id": "org_001",
  "project_id": "proj_001",
  "document_id": "doc_001",
  "page_number": 1,
  "chunk_type": "text",
  "document_type": "invoice",
  "source": "ocr | text_upload | pdf_text",
  "created_at": "2026-05-20T00:00:00Z"
}
```

驗收標準：

- 文件解析完成後自動建立 chunks。
- chunks 寫入 PostgreSQL。
- embeddings 寫入 Qdrant。
- Qdrant payload 需包含 tenant、project、document metadata。
- 可重新索引單一文件或整個 project。

---

### F-007 RAG Chat 問答

系統需提供可引用來源的問答功能。

流程：

1. 接收使用者問題。
2. Query rewrite。
3. Retrieval top K。
4. Rerank。
5. Context packing。
6. LLM answer generation。
7. Citation output。
8. Trace logging。

回傳格式：

```json
{
  "answer": "這份發票的總金額為 NT$52,500。",
  "citations": [
    {
      "document_id": "doc_001",
      "filename": "invoice_001.pdf",
      "page_number": 1,
      "chunk_id": "chunk_001",
      "text": "總金額：NT$52,500"
    }
  ],
  "trace": {
    "retrieval_top_k": 30,
    "rerank_top_k": 5,
    "retrieval_latency_ms": 120,
    "rerank_latency_ms": 300,
    "generation_latency_ms": 1500
  }
}
```

驗收標準：

- 使用者可對 indexed 文件提問。
- 回答必須附 citation。
- UI 顯示引用文件、頁碼與原文片段。
- 系統記錄 retrieval、rerank、generation latency。

---

### F-008 Rerank 模組

系統需支援 reranker 對候選 chunk 重新排序。

流程：

1. Vector Search 取 top 30。
2. Reranker 對 query-chunk pair 打分。
3. 取 top 5 進入 context。
4. 記錄 rerank 前後排名。

驗收標準：

- UI 可顯示 rerank 前後排序。
- 每個 chunk 顯示 similarity score 與 rerank score。
- 評估模組可比較 rerank 前後 Hit Rate / MRR。
- Rerank 可透過設定開啟或關閉。

---

### F-009 RAG 評估模組

系統需支援建立 eval dataset 並執行檢索評估。

eval dataset 格式：

```json
{
  "question": "這張發票的總金額是多少？",
  "expected_answer": "NT$52,500",
  "gold_document_id": "doc_001",
  "gold_chunk_ids": ["chunk_001"],
  "metadata": {
    "document_type": "invoice",
    "difficulty": "table"
  }
}
```

評估指標：

| 指標 | 說明 |
|---|---|
| Hit Rate@K | gold chunk 是否出現在 top K |
| Recall@K | 找回 gold chunks 的比例 |
| MRR@K | 第一個正確 chunk 的 reciprocal rank |
| Precision@K | top K 中相關 chunk 的比例 |
| Latency | 查詢平均延遲 |
| Failure Cases | 找不到 gold chunk 的問題列表 |

驗收標準：

- 可建立 eval dataset。
- 可選擇 retrieval strategy。
- 可執行 eval run。
- UI 顯示 Hit Rate、MRR、Recall@K、Latency。
- 可查看失敗案例。

---

### F-010 AI Agent

系統需支援 Agent 執行多步任務。

Agent tools：

| Tool | 功能 |
|---|---|
| search_documents | 查詢文件 chunks |
| query_sql | 查詢結構化欄位 |
| extract_invoice_fields | 抽取單據欄位 |
| compare_documents | 比較多份文件 |
| run_rag_eval | 執行 RAG 評估 |
| generate_report | 產生摘要報告 |
| reindex_project | 重新索引 project |

Agent 任務範例：

> 找出這批單據中總金額最高的前三張，並確認是否有缺少統編。

Agent plan：

1. 使用 `query_sql` 查詢單據欄位。
2. 依總金額排序。
3. 檢查統編欄位是否缺漏。
4. 使用 `search_documents` 補充來源。
5. 回傳表格與 citation。

驗收標準：

- Agent 可顯示執行步驟。
- Agent 可選擇至少 3 種工具。
- 任務結果需包含來源或 trace。
- 工具執行錯誤需有 fallback 訊息。

---

### F-011 Redis 快取與 Session

Redis 用途：

- Session cache。
- Query cache。
- Rate limit。
- Worker lock。
- Chat history short-term cache。
- 任務狀態快取。

驗收標準：

- 登入 session 可由 Redis 管理。
- 相同 query 可命中 cache。
- API rate limit 可限制高頻請求。
- 同一文件不可同時重複索引。

---

### F-012 NATS 非同步任務

系統需使用 NATS 建立事件驅動 worker 架構。

事件 topics：

| Topic | 功能 |
|---|---|
| document.uploaded | 文件上傳完成 |
| document.ocr.requested | OCR 任務 |
| document.ocr.completed | OCR 完成 |
| document.parse.requested | VLM / Parser 任務 |
| document.index.requested | 建立索引 |
| rag.eval.requested | 執行 RAG 評估 |
| agent.task.requested | 執行 Agent 任務 |

驗收標準：

- 上傳文件後透過 NATS 觸發 worker。
- OCR、Parser、Embedding、Eval 需可分 worker 執行。
- 任務失敗需可重試。
- UI 可查看任務狀態。

---

### F-013 推論後端

系統需支援可切換推論服務。

支援模式：

| 模式 | 用途 |
|---|---|
| vLLM | 高效能 LLM serving |
| Ollama | 本地開發 |
| OpenAI-compatible API | 可接雲端或企業內部模型 |
| llama.cpp | 輕量本地推論，可作 optional |

初始推薦模型配置：

| 角色 | 初始 provider | 初始模型 / 工具 | 用途 |
|---|---|---|---|
| LLM | Ollama | `qwen3.5:4b` | RAG 回答、query rewrite、摘要、Agent planning |
| VLM | Ollama | `qwen3.5:4b` | 掃描 PDF、圖片、發票與表格理解、JSON 欄位抽取 |
| Embedding | FastEmbed | `BAAI/bge-m3` | 文件 chunk 與 query 向量化，寫入 Qdrant |
| Reranker | FastEmbed | `BAAI/bge-reranker-v2-m3` | 對 retrieval top K 重新排序，支援 Hit Rate / MRR 比較 |
| OCR | Local engine | `paddleocr` | 先產生文字層與版面基礎，VLM 作為 parser 或補強 |

模型設定範例：

```env
DOCURAG_LLM_PROVIDER=ollama
DOCURAG_LLM_BASE_URL=http://127.0.0.1:11434
DOCURAG_LLM_MODEL=qwen3.5:4b
DOCURAG_VLM_PROVIDER=ollama
DOCURAG_VLM_MODEL=qwen3.5:4b
EMBEDDING_PROVIDER=fastembed
EMBEDDING_MODEL=BAAI/bge-m3
RERANKER_PROVIDER=fastembed
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
OCR_ENGINE=paddleocr
```

設計原則：

- LLM 與 VLM 概念上分工，但可由同一套 OpenAI-compatible client 抽象呼叫。
- 第一版本機 demo 以 `qwen3.5:4b` 作為 LLM / VLM 共同目標，降低 RTX 5070 Ti 16GB VRAM 下同時搭配 PaddleOCR 的壓力。
- 較新的大型 Qwen 系列可保留為 OpenAI-compatible API 或後續 serving fallback；未公開或未上架的 4B 型號不寫入預設路線。
- Embedding 與 Reranker 保持獨立，方便在 eval run 中比較檢索策略。
- vLLM 保留為後續 LLMOps / serving / latency 展示，第一版優先用 Ollama 降低本地整合成本。

驗收標準：

- `.env` 可設定 LLM provider。
- Chat API 不依賴特定模型服務。
- 可記錄 prompt tokens、completion tokens、latency。
- README 需說明如何切換 provider。

---

### F-014 Docker Compose 與部署

系統需提供 Docker Compose 啟動環境。

服務列表：

```yaml
services:
  frontend:
  api:
  worker-ocr:
  worker-parser:
  worker-embedding:
  worker-rerank:
  worker-eval:
  postgres:
  redis:
  qdrant:
  nats:
  ollama:
  grafana:
  loki:
```

驗收標準：

- `docker compose up` 可啟動主要服務。
- README 有啟動流程。
- `.env.example` 包含必要設定。
- 提供 basic K8s manifests 作為延伸展示。

---

## 7. 非功能需求

### 7.1 效能需求

| 項目 | MVP 目標 |
|---|---|
| 文件上傳 API | 單檔 20MB 以內 |
| OCR 任務 | 單頁圖片 10 秒內完成，視硬體可調整 |
| RAG retrieval | 500ms 內 |
| Rerank | 1 秒內，top 30 candidates |
| LLM 回答 | 5 秒內回傳 first response，視模型可調整 |
| Eval run | 100 筆問題可批次執行 |

### 7.2 安全需求

- 密碼需 hash，不可明文儲存。
- API 需使用 JWT 或 session-based auth。
- 所有資料查詢需檢查 organization / project 權限。
- 文件下載需檢查使用者權限。
- 系統需避免跨 tenant 資料外洩。
- `.env` 不可提交真實密鑰。

### 7.3 可觀測性需求

需記錄：

- API request log。
- Error log。
- Worker task log。
- RAG trace。
- Retrieval latency。
- Rerank latency。
- LLM generation latency。
- Token usage。
- Eval metrics。

### 7.4 可維護性需求

- 後端採分層架構：API、Service、Repository、Worker。
- RAG pipeline 模組化，方便替換 embedding model、reranker、LLM provider。
- 前後端 API schema 明確。
- 提供 seed demo data。
- 提供測試資料與 eval dataset。

---

## 8. 系統架構

### 8.1 高階架構

```text
Vue3 Frontend
    |
FastAPI API Gateway
    |
    |-- Auth / RBAC
    |-- Document API
    |-- Chat API
    |-- Agent API
    |-- Eval API
    |-- Admin API
    |
PostgreSQL ---------------- Redis
    |                        |
    |                        |-- Session Cache
    |                        |-- Query Cache
    |                        |-- Rate Limit
    |
Qdrant Vector DB
    |
NATS Message Bus
    |
    |-- OCR Worker
    |-- Parser Worker
    |-- Embedding Worker
    |-- Rerank Worker
    |-- Eval Worker
    |
LLM Inference Server
    |-- vLLM
    |-- Ollama
    |-- OpenAI-compatible API
```

### 8.2 Backend 模組

```text
backend/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── documents.py
│   │   ├── chat.py
│   │   ├── agent.py
│   │   └── eval.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── ocr_service.py
│   │   ├── parser_service.py
│   │   ├── eval_service.py
│   │   └── agent_service.py
│   ├── repositories/
│   └── main.py
├── workers/
│   ├── ocr_worker.py
│   ├── parser_worker.py
│   ├── embedding_worker.py
│   ├── rerank_worker.py
│   └── eval_worker.py
└── tests/
```

### 8.3 Frontend 模組

```text
frontend/
├── src/
│   ├── pages/
│   │   ├── Login.vue
│   │   ├── Dashboard.vue
│   │   ├── Projects.vue
│   │   ├── Documents.vue
│   │   ├── DocumentDetail.vue
│   │   ├── Chat.vue
│   │   ├── Agent.vue
│   │   ├── Eval.vue
│   │   └── Admin.vue
│   ├── components/
│   ├── api/
│   ├── stores/
│   └── router/
```

---

## 9. 資料庫設計

### 9.1 users

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | 使用者 ID |
| email | string | Email |
| password_hash | string | 密碼 hash |
| display_name | string | 顯示名稱 |
| is_active | bool | 是否啟用 |
| created_at | datetime | 建立時間 |

### 9.2 organizations

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | 組織 ID |
| name | string | 組織名稱 |
| plan | string | 方案 |
| created_at | datetime | 建立時間 |

### 9.3 memberships

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | membership ID |
| user_id | UUID | 使用者 ID |
| organization_id | UUID | 組織 ID |
| role | string | admin / manager / analyst / viewer |

### 9.4 projects

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | 專案 ID |
| organization_id | UUID | 組織 ID |
| name | string | 專案名稱 |
| description | text | 專案描述 |
| vector_collection | string | Qdrant collection |
| created_by | UUID | 建立者 |
| created_at | datetime | 建立時間 |

### 9.5 documents

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | 文件 ID |
| project_id | UUID | 專案 ID |
| filename | string | 檔名 |
| file_type | string | pdf / jpg / png |
| document_type | string | invoice / contract / report |
| status | string | 處理狀態 |
| storage_path | string | 檔案路徑 |
| page_count | int | 頁數 |
| created_by | UUID | 上傳者 |
| created_at | datetime | 建立時間 |

### 9.6 document_pages

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | page ID |
| document_id | UUID | 文件 ID |
| page_number | int | 頁碼 |
| image_path | string | 頁面圖片 |
| ocr_text | text | OCR 文字 |
| ocr_blocks | jsonb | OCR 區塊與座標 |

### 9.7 document_chunks

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | chunk ID |
| document_id | UUID | 文件 ID |
| page_number | int | 頁碼 |
| chunk_text | text | chunk 內容 |
| chunk_type | string | text / table / field |
| token_count | int | token 數 |
| embedding_model | string | embedding model |
| metadata | jsonb | metadata |

### 9.8 extracted_fields

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | 欄位 ID |
| document_id | UUID | 文件 ID |
| field_name | string | 欄位名稱 |
| field_value | text | 欄位值 |
| confidence | float | 信心分數 |
| source_page | int | 來源頁 |
| source_bbox | jsonb | 來源座標 |
| corrected_by | UUID | 修正者 |
| updated_at | datetime | 更新時間 |

### 9.9 chat_sessions

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | chat session ID |
| project_id | UUID | 專案 ID |
| user_id | UUID | 使用者 ID |
| title | string | 對話標題 |
| created_at | datetime | 建立時間 |

### 9.10 chat_messages

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | message ID |
| session_id | UUID | chat session ID |
| role | string | user / assistant / tool |
| content | text | 訊息內容 |
| trace | jsonb | RAG trace |
| created_at | datetime | 建立時間 |

### 9.11 eval_datasets

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | dataset ID |
| project_id | UUID | 專案 ID |
| name | string | dataset 名稱 |
| description | text | 描述 |
| created_by | UUID | 建立者 |

### 9.12 eval_items

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | item ID |
| dataset_id | UUID | dataset ID |
| question | text | 問題 |
| expected_answer | text | 標準答案 |
| gold_document_id | UUID | 正確文件 |
| gold_chunk_ids | jsonb | 正確 chunks |
| metadata | jsonb | metadata |

### 9.13 eval_runs

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | UUID | run ID |
| dataset_id | UUID | dataset ID |
| strategy_name | string | 策略名稱 |
| config | jsonb | 實驗設定 |
| hit_rate_at_k | float | Hit Rate@K |
| recall_at_k | float | Recall@K |
| mrr_at_k | float | MRR@K |
| avg_latency_ms | float | 平均延遲 |
| created_at | datetime | 建立時間 |

---

## 10. API 規格

### 10.1 Auth API

| Method | Endpoint | 說明 |
|---|---|---|
| POST | `/auth/login` | 登入 |
| POST | `/auth/logout` | 登出 |
| GET | `/auth/me` | 取得目前使用者 |
| POST | `/auth/refresh` | 更新 token |

### 10.2 Project API

| Method | Endpoint | 說明 |
|---|---|---|
| GET | `/projects` | 取得 project list |
| POST | `/projects` | 建立 project |
| GET | `/projects/{project_id}` | 取得 project detail |
| PATCH | `/projects/{project_id}` | 更新 project |
| DELETE | `/projects/{project_id}` | 刪除 project |

### 10.3 Document API

| Method | Endpoint | 說明 |
|---|---|---|
| POST | `/projects/{project_id}/documents` | 上傳文件 |
| GET | `/projects/{project_id}/documents` | 文件列表 |
| GET | `/documents/{document_id}` | 文件詳情 |
| GET | `/documents/{document_id}/pages` | 文件頁面與 OCR |
| GET | `/documents/{document_id}/fields` | 結構化欄位 |
| PATCH | `/documents/{document_id}/fields/{field_id}` | 修正欄位 |
| POST | `/documents/{document_id}/reparse` | 重新解析 |
| POST | `/documents/{document_id}/reindex` | 重新索引 |

### 10.4 Chat API

| Method | Endpoint | 說明 |
|---|---|---|
| POST | `/projects/{project_id}/chat/sessions` | 建立 chat session |
| GET | `/projects/{project_id}/chat/sessions` | 取得 chat sessions |
| POST | `/chat/sessions/{session_id}/messages` | 送出問題 |
| GET | `/chat/messages/{message_id}/trace` | 查看 RAG trace |
| GET | `/chat/messages/{message_id}/citations` | 查看引用來源 |

### 10.5 Agent API

| Method | Endpoint | 說明 |
|---|---|---|
| POST | `/projects/{project_id}/agent/run` | 執行 Agent 任務 |
| GET | `/agent/runs/{run_id}` | 查看 Agent 結果 |
| GET | `/agent/runs/{run_id}/steps` | 查看 Agent steps |

### 10.6 Eval API

| Method | Endpoint | 說明 |
|---|---|---|
| POST | `/projects/{project_id}/eval-datasets` | 建立 eval dataset |
| GET | `/projects/{project_id}/eval-datasets` | 列出 eval datasets |
| POST | `/eval-datasets/{dataset_id}/items` | 新增 eval item |
| POST | `/eval-datasets/{dataset_id}/runs` | 執行 eval |
| GET | `/eval-runs/{run_id}` | 查看 eval result |
| GET | `/eval-runs/{run_id}/failures` | 查看失敗案例 |

---

## 11. RAG Pipeline 規格

### 11.1 Indexing Pipeline

```text
Document Uploaded
    ↓
OCR
    ↓
VLM / Parser
    ↓
Text Normalization
    ↓
Chunking
    ↓
Embedding
    ↓
Qdrant Upsert
    ↓
Indexed
```

### 11.2 Query Pipeline

```text
User Query
    ↓
Query Rewrite
    ↓
Dense / Hybrid Retrieval
    ↓
Rerank
    ↓
Context Packing
    ↓
LLM Generation
    ↓
Citation Mapping
    ↓
Answer + Trace
```

### 11.3 Retrieval Strategy

| 策略 | 說明 |
|---|---|
| dense | 使用 embedding similarity |
| sparse | 使用 BM25 / keyword matching |
| hybrid | dense + sparse |
| hybrid_rerank | hybrid retrieval 後接 reranker |

### 11.4 Context Packing

規則：

- 優先選擇 rerank score 高的 chunks。
- 避免同一頁面重複過多 chunks。
- 保留 citation metadata。
- 控制 token budget。
- 若有 parent-child chunk，回傳 parent context。

---

## 12. AI Agent 規格

### 12.1 Agent 架構

```text
User Task
    ↓
Planner
    ↓
Tool Selection
    ↓
Tool Execution
    ↓
Observation
    ↓
Reflection / Next Step
    ↓
Final Answer
```

### 12.2 Agent Step 格式

```json
{
  "step": 1,
  "thought": "需要先查詢結構化單據資料。",
  "tool": "query_sql",
  "input": {
    "project_id": "proj_001",
    "query": "top invoices by total_amount"
  },
  "output": {
    "rows": []
  }
}
```

### 12.3 Agent 限制

- Agent 不可直接執行任意 SQL。
- `query_sql` 需使用 allowlist template。
- 破壞性操作如 delete、reindex 需檢查角色。
- Agent 所有工具調用需寫入 trace。

---

## 13. RAG 評估規格

### 13.1 實驗設定

每次 eval run 需記錄：

```json
{
  "strategy_name": "hybrid_rerank",
  "chunking": "semantic",
  "embedding_model": "BAAI/bge-m3",
  "reranker_model": "BAAI/bge-reranker-v2-m3",
  "retrieval_top_k": 30,
  "rerank_top_k": 5,
  "llm_model": "qwen3.5:4b",
  "vlm_model": "qwen3.5:4b"
}
```

### 13.2 指標計算

Hit Rate@K：

```text
若 top K retrieval results 中包含任一 gold_chunk_id，則該題 hit = 1，否則 hit = 0。
Hit Rate@K = hit 題數 / 總題數
```

MRR@K：

```text
若第一個正確 chunk 排名為 r，則 reciprocal rank = 1 / r。
若 top K 沒有正確 chunk，則 reciprocal rank = 0。
MRR@K = 所有 reciprocal rank 平均值。
```

Recall@K：

```text
Recall@K = top K 中找回的 gold chunks 數量 / gold chunks 總數
```

### 13.3 評估輸出

```json
{
  "run_id": "eval_run_001",
  "strategy_name": "hybrid_rerank",
  "metrics": {
    "hit_rate_at_5": 0.88,
    "mrr_at_10": 0.77,
    "recall_at_10": 0.82,
    "avg_latency_ms": 620
  },
  "failures": [
    {
      "question": "付款條件是什麼？",
      "gold_chunk_ids": ["chunk_005"],
      "retrieved_chunk_ids": ["chunk_010", "chunk_011"],
      "reason": "semantic mismatch"
    }
  ]
}
```

---

## 14. UI 頁面規格

### 14.1 Login Page

功能：

- Email / password 登入。
- 顯示登入錯誤。
- 登入成功後導向 Dashboard。

### 14.2 Dashboard

顯示：

- 文件數量。
- 已索引文件數。
- OCR 失敗數。
- 今日查詢量。
- 平均 retrieval latency。
- 平均 generation latency。
- 最近 eval run 結果。
- Worker 任務狀態。

### 14.3 Documents Page

功能：

- 文件列表。
- 上傳文件。
- 顯示狀態。
- 顯示類型。
- 重新解析。
- 重新索引。

### 14.4 Document Detail Page

功能：

- 預覽 PDF / 圖片。
- 查看 OCR 文字。
- 查看 extracted fields。
- 人工修正欄位。
- 查看 chunks。
- 查看 indexing 狀態。

### 14.5 Chat Page

功能：

- 問答輸入。
- 顯示回答。
- 顯示 citation cards。
- 顯示 retrieval / rerank trace。
- 顯示 latency 與 token usage。
- 可切換檢索策略。

### 14.6 Agent Page

功能：

- 輸入任務。
- 顯示 Agent plan。
- 顯示每一步 tool call。
- 顯示 observation。
- 顯示 final answer。

### 14.7 Eval Page

功能：

- 建立 eval dataset。
- 上傳 eval items。
- 選擇策略。
- 執行 eval。
- 顯示 metric table。
- 顯示 failure cases。

### 14.8 Admin Page

功能：

- 使用者管理。
- 角色管理。
- 專案管理。
- 模型 endpoint 設定。
- 系統日誌。
- Worker 狀態。

---

## 15. GitHub Repository 規格

建議目錄：

```text
docurag-agentops/
├── README.md
├── goal.md
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── API_SPEC.md
│   ├── DB_SCHEMA.md
│   ├── RAG_EVAL_REPORT.md
│   ├── INFERENCE_BENCHMARK.md
│   └── RBAC_DESIGN.md
├── backend/
│   ├── app/
│   ├── workers/
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   └── package.json
├── eval/
│   ├── datasets/
│   ├── notebooks/
│   └── run_eval.py
├── fine-tuning/
│   ├── synthetic_data/
│   ├── train_embedding.py
│   └── sft_schema_extractor.md
├── infra/
│   ├── docker-compose.yml
│   ├── k8s/
│   └── grafana/
├── sample-data/
│   ├── invoices/
│   ├── contracts/
│   └── eval_sets/
└── scripts/
    ├── seed_demo_data.py
    ├── run_local_demo.sh
    └── benchmark_inference.py
```

---

## 16. 開發里程碑

### Phase 0：Repository Bootstrap

目標：

- 建立 repo 結構。
- 建立 README。
- 建立 `.env.example`。
- 建立 docker-compose skeleton。
- 建立 FastAPI health check。
- 建立 Vue3 skeleton。

驗收：

- `docker compose up` 可啟動 api、frontend、postgres、redis、qdrant、nats。
- `/health` 回傳 OK。
- frontend 可開啟首頁。

### Phase 1：Auth / RBAC / Project

目標：

- 使用者登入。
- RBAC。
- Organization / Project schema。
- Project CRUD。

驗收：

- 不同角色權限正確。
- 使用者只能存取自己 organization 的 project。

### Phase 2：Document Upload / OCR

目標：

- 文件上傳。
- OCR worker。
- OCR 結果儲存與顯示。
- 任務狀態管理。

驗收：

- 上傳 PDF / 圖片後可看到 OCR 文字。
- OCR 任務透過 NATS 執行。

### Phase 3：Parser / Chunking / Indexing

目標：

- VLM / Parser schema extraction。
- Chunking。
- Embedding。
- Qdrant indexing。

驗收：

- 發票 sample 可抽出 JSON。
- 文件可被向量檢索。

### Phase 4：RAG Chat / Citation / Trace

目標：

- RAG Chat。
- Citation。
- Rerank。
- RAG trace viewer。

驗收：

- 問答可回傳答案與來源。
- UI 顯示 retrieval 與 rerank 資訊。

### Phase 5：Eval / Agent / Ops

目標：

- Eval dataset。
- Hit Rate / MRR。
- Agent tool-use。
- Redis cache。
- 推論 latency log。
- Docker / K8s 文件。

驗收：

- 可比較不同 RAG 策略。
- Agent 可完成多步任務。
- README 包含完整 demo 流程。

---

## 17. MVP 驗收清單

| 編號 | 項目 | 必須完成 |
|---|---|---|
| A-001 | FastAPI health check | 是 |
| A-002 | Vue3 dashboard skeleton | 是 |
| A-003 | PostgreSQL schema | 是 |
| A-004 | Redis session / cache | 是 |
| A-005 | NATS worker skeleton | 是 |
| A-006 | Qdrant indexing | 是 |
| A-007 | 文件上傳 | 是 |
| A-008 | OCR 結果顯示 | 是 |
| A-009 | invoice JSON extraction | 是 |
| A-010 | chunking | 是 |
| A-011 | embedding | 是 |
| A-012 | RAG Chat | 是 |
| A-013 | citation | 是 |
| A-014 | rerank | 是 |
| A-015 | Hit Rate / MRR eval | 是 |
| A-016 | Agent tool-use | 是 |
| A-017 | Docker Compose | 是 |
| A-018 | README demo guide | 是 |
| A-019 | K8s manifests | 選做 |
| A-020 | SFT / LoRA notebook | 選做 |

---

## 18. Demo 劇本

### 18.1 面試 Demo 流程

1. 開啟 GitHub README，介紹專案目的。
2. 顯示系統架構圖。
3. 使用測試帳號登入。
4. 建立或切換 project。
5. 上傳一份 invoice PDF。
6. 顯示 OCR 結果。
7. 顯示 VLM 抽出的 JSON 欄位。
8. 切換到 Chat 頁面詢問單據內容。
9. 顯示回答與 citation。
10. 打開 trace，顯示 retrieval top K 與 rerank score。
11. 切換到 Eval 頁面，顯示 Dense vs Hybrid vs Rerank 結果。
12. 切換到 Agent 頁面，執行多步文件分析任務。
13. 顯示 Docker Compose 與部署文件。

### 18.2 Demo 問題範例

- 這張發票的總金額是多少？
- 這份合約的付款條件是什麼？
- 找出所有缺少統編的單據。
- 比較 A 合約與 B 合約的違約條款差異。
- 執行 hybrid_rerank 策略的 RAG 評估。
- 幫我產生本批單據的摘要報告。

---

## 19. 面試講解重點

可用以下方式介紹本專案：

> DocuRAG AgentOps 是一個企業級文件智能平台，整合 OCR/VLM 文件解析、RAG 問答、Rerank、檢索評估與 AI Agent tool-use。  
>  
> 我特別把 RAG 做成可觀測與可量化，而不是只做一般聊天功能。系統可以比較 Dense Search、Hybrid Search、Rerank 與不同 chunking 策略，並輸出 Hit Rate、MRR、Recall@K 與 latency。  
>  
> 工程架構上，我使用 FastAPI、Vue3、PostgreSQL、Redis、NATS、Qdrant 與 vLLM/Ollama，並以 Docker Compose 整合服務。這讓專案同時展示 AI Core、後端系統設計、非同步任務、權限管理、推論部署與維運觀念。

---

## 20. 技術風險與取捨

| 風險 | 說明 | 對策 |
|---|---|---|
| OCR 品質不穩 | 掃描品質差會影響解析 | 提供人工修正與 confidence |
| VLM 成本較高 | Vision model 推論較慢 | MVP 可先用 OCR + LLM parser |
| Rerank 延遲增加 | Cross-encoder 成本較高 | 提供開關與 top K 限制 |
| 多租戶資料隔離 | 容易發生跨 project 查詢 | API 與 vector metadata 雙層檢查 |
| 本地模型資源有限 | 16GB VRAM 適合優先跑 7B / 8B 級模型 | 第一版使用 Ollama + Qwen3 8B / Qwen3-VL 8B，較大的模型改用 OpenAI-compatible fallback |
| vLLM 本地資源不足 | GPU 記憶體與部署複雜度可能卡住 MVP | vLLM 保留為後續 LLMOps 展示，先支援 Ollama / OpenAI-compatible fallback |
| K8s 實作時間較長 | 完整 production 部署複雜 | MVP 僅提供 basic manifests |

---

## 21. 不在 MVP 範圍

以下功能不列入 v0.1 必做範圍：

- 完整金流或 SaaS billing。
- 真正 production-grade K8s autoscaling。
- 完整 SFT 訓練 pipeline。
- 大規模多 GPU serving。
- 企業 SSO / SAML。
- 完整 ELK logging stack。
- 完整資料標註平台。
- 高精度表格重建引擎。

---

## 22. 成功標準

本專案完成後，需達成以下成果：

1. GitHub repo 可公開展示。
2. README 可在 3 分鐘內讓人理解專案價值。
3. Docker Compose 可啟動主要服務。
4. 有至少 5 份 sample documents。
5. 有至少 20 筆 eval questions。
6. RAG Chat 可回答並附 citation。
7. Eval 頁可顯示不同策略比較。
8. Agent 可執行至少一個多步任務。
9. 有系統架構圖與資料庫設計文件。
10. 有面試 Demo 劇本與截圖或 GIF。

---

## 23. 第一版開發優先順序

若時間有限，優先順序如下：

1. FastAPI + Vue3 + Docker Compose skeleton。
2. PostgreSQL schema + Auth + Project。
3. 文件上傳 + OCR。
4. Parser JSON extraction。
5. Chunking + Embedding + Qdrant indexing。
6. RAG Chat + citation。
7. Rerank + RAG trace。
8. Eval metrics。
9. Agent tool-use。
10. Redis / NATS / Ops 文件補強。

### 23.1 目前 ticket 優先順序覆寫

Phase 09 performance hardening 已收斂為 `v0.9.1`。Phase 10 已依 ticket-first 順序完成 10-01 provider decision、10-02 Ollama client、10-03 optional generation path 與 10-04 demo smoke / answer source / `v0.10.0` release sync：

1. [x] `tasks/phase-09-gpu-runtime/09-03-paddleocr-engine-lifecycle-preload.md`：只處理 OCR engine lifecycle、backend startup preload 與 provider reuse，避免每次 OCR request 重新 cold start。
2. [x] `tasks/phase-09-gpu-runtime/09-04-paddleocr-performance-observability-tuning.md`：只處理 OCR timing log / baseline，並小範圍評估 `cls=True`、warmup、圖片尺寸與推論參數對速度的影響。
3. [x] `tasks/phase-10-llm-rag/10-01-qwen3-ollama-provider-decision.md`：只固定 Ollama `qwen3.5:4b` LLM / VLM provider decision 與 env 文件，不實作 backend LLM client。
4. [x] `tasks/phase-10-llm-rag/10-02-ollama-qwen3-client.md`：只新增最小 Ollama LLM client、timeout / error handling 與 health helper，不改既有 `/rag/query` deterministic baseline。
5. [x] `tasks/phase-10-llm-rag/10-03-qwen3-rag-generation.md`：只在 existing keyword retrieval 與 citation contract 上加入可選 LLM generation path，prompt 只使用 query 與 retrieved chunks。
6. [x] `tasks/phase-10-llm-rag/10-04-qwen3-demo-smoke.md`：只補齊 demo smoke、UI answer source、optional LLM smoke 與 `v0.10.0` release/version sync。

執行限制：

- `09-03` 不處理 OCR timing、baseline、warmup 或參數調校。
- `09-04` 不處理 provider lifecycle 以外的大型架構變更，只做效能觀測與小範圍調校。
- 不提前實作 worker queue、Redis、NATS、資料庫 schema、登入、權限、PDF rendering、多頁 OCR pipeline 或 production-grade OCR tuning。
- Phase 10 照 Qwen3 / Ollama / RAG demo 順序執行完成；不要在同一輪回頭擴張 Phase 10 scope。
- Phase 10 不提前實作 embedding、Qdrant、rerank、worker、Redis、NATS、資料庫 schema、登入、權限、VLM parser、PDF rendering 或 streaming。

---

## 24. 最小可展示版本定義

最小可展示版本只需完成以下流程：

```text
Login
  ↓
Create Project
  ↓
Upload Invoice PDF
  ↓
OCR Text
  ↓
Extract JSON Fields
  ↓
Index Chunks to Qdrant
  ↓
Ask Question
  ↓
Answer with Citation
  ↓
Show RAG Trace
  ↓
Run Eval
  ↓
Compare Metrics
```

只要這條流程完整可跑，即可作為面試展示作品。

---

## 25. 結論

DocuRAG AgentOps 是一個專門為 AI 軟體應用開發職缺設計的 Side Project。它同時涵蓋 AI Core、RAG 評估、OCR/VLM、Agent、後端架構、權限系統、非同步任務、快取、推論部署與容器化維運。

本專案的核心價值在於：

- 不只會串接 LLM，而是能設計完整 AI 系統。
- 不只會做 RAG，而是能評估 RAG。
- 不只會做模型功能，而是能做可部署、可管理、可觀測的工程平台。
- 不只展示單點技術，而是展示端到端 AI Application Engineering 能力。
