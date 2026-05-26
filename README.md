# DocuRAG

> 開發紀錄、ticket 進度、版本更新日誌與本地開發備忘請見：[README_DEV.md](./README_DEV.md)

文件知識庫問答與後台管理。

DocuRAG 是面試展示用的 AI 文件客服助理，將文件上傳、OCR / VLM 解析、hybrid RAG、引用來源、RAG 評估與 Agent tool-use 串成可本機驗證的 demo。主線聚焦「前台查詢、後台建庫」：Viewer 詢問已建立的知識庫，Admin / Analyst 建立文件資料並查看解析細節。

## 畫面預覽

![前台知識庫查詢](docs/demo-media/readme-viewer-query.jpg)

![後台知識庫管理](docs/demo-media/readme-admin-ingestion.jpg)

<<<<<<< HEAD
- Vue 3 + Vite frontend：Viewer Chat、Admin / Analyst ingestion surface、structured fields、Agent trace。
- FastAPI backend：health、demo auth、document upload/list/detail、OCR、parser、RAG、Agent run、manual vector indexing API。
- PaddleOCR GPU-first OCR flow：provider-selected OCR 預設走 PaddleOCR，mock OCR 只作手動 fallback。
- VLM-first parser provider spike：`vlm_invoice` 優先，request 會帶原始圖片與 compact OCR context；Ollama `response` / `thinking` / fenced JSON 會被正規化，欄位值可對回 OCR line / bbox，provider unavailable / timeout / invalid response 時 fallback 到 deterministic parser。
- Default `hybrid_rerank` RAG / Agent search：優先走 hybrid rerank，Ollama embedding、Qdrant 或 FastEmbed 不可用時回到 keyword evidence。
- Direct `.txt` ingestion：`.txt` 上傳後直接建立 `text_upload` chunks，可被 RAG、Qdrant vector indexing 與 Agent search 使用，不再先包成 mock OCR。
- Text-native PDF ingestion：可複製文字的 PDF 會抽文字層並建立 `pdf_text` chunks，保留 page number；scanned / empty PDF 只標示 `pdf_scanned_pending_ocr`。
- Document Source Router contract：文件來源已明確分成 `image_ocr`、`text_upload`、`pdf_text` 與 `pdf_scanned_pending_ocr`，不把文字檔、PDF 與 OCR 混成同一路徑。
- 後台多檔依序 ingestion：Admin / Analyst 可在檔案選擇器一次選多個文件，frontend 逐檔呼叫既有 upload / OCR / parser / vector indexing 流程；不是 batch API、queue 或 background worker。
- Demo auth mode：`DOCURAG_AUTH_MODE=demo` 會啟用 Admin / Analyst / Viewer demo login、`/auth/login` / `/auth/me` / `/auth/logout` 與 backend write API role guard；預設仍是 `disabled`，且不是正式 RBAC。
- 後台「測試RAG」：Admin / Analyst 可直接執行內建 10 張 synthetic 中文發票 retrieval benchmark，固定 `hybrid_rerank`，只呈現 Hit Rate@K、MRR@K、平均延遲與 Failure / Fallback。
- Retrieval eval runner：輸出 Hit Rate@K、MRR@K、Recall@K、latency、failure / fallback count 與 trace metadata count。
- Deterministic Agent tool-use MVP：用 allowlisted read-only tools 串接 structured fields、document search 與 invoice summary。
=======
## 功能
>>>>>>> b8ba5379cb5100c5c9e032d4df58ebaae2880b67

- 前台知識庫問答
- 回答引用來源
- 後台文件匯入
- PaddleOCR 優先 OCR
- VLM-first 欄位解析
- Hybrid rerank 檢索
- 內建 RAG 測試
- Agent tool-use trace

## 需求

<<<<<<< HEAD
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
4. 切到 Admin / Analyst ingestion，展示單檔或多檔依序上傳、OCR 文字層、VLM parser structured fields 與欄位 evidence 狀態。
5. 在後台執行「測試RAG」，展示 10 張 synthetic 中文發票的 Hit Rate@K、MRR@K、平均延遲與 Failure / Fallback。
6. 展開 Agent trace，說明 deterministic planner 如何用 allowlisted tools 讀取欄位、搜尋文件並產生 source-backed answer。
7. 最後補充目前邊界：這是 demo-first MVP，不是 production DB / worker / RBAC / scanned PDF pipeline。
=======
- Python 3.12
- Node.js 18+
- 本機可選 Ollama
- 本機可選 Qdrant
- 本機可選 PaddleOCR GPU
>>>>>>> b8ba5379cb5100c5c9e032d4df58ebaae2880b67

## 快速啟動

Backend：

```bat
cd /d C:\Users\USER\Desktop\DocuRAG\backend
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

Frontend：

```bat
cd /d C:\Users\USER\Desktop\DocuRAG\frontend
npm.cmd install
set "VITE_API_BASE_URL=http://127.0.0.1:8000"
npm.cmd run dev
```

Demo UI：

```text
http://localhost:5173
```

API docs：

```text
http://127.0.0.1:8000/docs
```

## 使用方式

1. 用 Admin 登入後台。
2. 上傳文件或圖片。
3. 執行 OCR 與欄位解析。
4. 建立可查詢知識庫。
5. 回到前台送出問題。
6. 查看回答與引用來源。

Demo 帳號：

```text
admin / demo-admin-pass
analyst / demo-analyst-pass
viewer / demo-viewer-pass
```

若未啟用 `DOCURAG_AUTH_MODE=demo`，系統會以無登入的本機 demo 模式啟動。

## 技術棧

- Frontend：Vue 3、Vite、TypeScript
- Backend：FastAPI、Pydantic、pytest
- OCR / VLM：PaddleOCR、Ollama-compatible VLM
- RAG：Ollama embedding、Qdrant、FastEmbed reranker
- Storage：本機 JSON metadata 與 uploaded files
- Workflow：ticket-first 小步開發

## API 串接

- `GET /health`：檢查服務版本與狀態。
- `POST /documents/upload`：上傳文件。
- `POST /documents/{document_id}/ocr`：執行 OCR。
- `POST /documents/{document_id}/parse`：解析欄位。
- `POST /documents/{document_id}/index/vector`：建立向量索引。
- `POST /rag/query`：送出知識庫問題。
- `POST /eval/rag/built-in`：執行內建 RAG 測試。
- `POST /agent/run`：執行 demo-safe Agent task。

## 開發與驗證

Backend tests：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1
```

Demo smoke：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1
```

Retrieval eval：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1
```

完整進階設定、release log 與本地驗證紀錄請看 [README_DEV.md](./README_DEV.md)。

## 目前邊界

<<<<<<< HEAD
目前仍刻意不宣稱下列 production 能力已完成：

- production-grade VLM parser、scanned PDF OCR pipeline、多頁文件處理、batch upload worker 或表格重建。
- scanned PDF rendering / OCR pipeline；目前只支援 text-native PDF 文字層抽取，不做 PDF page image conversion、layout analysis 或 scanned PDF OCR。
- PostgreSQL schema、migration、正式登入、RBAC、tenant isolation 或 project permission；Phase 28 demo auth mode 只是本機展示用角色閘門。
- Redis、NATS、background worker、async queue、production indexing pipeline。
- OpenAI API / vLLM serving、production eval dashboard、自訂 eval dataset、LLM-as-judge 或 answer faithfulness scoring；v0.29.0「測試RAG」只是 built-in retrieval benchmark。
- K8s deployment hardening。
=======
目前是面試展示用 MVP，不宣稱已完成 production 系統。尚未包含正式 RBAC、tenant isolation、PostgreSQL schema、Redis、NATS、worker、scanned PDF OCR pipeline、K8s hardening、自訂 eval dashboard 或 production autonomous Agent。
>>>>>>> b8ba5379cb5100c5c9e032d4df58ebaae2880b67

## 文件入口

- [README_DEV.md](./README_DEV.md)：完整開發紀錄、release log、ticket 進度與本地開發備忘。
- [docs/PRD.md](./docs/PRD.md)：MVP 產品需求。
- [docs/architecture.md](./docs/architecture.md)：目前架構與延後項目。
- [docs/ROADMAP.md](./docs/ROADMAP.md)：phase / milestone 路線圖。
- [docs/demo-script.md](./docs/demo-script.md)：面試 demo 講解腳本。
- [docs/api.md](./docs/api.md)：API contract 補充。
- [tasks/](./tasks/)：ticket-first 開發任務票。
