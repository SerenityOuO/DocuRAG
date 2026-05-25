# DocuRAG

> 開發紀錄、ticket 進度、版本更新日誌與本地開發備忘請見：[README_DEV.md](./README_DEV.md)

DocuRAG AgentOps 是一個面試展示用的 AI 文件平台 side project，目標是把文件上傳、OCR / VLM 解析、RAG 問答、retrieval trace、評估指標與 Agent tool-use 串成一個可驗證的端到端 demo。

這不是單純的聊天機器人範例，而是用受控 MVP 展示 AI Application Engineering 的完整切片：API contract、模型 provider 邊界、fallback 策略、trace metadata、evaluation runner、frontend demo surface 與 ticket-first 開發流程。

## 目前狀態

目前文件中的最新已完成展示版本是 `v0.27.0`。Phase 28 已有 backlog 規劃，但尚未標記完成。

已可展示的主線能力：

- Vue 3 + Vite frontend：Viewer Chat、Admin / Analyst ingestion surface、structured fields、Agent trace。
- FastAPI backend：health、document upload/list/detail、OCR、parser、RAG、Agent run、manual vector indexing API。
- PaddleOCR GPU-first OCR flow：provider-selected OCR 預設走 PaddleOCR，mock OCR 只作手動 fallback。
- VLM-first parser provider spike：`vlm_invoice` 優先，provider unavailable / invalid response 時 fallback 到 deterministic parser。
- Default `hybrid_rerank` RAG / Agent search：優先走 hybrid rerank，Ollama embedding、Qdrant 或 FastEmbed 不可用時回到 keyword evidence。
- Retrieval eval runner：輸出 Hit Rate@K、MRR@K、Recall@K、latency、failure / fallback count 與 trace metadata count。
- Deterministic Agent tool-use MVP：用 allowlisted read-only tools 串接 structured fields、document search 與 invoice summary。

## 技術亮點

- **清楚的 AI provider 邊界**：OCR、LLM、VLM、embedding、reranker 都有明確 provider / fallback policy，不把外部 runtime availability 偽裝成一定成功。
- **RAG 可觀測性**：回答不只輸出文字，也保留 citations、retrieved chunks、retrieval source、answer source 與 trace metadata。
- **評估不是附屬品**：內建 retrieval eval dataset 與 smoke runner，可比較 keyword、vector、vector_rerank、hybrid、hybrid_rerank 策略。
- **面試可講的產品邊界**：Viewer 只查詢既有知識庫；Admin / Analyst 才操作 upload、OCR、parser、indexing 與 Agent trace。
- **ticket-first 工程流程**：每個功能用小 ticket 控制 Goal、Scope、Out of Scope、Acceptance Criteria 與 Validation，避免提前塞入 DB、worker、auth 等未排定能力。

## 架構概覽

```text
Vue Frontend
  |-- Viewer Chat
  |-- Admin / Analyst Ingestion
  |-- Structured Fields / Agent Trace
          |
FastAPI Backend
  |-- Document / OCR / Parser APIs
  |-- RAG Query / Agent Run APIs
  |-- Retrieval Eval Runner
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
2. 啟動 frontend，展示 Viewer Chat 對既有知識庫提問，觀察 answer source、retrieval source 與 citations。
3. 切到 Admin / Analyst ingestion，展示文件上傳、OCR、parser structured fields 與 ingestion 狀態。
4. 展示 Agent trace，說明 deterministic planner 如何用 allowlisted tools 讀取欄位、搜尋文件並產生 source-backed answer。
5. 展示 retrieval eval smoke 結果，說明 Hit Rate@K、MRR@K、Recall@K 與 fallback count 如何幫助分析 RAG 品質。
6. 最後補充目前邊界：這是 demo-first MVP，不是 production DB / worker / RBAC / scanned PDF pipeline。

## 快速啟動

Backend：

```powershell
cd backend
py -3.12 -m pip install -e ".[dev]"
py -3.12 -m uvicorn app.main:app --reload
```

Frontend：

```powershell
cd frontend
npm.cmd install
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
- PostgreSQL schema、migration、正式登入、RBAC、tenant isolation 或 project permission。
- Redis、NATS、background worker、async queue、production indexing pipeline。
- OpenAI API / vLLM serving、production eval dashboard、LLM-as-judge 或 answer faithfulness scoring。
- K8s deployment hardening。

## 文件入口

- [README_DEV.md](./README_DEV.md)：完整開發紀錄、release log、ticket 進度與本地開發備忘。
- [docs/PRD.md](./docs/PRD.md)：MVP 產品需求。
- [docs/architecture.md](./docs/architecture.md)：目前架構與延後項目。
- [docs/ROADMAP.md](./docs/ROADMAP.md)：phase / milestone 路線圖。
- [docs/demo-script.md](./docs/demo-script.md)：面試 demo 講解腳本。
- [docs/api.md](./docs/api.md)：API contract 補充。
- [tasks/](./tasks/)：ticket-first 開發任務票。
