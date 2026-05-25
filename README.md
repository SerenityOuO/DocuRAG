# DocuRAG

> 開發紀錄、ticket 進度、版本更新日誌與本地開發備忘請見：[README_DEV.md](./README_DEV.md)

DocuRAG AgentOps 是一個面試展示用的 AI 文件平台 side project，目標是把文件上傳、OCR / VLM 解析、RAG 問答、retrieval trace、評估指標與 Agent tool-use 串成一個可驗證的端到端 demo。

這不是單純的聊天機器人範例，而是用受控 MVP 展示 AI Application Engineering 的完整切片：API contract、模型 provider 邊界、fallback 策略、trace metadata、evaluation runner、frontend demo surface 與 ticket-first 開發流程。

## 目前狀態

目前文件中的最新已完成展示版本是 `v0.29.0`。Phase 29 已在後台新增固定 `hybrid_rerank` 的「測試RAG」內建基準測試，並將 Agent 執行紀錄改成可摺疊。

已可展示的主線能力：

- Vue 3 + Vite frontend：Viewer Chat、Admin / Analyst ingestion surface、structured fields、Agent trace。
- FastAPI backend：health、demo auth、document upload/list/detail、OCR、parser、RAG、Agent run、manual vector indexing API。
- PaddleOCR GPU-first OCR flow：provider-selected OCR 預設走 PaddleOCR，mock OCR 只作手動 fallback。
- VLM-first parser provider spike：`vlm_invoice` 優先，request 會帶原始圖片與 compact OCR context；欄位值可對回 OCR line / bbox，provider unavailable / invalid response 時 fallback 到 deterministic parser。
- Default `hybrid_rerank` RAG / Agent search：優先走 hybrid rerank，Ollama embedding、Qdrant 或 FastEmbed 不可用時回到 keyword evidence。
- Direct `.txt` ingestion：`.txt` 上傳後直接建立 `text_upload` chunks，可被 RAG、Qdrant vector indexing 與 Agent search 使用，不再先包成 mock OCR。
- Text-native PDF ingestion：可複製文字的 PDF 會抽文字層並建立 `pdf_text` chunks，保留 page number；scanned / empty PDF 只標示 `pdf_scanned_pending_ocr`。
- Document Source Router contract：文件來源已明確分成 `image_ocr`、`text_upload`、`pdf_text` 與 `pdf_scanned_pending_ocr`，不把文字檔、PDF 與 OCR 混成同一路徑。
- Demo auth mode：`DOCURAG_AUTH_MODE=demo` 會啟用 Admin / Analyst / Viewer demo login、`/auth/login` / `/auth/me` / `/auth/logout` 與 backend write API role guard；預設仍是 `disabled`，且不是正式 RBAC。
- 後台「測試RAG」：Admin / Analyst 可直接執行內建 10 張 synthetic 中文發票 retrieval benchmark，固定 `hybrid_rerank`，只呈現 Hit Rate@K、MRR@K、平均延遲與 Failure / Fallback。
- Retrieval eval runner：輸出 Hit Rate@K、MRR@K、Recall@K、latency、failure / fallback count 與 trace metadata count。
- Deterministic Agent tool-use MVP：用 allowlisted read-only tools 串接 structured fields、document search 與 invoice summary。

## 技術亮點

- **清楚的 AI provider 邊界**：OCR、LLM、VLM、embedding、reranker 都有明確 provider / fallback policy，不把外部 runtime availability 偽裝成一定成功。
- **RAG 可觀測性**：回答不只輸出文字，也保留 citations、retrieved chunks、retrieval source、answer source 與 trace metadata。
- **評估不是附屬品**：內建 retrieval eval dataset 與 smoke runner，可比較 keyword、vector、vector_rerank、hybrid、hybrid_rerank 策略。
- **面試可講的產品邊界**：Viewer 只查詢既有知識庫；Admin / Analyst 才操作 upload、OCR、parser、indexing 與 Agent trace；demo auth mode 會在 UI 與 backend write API 上呈現基本 role gates。
- **ticket-first 工程流程**：每個功能用小 ticket 控制 Goal、Scope、Out of Scope、Acceptance Criteria 與 Validation，避免提前塞入 DB、worker、auth 等未排定能力。

## 架構概覽

```text
Vue Frontend
  |-- Demo Login / Role-gated Surfaces
  |-- Viewer Chat
  |-- Admin / Analyst Ingestion
  |-- Structured Fields / 測試RAG / Agent Trace
          |
FastAPI Backend
  |-- Demo Auth APIs / Write API Role Guards
  |-- Document / OCR / Parser APIs
  |-- RAG Query / Agent Run APIs
  |-- Built-in RAG Eval API / Retrieval Eval Runner
          |
Local JSON Store + Uploaded Files
          |
Optional Local AI Runtime
  |-- PaddleOCR GPU
  |-- Ollama LLM / Embedding
  |-- Qdrant
  |-- FastEmbed Reranker
  |-- Local VLM Provider
```

外部 AI runtime 不可用時，demo 會保留清楚 fallback，而不是靜默假裝完整 production pipeline 已存在。

## 面試 Demo Path

5 到 10 分鐘建議順序：

1. 開 README，先說明這是一個文件智能平台，不是只有 RAG chat。
2. 若啟用 `DOCURAG_AUTH_MODE=demo`，先用 Admin 登入並展示 role-gated surface。
3. 展示 Viewer Chat 對既有知識庫提問，觀察 answer source、retrieval source 與 citations。
4. 切到 Admin / Analyst ingestion，展示文件上傳、OCR 文字層、VLM parser structured fields 與欄位 evidence 狀態。
5. 在後台執行「測試RAG」，展示 10 張 synthetic 中文發票的 Hit Rate@K、MRR@K、平均延遲與 Failure / Fallback。
6. 展開 Agent trace，說明 deterministic planner 如何用 allowlisted tools 讀取欄位、搜尋文件並產生 source-backed answer。
7. 最後補充目前邊界：這是 demo-first MVP，不是 production DB / worker / RBAC / scanned PDF pipeline。

## 快速啟動

Windows CMD 進階 demo 全開版：

```bat
cd /d C:\Users\USER\Desktop\DocuRAG
docker-compose -f infra\docker-compose.yml up -d qdrant
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\qdrant-collection-smoke.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ollama-embedding-smoke.ps1
```

Backend terminal：

```bat
cd /d C:\Users\USER\Desktop\DocuRAG\backend
python -m pip install -e ".[dev,real-ocr]"

set "DOCURAG_AUTH_MODE=demo"
set "DOCURAG_AUTH_DEMO_SECRET=change-this-local-demo-secret"
set "DOCURAG_OCR_PROVIDER=paddleocr"
set "DOCURAG_LLM_PROVIDER=ollama"
set "DOCURAG_LLM_BASE_URL=http://127.0.0.1:11434"
set "DOCURAG_LLM_MODEL=qwen3.5:4b"
set "DOCURAG_VLM_PROVIDER=ollama"
set "DOCURAG_VLM_BASE_URL=http://127.0.0.1:11434"
set "DOCURAG_VLM_MODEL=qwen3.5:4b"
set "DOCURAG_RAG_RETRIEVAL_PROVIDER=hybrid_rerank"
set "DOCURAG_EMBEDDING_PROVIDER=ollama"
set "DOCURAG_EMBEDDING_BASE_URL=http://127.0.0.1:11434"
set "DOCURAG_EMBEDDING_MODEL=qwen3-embedding:0.6b"
set "DOCURAG_QDRANT_URL=http://127.0.0.1:6333"
set "DOCURAG_QDRANT_COLLECTION=docurag_chunks_v1"
set "DOCURAG_QDRANT_VECTOR_SIZE=1024"
set "DOCURAG_RERANK_PROVIDER=fastembed"
set "DOCURAG_RERANK_MODEL=BAAI/bge-reranker-base"

python -m uvicorn app.main:app --reload
```

Frontend terminal：

```bat
cd /d C:\Users\USER\Desktop\DocuRAG\frontend
set "VITE_API_BASE_URL=http://127.0.0.1:8000"
npm.cmd install
npm.cmd run dev
```

Demo UI：

```text
http://localhost:5173
```

Demo login：`admin / demo-admin-pass`、`analyst / demo-analyst-pass`、`viewer / demo-viewer-pass`。

API docs：

```text
http://127.0.0.1:8000/docs
```

Baseline validation：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1
```

進階 demo 可另外啟動 PaddleOCR GPU、Ollama、Qdrant、FastEmbed reranker 或 local VLM provider；完整設定與版本紀錄請看 [README_DEV.md](./README_DEV.md)。

## 目前邊界

目前仍刻意不宣稱下列 production 能力已完成：

- production-grade VLM parser、scanned PDF OCR pipeline、多頁文件處理或表格重建。
- scanned PDF rendering / OCR pipeline；目前只支援 text-native PDF 文字層抽取，不做 PDF page image conversion、layout analysis 或 scanned PDF OCR。
- PostgreSQL schema、migration、正式登入、RBAC、tenant isolation 或 project permission；Phase 28 demo auth mode 只是本機展示用角色閘門。
- Redis、NATS、background worker、async queue、production indexing pipeline。
- OpenAI API / vLLM serving、production eval dashboard、自訂 eval dataset、LLM-as-judge 或 answer faithfulness scoring；v0.29.0「測試RAG」只是 built-in retrieval benchmark。
- K8s deployment hardening。

## 文件入口

- [README_DEV.md](./README_DEV.md)：完整開發紀錄、release log、ticket 進度與本地開發備忘。
- [docs/PRD.md](./docs/PRD.md)：MVP 產品需求。
- [docs/architecture.md](./docs/architecture.md)：目前架構與延後項目。
- [docs/ROADMAP.md](./docs/ROADMAP.md)：phase / milestone 路線圖。
- [docs/demo-script.md](./docs/demo-script.md)：面試 demo 講解腳本。
- [docs/api.md](./docs/api.md)：API contract 補充。
- [tasks/](./tasks/)：ticket-first 開發任務票。
