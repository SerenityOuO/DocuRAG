# v0.7.0 Real OCR Demo Hardening

## Goal

把 Phase 07 real OCR spike 整理成可重跑 demo：文件說明、sample input、smoke validation 與 fallback 指引都要清楚，讓沒有安裝 real OCR dependency 的環境仍可使用 mock demo。

## Scope

- 更新 README、backend README、frontend README 與 LOCAL_DEV_SETUP，說明 real OCR provider 安裝與 fallback。
- 若需要 sample OCR input，加入不含敏感資料的公開或自造 sample。
- 更新 demo / smoke script，只驗證可攜的 mock flow；real OCR validation 必須是 optional。
- 明確標示 real OCR 是 spike，不是 production OCR pipeline。
- 確認 Docker / local dev 不會因缺少 real OCR dependency 而完全不可用。

## Out of Scope

- 不要求 CI 安裝 real OCR binary。
- 不新增 queue、worker、Redis、NATS、Qdrant、embedding、rerank、LLM、PostgreSQL、登入或 RBAC。
- 不建立 production OCR quality benchmark。
- 不新增 job dashboard。

## Files likely to change

- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/LOCAL_DEV_SETUP.md`
- `scripts/demo-smoke-test.ps1`
- `scripts/seed-demo-data.ps1`
- `sample-data/documents/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] README 清楚說明 mock flow 與 optional real OCR flow。
- [ ] 缺少 real OCR dependency 時 mock demo 仍可重跑。
- [ ] smoke test 不因 real OCR dependency 缺失而失敗。
- [ ] sample data 不包含真實個資或公司敏感資料。
- [ ] 文件明確標示 Phase 07 不包含 queue、DB、Qdrant、embedding、LLM 或權限系統。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`
