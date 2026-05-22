# 10-04 LLM Demo Smoke And UI Copy

## Goal

補齊 LLM-based RAG demo 的本機 smoke test、文件與最小 UI 狀態呈現，讓展示時可以分辨 deterministic baseline 與 LLM answer。

## Scope

- 更新 demo smoke script，加入 optional LLM smoke 參數。
- 更新 frontend copy / state，顯示目前 RAG answer 來源是 deterministic baseline 或 LLM provider。
- 更新 README / backend README / frontend README 的本機 demo 步驟。
- 確認未啟用 LLM 時既有 demo 仍可重跑。

## Out of Scope

- 不新增 streaming UI。
- 不新增模型下載管理。
- 不接 embedding、Qdrant、rerank、worker、Redis、NATS、資料庫 schema、登入或權限。
- 不改 OCR GPU 或 OCR model selection。

## Files likely to change

- `scripts/demo-smoke-test.ps1`
- `frontend/src/App.vue`
- `frontend/src/api/client.ts`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/LOCAL_DEV_SETUP.md`

## Acceptance Criteria

- [ ] 未啟用 LLM 時 demo smoke 仍通過。
- [ ] 啟用 optional LLM smoke 時，script 會驗證 LLM answer path。
- [ ] UI 能明確顯示 answer 來源。
- [ ] 文件說明如何啟動本機模型服務與執行 demo。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunLlm`
