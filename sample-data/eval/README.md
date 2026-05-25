# Sample Eval Data

此目錄提供 DocuRAG AgentOps 的公開 evaluation fixture。Phase 13 先建立 retrieval evaluation baseline，用固定 query set 驗證 keyword baseline 與 optional vector retrieval 的命中率、MRR 與 recall。Phase 20 將 dataset 擴充到至少 20 筆 demo-safe synthetic cases，方便面試展示 invoice、contract / support、cross-document ambiguity、numeric lookup、multi-evidence、lexical mismatch 與 trace 說明。Phase 29 新增後台「測試RAG」專用 built-in dataset，固定用 `hybrid_rerank` 跑 10 張 synthetic 中文發票 retrieval benchmark。

目前資料集：

- `retrieval-eval.json`：retrieval eval dataset，使用 `sample-data/documents/` 既有虛構 invoice、support contract、data processing addendum 與 incident playbook sample。
- `built-in-rag-eval-zh-invoices.json`：後台「測試RAG」內建 dataset，使用 10 張 demo-safe synthetic 中文發票 fixture，供應商分布為 `NVDLA` 1、`GOOGLE` 1、`OpenAI` 1、`Intel` 3、`DocuRAG` 4；日期 / 金額皆不同且幣別皆為 TWD。

## Data Safety

資料集只引用公開虛構 sample documents：

- `mock-invoice-aurora.txt`
- `mock-invoice-orion.txt`
- `mock-contract-support.txt`
- `mock-contract-harbor.txt`
- `mock-support-playbook.txt`
- `zh-invoice-*.txt`

內容不包含真實個資、真實客戶資料、真實供應商資料或公司敏感資訊。`zh-invoice-*.txt` 若使用真實品牌名作為 vendor label，也只代表 synthetic demo invoice，不包含真實稅號、地址、logo、交易資料或付款資料。請勿在此目錄提交真實文件、外部下載資料或私有資料。新增 cases 必須能從公開 sample documents 找到 expected evidence。

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

`built-in-rag-eval-zh-invoices.json` 使用相同 schema，但只服務 v0.29.0 後台 built-in benchmark。它不是 OCR eval、PDF layout eval、VLM parser accuracy eval、LLM-as-judge 或 answer faithfulness scoring。

## Runner Usage

`retrieval-eval-smoke.ps1` 會讀取此 dataset，對每筆 case 執行 keyword baseline retrieval；optional vector、`vector_rerank`、`hybrid` 與 `hybrid_rerank` mode 必須透過 explicit flag、embedding / Qdrant preflight 與 manual vector indexing 完成後才執行。

`hybrid_rerank` 可用 `scripts/retrieval-eval-smoke.ps1 -RunHybridRerank` 明確 opt in。它只屬於 retrieval eval runner：先產生 hybrid candidates，再對 candidates 執行 optional rerank；不代表 `/rag/query`、frontend chat 或 production eval dashboard 已支援此策略。

v0.29.0 的後台「測試RAG」會呼叫 backend built-in API 直接載入 `built-in-rag-eval-zh-invoices.json`，策略固定為 `hybrid_rerank`，UI 只顯示 Hit Rate@K、MRR@K、平均延遲與 Failure / Fallback。若 embedding、Qdrant 或 reranker runtime 不可用，built-in API 會用明確 fallback metadata 回到 keyword evidence，不讓 UI 靜默假裝完整 vector / rerank 成功。

Baseline eval 不依賴 Ollama embedding、Qdrant 或 FastEmbed runtime。Optional runtime 不可用時，baseline keyword smoke 仍應可重跑；vector-backed optional smoke 會在 preflight 階段停止並回報缺少的 local runtime。

`hybrid_rerank` candidate metadata 會刻意分開 score source：`keyword_score` / `vector_score` 是 branch score，`merged_score` / `merged_rank` 是 hybrid merge 後的分數與排名，`rerank_score` / `rerank_rank` 是 reranker 結果，`final_score_source` 說明最後排序使用的是 rerank 或 fallback 分數。缺少 optional metadata 時，report 應顯示 `metadata unavailable` 或明確 fallback state，而不是把缺值當成錯誤。

## Summary Output

Eval result JSON 的 `summary` 會輸出：

- `case_count`：本次 eval cases 數量。
- `hit_rate_at_k`：top K 內至少命中一個 expected evidence 的比例。
- `mrr_at_k`：第一個 relevant chunk 的 reciprocal rank 平均值。
- `recall_at_k`：expected terms 或 expected evidence 覆蓋比例。
- `average_latency_ms`：每筆 case 的平均 retrieval latency。
- `failure_count`：真正讓該 strategy 失敗的 case 數；keyword baseline 應維持 `0`。
- `fallback_count`：有 optional branch fallback、rerank fallback 或 unavailable metadata 的 case 數。
- `trace_metadata_count`：retrieved chunks 中帶有 metadata 的筆數，方便確認 trace metadata 是否仍存在。
- `result_strategy_counts`：實際 result strategy 分布，例如 `keyword`、`vector_unavailable_fallback`、`hybrid` 或 `hybrid_rerank`。
- `fallback_reasons`：fallback / unavailable 原因與出現次數，用於 demo 摘錄與 regression 檢查。

此 dataset 不評估 answer faithfulness、citation quality、LLM-as-judge 或 production eval dashboard。
