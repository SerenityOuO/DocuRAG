# 09-01 PaddleOCR Chinese Language Support

## Goal

讓 provider-selected PaddleOCR 可以支援中文與中英混合文件，並保留目前英文 sample OCR 的可重跑驗證。

## Scope

- 將 PaddleOCR language 從硬編碼 `en` 改成可設定值，例如 `DOCURAG_OCR_LANG`。
- 文件化建議值：英文 `en`、簡中 / 通用中文 `ch`、繁中場景的限制與驗證方式。
- 更新 local dev 說明，提醒第一次切換語言時會下載對應 PaddleOCR model cache。
- 新增或調整最小測試，確認 provider 初始化會使用設定的 language。

## Out of Scope

- 不啟用 GPU。
- 不實作 PDF rendering、image preprocessing、版面分析或表格抽取。
- 不新增 embedding、Qdrant、rerank、LLM、worker、Redis、NATS、資料庫 schema、登入或權限。
- 不承諾 OCR 品質調校；本 ticket 只處理可設定語言與可驗證 baseline。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/api/routes/documents.py`
- `backend/app/services/ocr.py`
- `backend/tests/test_documents.py`
- `scripts/check-dev-env.ps1`
- `docs/LOCAL_DEV_SETUP.md`
- `backend/README.md`

## Acceptance Criteria

- [ ] 未設定 `DOCURAG_OCR_LANG` 時仍維持既有英文 OCR baseline 可用。
- [ ] 設定 `DOCURAG_OCR_LANG=ch` 時，`PaddleOcrProvider` 使用中文模型初始化。
- [ ] 文件說明中文 / 中英混合 OCR 的啟動方式與模型 cache 行為。
- [ ] mock OCR path 不受 language 設定影響。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr`
- 手動以中文 sample image 執行 provider-selected OCR，確認可回傳中文文字或清楚失敗原因。
