# Demo Script

此 demo script 用於面試展示，目標是在 5 到 10 分鐘內說清楚產品價值與工程取捨。

## 1. Project Intro

DocuRAG AgentOps 是一個面試展示用的 AI 文件平台，展示文件上傳、OCR、local RAG、citation trace、retrieval evaluation 與 AgentOps 產品思維。

目前可展示的是受控 single-user / local-demo MVP：v0.17.0 已完成 frontend trace visibility，v0.18.0 是 `hybrid_rerank` planning-only，v0.19.0 已把 `hybrid_rerank` 落地成 optional eval runner strategy，v0.20.0 完成 interview packaging，v0.21.0 將 upload + OCR demo path 改為 real GPU OCR-first，v0.23.0 完成 Viewer Chat / Admin Ingestion role split，v0.24.0 補上 deterministic invoice parser fallback、parse / fields API 與 frontend structured fields surface，v0.25.0 補上 deterministic Agent tool-use trace，把 structured fields、document search 與 deterministic invoice summary 串成 source-backed final answer。這不是 production-ready 平台，而是可說清楚取捨的面試展示切片。

## 2. Architecture

說明目前架構分成四層：

- FastAPI backend：health、document upload/list/detail、OCR、parse / fields、Agent run / lookup、RAG query、manual vector indexing 與 retrieval eval runner。
- Local persistence：以 repo-local `data/` 保存 metadata、uploads、OCR result、parser result、Agent runs 與 chunks，避免在 MVP 階段提前加入 database schema。
- AI runtime：Admin / Analyst ingestion flow 使用 provider-selected PaddleOCR GPU OCR；Ollama generation / embedding、Qdrant vector retrieval、FastEmbed rerank adapter 仍採 explicit opt-in。
- Vue demo UI：Phase 23 產品邊界拆成 Viewer Chat 與 Admin / Analyst Ingestion。Viewer 只查詢已建立知識庫；文件上傳、OCR result、structured fields、Agent trace、chunks、document list、retrieved chunks、trace metadata 與 eval metrics 留在後台 surface、backend API、CLI 或 smoke scripts。

要講清楚的取捨：`/rag/query` 預設仍是 deterministic keyword baseline；`vector`、`vector_rerank`、`hybrid` 與 `hybrid_rerank` 用於 optional demo / eval runner，不是 default production retrieval。

## 3. Demo Flow

```text
00:00 - 01:00  Project intro: document AI platform, not just a chatbot.
01:00 - 02:30  Viewer Chat: ask the seeded knowledge base and show answer source, retrieval source and citations.
02:30 - 04:00  Admin / Analyst Ingestion: upload a sample image and let backend run provider-selected GPU OCR.
04:00 - 05:15  Trigger deterministic parser and show invoice structured fields with source trace.
05:15 - 06:45  Run Agent trace: deterministic plan -> allowlisted tools -> observations -> source-backed final answer.
06:45 - 07:30  Explain OCR -> structured fields -> Agent tool-use -> local chunks -> RAG citation flow without calling it production indexing.
07:30 - 08:30  Open trace panel and explain retrieval source, candidate rows and fallback states.
08:30 - 09:20  Run retrieval eval smoke and explain Hit Rate@K, MRR@K, Recall@K and trace metadata count.
09:20 - 10:00  Explain optional strategies: vector, vector_rerank, hybrid and hybrid_rerank.
```

## 4. Interview Talking Points

- 不只做 Chatbot，而是設計可觀測、可評估的 RAG 平台。
- Citation 與 trace 是文件型 AI 系統可信度的核心。
- Viewer Chat 與 Admin / Analyst Ingestion 是兩個產品入口：Viewer 問已建立的知識庫，Admin / Analyst 才負責上傳與 OCR。
- Phase 24 parser 是 deterministic MVP fallback：展示 OCR 後可抽 invoice structured fields、confidence 與 source text，並保留 future VLM-compatible contract。
- Phase 25 Agent 是 deterministic planner + allowlisted read-only tools：`get_document_fields`、`search_documents` 與 `summarize_invoice_fields`，不是 production autonomous Agent 或任意 tool execution。
- MVP 刻意控制 scope：single-user、本機 demo、explicit opt-in runtime、每張 ticket 可單獨驗證。
- Phase 18 是 `hybrid_rerank` planning-only，Phase 19 才是 optional `hybrid_rerank` eval implementation。
- 已完成 provider-selected PaddleOCR、frontend real GPU OCR-first upload、optional vector retrieval、optional vector rerank eval、optional hybrid eval、optional hybrid rerank eval 與 retrieval trace visibility。
- mock OCR 仍保留為無 GPU / runtime error 時的明確手動 fallback，不是 frontend upload 主線。
- 仍未完成 production VLM parser、LLM parser、production autonomous Agent、production eval dashboard、Auth/RBAC、PostgreSQL、Redis、NATS、worker、PDF rendering 或 deployment hardening。

## 5. Demo Media

- `docs/demo-media/frontend-overview.png`：早期 mixed UI 工程參考；Phase 23 live demo 以 localhost 的 Viewer Chat / Admin Ingestion 分流畫面為準。
- `docs/demo-media/frontend-trace.png`：早期 trace UI 工程參考；Phase 23 Viewer Chat 只顯示 answer source、retrieval source 與 citation summary，詳細 trace 改由 backend response、smoke script 或 eval CLI 檢查。
- `docs/demo-media/eval-summary.png`：retrieval eval smoke summary，展示 `case_count=20`、Hit Rate@K、MRR@K、Recall@K、failure count 與 trace metadata count。

這些素材只使用 repo 內公開 synthetic sample data，不包含真實個資、公司文件、本機 token 或外部服務截圖。

## 6. Demo Guardrails

- 不把 optional eval strategy 說成 default `/rag/query` production path。
- 不把 local JSON storage 說成 production database。
- 不把 PaddleOCR provider-selected flow 說成完整 production OCR pipeline。
- 不把 Viewer Chat 說成可以直接對圖片聊天；OCR 是 backend ingestion layer。
- 不把 Admin / Analyst ingestion surface 說成已完成 auth / RBAC 或正式權限系統。
- 不把 deterministic Agent trace 說成 production autonomous Agent、LLM planner、Agent permission model 或任意 tool execution。
- 不把 real OCR-first flow 說成已完成 PDF rendering、image preprocessing、VLM parser 或多頁 production OCR。
- 不把 deterministic parser fallback 說成真正 VLM parser、LLM parser、人工修正流程、欄位版本紀錄、worker 或 DB pipeline。
- 不把 Phase 20 packaging 說成新增 runtime feature；Phase 20 只補 demo readiness、sample / eval coverage、media 與 final validation；Phase 21 只改 frontend upload 主線與 mock fallback 呈現。
