# 21-01 Real GPU OCR Frontend Flow

## Goal

讓面試主線的 frontend upload 預設使用 provider-selected real GPU OCR (`POST /documents/{document_id}/ocr`)，失敗時才提示使用者可手動改用 mock OCR fallback，不再把 mock OCR 當作前端上傳主線。

## Scope

- 新增 Phase 21 / `v0.21.0` ticket，聚焦 real GPU OCR interview demo path。
- 更新 Vue frontend upload flow：文件上傳成功後呼叫 `runSelectedOcr`，成功時顯示 GPU OCR 已完成。
- real OCR 失敗時保留已上傳 document，顯示錯誤與 mock OCR fallback button；只有使用者手動點擊時才呼叫 `POST /documents/{document_id}/ocr/mock`。
- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `0.21.0`。
- 更新 README、backend README、frontend README、TODO、ROADMAP 與 demo script，說明面試主線是 real GPU OCR-first，mock 是無 GPU / runtime 失敗時的明確備援。

## Out of Scope

- 不修改 PaddleOCR provider、engine lifecycle、模型設定、OCR normalization 或 backend OCR API contract。
- 不新增 PDF rendering、image preprocessing、VLM parser、多頁 production OCR pipeline 或 OCR accuracy tuning。
- 不新增 default-on vector retrieval、default-on rerank、default-on hybrid / `hybrid_rerank` chat path、eval dashboard 或 streaming UI。
- 不新增 DB schema、Auth、RBAC、Redis、NATS、worker、queue、Agent runtime、deployment 或 K8s 設定。
- 不刪除 mock OCR endpoint；mock 只從 frontend 主線改為手動 fallback。

## Release Impact

- Target version: `v0.21.0`。
- Version bump required: yes。
- 原因：Phase 21 會改變面試 demo 的 frontend upload 主線，從 mock OCR ingestion 改為 provider-selected real GPU OCR-first flow，並形成新的 release 狀態與文件同步。

## Files likely to change

- `frontend/src/App.vue`
- `frontend/package.json`
- `frontend/package-lock.json`
- `backend/app/core/config.py`
- `backend/tests/test_health.py`
- `backend/pyproject.toml`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `docs/demo-script.md`

## Acceptance Criteria

- [x] Frontend upload 成功後預設呼叫 provider-selected `POST /documents/{document_id}/ocr`，不再直接呼叫 `/ocr/mock`。
- [x] real OCR 成功時，frontend 顯示 GPU OCR 完成並保留文件上傳摘要。
- [x] real OCR 失敗時，frontend 顯示錯誤、保留已上傳文件，並提供手動 mock OCR fallback button。
- [x] mock fallback 成功時，frontend 顯示已改用 mock OCR 備援完成；失敗時顯示 fallback error。
- [x] backend / frontend / Compose / health test version 同步到 `0.21.0`，frontend fallback label 同步到 `v0.21.0`。
- [x] README、backend README、frontend README、TODO、ROADMAP 與 demo script 都說明 Phase 21 / `v0.21.0` 的 real GPU OCR-first interview demo path。
- [x] 本 ticket 沒有新增 out-of-scope backend runtime、infra、auth、DB 或 deployment 功能。

## Validation

- `npm.cmd run build`（於 `frontend/`）
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr`
- `rg -n "v0.21.0|Phase 21|real GPU OCR|RunRealOcr" README.md backend/README.md frontend/README.md TODO.md docs/ROADMAP.md docs/demo-script.md tasks/phase-21-real-gpu-ocr-demo/21-01-real-gpu-ocr-frontend-flow.md`
- `git diff --check`

Validation result：

- `npm.cmd run build` 於 `frontend/` 通過。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`129 passed`（僅 pytest cache 權限警告）。
- Baseline `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 通過，health version `0.21.0`、answer source `ollama/qwen3.5:4b`、retrieval source `keyword baseline`。
- 以臨時 `DOCURAG_OCR_PROVIDER=paddleocr` backend 跑 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8012 -RunRealOcr` 通過，provider-selected OCR completed 且 metadata OK。
- Ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
