# 09-04 PaddleOCR Performance Observability and Tuning

## Goal

加入 OCR timing log / baseline，並用小範圍參數實驗評估 `cls=True`、startup warmup、圖片尺寸與 PaddleOCR 推論參數對速度的影響，收斂 Phase 09 OCR performance hardening。

## Scope

- 在 PaddleOCR provider 加入 timing measurement，至少記錄 engine preload / inference / normalization / total duration。
- 將 OCR timing 以 backend log 與 safe metadata 形式輸出，方便 demo 與 smoke test 觀察單張圖片耗時。
- 建立本機 baseline 記錄，包含 sample image、GPU runtime、模型設定、圖片尺寸、`cls` 設定、warmup 狀態與 OCR duration。
- 評估 `cls=True` / `cls=False` 對速度與 sample OCR 結果的影響，並把選定預設值寫入文件。
- 評估 startup warmup 是否能降低第一張圖的 request latency；若採用 warmup，必須維持 09-03 的 provider lifecycle 邊界。
- 評估圖片尺寸與少量 PaddleOCR inference 參數對速度的影響，只允許採納可清楚驗證且不擴大 pipeline 的設定。
- 更新 README / backend README / TODO / ROADMAP，記錄 baseline 結果、預設參數與限制。

## Out of Scope

- 不新增 worker queue、Redis、NATS、資料庫 schema、登入或權限。
- 不實作 PDF rendering、多頁 OCR pipeline、image preprocessing pipeline、版面分析、表格抽取或 production-grade OCR tuning。
- 不新增外部 APM、metrics backend、Prometheus、OpenTelemetry 或 tracing service。
- 不改用 server model、VLM parser、PaddleOCR v5 或繁中專用 recognition model。
- 不接 LLM、Ollama、vLLM、embedding、Qdrant 或 rerank。

## Release Impact

- Target version: `v0.9.1`。
- Version bump required: yes，本 ticket 收斂 Phase 09 performance hardening patch release。
- 完成後同步更新 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP。

## Files likely to change

- `backend/app/services/ocr.py`
- `backend/app/core/config.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_health.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/App.vue`
- `infra/docker-compose.yml`
- `scripts/check-dev-env.ps1`
- `docs/LOCAL_DEV_SETUP.md`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Provider-selected PaddleOCR OCR 會輸出可讀 timing log。
- [ ] OCR result metadata 包含安全的 timing 欄位，可用來比較單張圖片耗時。
- [ ] 文件記錄至少一組 baseline：sample image、GPU runtime、模型設定、圖片尺寸、`cls` 設定、warmup 狀態與 total duration。
- [ ] 文件記錄 `cls=True` / `cls=False` 評估結果與最終預設值。
- [ ] 文件記錄 startup warmup 是否採用，以及採用 / 不採用原因。
- [ ] 若調整 PaddleOCR 推論參數，測試與文件需說明對 mock path 無影響。
- [ ] Phase 10 Qwen3 / Ollama / RAG demo scope 不包含本 ticket 的 OCR performance work。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr`
- 手動以 sample invoice 與繁中 sample image 各執行 provider-selected OCR，記錄 timing log 與 baseline 結果。
