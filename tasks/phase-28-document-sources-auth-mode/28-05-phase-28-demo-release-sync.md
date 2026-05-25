# 28-05 Phase 28 Demo Release Sync

## Goal

完成 Phase 28 release sync，確認文件來源擴充與 demo login mode 可以作為 `v0.28.0` 展示版本：

- `.txt` 直接進 chunks / RAG / Qdrant / Agent，不再走 mock OCR。
- text-native PDF 可抽文字後進 chunks / RAG / Qdrant / Agent。
- scanned PDF 有清楚 pending / unsupported 狀態，不假裝已完成。
- demo login mode 可登入、登出、取得目前使用者，並依 role 控制 ingestion 功能。

## Scope

- 重跑 Phase 28 final validation：backend tests、frontend build、demo smoke、必要的 PDF / text focused smoke、Browser login / role check。
- 同步 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION` 與 `.env.example`。
- 更新 README、backend README、frontend README、docs/api.md、docs/architecture.md、docs/demo-script.md、TODO.md 與 docs/ROADMAP.md。
- 確認文件說法不誇大：Phase 28 是 direct text + text-native PDF + demo auth，不是 scanned PDF OCR、正式 RBAC、PostgreSQL tenant isolation 或 production worker。
- 確認 Phase 27 的 `27-02` / `27-03` 狀態不被錯誤標成已完成，除非那些 ticket 已在同一 release 前完成。

## Out of Scope

- 不新增版本 tag，除非使用者或 ticket 明確指定 tag 名稱。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、SSO、OAuth、MFA、K8s 或 deployment 設定。
- 不新增 scanned PDF rendering / OCR pipeline。
- 不改 embedding model、rerank algorithm、Agent planner 或 VLM parser behavior，除非前置 Phase 28 ticket 已明確要求。

## Release Impact

- Target version: `v0.28.0`.
- Version bump required: yes.
- 原因：Phase 28 改變 upload / ingestion / login 的使用者可見主流程，需形成明確 release 紀錄。

## Files likely to change

- `backend/pyproject.toml`
- `backend/app/core/config.py`
- `backend/tests/test_health.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/api/client.ts`
- `infra/docker-compose.yml`
- `.env.example`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/demo-script.md`
- `docs/ROADMAP.md`
- `TODO.md`

## Acceptance Criteria

- [x] `/health` 回傳 `0.28.0`。
- [x] `.txt` demo flow 可完成 direct ingestion、RAG query、Agent search。
- [x] text-native PDF demo flow 可完成 PDF text extraction、RAG query、Agent search；scanned PDF 顯示 clear pending / unsupported state。
- [x] Demo auth flow 可登入 Admin / Analyst / Viewer；Viewer 無法操作 ingestion write API。
- [x] README / docs 明確說明 Phase 28 不等於正式 RBAC、tenant isolation、production worker 或 scanned PDF OCR。
- [x] `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 28 狀態與 validation 結果已同步。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Browser check for local frontend: login flow, Admin / Analyst ingestion, Viewer read-only, desktop and mobile width without horizontal overflow.
- `rg -n "v0.28.0|Phase 28|text_upload|pdf_text|pdf_scanned_pending_ocr|DOCURAG_AUTH_MODE|demo auth|role guard" README.md backend/README.md frontend/README.md docs/api.md docs/architecture.md docs/demo-script.md docs/ROADMAP.md TODO.md backend/app frontend/src scripts infra tasks/phase-28-document-sources-auth-mode`
- `git diff --check`

## Validation Result

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`185 passed`（僅 pytest cache 權限警告）；測試涵蓋 direct text、text-native PDF、scanned / empty PDF pending state、demo auth role guard 與 health version `0.28.0`。
- `npm.cmd run build` 通過。
- `DOCURAG_AUTH_MODE=demo` backend 下執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 通過，health version `0.28.0`，包含 admin login、direct text ingestion、parser、Agent run、vector fallback 與 RAG query。
- Browser check 通過：`v0.28.0` label 可見，login screen 可見，Admin 登入後可看到 ingestion upload control，Viewer 登入後 upload controls 隱藏且後台入口 disabled；desktop 1280px 與 mobile 390px 無 horizontal overflow。
- `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
