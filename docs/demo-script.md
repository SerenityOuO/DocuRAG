# Demo Script

此 demo script 用於面試展示，目標是在 5 到 10 分鐘內說清楚產品價值與工程取捨。

## 1. Project Intro

DocuRAG AgentOps 是一個面試展示用的 AI 文件平台，展示文件上傳、OCR、local RAG、citation trace、retrieval evaluation 與 AgentOps 產品思維。

目前可展示的是受控 single-user / local-demo MVP：v0.17.0 已完成 frontend trace visibility，v0.18.0 是 `hybrid_rerank` planning-only，v0.19.0 已把 `hybrid_rerank` 落地成 optional eval runner strategy。Phase 20 的目標是把這條主線包裝成面試可快速理解的 demo，而不是宣稱已是 production-ready 平台。

## 2. Architecture

說明目前架構分成四層：

- FastAPI backend：health、document upload/list/detail、OCR、RAG query、manual vector indexing 與 retrieval eval runner。
- Local persistence：以 repo-local `data/` 保存 metadata、uploads、OCR result 與 chunks，避免在 MVP 階段提前加入 database schema。
- Optional AI runtime：PaddleOCR GPU provider、Ollama generation / embedding、Qdrant vector retrieval、FastEmbed rerank adapter 都採 explicit opt-in。
- Vue demo UI：支援 upload、document detail、OCR result、RAG answer、citations、retrieved chunks 與 compact trace panel。

要講清楚的取捨：`/rag/query` 預設仍是 deterministic keyword baseline；`vector`、`vector_rerank`、`hybrid` 與 `hybrid_rerank` 用於 optional demo / eval runner，不是 default production retrieval。

## 3. Demo Flow

```text
00:00 - 01:00  Project intro: document AI platform, not just a chatbot.
01:00 - 02:30  Upload a sample document and show metadata / document detail.
02:30 - 04:00  Run OCR or mock override, then show OCR text and generated chunks.
04:00 - 05:30  Ask a RAG question and show deterministic answer, citations and retrieved chunks.
05:30 - 07:00  Open trace panel and explain retrieval source, candidate rows and fallback states.
07:00 - 08:30  Run retrieval eval smoke and explain Hit Rate@K, MRR@K, Recall@K and trace metadata count.
08:30 - 10:00  Explain optional strategies: vector, vector_rerank, hybrid and hybrid_rerank.
```

## 4. Interview Talking Points

- 不只做 Chatbot，而是設計可觀測、可評估的 RAG 平台。
- Citation 與 trace 是文件型 AI 系統可信度的核心。
- MVP 刻意控制 scope：single-user、本機 demo、explicit opt-in runtime、每張 ticket 可單獨驗證。
- Phase 18 是 `hybrid_rerank` planning-only，Phase 19 才是 optional `hybrid_rerank` eval implementation。
- 已完成 provider-selected PaddleOCR、optional vector retrieval、optional vector rerank eval、optional hybrid eval、optional hybrid rerank eval 與 frontend trace visibility。
- 仍未完成 production eval dashboard、Auth/RBAC、PostgreSQL、Redis、NATS、worker、Agent runtime、VLM parser、PDF rendering 或 deployment hardening。

## 5. Demo Media

- `docs/demo-media/frontend-overview.png`：frontend health、upload panel 與 local API boundary。
- `docs/demo-media/frontend-trace.png`：RAG answer、retrieval trace table、citations 與 retrieved chunks。
- `docs/demo-media/eval-summary.png`：retrieval eval smoke summary，展示 `case_count=20`、Hit Rate@K、MRR@K、Recall@K、failure count 與 trace metadata count。

這些素材只使用 repo 內公開 synthetic sample data，不包含真實個資、公司文件、本機 token 或外部服務截圖。

## 6. Demo Guardrails

- 不把 optional eval strategy 說成 default `/rag/query` production path。
- 不把 local JSON storage 說成 production database。
- 不把 PaddleOCR provider-selected flow 說成完整 production OCR pipeline。
- 不把 Phase 20 packaging 說成新增 runtime feature；Phase 20 只補 demo readiness、sample / eval coverage、media 與 final validation。
