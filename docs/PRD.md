# Product Requirements Document

## Product Summary

DocuRAG AgentOps 是一個面試展示用的 AI 文件平台。長期目標是整合文件上傳、OCR/VLM 解析、RAG 問答、citation trace、RAG 評估與 AI Agent tool-use，展示端到端 AI Application Engineering 能力。

目前 MVP 不追求一次完成所有 AI 與 infra 元件，而是用 single-user / local-demo 邊界逐步交付可展示切片。到 v0.19.0 為止，主線已具備文件上傳、provider-selected OCR、local RAG、citation trace、retrieval eval runner、frontend trace visibility，以及 optional vector / rerank / hybrid / `hybrid_rerank` eval strategy。Phase 20 聚焦 interview MVP packaging，不把 production runtime 提前塞進目前 MVP。

## Problem

企業內部常有大量 PDF、掃描檔、發票、合約與報告。這些文件通常有三個痛點：

- 非結構化內容難以查詢與分析。
- 一般 RAG chatbot 難以解釋檢索品質與回答來源。
- 真實企業應用需要 API、權限、任務狀態、可觀測性與部署邊界。

## Product Goals

- 建立可展示的文件智能平台骨架。
- 保留後續 OCR、VLM parser、RAG、rerank、eval 與 Agent 的擴充位置。
- 讓每個功能以小 ticket 逐步交付，每次完成後都能單獨 commit。
- 用 README、docs 與 tasks 讓面試官快速理解專案價值與工程取捨。

## Target Users

| User | Need |
|---|---|
| Admin | 管理系統設定、使用者與服務狀態。 |
| Manager | 建立文件專案、查看文件處理與評估結果。 |
| Analyst | 上傳文件、查看解析結果、使用問答與引用來源。 |
| Viewer | 查詢文件內容與查看 citation。 |

## Current MVP Scope

目前受控 MVP 已完成或可展示：

- FastAPI backend health、document upload/list/detail、metadata persistence 與 local JSON storage。
- Provider-selected PaddleOCR OCR flow、mock OCR override、OCR line normalization、chunks 與 citation metadata。
- Local keyword RAG baseline，回傳 deterministic answer、citations、retrieved chunks 與 trace metadata。
- Optional Ollama generation、manual vector indexing、Qdrant vector retrieval、FastEmbed rerank adapter、`vector_rerank` / `hybrid` / `hybrid_rerank` eval strategy。
- Retrieval evaluation runner，輸出 Hit Rate@K、MRR@K、Recall@K、latency、failure / fallback count 與 trace metadata count。
- Vue demo UI，支援 upload、document detail、OCR result、RAG chat、citations、retrieved chunks 與 compact trace panel。
- README、demo script、roadmap、TODO 與 tickets，支援 5 到 10 分鐘面試展示。

## Out of Current MVP

以下能力仍屬於後續階段，不在目前 Phase 20 interview MVP packaging 範圍：

- Production eval dashboard、strategy comparison page 或 live eval runner UI。
- Default-on vector retrieval、default-on rerank、default-on hybrid / `hybrid_rerank` chat path。
- LLM-as-judge、answer faithfulness scoring、citation quality scoring、query rewriting 或 BM25 dependency。
- VLM parser、PDF rendering、image preprocessing、多頁 production OCR pipeline。
- PostgreSQL schema、multi-user project isolation、登入、RBAC 或權限管理。
- Redis、NATS、async worker、queue、Agent runtime、K8s 或 deployment hardening。

## Success Criteria

- README 與 demo script 能在 5 到 10 分鐘內說明 upload -> OCR -> RAG -> citation -> trace -> eval 的核心價值。
- AGENTS 能指引 Codex 後續用小 ticket 開發。
- TODO 有 Phase 00 到 Phase 20 的 checklist。
- docs 中有 PRD、MVP architecture、demo script 與 roadmap。
- tasks 中每張 ticket 都有 Goal、Scope、Out of Scope、Files likely to change、Acceptance Criteria 與 Validation。
- 每張 ticket 都足夠小，完成後可以單獨 commit。

## Product Risks

| Risk | Mitigation |
|---|---|
| 過早引入完整 AI pipeline 導致範圍失控 | 用 ticket 的 Out of Scope 明確限制。 |
| 架構文件過度設計 | `docs/ARCHITECTURE.md` 只描述 MVP 架構與延後元件。 |
| 後續 Codex 任務切太大 | 用 `tasks/_TEMPLATE.md` 固定票券格式。 |
| 實作與文件不同步 | 每張 ticket 完成後更新 TODO 與相關 docs。 |
