# Phase 46 Admin Document Delete Flow

## Goal

讓 Admin / Analyst 可以在後台「資料匯入狀態」直接刪除文件紀錄與本機上傳檔案，補齊使用者在匯入管理流程中期待的刪除操作。

## Scope

- 新增 role-gated `DELETE /documents/{document_id}` API。
- 刪除 local JSON / opt-in PostgreSQL metadata 中的文件、chunks、parser fields 與 processing jobs。
- 刪除本機 upload artifact 與 PDF page image artifact，並維持 path safety 檢查，避免刪到 data dir 外部檔案。
- 前端後台資料匯入狀態新增「刪除文件」按鈕、確認訊息、刪除中 / 成功 / 失敗狀態。
- Viewer 在 demo / formal auth mode 下不可刪除文件。
- 同步 `v0.46.0` release version、README / README_DEV、backend README、frontend README、TODO、ROADMAP 與 validation 紀錄。

## Out of Scope

- 不新增 Agent destructive tool、任意 SQL、shell、filesystem command 或外部 side-effect tool。
- 不新增 production approval workflow、audit storage、restore / recycle bin、soft delete、batch delete 或 multi-review deletion workflow。
- 不新增 Qdrant vector cleanup API、production indexing worker、Redis / NATS worker 清理流程、database migration、schema 變更或 deployment 變更。
- 不刪除 eval dataset、eval item、Agent run history 或其他非目標 document 的資料。
- 不回溯修復既有已錯誤保存的舊 metadata。

## Release Impact

- Target version: `v0.46.0`
- Version bump required: yes
- 原因：本 ticket 新增使用者可見的後台文件刪除能力與 backend API，需要同步 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、README_DEV、backend README、frontend README、TODO 與 ROADMAP。

## Files likely to change

- `backend/app/api/routes/documents.py`
- `backend/app/repositories/document_metadata.py`
- `backend/app/schemas/documents.py`
- `backend/app/services/document_storage.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_health.py`
- `backend/app/core/config.py`
- `frontend/src/api/client.ts`
- `frontend/src/App.vue`
- `frontend/package.json`
- `frontend/package-lock.json`
- `.env.example`
- `infra/docker-compose.yml`
- `scripts/demo-smoke-test.ps1`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/api.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-46-admin-document-delete/46-01-admin-document-delete-flow.md`

## Acceptance Criteria

- [x] Admin / Analyst 可呼叫 `DELETE /documents/{document_id}` 刪除可存取的文件。
- [x] Viewer 呼叫文件刪除 API 會收到 `403 forbidden`。
- [x] 刪除成功後文件不再出現在文件列表，文件詳情回 `404`。
- [x] 刪除成功後本機 upload artifact 與 PDF page image artifact 會被移除；不存在的 artifact 不會阻止 metadata 刪除。
- [x] 前端後台資料匯入狀態每筆文件有明確「刪除文件」操作，刪除後列表即時更新。
- [x] `v0.46.0` 版本與文件同步完成，且未提前實作 out-of-scope 項目。

## Validation

- `python -m pytest backend/tests/test_documents.py backend/tests/test_auth.py backend/tests/test_health.py -q`
- `npm.cmd run build`
- `rg -n "v0.46.0|0.46.0|DELETE /documents|deleteDocument|刪除文件|Phase 46" README.md README_DEV.md backend/README.md frontend/README.md docs/api.md docs/ROADMAP.md TODO.md backend frontend scripts infra tasks/phase-46-admin-document-delete`
- `git diff --check`

## Completion Notes

- Backend 新增 `DELETE /documents/{document_id}`，沿用既有 ingestion write guard 與 project access check；Admin / Analyst 可刪，Viewer forbidden。
- `DocumentStorage.delete_document()` 會刪除目標 document metadata、本機 upload artifact 與 PDF page image artifact；missing artifact 不阻止刪除，unsafe path 會被 skipped。
- Frontend 後台資料匯入狀態新增「刪除文件」按鈕，成功後即時移除列表紀錄並顯示成功訊息。
- `v0.46.0` release version、README / README_DEV、backend README、frontend README、TODO、ROADMAP、API 文件與 smoke expected version 已同步。
- Validation 已通過：focused backend document / auth / health tests、frontend build、Phase 46 keyword `rg` 與 `git diff --check`。
