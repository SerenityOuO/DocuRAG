# Sample Eval Data

此目錄提供 DocuRAG AgentOps 的公開 evaluation fixture。Phase 13 先建立 retrieval evaluation baseline，用固定 query set 驗證 keyword baseline 與 optional vector retrieval 的命中率、MRR 與 recall。

目前資料集：

- `retrieval-eval.json`：最小 retrieval eval dataset，使用 `sample-data/documents/` 既有虛構 invoice 與 support contract sample。

## Data Safety

資料集只引用公開虛構 sample documents：

- `mock-invoice-aurora.txt`
- `mock-contract-support.txt`

內容不包含真實個資、真實客戶資料、真實供應商資料或公司敏感資訊。請勿在此目錄提交真實文件或私有資料。

## Dataset Schema

`retrieval-eval.json` 是 JSON array，每筆 case 包含：

- `id`：穩定 eval case id。
- `query`：要送入 retrieval 的查詢文字。
- `top_k`：此 case 的 retrieval cutoff。
- `expected_document_filenames`：期望命中的 sample document filename list。Phase 13 不依賴固定 document id。
- `expected_chunk_hints`：期望命中 chunk 的文字線索，供 runner 判斷 evidence 是否合理。
- `expected_terms`：必須能在 sample evidence 中找到的關鍵字。
- `tags`：分類標籤，例如 `invoice`、`contract`、`support`、`date`、`amount`。
- `notes`：補充 case 來源或預期 evidence。

## Runner Usage

後續 `13-03` runner 會讀取此 dataset，對每筆 case 執行 keyword baseline retrieval；optional vector mode 必須在明確 env、Qdrant collection 與 manual vector indexing 完成後才執行。

Baseline eval 不依賴 Ollama embedding 或 Qdrant。Phase 13 不使用此 dataset 評估 answer faithfulness、citation quality、rerank 或 hybrid search。
