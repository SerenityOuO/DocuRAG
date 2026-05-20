# Product Requirements Document

## Product Summary

DocuRAG AgentOps 是一個面試展示用的 AI 文件平台。長期目標是整合文件上傳、OCR/VLM 解析、RAG 問答、citation trace、RAG 評估與 AI Agent tool-use，展示端到端 AI Application Engineering 能力。

目前 MVP 不追求一次完成所有 AI 與 infra 元件，而是先建立清楚的產品邊界、文件規格與可逐步開發的任務票。

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

## MVP Scope

MVP 初期聚焦 Phase 00 到 Phase 02：

- Phase 00：建立文件、任務票、開發規範與 roadmap。
- Phase 01：建立最小 backend healthcheck 與 Docker 啟動邊界。
- Phase 02：建立文件上傳 API 與 document metadata schema 基礎。

## Out of MVP for Current Phase

以下能力屬於後續階段，不在 Phase 00 文件與任務票建立範圍：

- backend 程式碼實作。
- FastAPI app 建立。
- Vue app 建立。
- package manager 檔案。
- OCR / VLM parser。
- RAG、rerank 與 citation generation。
- Qdrant、Redis、NATS、vLLM。
- 登入、權限或資料庫 schema 實作。

## Success Criteria

- README 能在 3 分鐘內說明專案目標、MVP 範圍與開發方向。
- AGENTS 能指引 Codex 後續用小 ticket 開發。
- TODO 有 Phase 00 到 Phase 02 的 checklist。
- docs 中有 PRD、MVP architecture 與 roadmap。
- tasks 中每張 ticket 都有 Goal、Scope、Out of Scope、Files likely to change、Acceptance Criteria 與 Validation。
- 每張 ticket 都足夠小，完成後可以單獨 commit。

## Product Risks

| Risk | Mitigation |
|---|---|
| 過早引入完整 AI pipeline 導致範圍失控 | 用 ticket 的 Out of Scope 明確限制。 |
| 架構文件過度設計 | `docs/ARCHITECTURE.md` 只描述 MVP 架構與延後元件。 |
| 後續 Codex 任務切太大 | 用 `tasks/_TEMPLATE.md` 固定票券格式。 |
| 實作與文件不同步 | 每張 ticket 完成後更新 TODO 與相關 docs。 |
