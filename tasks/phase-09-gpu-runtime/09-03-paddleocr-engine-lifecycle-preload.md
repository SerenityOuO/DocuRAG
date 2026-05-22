# 09-03 PaddleOCR Engine Lifecycle Preload

## Goal

讓 backend 在啟動階段初始化並持有 PaddleOCR engine，後續 provider-selected OCR request 重用同一個 provider / engine，避免每次 OCR request 都重新 cold start。

## Scope

- 在 backend app startup path 初始化 selected OCR provider；當 `DOCURAG_OCR_PROVIDER=paddleocr` 時，預先載入 PaddleOCR engine。
- 調整 provider dependency / factory，讓同一個 backend process 內的 provider-selected OCR request 重用已初始化的 `PaddleOcrProvider` instance。
- 將 `PaddleOcrProvider` 的 engine loading 變成明確 lifecycle 方法，讓 startup preload 與 request-time extraction 使用同一條初始化邏輯。
- 保留 mock OCR override path；`POST /documents/{document_id}/ocr/mock` 不應觸發 PaddleOCR preload。
- PaddleOCR preload 失敗時必須有清楚錯誤行為與 log，不可靜默 fallback 到 mock。
- 補上最小測試，確認 request dependency 不再每次建立新的 PaddleOCR provider / engine。

## Out of Scope

- 不做 OCR timing log、baseline 表、效能參數調校或 warmup 實驗；由 `09-04` 處理。
- 不新增 worker queue、Redis、NATS、資料庫 schema、登入或權限。
- 不實作 PDF rendering、多頁 OCR pipeline、image preprocessing、版面分析、表格抽取或 production-grade OCR tuning。
- 不改變 PP-OCRv4 mobile 模型選擇；`09-02` 已固定模型設定。
- 不接 LLM、Ollama、vLLM、embedding、Qdrant 或 rerank。

## Release Impact

- Target version: `v0.9.1`。
- Version bump required: no，本 ticket 是 Phase 09 performance hardening 的第一張；最終 patch release 版本更新由 `09-04` 收斂。
- 完成後更新 TODO 與相關文件，標示 Phase 09 performance hardening 尚未 release complete。

## Files likely to change

- `backend/app/main.py`
- `backend/app/api/routes/documents.py`
- `backend/app/services/ocr.py`
- `backend/app/core/config.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_health.py`
- `README.md`
- `backend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Backend startup 可在 selected provider 為 PaddleOCR 時預先初始化 OCR engine。
- [ ] Provider-selected OCR request 不再每次建立新的 PaddleOCR engine。
- [ ] 第二次以上 OCR request 可重用同一個 process 內已載入的 engine。
- [ ] PaddleOCR preload 失敗時有明確錯誤與 log，不會自動改跑 mock。
- [ ] Mock OCR override path 不受 PaddleOCR preload 影響。
- [ ] 測試可驗證 provider reuse / engine lifecycle 行為。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr`
- 手動啟動 backend，確認 startup log 顯示 PaddleOCR preload 結果。
- 連續對同一張 sample image 執行兩次 provider-selected OCR，確認第二次 request 不重新 cold start engine。
