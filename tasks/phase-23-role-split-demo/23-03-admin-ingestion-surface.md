# 23-03 Admin / Analyst Ingestion Surface

## Goal

把文件上傳與 OCR 操作移到明確的後台知識庫管理入口，讓 Admin / Analyst 的 ingestion flow 與 Viewer Chat 分離，但仍沿用現有 backend API 與 local MVP ingestion 能力。

## Scope

- 在 frontend 建立明確的後台知識庫管理 surface，例如同一 SPA 內的 admin mode、hash route 或簡單分頁；命名需清楚表達 Admin / Analyst / Knowledge Base Ingestion。
- 後台 surface 可以使用既有 API：
  - `POST /documents/upload`
  - `POST /documents/{document_id}/ocr`
  - `POST /documents/{document_id}/ocr/mock` 作為 real OCR failure 後的手動 fallback
  - `GET /documents`
  - `GET /documents/{document_id}/ocr`
- 後台 surface 顯示處理狀態：uploaded、OCR running / completed / failed、local chunks ready / not ready，以及 real OCR failure reason。
- 文案需說明現階段 ingestion 完成的是 backend upload + provider-selected OCR + local chunking；VLM parser、production indexing 與 worker pipeline 尚未完成。
- 不讓後台入口出現在 Viewer Chat 的主要工作流中；可以用次要導覽或明確 admin link 進入。

## Out of Scope

- 不新增真實登入、RBAC、role guard、multi-user project boundary 或 permission checks。
- 不新增 backend endpoint、worker、Redis、NATS、PostgreSQL、database migration 或 async queue。
- 不新增 VLM parser、PDF rendering、多頁 OCR pipeline、automatic Qdrant indexing、default-on vector retrieval 或 production ingestion scheduler。
- 不改 PaddleOCR provider、OCR normalization、LLM provider、RAG provider 或 retrieval eval runner。

## Release Impact

- Target version: `v0.23.0`
- Version bump required: no
- 原因：本 ticket 是 Phase 23 的後台 ingestion UI 子切片；完整 release sync 由 `23-04` 完成。

## Files likely to change

- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `frontend/README.md`
- `TODO.md`

## Acceptance Criteria

- [x] 文件上傳與 OCR 操作只出現在明確的 Admin / Analyst ingestion surface。
- [x] 後台 ingestion surface 成功上傳後會呼叫 provider-selected OCR，real OCR 失敗時保留手動 mock fallback。
- [x] 後台 surface 顯示 document processing / OCR / local chunks 狀態，不宣稱已完成 VLM parser 或 production indexing。
- [x] Viewer Chat 與 Admin / Analyst ingestion 有明確導覽或模式切換，但首頁主流程仍是 Viewer Chat。
- [x] 既有 API contract 不變，frontend build 通過。

## Validation

- `cd frontend; npm.cmd run build`
- Browser 檢查 local frontend：Viewer Chat 首屏無 upload；Admin / Analyst ingestion surface 可看到 upload / OCR flow。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `rg -n "Admin|Analyst|Knowledge Base|Ingestion|知識庫管理|provider-selected|mock fallback|VLM parser|production indexing" frontend/src frontend/README.md TODO.md`
- `git diff --check`
