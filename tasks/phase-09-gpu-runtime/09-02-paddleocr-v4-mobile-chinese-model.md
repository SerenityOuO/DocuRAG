# 09-02 PaddleOCR PP-OCRv4 Mobile Chinese Model

## Goal

讓 PaddleOCR provider 使用 PP-OCRv4 mobile 系列模型處理中文與中英混合文件，並清楚記錄繁中支援邊界。

## Scope

- 將 PaddleOCR 初始化改成可指定模型版本與語言，目標為 PP-OCRv4 mobile。
- 評估並固定 model selection：`PP-OCRv4_mobile_det` 與 `PP-OCRv4_mobile_rec`，以中文 / 中英混合 OCR 為主要驗證目標。
- 驗證官方模型清單中的中文能力：PP-OCRv4 mobile detection 支援中英文與多語種文本偵測；PP-OCRv4 mobile recognition 支援中英文與數字識別。
- 使用中文 sample image 驗證 provider-selected OCR。
- 針對繁中建立明確驗證結果；若 PP-OCRv4 mobile 對繁中不足，只記錄限制與後續選項，不在本 ticket 自動改用 PP-OCRv3 繁中專用模型。
- 更新文件說明模型 cache、模型目錄與切換方式。

## Out of Scope

- 不啟用 GPU runtime；由 `09-01` 負責。
- 不改用 server model、VLM parser 或 PaddleOCR v5，除非後續 ticket 明確決策。
- 不做 PDF rendering、image preprocessing、版面分析、表格抽取或 OCR quality tuning。
- 不新增 embedding、Qdrant、rerank、LLM、worker、Redis、NATS、資料庫 schema、登入或權限。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/api/routes/documents.py`
- `backend/app/services/ocr.py`
- `backend/tests/test_documents.py`
- `scripts/check-dev-env.ps1`
- `docs/LOCAL_DEV_SETUP.md`
- `backend/README.md`

## Acceptance Criteria

- [ ] PaddleOCR provider 可設定並使用 PP-OCRv4 mobile 中文 / 中英模型。
- [ ] 文件列出實際使用的 det / rec / cls model directory。
- [ ] 中文 sample image OCR 可完成，並保存 line text、bbox、confidence 與 trace metadata。
- [ ] 繁中 sample 的結果被記錄；若效果不足，文件明確說明限制與下一步候選模型。
- [ ] mock OCR path 不受模型設定影響。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr`
- 手動以中文與繁中 sample image 執行 provider-selected OCR，確認結果或清楚失敗原因。
