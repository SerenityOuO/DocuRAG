# 08-01 PaddleOCR Environment Baseline

## Goal

釐清目前 Windows 本機與 Docker 環境中 PaddleOCR 無法穩定執行的實際失敗點，建立後續修復 ticket 的可重現 baseline。

## Scope

- 檢查 backend 以 `DOCURAG_OCR_PROVIDER=paddleocr` 啟動時的 Python、`paddleocr`、`paddlepaddle` 與模型初始化狀態。
- 建立或更新最小環境檢查流程，能輸出 PaddleOCR dependency import、engine 初始化與 sample image OCR 的結果。
- 記錄本機與 Docker 是否需要分開處理。
- 保存實際錯誤訊息與重現指令到既有開發文件或 ticket 記錄。

## Out of Scope

- 不修改 OCR response schema。
- 不改 RAG、Qdrant、embedding、Redis、NATS、worker、LLM、登入、權限或資料庫 schema。
- 不把 PDF rendering、image preprocessing 或 batch OCR 納入本 ticket。
- 不靜默 fallback 到 mock provider。

## Files likely to change

- `docs/LOCAL_DEV_SETUP.md`
- `scripts/check-dev-env.ps1`
- `scripts/demo-smoke-test.ps1`
- `backend/README.md`

## Acceptance Criteria

- [ ] 可以用一組明確指令重現 PaddleOCR 目前的環境問題。
- [ ] 檢查結果能區分 dependency import、engine initialization、model download 與 runtime OCR failure。
- [ ] 文件記錄 Windows 本機與 Docker 的觀察結果。
- [ ] 若 PaddleOCR 不可用，backend 仍回傳清楚錯誤，不改跑 mock。

## Validation

- 從 repo root 執行 PaddleOCR 環境檢查指令。
- 從 repo root 執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr`，保存成功或失敗結果。
