# 08-03 PaddleOCR Default Flow Validation

## Goal

在 PaddleOCR dependency 修復後，驗證「預設走 PaddleOCR」的本機 demo flow 可以完成 upload -> provider-selected OCR -> OCR result -> local chunks。

## Scope

- 確認 `DOCURAG_OCR_PROVIDER` 的預設值是否應切為 `paddleocr`，並保留 `mock` 明確 override。
- 讓 `sample-data/documents/sample-ocr-invoice.png` 的 provider-selected OCR smoke check 成功完成。
- 驗證 real OCR result 會正確寫入 `OcrResult.lines`、chunks、processing status 與 processing job metadata。
- 更新 frontend / README / demo script 文字，讓使用者知道目前預設流程與 mock fallback 的使用方式。

## Out of Scope

- 不新增 PDF rendering。
- 不新增 image preprocessing、版面分析、多頁文件處理或 OCR accuracy tuning。
- 不新增 Qdrant、embedding、rerank、LLM、Redis、NATS、worker、登入、權限或資料庫 schema。
- 不把 PaddleOCR 失敗時改成靜默 mock fallback。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/services/ocr.py`
- `backend/tests/test_documents.py`
- `scripts/demo-smoke-test.ps1`
- `scripts/seed-demo-data.ps1`
- `frontend/src/App.vue`
- `frontend/README.md`
- `README.md`
- `TODO.md`

## Acceptance Criteria

- [ ] 不設定 `DOCURAG_OCR_PROVIDER` 時，provider-selected OCR 的預設行為符合本 ticket 決策。
- [ ] 設定 `DOCURAG_OCR_PROVIDER=mock` 時，mock demo 仍可完整重跑。
- [ ] 設定或預設 `paddleocr` 時，sample image OCR 回傳 `status=completed` 且 `extracted_fields.provider=paddleocr`。
- [ ] real OCR 完成後文件的 OCR、indexing、ready 與 latest job 狀態一致。
- [ ] frontend 文案不誤導使用者以為 PDF 或 production OCR pipeline 已完成。

## Validation

- `py -3 -m pytest`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr`
- 手動上傳 `sample-data/documents/sample-ocr-invoice.png` 並呼叫 `POST /documents/{document_id}/ocr`
