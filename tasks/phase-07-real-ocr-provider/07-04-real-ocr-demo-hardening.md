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

## Implementation Notes

- 新增自造 sample image `sample-data/documents/sample-ocr-invoice.png`，內容是虛構 invoice，不含真實個資、真實客戶資料或公司敏感內容。
- `demo-smoke-test.ps1` 與 `seed-demo-data.ps1` 預設仍只驗證 mock flow。
- 兩支 demo script 新增 `-RunRealOcr` 與 `-RealOcrSamplePath`，讓 real OCR validation 成為 optional。
- optional real OCR check 若因 PaddleOCR dependency、模型或 provider 設定不可用而失敗，會輸出 warning，不會讓預設 mock demo 失效。
- README、backend README、frontend README、LOCAL_DEV_SETUP、ROADMAP、TODO 與 sample-data README 均補上 mock flow / optional real OCR flow 邊界。

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

- [x] README 清楚說明 mock flow 與 optional real OCR flow。
- [x] 缺少 real OCR dependency 時 mock demo 仍可重跑。
- [x] smoke test 不因 real OCR dependency 缺失而失敗。
- [x] sample data 不包含真實個資或公司敏感資料。
- [x] 文件明確標示 Phase 07 不包含 queue、DB、Qdrant、embedding、LLM 或權限系統。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`

## Validation Notes

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` passed: 46 tests passed.
- `cd frontend; npm.cmd run build` passed outside the sandbox; sandbox file permissions block Vite config resolution.
- `docker build -t docurag-backend ./backend` blocked because Docker Desktop daemon was not running (`dockerDesktopLinuxEngine` pipe not found).
- `docker compose -f infra/docker-compose.yml up -d --build` and `docker compose -f infra/docker-compose.yml down` were also blocked by the same Docker daemon issue.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` could not run immediately after Compose because the Compose backend was not started.
- Local uvicorn fallback validation passed: `demo-smoke-test.ps1`, `seed-demo-data.ps1`, and `demo-smoke-test.ps1 -RunRealOcr` all completed against a temp-data backend. The `-RunRealOcr` path warned when the provider-selected endpoint was still using default mock provider, as expected.
- Mock OCR path remains the default provider path and remains validated without real OCR dependency.
