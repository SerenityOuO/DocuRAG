# v0.5.1 Demo Hardening

## Goal

讓 v0.5.0 的 upload -> OCR mock -> local RAG -> citations 流程更適合 GitHub 與面試展示，提供可公開 sample data、可重跑的 demo seed script、API smoke test 與清楚的 README demo flow。

## Scope

- 建立 1 到 3 份可公開 demo sample 文件，不包含真實個資或公司敏感資料。
- 建立 demo seed script，自動上傳 sample 文件、執行 OCR mock、執行一個 RAG query，並輸出 answer、citations、retrieved chunks。
- 建立可重跑的 API demo smoke test，驗證 `/health`、upload、OCR mock 與 `/rag/query`。
- 強化 OCR mock，讓公開 text sample 的內容可以進入 deterministic mock OCR text，方便 local keyword RAG demo 命中具體欄位。
- 更新 README demo flow，加入 5 分鐘 demo 指令、backend、frontend、Docker 啟動方式、範例問題與預期結果。
- 更新 `TODO.md`、`docs/ROADMAP.md`、`backend/README.md` 與 `frontend/README.md`。
- backend version 更新為 `0.5.1`。
- frontend package version 更新為 `0.5.1`。
- 測試與 Docker 驗證通過後 commit、建立 `v0.5.1` tag，並 push `main` 與 `v0.5.1`。

## Out of Scope

- 不做 Qdrant。
- 不做 embedding。
- 不做 rerank。
- 不接真正 LLM。
- 不接 OpenAI API。
- 不接 Ollama 或 vLLM。
- 不做 Redis 或 NATS。
- 不做 PostgreSQL、資料庫 schema 或 migration。
- 不做登入、RBAC 或權限。
- 不改既有 `v0.1.0` 到 `v0.5.0` tags。
- 不做 force push。
- 不開始 v0.6.0。

## Files likely to change

- `sample-data/documents/*`
- `scripts/seed-demo-data.ps1`
- `scripts/demo-smoke-test.ps1`
- `backend/app/core/config.py`
- `backend/app/api/routes/rag.py`
- `backend/app/services/document_storage.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_health.py`
- `backend/tests/test_rag.py`
- `backend/pyproject.toml`
- `frontend/src/App.vue`
- `frontend/package.json`
- `frontend/package-lock.json`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `infra/docker-compose.yml`

## Acceptance Criteria

- [x] `sample-data/` 內有 1 到 3 份可公開 demo 文件。
- [x] demo sample 不包含真實個資或公司敏感資料。
- [x] demo seed script 可自動完成 upload、OCR mock 與 RAG query。
- [x] demo seed script 輸出 answer、citations、retrieved chunks。
- [x] demo smoke test 可重跑並驗證 `/health`、upload、OCR mock 與 `/rag/query`。
- [x] README 有 5 分鐘 demo 指令。
- [x] README 說明 backend、frontend 與 Docker 啟動方式。
- [x] README 有範例問題與預期結果。
- [x] README 說明目前是 local keyword RAG baseline，不是 embedding、Qdrant 或 LLM。
- [x] `TODO.md`、`docs/ROADMAP.md`、`backend/README.md` 與 `frontend/README.md` 已更新。
- [x] backend version 更新為 `0.5.1`。
- [x] frontend package version 更新為 `0.5.1`。
- [x] `/health` 回傳 `0.5.1`。
- [x] backend pytest 通過。
- [x] frontend build 通過。
- [x] Docker build 通過。
- [x] Docker Compose 驗證通過。
- [x] demo seed script 可以跑完 upload、OCR mock、RAG query。
- [x] 測試通過後建立 commit 與 `v0.5.1` tag。
- [x] push `main` 與 `v0.5.1` 成功。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1`
- `curl http://127.0.0.1:8000/health`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`
