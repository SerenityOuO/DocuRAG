# Sample Documents

此目錄提供 demo 可公開使用的 sample documents。內容皆為 demo-safe synthetic / 虛構資料，只用於展示 upload -> OCR mock -> local keyword RAG -> citations -> trace -> eval flow。

目前樣本：

- `mock-invoice-aurora.txt`：虛構 invoice，適合查詢 `payment due date`、`AUR-2026-051` 或 `Net 15`。
- `mock-invoice-orion.txt`：虛構 SaaS invoice，適合查詢 `ORN-2026-118`、`2026-06-30`、tax / amount due 或 line items。
- `rag-eval-invoice-01-nvdla.txt` 到 `rag-eval-invoice-10-docurag.txt`：Phase 29 內建 RAG 評估用 synthetic 中文發票 fixture，共 10 張，供應商分布為 `NVDLA` 1 張、`GOOGLE` 1 張、`OpenAI` 1 張、`Intel` 3 張、`DocuRAG` 4 張；每份皆可作為 `.txt` direct ingestion 匯入後台知識庫。
- `mock-contract-support.txt`：虛構 support contract excerpt，適合查詢 `SLA`、`renewal date` 或 `support credits`。
- `mock-contract-harbor.txt`：虛構 data processing addendum，適合查詢 termination notice、confidentiality period 或 export request acknowledgement。
- `mock-support-playbook.txt`：虛構 incident playbook，適合查詢 escalation channel、P1 response target、customer update cadence 或 demo-safe trace behavior。
- `sample-ocr-invoice.png`：自造 PNG invoice 圖片，只用於 optional Phase 07 provider-selected OCR demo，文字為 `OCR-2026-001`、`USD 42.00` 與 `2026-06-30`。
- `sample-ocr-zh-tw.png`：自造繁中 PNG 圖片，只用於 Phase 09 PP-OCRv4 mobile 中文 / 中英混合 OCR 驗證，文字包含 `DocuRAG 繁中 OCR 測試`、`OCR-2026-009`、`星河科技股份有限公司` 與 `NT$ 12,345`。

請勿在此目錄提交真實個資、真實客戶資料、公司內部文件或敏感內容。新增 sample 時應保留 synthetic / fictional 說明，並確保 eval expected evidence 可直接由公開 sample documents 支撐。
