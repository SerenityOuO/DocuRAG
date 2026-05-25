# TODO

本 checklist 追蹤 DocuRAG AgentOps 目前的 Phase 00 到 v0.27 Aggressive Demo Defaults backlog。每張 ticket 完成後應可單獨 commit，並更新對應項目。

## Release Version Map

已完成舊 ticket 不回填 `Release Impact`；從目前 release 修正與後續 backlog 起，Phase 與版本號必須明確對應：

- Phase 08 -> `v0.8.0`
- Phase 09 -> `v0.9.0`
- Phase 09 performance hardening -> `v0.9.1`
- Phase 10 -> `v0.10.0`
- Phase 11 -> `v0.11.0`
- Phase 12 -> `v0.12.0`
- Phase 13 -> `v0.13.0`
- Phase 14 -> `v0.14.0`
- Phase 15 -> `v0.15.0`
- Phase 16 -> `v0.16.0`
- Phase 17 -> `v0.17.0`
- Phase 18 -> `v0.18.0`
- Phase 19 -> `v0.19.0`
- Phase 20 -> `v0.20.0`
- Phase 21 -> `v0.21.0`
- Phase 22 -> `v0.22.0`
- Phase 23 -> `v0.23.0`
- Phase 24 -> `v0.24.0`
- Phase 25 -> `v0.25.0`
- Phase 26 -> `v0.26.0`
- Phase 27 -> `v0.27.0`

後續 ticket 若完成整個 Phase，必須同步更新版本號、README、TODO、ROADMAP 與 validation 狀態；若不 bump version，ticket 必須明確寫原因。

目前已完成優先順序：

1. `tasks/phase-09-gpu-runtime/09-03-paddleocr-engine-lifecycle-preload.md` 已完成。
2. `tasks/phase-09-gpu-runtime/09-04-paddleocr-performance-observability-tuning.md` 已完成。
3. `tasks/phase-10-llm-rag/10-01-qwen3-ollama-provider-decision.md` 已完成，只固定 Ollama `qwen3.5:4b` provider decision 與 env 文件。
4. `tasks/phase-10-llm-rag/10-02-ollama-qwen3-client.md` 已完成，只新增最小 Ollama client building block，未改變既有 `/rag/query` deterministic baseline 預設。
5. `tasks/phase-10-llm-rag/10-03-qwen3-rag-generation.md` 已完成，只在 retrieved chunks 與 query 上加入可選 generation path。
6. `tasks/phase-10-llm-rag/10-04-qwen3-demo-smoke.md` 已完成，補齊 demo smoke、UI answer source 與 `v0.10.0` release/version sync。
7. `tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md` 已完成，只固定 Phase 11 embedding / Qdrant provider decision 與 backlog，不新增 runtime。
8. `tasks/phase-11-vector-rag/11-02-ollama-embedding-client.md` 已完成，只新增 disabled-by-default Ollama embedding client。
9. `tasks/phase-11-vector-rag/11-03-qdrant-local-runtime.md` 已完成，只新增 optional Qdrant local runtime / collection smoke。
10. `tasks/phase-11-vector-rag/11-04-vector-retrieval-demo-smoke.md` 已完成，補齊 optional vector retrieval path、fallback trace metadata、demo smoke 與 `v0.11.0` release/version sync。
11. `tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md` 已完成，固定 manual vector indexing contract 與 guardrails。
12. `tasks/phase-12-vector-indexing/12-02-vector-indexing-service.md` 已完成，新增同步 vector indexing service / helper。
13. `tasks/phase-12-vector-indexing/12-03-vector-indexing-api.md` 已完成，新增手動 vector indexing API。
14. `tasks/phase-12-vector-indexing/12-04-vector-indexing-demo-smoke.md` 已完成，補齊 optional vector indexing smoke 與 `v0.12.0` release/version sync。
15. `tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md` 已完成，固定 retrieval evaluation contract。
16. `tasks/phase-13-retrieval-eval/13-02-retrieval-eval-dataset.md` 已完成，新增公開 retrieval eval dataset。
17. `tasks/phase-13-retrieval-eval/13-03-retrieval-eval-runner.md` 已完成，新增本機 retrieval eval runner。
18. `tasks/phase-13-retrieval-eval/13-04-retrieval-eval-demo-smoke.md` 已完成，補齊 retrieval eval smoke 與 `v0.13.0` release/version sync。

下一步優先順序：

1. `tasks/phase-14-retrieval-quality/14-01-rerank-provider-decision.md` 已完成，固定 Phase 14 retrieval quality planning boundary。
2. `tasks/phase-14-retrieval-quality/14-02-retrieval-quality-contract.md` 已完成，規劃 future rerank / hybrid trace contract。
3. `tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md` 已完成，規劃 eval dataset 擴充方向。
4. `tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md` 已完成，規劃 future demo / validation / release checklist。
5. `tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md` 已完成，選定 FastEmbed + `BAAI/bge-reranker-base` 作為 disabled-by-default `vector_rerank` runtime spike 起點。
6. `tasks/phase-15-rerank-runtime/15-02-rerank-provider-adapter.md` 已完成，新增 disabled-by-default FastEmbed rerank adapter building block。
7. `tasks/phase-15-rerank-runtime/15-03-vector-rerank-eval-integration.md` 已完成，將 optional `vector_rerank` 接入 retrieval eval runner。
8. `tasks/phase-15-rerank-runtime/15-04-rerank-demo-release-sync.md` 已完成，補齊 rerank demo / eval smoke 文件並完成 `v0.15.0` release/version sync。
9. `tasks/phase-16-hybrid-retrieval/16-01-hybrid-retrieval-contract.md` 已完成，固定 optional `hybrid` retrieval contract、merge policy、dedupe key 與 fallback trace metadata。
10. `tasks/phase-16-hybrid-retrieval/16-02-eval-dataset-expansion-json.md` 已完成，公開 retrieval eval dataset 已擴充到 12 筆並覆蓋 Phase 16 retrieval quality case tags。
11. `tasks/phase-16-hybrid-retrieval/16-03-hybrid-eval-strategy-integration.md` 已完成，將 optional `hybrid` 接入 retrieval eval runner 並新增 explicit `-RunHybrid` smoke flag。
12. `tasks/phase-16-hybrid-retrieval/16-04-hybrid-demo-release-sync.md` 已完成，補齊 hybrid demo / eval smoke 並執行 `v0.16.0` release/version sync。
13. `tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md` 已完成，固定 retrieval trace UI / eval visibility contract。
14. `tasks/phase-17-retrieval-trace-ui/17-02-frontend-retrieval-trace-panel.md` 已完成，在既有 RAG result UI 實作 frontend trace panel。
15. `tasks/phase-17-retrieval-trace-ui/17-03-eval-result-report-summary.md` 已完成，改善 eval result summary 與 fallback visibility。
16. `tasks/phase-17-retrieval-trace-ui/17-04-trace-ui-demo-release-sync.md` 已完成，補齊 trace UI / eval visibility demo validation 並執行 `v0.17.0` release/version sync。
17. `tasks/phase-18-hybrid-rerank-planning/18-01-hybrid-rerank-boundary-contract.md` 已完成，固定 `hybrid_rerank` planning boundary、candidate flow、trace metadata 與 fallback states。
18. `tasks/phase-18-hybrid-rerank-planning/18-02-hybrid-rerank-eval-dataset-plan.md` 已完成，規劃 future eval dataset case 類型、demo-safe 資料邊界與 metrics 摘要使用方式。
19. `tasks/phase-18-hybrid-rerank-planning/18-03-hybrid-rerank-trace-report-plan.md` 已完成，規劃 future trace / report visibility、report fields 與 missing metadata behavior。
20. `tasks/phase-18-hybrid-rerank-planning/18-04-phase-18-demo-release-plan.md` 已完成，規劃 future demo validation、release sync checklist 與 deferred items。
21. `tasks/phase-19-hybrid-rerank-runtime/19-01-hybrid-rerank-eval-provider.md` 已完成，實作 optional `hybrid_rerank` eval provider，將 hybrid candidates 交給 rerank service 重新排序。
22. `tasks/phase-19-hybrid-rerank-runtime/19-02-hybrid-rerank-smoke-flag.md` 已完成，新增 eval runner / smoke script 的 explicit `hybrid_rerank` strategy 與 `-RunHybridRerank` flag。
23. `tasks/phase-19-hybrid-rerank-runtime/19-03-hybrid-rerank-trace-report-sync.md` 已完成，補齊 `hybrid_rerank` trace / report visibility 與文件解讀。
24. `tasks/phase-19-hybrid-rerank-runtime/19-04-hybrid-rerank-demo-release-sync.md`：重跑 final validation，並在 Phase 19 完成時執行 `v0.19.0` release/version sync。
25. `tasks/phase-20-interview-mvp-packaging/20-01-interview-demo-doc-refresh.md`：更新面試 demo 文件，對齊目前已完成 runtime、Phase 18 planning-only 與 Phase 19 `hybrid_rerank` implementation 狀態。
26. `tasks/phase-20-interview-mvp-packaging/20-02-sample-eval-coverage-expansion.md`：補齊公開 sample data 與 retrieval eval dataset 覆蓋率，目標至少 5 份 sample documents 與 20 筆 eval cases。
27. `tasks/phase-20-interview-mvp-packaging/20-03-demo-media-and-readme-polish.md`：補齊 README 面試導覽、截圖或 GIF 等 demo media。
28. `tasks/phase-20-interview-mvp-packaging/20-04-final-interview-mvp-validation.md`：重跑 final validation，並在 Phase 20 完成時執行 `v0.20.0` release/version sync。
29. `tasks/phase-21-real-gpu-ocr-demo/21-01-real-gpu-ocr-frontend-flow.md`：將 frontend upload 面試主線改為 provider-selected real GPU OCR-first，mock OCR 只保留為手動 fallback，並同步 `v0.21.0` release 文件與版本。
30. `tasks/phase-22-rag-query-hardening/22-01-keyword-query-normalization.md`：強化 default keyword RAG query normalization，讓中文 query 與 demo-safe alias 可命中英文 OCR chunks，並同步 `v0.22.0` release 文件與版本。
31. `tasks/phase-23-role-split-demo/23-01-role-boundary-contract.md`：固定 Viewer Chat 與 Admin / Analyst Ingestion 的產品邊界，讓前台只負責查詢既有知識庫，後台才操作 upload / OCR / ingestion。
32. `tasks/phase-23-role-split-demo/23-02-viewer-chat-only-surface.md`：將 frontend 預設入口收斂為 Viewer Chat-only，不在前台主畫面顯示 upload / OCR / mock fallback。
33. `tasks/phase-23-role-split-demo/23-03-admin-ingestion-surface.md`：建立明確 Admin / Analyst 後台知識庫管理 surface，承接 upload、provider-selected OCR、狀態與手動 fallback。
34. `tasks/phase-23-role-split-demo/23-04-role-split-demo-release-sync.md`：完成 `v0.23.0` release/version sync 與 final validation。
35. `tasks/phase-24-vlm-parser-mvp/24-01-parser-contract.md`：固定 VLM-compatible parser contract、invoice structured fields、parser status 與 fallback metadata；文件 / contract ticket，不 bump version。
36. `tasks/phase-24-vlm-parser-mvp/24-02-invoice-parser-service.md`：實作 deterministic invoice parser service，從既有 OCR text 抽取 demo-safe structured fields，作為 future VLM / LLM parser fallback。
37. `tasks/phase-24-vlm-parser-mvp/24-03-document-fields-api.md`：新增 parse / fields API，將 parser result 保存到 local JSON metadata store。
38. `tasks/phase-24-vlm-parser-mvp/24-04-frontend-fields-surface.md`：在 Admin / Analyst ingestion surface 顯示 structured fields 摘要，Viewer Chat 仍保持只查詢。
39. `tasks/phase-24-vlm-parser-mvp/24-05-parser-demo-release-sync.md`：補齊 parser demo validation，並在 Phase 24 完成時執行 `v0.24.0` release/version sync。
40. `tasks/phase-25-agent-tool-use-mvp/25-01-agent-boundary-contract.md` 已完成，固定 Agent MVP boundary、allowlisted tools、deterministic planner 與 trace schema；文件 / contract ticket，不 bump version。
41. `tasks/phase-25-agent-tool-use-mvp/25-02-agent-tool-adapters.md` 已完成，實作 `get_document_fields`、`search_documents` 與 `summarize_invoice_fields` allowlisted tool adapters。
42. `tasks/phase-25-agent-tool-use-mvp/25-03-agent-run-api.md` 已完成，新增 `POST /agent/run` 與 `GET /agent/runs/{run_id}`，用 deterministic planner 串接 allowlisted tools。
43. `tasks/phase-25-agent-tool-use-mvp/25-04-frontend-agent-trace-surface.md` 已完成，在 demo UI 顯示 Agent plan、tool calls、observations、final answer 與 citations。
44. `tasks/phase-25-agent-tool-use-mvp/25-05-agent-demo-release-sync.md` 已完成，版本 / 文件 / smoke / Browser validation 已補齊。
45. `tasks/phase-26-vlm-parser-provider-spike/26-01-vlm-provider-decision.md` 已完成，固定 VLM provider env、input / output contract、fallback policy 與 Agent 承接方式；文件 / contract ticket，不 bump version。
46. `tasks/phase-26-vlm-parser-provider-spike/26-02-vlm-input-resolver.md` 已完成，新增 demo-safe image input resolver，只解析既有上傳檔案，不做 PDF rendering 或 VLM call。
47. `tasks/phase-26-vlm-parser-provider-spike/26-03-vlm-parser-adapter.md` 已完成，新增 VLM-first `vlm_invoice` parser adapter，輸出沿用 Phase 24 `DocumentFields` schema。
48. `tasks/phase-26-vlm-parser-provider-spike/26-04-parser-source-comparison.md` 已完成，在 API / trace 顯示 `deterministic_invoice` vs `vlm_invoice` 的 parser source、fallback reason 與 confidence。
49. `tasks/phase-26-vlm-parser-provider-spike/26-05-vlm-parser-demo-release-sync.md` 已完成，補齊 VLM parser demo validation、版本 / 文件同步與 `v0.26.0` release sync。
50. `tasks/phase-27-aggressive-defaults/27-01-aggressive-demo-defaults.md` 已完成，啟用 default `hybrid_rerank` RAG / Agent search、Ollama embedding、FastEmbed rerank adapter、frontend parser + vector indexing best-effort flow 與 `v0.27.0` release sync。

## Phase 00 - Bootstrap Documents and Tickets

- [x] 建立 Phase 00 文件與任務票規範。
- [x] 更新 `README.md`，說明專案目標、MVP 範圍與開發方向。
- [x] 更新 `AGENTS.md`，說明 Codex 後續如何用小 ticket 開發。
- [x] 建立 `docs/PRD.md`。
- [x] 建立 `docs/ARCHITECTURE.md`。
- [x] 建立 `docs/ROADMAP.md`。
- [x] 建立 `tasks/_TEMPLATE.md`。
- [x] 建立 Phase 00 到 Phase 02 的初始 ticket。
- [x] 執行 `tasks/phase-00-bootstrap/00-01-repo-structure.md`。
- [x] 執行 `tasks/phase-00-bootstrap/00-02-project-docs.md`。

## Phase 01 - Backend Bootstrap

- [x] 執行 `tasks/phase-01-backend-bootstrap/01-01-backend-healthcheck.md`。
- [x] 執行 `tasks/phase-01-backend-bootstrap/01-02-backend-docker.md`。
- [x] 確認 backend healthcheck 可以用 ticket 指定方式驗證。
- [x] 確認 Docker 啟動邊界只涵蓋 Phase 01 所需範圍。

## Phase 02 - Document Foundation

- [x] 執行 `tasks/phase-02-document-foundation/02-01-document-upload-api.md`。
- [x] 執行 `tasks/phase-02-document-foundation/02-02-document-metadata-schema.md`。
- [x] 確認文件上傳 API 不觸發 OCR、RAG 或 async worker。
- [x] 確認 document metadata schema 可支援後續 OCR 與 RAG 狀態，但不提前實作資料庫遷移。

## MVP v0.1 Local Verification

- [x] 建立 `scripts/check-dev-env.ps1`。
- [x] 建立 `scripts/test-backend.ps1`。
- [x] 建立 `docs/LOCAL_DEV_SETUP.md`。
- [x] 診斷 Python：`py` launcher 不存在，`python` 目前無法執行。
- [x] 診斷 Docker：`docker` CLI 不在 PATH。
- [x] 修復本機 Python 後重跑 `scripts/test-backend.ps1`。
- [x] 修復 Docker 後重跑 `docker build` 與 `docker compose build`。

## MVP v0.2 Demo UI

- [x] 建立 GitHub Actions `Backend CI` workflow。
- [x] 建立最小 Vue 3 + Vite + TypeScript frontend。
- [x] frontend 可呼叫 `GET /health`。
- [x] frontend 可選擇檔案並呼叫 `POST /documents/upload` stub。
- [x] backend 加上 local frontend CORS 設定。
- [x] 建立 `frontend/README.md`。
- [x] 更新 demo 啟動與驗證文件。
- [x] 驗證 Docker CLI、Docker build 與 Docker Compose healthcheck。

## MVP v0.3 Document Local Storage

- [x] 將 `POST /documents/upload` 從 stub 升級為本機存檔。
- [x] 保存 document metadata 到 local JSON store。
- [x] 新增 `GET /documents` 文件列表 API。
- [x] 新增 `GET /documents/{document_id}` 文件詳情 API。
- [x] 新增安全下載端點 `GET /documents/{document_id}/download`。
- [x] 測試 unsafe filename 不會 path traversal。
- [x] frontend 顯示文件列表與 document metadata JSON。
- [x] Docker Compose 掛載 `data/` 並驗證 upload API。

## MVP v0.4 OCR Mock Pipeline

- [x] 建立 `tasks/phase-03-ocr-mock/03-01-ocr-mock-pipeline.md`。
- [x] 新增 `POST /documents/{document_id}/ocr/mock`。
- [x] 新增 `GET /documents/{document_id}/ocr`。
- [x] 保存 OCR mock result 到 local JSON metadata store。
- [x] 未執行 OCR 的文件回傳 `pending` OCR status。
- [x] OCR result 包含 status、text、extracted fields 與 updated timestamp。
- [x] frontend 可對文件執行 Run Mock OCR。
- [x] frontend 顯示 OCR status、OCR text 與 extracted fields。
- [x] 確認未接 PaddleOCR、Tesseract、VLM、RAG、Qdrant、Redis、NATS、vLLM、登入或 PostgreSQL。

## MVP v0.5 Local RAG Baseline

- [x] 建立 `tasks/phase-05-rag-baseline/05-01-local-rag-baseline.md`。
- [x] 從 OCR mock text 產生 chunks。
- [x] 每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。
- [x] chunks 保存到 local JSON metadata store，不新增 DB。
- [x] 新增 local keyword retrieval，依 query 回傳 `top_k` matched chunks。
- [x] retrieval result 包含 score、`document_id` 與 `chunk_id`。
- [x] 新增 `POST /rag/query`。
- [x] RAG response 包含 deterministic answer、citations 與 retrieved chunks。
- [x] citations 包含 `document_id`、`filename` 與 `chunk_id`。
- [x] frontend 新增 RAG chat，可顯示 answer、citations 與 retrieved chunks。
- [x] 保留既有 health、upload、document list 與 OCR mock UI。
- [x] backend version 更新為 `0.5.0`。
- [x] frontend package version 更新為 `0.5.0`。
- [x] 確認未接真正 LLM、OpenAI API、Ollama、vLLM、embedding、Qdrant、rerank、Redis、NATS、PostgreSQL、登入或 RBAC。

## MVP v0.5.1 Demo Hardening

- [x] 建立 `tasks/phase-05-rag-baseline/05-02-demo-hardening.md`。
- [x] 建立公開 sample documents，不包含真實個資或公司敏感資料。
- [x] 建立 `scripts/seed-demo-data.ps1`，可自動 upload、OCR mock、RAG query。
- [x] seed script 輸出 answer、citations 與 retrieved chunks。
- [x] 建立 `scripts/demo-smoke-test.ps1`，可驗證 `/health`、upload、OCR mock 與 `/rag/query`。
- [x] README 加入 5 分鐘 demo 指令、backend/frontend/Docker 啟動方式、範例問題與預期結果。
- [x] backend README 與 frontend README 加入 v0.5.1 demo flow。
- [x] OCR mock 對 text sample 納入公開 sample 文字，方便 local keyword RAG demo。
- [x] backend version 更新為 `0.5.1`。
- [x] frontend package version 更新為 `0.5.1`。
- [x] 確認仍未接 Qdrant、embedding、rerank、真正 LLM、OpenAI API、Ollama、vLLM、Redis、NATS、PostgreSQL、登入或 RBAC。

## MVP v0.6 Bridge Contracts

- [x] 建立 `tasks/phase-06-bridge/06-01-ocr-provider-interface.md`。
- [x] 建立 `tasks/phase-06-bridge/06-02-rag-provider-interface.md`。
- [x] 建立 `tasks/phase-06-bridge/06-03-processing-status-contract.md`。
- [x] 建立 `tasks/phase-06-bridge/06-04-chunk-citation-schema.md`。
- [x] 建立 `tasks/phase-06-bridge/06-05-processing-job-contract.md`。
- [x] 執行 OCR provider interface bridge，保留 mock provider 並維持 OCR API 相容。
- [x] 執行 RAG provider interface bridge，保留 local keyword provider 並維持 `/rag/query` 相容。
- [x] 執行 processing status contract，明確定義 upload、OCR、indexing、ready 與 failed 狀態。
- [x] 執行 chunk / citation schema bridge，補齊 page、bbox、confidence 與 trace metadata contract。
- [x] 執行 processing job contract，建立同步 job metadata，不引入真正 worker 或 queue。
- [x] 確認 v0.6 bridge 階段仍未接真正 OCR、embedding、Qdrant、rerank、LLM、Redis、NATS、PostgreSQL、登入或 RBAC。

## MVP v0.7 Real OCR Provider Spike

- [x] 建立 `tasks/phase-07-real-ocr-provider/07-01-ocr-provider-decision.md`。
- [x] 建立 `tasks/phase-07-real-ocr-provider/07-02-ocr-provider-adapter.md`。
- [x] 建立 `tasks/phase-07-real-ocr-provider/07-03-ocr-output-normalization.md`。
- [x] 建立 `tasks/phase-07-real-ocr-provider/07-04-real-ocr-demo-hardening.md`。
- [x] 執行 OCR provider decision spike，選定 PaddleOCR，並定義 real provider 不可用時明確失敗、mock path 保持可用。
- [x] 執行 local OCR provider adapter，新增 provider-selected `/documents/{document_id}/ocr`，預設仍保留 mock provider。
- [x] 執行 OCR output normalization，將 PaddleOCR lines 映射到 page、bbox、confidence 與 trace metadata。
- [x] 執行 real OCR demo hardening，讓缺少 real OCR dependency 時 mock demo 仍可重跑。
- [x] frontend UI 只顯示目前版本號，並提供 provider-selected OCR 操作。
- [x] backend 與 frontend 版本更新為 `0.7.0`。
- [x] 確認 Phase 07 仍未接 queue、Redis、NATS、Qdrant、embedding、rerank、LLM、PostgreSQL、登入或 RBAC。

## MVP v0.8.0 PaddleOCR Runtime Stabilization

- [x] 執行 `tasks/phase-08-paddleocr-runtime/08-01-paddleocr-environment-baseline.md`。
- [x] 執行 `tasks/phase-08-paddleocr-runtime/08-02-paddleocr-dependency-fix.md`。
- [x] 執行 `tasks/phase-08-paddleocr-runtime/08-03-paddleocr-default-flow-validation.md`。
- [x] 確認預設 PaddleOCR flow 可驗證，且 mock override 仍可重跑。
- [x] 確認 v0.8.0 不新增 PDF rendering、Qdrant、embedding、rerank、LLM、Redis、NATS、worker、資料庫 schema、登入或權限。
- [x] 以 Python 3.12、PaddleOCR 2.10.0 與 PaddlePaddle 3.0.0 驗證 real OCR sample，可完成 provider-selected OCR 與 chunks 產生。
- [x] backend 與 frontend 版本更新為 `0.8.0`。
- [x] Release 文件以 `v0.8.0` 記錄 Phase 08，不再用裸 `Phase 08` 當 release 條目。

## Parking Lot

- [ ] Production-grade OCR / VLM parser（v0.7 / v0.8 只先完成 provider spike 與 runtime stabilization）。
- [ ] Production-grade background embedding / Qdrant indexing pipeline（v0.27.0 只有 demo best-effort / manual indexing，不是正式 worker）。
- [ ] Redis session / cache / rate limit。
- [ ] NATS worker。
- [ ] Production-grade LLM / rerank / citation quality evaluation（local Ollama generation 與 FastEmbed adapter 已有 demo default，正式評測仍未做）。
- [ ] vLLM / OpenAI-compatible provider。

## MVP v0.9.x GPU Runtime Backlog

- [x] `tasks/phase-09-gpu-runtime/09-01-paddleocr-gpu-only-runtime.md`: PaddleOCR GPU-only runtime baseline；本機已以 Python 3.12.10、`paddlepaddle-gpu==3.3.0`、CUDA 12.9 runtime wheel 與 RTX 5070 Ti 通過 `paddle.utils.run_check()`、`check-dev-env.ps1 -CheckPaddleOcr` 與 provider-selected real OCR smoke。
- [x] `tasks/phase-09-gpu-runtime/09-02-paddleocr-v4-mobile-chinese-model.md`: PaddleOCR PP-OCRv4 mobile 中文 / 中英混合模型；已固定模型設定、記錄 det / rec / cls model directory、建立並驗證繁中 sample，mock OCR path 不受影響。
- [x] `tasks/phase-09-gpu-runtime/09-03-paddleocr-engine-lifecycle-preload.md`: 後端啟動時初始化 PaddleOCR engine，provider-selected OCR request 重用同一個 provider / engine，避免每次 request cold start。
- [x] `tasks/phase-09-gpu-runtime/09-04-paddleocr-performance-observability-tuning.md`: 加入 OCR timing log / baseline，評估 `cls=True`、warmup、圖片尺寸與推論參數對速度的影響，收斂 v0.9.1 performance hardening。

## MVP v0.10.0 LLM RAG Backlog

- [x] `tasks/phase-10-llm-rag/10-01-qwen3-ollama-provider-decision.md`: 依 `goal.md` 固定 Ollama `qwen3.5:4b` LLM / VLM provider 決策；已補齊 `DOCURAG_LLM_BASE_URL=http://127.0.0.1:11434` 與 `.env.example` provider env。
- [x] 10-01 validation：`nvidia-smi` 通過，GPU 為 RTX 5070 Ti；`ollama` CLI 目前不在 PATH，`http://127.0.0.1:11434/api/tags` 目前無服務回應，屬 10-02 前需補齊的本機前置條件。
- [x] `tasks/phase-10-llm-rag/10-02-ollama-qwen3-client.md`: 新增 Ollama `qwen3.5:4b` LLM client；預設 disabled，設定 `DOCURAG_LLM_PROVIDER=ollama` 後使用 native `POST /api/generate` 與 `stream=false`，並以 `GET /api/tags` 做 health helper。
- [x] 10-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`58 passed`；`curl.exe http://127.0.0.1:11434/api/tags` 仍因本機 Ollama service 未啟動而無法連線，mock HTTP / monkeypatch 測試已覆蓋 request / response。
- [x] `tasks/phase-10-llm-rag/10-03-qwen3-rag-generation.md`: 在既有 citations contract 上加入可選 `qwen3.5:4b` answer generation；prompt 只使用 query 與 retrieved chunks，LLM failure 會明確 fallback 到 retrieved OCR chunks。
- [x] 10-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`61 passed`；mock LLM client 測試已覆蓋 prompt assembly、成功生成、failure fallback、citation preservation 與 trace metadata。
- [x] `tasks/phase-10-llm-rag/10-04-qwen3-demo-smoke.md`: 補齊 Qwen3.5 demo smoke、UI answer source、`-RunLlm` optional smoke 與 `v0.10.0` release/version sync。
- [x] 10-04 validation：backend test script 通過，`61 passed`；`npm.cmd run build` 通過；`scripts/demo-smoke-test.ps1` 通過並確認 answer source 為 `deterministic baseline`；2026-05-22 follow-up 已安裝 Ollama 0.24.0、pull `qwen3.5:4b`，並以 LLM-enabled backend 跑通 `scripts/demo-smoke-test.ps1 -RunLlm`，確認 answer source 為 `ollama/qwen3.5:4b`。

## MVP v0.11.0 Vector RAG Backlog

- [x] `tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md`: 固定 Phase 11 第一版 embedding / vector store provider decision；選定 Ollama `qwen3-embedding:0.6b` 作為 local embedding 起點，Qdrant self-hosted Docker / Docker Compose 作為 vector store，並定義 `docurag_chunks_v1` collection 與 chunk payload metadata。
- [x] 11-01 validation：`rg -n "v0.11.0|phase-11|qwen3-embedding|Qdrant" TODO.md docs/ROADMAP.md tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-11-vector-rag/11-02-ollama-embedding-client.md`: 新增最小 Ollama embedding client building block；預設 disabled，設定 `DOCURAG_EMBEDDING_PROVIDER=ollama` 後使用 native `POST /api/embed` 與 `qwen3-embedding:0.6b`，不改 `/rag/query` 預設 keyword baseline。
- [x] 11-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`70 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`git diff --check` 通過。mock HTTP tests 已覆蓋 successful embed、connection error、HTTP error、timeout、missing model health 與 malformed response；2026-05-22 follow-up 已透過 Ollama API pull `qwen3-embedding:0.6b`，`scripts/ollama-embedding-smoke.ps1` 通過並確認實際 vector dimension 為 `1024`。
- [x] `tasks/phase-11-vector-rag/11-03-qdrant-local-runtime.md`: 新增 Qdrant local runtime / collection smoke；Docker Compose 包含 optional `qdrant` service，backend 不 `depends_on` Qdrant，`QdrantVectorStore` 可建立/檢查 `docurag_chunks_v1` collection，預設 vector size `1024`。
- [x] 11-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`76 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；mock Qdrant tests 覆蓋 collection exists、create collection、vector size mismatch、connection error、timeout 與 malformed response。2026-05-22 follow-up 已啟動 Docker Desktop、用 Docker Compose 啟動 Qdrant，並跑通 `scripts/qdrant-collection-smoke.ps1`，建立/確認 `docurag_chunks_v1` collection，vector size `1024`、distance `Cosine`。
- [x] `tasks/phase-11-vector-rag/11-04-vector-retrieval-demo-smoke.md`: 加入 optional vector retrieval path；預設仍是 keyword baseline，設定 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector` 後才嘗試 Ollama embedding + Qdrant search，任一 external runtime failure 會明確 fallback 到 keyword retrieval 並寫入 trace metadata。
- [x] 11-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`84 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`frontend` 的 `npm.cmd run build` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，answer source 為 `deterministic baseline`、retrieval source 為 `keyword baseline`；`git diff --check` 通過。2026-05-22 follow-up 已在本機準備 Ollama `qwen3-embedding:0.6b` 與 Qdrant，並用 vector-enabled backend 跑通 `scripts/demo-smoke-test.ps1 -RunVector`，answer source 為 `deterministic baseline`、retrieval source 為 `vector/qdrant`。Mock/unit tests 已覆蓋 default keyword path、vector success、embedding failure fallback、Qdrant failure fallback、collection missing fallback、route provider selection、Qdrant upsert/search。

## MVP v0.12.0 Vector Indexing Hardening Backlog

- [x] `tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md`: 固定 local vector indexing contract、Qdrant payload metadata、stable point id、failure / fallback 行為與 Phase 12 guardrails；文件 ticket，不 bump version。
- [x] 12-01 validation：`rg -n "v0.12.0|phase-12|Vector Indexing|docurag_chunks_v1" TODO.md docs/ROADMAP.md tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-12-vector-indexing/12-02-vector-indexing-service.md`: 新增最小同步 vector indexing service/helper，將 existing document chunks idempotently embed + upsert 到 Qdrant；不新增 API、worker、DB 或 default-on vector path。
- [x] 12-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`91 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`git diff --check` 通過。單元測試覆蓋 stable point id、payload metadata、empty chunks skipped、embedding failure、Qdrant failure、collection size mismatch 與 embedding dimension mismatch。
- [x] `tasks/phase-12-vector-indexing/12-03-vector-indexing-api.md`: 新增手動 vector indexing API，例如 `POST /documents/{document_id}/index/vector`，讓 demo 可明確執行 indexing；不新增 batch indexing、frontend 大改版或 async queue。
- [x] 12-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`97 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`git diff --check` 通過。Endpoint tests 覆蓋 success、document not found、OCR 未完成、empty chunks skipped、provider disabled 與 Qdrant failure。
- [x] `tasks/phase-12-vector-indexing/12-04-vector-indexing-demo-smoke.md`: 更新 optional vector demo smoke，先手動 vector indexing 再 vector retrieval query，並完成 `v0.12.0` release/version sync。
- [x] 12-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`97 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`frontend` 的 `npm.cmd run build` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，answer source 為 `deterministic baseline`、retrieval source 為 `keyword baseline`；optional vector indexing `scripts/demo-smoke-test.ps1 -RunVector` 通過，會先 manual vector indexing，retrieval source 為 `vector/qdrant`；`git diff --check` 通過。

Phase 12 guardrails：

- keyword RAG 仍為 baseline；vector indexing / retrieval 仍需明確 env 與手動 action。
- 保留 optional Ollama `qwen3.5:4b` generation path。
- 不實作 rerank、hybrid search、eval runner、Redis、NATS、worker、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- Qdrant 或 embedding 不可用時，baseline demo 不可被破壞。
- Stable vector point id 規則固定為 `uuid5(NAMESPACE_URL, f"docurag:{document_id}:{chunk_id}")`，重跑 manual indexing 只能 idempotently upsert 同一 chunk。
- Qdrant payload 必須保留 `document_id`、`filename`、`chunk_id`、`text`、`source`、`source_type`、`page_number`、`bbox`、`confidence`、`created_at` 與 chunk `metadata`。
- Empty chunks、embedding disabled / unavailable、Qdrant unavailable、collection missing 或 vector size mismatch 必須回傳清楚 skipped / failed result，不修改 local metadata，不影響 keyword RAG baseline。

## MVP v0.13.0 Retrieval Evaluation Baseline Backlog

- [x] `tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md`: 固定 retrieval evaluation dataset schema、metrics、result output contract 與 Phase 13 guardrails；文件 ticket，不 bump version。
- [x] 13-01 validation：`rg -n "v0.13.0|phase-13|Retrieval Evaluation|Hit Rate|MRR" TODO.md docs/ROADMAP.md tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-13-retrieval-eval/13-02-retrieval-eval-dataset.md`: 新增最小公開 retrieval eval dataset，使用既有虛構 sample documents，不新增 runner 或 runtime API。
- [x] 13-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`99 passed`（本機 PowerShell PATH 臨時補上 Codex bundled Python 3.12；pytest cache 權限警告不影響結果）；`git diff --check` 通過。
- [x] `tasks/phase-13-retrieval-eval/13-03-retrieval-eval-runner.md`: 新增本機 retrieval eval runner，計算 keyword baseline 與 optional vector retrieval 的 Hit Rate@K、MRR@K、Recall@K、latency 與 failure count。
- [x] 13-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`104 passed`（本機 PowerShell PATH 臨時補上 Codex bundled Python 3.12；pytest cache 權限警告不影響結果）；baseline `scripts/retrieval-eval-smoke.ps1` 通過，Hit Rate@K `0.8333`、MRR@K `0.6389`、Recall@K `0.75`、failure count `0`；optional vector `scripts/retrieval-eval-smoke.ps1 -RunVector` 通過，Hit Rate@K `0.6667`、MRR@K `0.6667`、Recall@K `0.5833`、failure count `0`；`git diff --check` 通過。
- [x] `tasks/phase-13-retrieval-eval/13-04-retrieval-eval-demo-smoke.md`: 補齊 retrieval eval demo smoke，完成 `v0.13.0` release/version sync。
- [x] 13-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`104 passed`（本機 PowerShell PATH 臨時補上 Codex bundled Python 3.12；pytest cache 權限警告不影響結果）；`frontend` 的 `npm.cmd run build` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，version `0.13.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；baseline `scripts/retrieval-eval-smoke.ps1` 通過，Hit Rate@K `0.8333`、MRR@K `0.6389`、Recall@K `0.75`、failure count `0`；optional vector `scripts/retrieval-eval-smoke.ps1 -RunVector` 通過，manual vector indexing API preflight indexed chunks `2`，Hit Rate@K `0.6667`、MRR@K `0.6667`、Recall@K `0.5833`、failure count `0`；`git diff --check` 通過。

Phase 13 guardrails：

- Phase 13 只建立 retrieval evaluation baseline，不實作 rerank、hybrid search、LLM-as-judge、answer faithfulness 或 citation quality scoring。
- Baseline eval 必須可在沒有 Ollama embedding 或 Qdrant 時執行 keyword retrieval 評估。
- Optional vector eval 必須明確 env、Qdrant collection 與 manual vector indexing；不可讓 eval、vector retrieval 或 vector indexing 成為 default-on path。
- Eval dataset 只使用公開虛構 sample data，不新增真實文件或敏感資料。
- 不新增 Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。

## MVP v0.14.0 Retrieval Quality Planning Backlog

- [x] `tasks/phase-14-retrieval-quality/14-01-rerank-provider-decision.md`: 固定 Phase 14 rerank provider decision 與 retrieval quality planning boundary，引用 Phase 13 metrics，記錄 local-first / disabled-by-default / fallback-safe decision criteria；只做文件決策，不新增 runtime。
- [x] 14-01 validation：`rg -n "v0.14.0|Phase 14|rerank|hybrid|retrieval quality" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-01-rerank-provider-decision.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-14-retrieval-quality/14-02-retrieval-quality-contract.md`: 定義 future strategy labels、rerank trace metadata、hybrid merge / dedupe trace metadata 與 fallback contract；只做 Markdown contract，不新增 implementation 或 version bump。
- [x] 14-02 validation：`rg -n "vector_rerank|hybrid_rerank|rerank score|fallback|default-on" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-02-retrieval-quality-contract.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md`: 規劃 retrieval eval dataset 擴充原則、lexical mismatch、multi-evidence、near-duplicate chunks、cross-document ambiguity、numeric / table lookup 等 future cases 與 quality gates；只做文件計畫，不修改 dataset JSON。
- [x] 14-03 validation：`rg -n "dataset expansion|lexical mismatch|multi-evidence|near-duplicate|cross-document" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md`: 規劃 future demo smoke preflight、validation checklist、release sync checklist 與 runtime implementation boundary；不執行 version bump、release sync、tag 或 runtime 實作。
- [x] 14-04 validation：`rg -n "v0.14.0|demo smoke|release sync|Version bump required: no|future implementation" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 14 guardrails：

- Phase 14 目前只做 retrieval quality planning 與 ticket 草案，不實作 rerank、hybrid search 或任何 runtime。
- 所有 Phase 14 ticket 都必須包含 `Release Impact`，且目前皆為 `Version bump required: no`。
- 不新增 backend / frontend 程式碼、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不修改 `sample-data/eval/retrieval-eval.json`，dataset 擴充只先做 Markdown planning。
- 不變更 keyword / vector retrieval 預設行為，不讓 future strategy 成為 default-on path。

## MVP v0.15.0 Rerank Runtime Spike Backlog

- [x] `tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md`: 決定 Phase 15 local-first rerank provider / model、dependency / model download 邊界與 `vector_rerank` 優先順序；文件票，不新增 runtime。
- [x] 15-01 validation：`rg -n "v0.15.0|Phase 15|rerank provider|vector_rerank|hybrid" TODO.md docs/ROADMAP.md tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-15-rerank-runtime/15-02-rerank-provider-adapter.md`: 實作 disabled-by-default rerank provider adapter，保留 keyword baseline 與 vector retrieval fallback。
- [x] 15-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-15-rerank-runtime/15-03-vector-rerank-eval-integration.md`: 將 optional `vector_rerank` 接入 retrieval eval runner，輸出 Phase 13 metrics 與 rerank trace metadata。
- [x] 15-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1` 通過；optional rerank eval smoke command documented as `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVectorRerank`；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-15-rerank-runtime/15-04-rerank-demo-release-sync.md`: 補齊 optional rerank demo / eval smoke 並執行 `v0.15.0` release/version sync。
- [x] 15-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過；`frontend` 的 `npm.cmd run build` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，version `0.15.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；baseline `scripts/retrieval-eval-smoke.ps1` 通過，Hit Rate@K `0.8333`、MRR@K `0.6389`、Recall@K `0.75`、failure count `0`；optional `vector_rerank` eval smoke command 已文件化為 `scripts/retrieval-eval-smoke.ps1 -RunVectorRerank`，本機未執行 optional rerank smoke，因為 `.venv` 未安裝 optional FastEmbed runtime（Ollama embedding 與 Qdrant collection 可連線）；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] Phase 15 planning validation：`rg -n "v0.15.0|Phase 15|15-01|15-04|rerank runtime" TODO.md docs/ROADMAP.md tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md tasks/phase-15-rerank-runtime/15-02-rerank-provider-adapter.md tasks/phase-15-rerank-runtime/15-03-vector-rerank-eval-integration.md tasks/phase-15-rerank-runtime/15-04-rerank-demo-release-sync.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 15 goal：

- 以 Phase 14 planning 為基礎，優先做 disabled-by-default `vector_rerank` runtime spike。
- 15-01 已選定第一版 rerank runtime 路線為 FastEmbed `TextCrossEncoder` + `BAAI/bge-reranker-base`；實作仍必須 disabled-by-default。
- 保留 keyword baseline 可在無 external runtime 時執行。
- 使用 Phase 13 eval metrics 比較 `vector` 與 `vector_rerank`，先不實作 hybrid search。

Phase 15 guardrails：

- 先執行 `15-01` provider decision，再開始任何 code implementation。
- 不讓 rerank、vector retrieval 或 eval strategy default-on。
- 不實作 hybrid search、BM25、score fusion、merge / dedupe policy 或 frontend trace UI，除非後續 ticket 明確要求。
- 不新增 Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 若需要外部依賴、模型下載或 Docker runtime，必須由 ticket 明確列出，並依工具要求取得 approval。
- Phase 15 完成後，hybrid search、dataset JSON expansion、frontend trace UI 與真正 dependency packaging 留到 Phase 16 或後續 ticket 規劃。

## MVP v0.16.0 Hybrid Retrieval Planning Backlog

- [x] `tasks/phase-16-hybrid-retrieval/16-01-hybrid-retrieval-contract.md`: 固定 optional `hybrid` strategy、candidate source、merge policy、dedupe key 與 trace metadata contract；文件 ticket，不 bump version。
- [x] `tasks/phase-16-hybrid-retrieval/16-02-eval-dataset-expansion-json.md`: 依 Phase 14 plan 擴充公開 retrieval eval dataset JSON，至少讓總 cases 達到 `12`，並保留 baseline keyword eval 可重跑。
- [x] `tasks/phase-16-hybrid-retrieval/16-03-hybrid-eval-strategy-integration.md`: 將 optional `hybrid` strategy 接入 retrieval eval runner，沿用 Phase 13 metrics 並保留 fallback trace metadata。
- [x] `tasks/phase-16-hybrid-retrieval/16-04-hybrid-demo-release-sync.md`: 補齊 optional hybrid demo / eval smoke，並在 implementation 完成時執行 `v0.16.0` release/version sync。
- [x] Phase 16 planning validation：`rg -n "v0.16.0|Phase 16|16-01|16-04|hybrid retrieval" TODO.md docs/ROADMAP.md tasks/phase-16-hybrid-retrieval/*.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 16 goal：

- 在 Phase 15 disabled-by-default `vector_rerank` runtime spike 後，規劃下一個 retrieval quality slice：公開 dataset expansion 與 optional `hybrid` eval strategy。
- `hybrid` 第一版只用既有 keyword branch 與 optional vector branch，不新增 BM25 dependency。
- 使用 Phase 13 eval metrics 比較 `keyword`、`vector`、`vector_rerank` 與 `hybrid`。
- 16-04 才允許 `v0.16.0` version bump 與 release docs sync。

Phase 16 guardrails：

- 先執行 `16-01` contract，再開始 dataset 或 runtime implementation。
- 不讓 hybrid、vector retrieval、rerank 或 eval strategy default-on。
- 不實作 `hybrid_rerank`、frontend trace UI、LLM-as-judge、answer faithfulness、citation quality scoring 或 eval dashboard，除非後續 ticket 明確要求。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 deployment 設定。
- Dataset expansion 只能使用公開虛構資料；若既有 sample documents 不足，必須停止並回報，不可自行加入真實或敏感資料。

16-01 contract status：

- Strategy label 固定為 `hybrid`，只作為 retrieval eval runner 的 optional strategy，不接 `/rag/query` 或 frontend UI。
- Candidate sources 固定為 existing keyword branch + optional vector branch；`vector_rerank` / `hybrid_rerank` 不屬於第一版 hybrid source。
- Dedupe key 優先使用 `(document_id, chunk_id)`；欄位不足時必須記錄 dedupe fallback metadata。
- Merge policy 固定為 deterministic `rank_based_fusion`，保留 branch rank / score，不直接相加 keyword score 與 vector similarity。
- Vector branch unavailable 時 fallback 到 keyword-only candidates，並記錄 branch failure / fallback reason，keyword baseline 不受影響。
- 16-01 validation：`rg -n "v0.16.0|Phase 16|hybrid retrieval|merge policy|dedupe" TODO.md docs/ROADMAP.md tasks/phase-16-hybrid-retrieval/16-01-hybrid-retrieval-contract.md` 通過；`git diff --check` 通過。

16-02 dataset status：

- `sample-data/eval/retrieval-eval.json` 已由 6 筆擴充到 12 筆。
- 新增 cases 只引用既有公開虛構 sample documents：`mock-invoice-aurora.txt` 與 `mock-contract-support.txt`。
- Tags 已覆蓋 `lexical_mismatch`、`multi_evidence`、`near_duplicate`、`cross_document_ambiguity` 與 `numeric_table_lookup`。
- Baseline keyword eval smoke 仍可在無 Ollama embedding、Qdrant 或 FastEmbed runtime 時執行。
- 16-02 validation：`scripts/test-backend.ps1` 通過；`scripts/retrieval-eval-smoke.ps1` 通過；`git diff --check` 通過。

16-03 hybrid eval status：

- Eval runner 已支援 explicit `hybrid` strategy，預設仍為 keyword baseline。
- `hybrid` 使用 existing keyword branch + optional vector branch，依 deterministic `rank_based_fusion` merge / dedupe candidates。
- Hybrid trace metadata 保留 branch ranks、branch scores、merged score、candidate counts、dedupe count、branch failures 與 fallback reason。
- Vector branch unavailable 時 fallback 到 keyword-only candidates，不讓 baseline eval 失敗，也不把 optional hybrid fallback 算成 eval failure。
- `scripts/retrieval-eval-smoke.ps1 -RunHybrid` 已可執行 optional hybrid eval smoke；本機 vector preflight 可用時已跑通，Hit Rate@K `0.5833`、MRR@K `0.5`、Recall@K `0.5833`、failure count `0`。
- 16-03 validation：`scripts/test-backend.ps1` 通過，`120 passed`；baseline `scripts/retrieval-eval-smoke.ps1` 通過，keyword Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`；optional `scripts/retrieval-eval-smoke.ps1 -RunHybrid` 通過；`git diff --check` 通過。

16-04 release sync status：

- Backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 已同步到 `0.16.0`。
- README、backend README、frontend README、TODO 與 ROADMAP 已補齊 `v0.16.0` release status。
- Baseline demo smoke 通過，version `0.16.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`。
- Baseline retrieval eval smoke 通過，Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`。
- Optional vector eval smoke 在本機 vector preflight 可用時通過，Hit Rate@K `0.5`、MRR@K `0.4167`、Recall@K `0.4583`、failure count `0`。
- Optional `vector_rerank` eval smoke 在本機 vector preflight 可用時通過，Hit Rate@K `0.5`、MRR@K `0.4167`、Recall@K `0.4583`、failure count `0`。
- Optional hybrid eval smoke 在本機 vector preflight 可用時通過，Hit Rate@K `0.5833`、MRR@K `0.5`、Recall@K `0.5833`、failure count `0`。
- `hybrid_rerank`、frontend trace UI、worker、DB、auth 與 deployment 仍留到後續 Phase。

## MVP v0.17.0 Retrieval Trace UI / Eval Visibility Backlog

- [x] `tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md`: 固定 frontend trace UI / eval visibility contract，涵蓋 keyword、vector、`vector_rerank`、`hybrid`、fallback 與 missing metadata display；文件 ticket，不 bump version。
- [x] 17-01 validation：`rg -n "v0.17.0|Phase 17|trace UI|hybrid|vector_rerank" TODO.md docs/ROADMAP.md tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-17-retrieval-trace-ui/17-02-frontend-retrieval-trace-panel.md`: 在既有 RAG result UI 顯示 retrieval trace panel，只讀既有 response，不新增 backend API。
- [x] 17-02 validation：`npm.cmd run build` 通過；Browser 檢查 `http://localhost:5173` RAG result trace panel 可顯示 baseline answer / retrieval source、candidate table、fallback state，且無水平溢出；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-17-retrieval-trace-ui/17-03-eval-result-report-summary.md`: 改善 retrieval eval runner / smoke summary，讓 strategy metrics、fallback count 與 trace metadata 更適合 demo / README 摘錄。
- [x] 17-03 validation：`PATH="/c/Users/USER/AppData/Local/Programs/Python/Python312:/c/Users/USER/AppData/Local/Programs/Python/Python312/Scripts:$PATH" powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`121 passed`（僅 pytest cache 權限警告）；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional vector-backed smoke 未完成，因 backend upload preflight 在本機 data dir 建立 `uploads` 時遇到 Windows `PermissionError`，因此 local preflight 不完整。
- [x] `tasks/phase-17-retrieval-trace-ui/17-04-trace-ui-demo-release-sync.md`: 補齊 trace UI / eval visibility demo validation，並完成 `v0.17.0` release/version sync。
- [x] 17-04 validation：`PATH="/c/Users/USER/AppData/Local/Programs/Python/Python312:/c/Users/USER/AppData/Local/Programs/Python/Python312/Scripts:$PATH" powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`121 passed`（僅 pytest cache 權限警告）；`npm.cmd run build` 通過；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/demo-smoke-test.ps1` 通過，version `0.17.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional `-RunVector`、`-RunVectorRerank` 與 `-RunHybrid` 均通過，`vector_rerank` 在未安裝 FastEmbed 時記錄 fallback count `12` 與 fallback reason；Browser 檢查 `http://localhost:5173` trace panel 可顯示 `v0.17.0` health、candidate table 與 fallback state，且無水平溢出。
- [x] Phase 17 planning validation：`rg -n "v0.17.0|Phase 17|17-01|17-04|trace UI|eval visibility" TODO.md docs/ROADMAP.md tasks/phase-17-retrieval-trace-ui/*.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 17 goal：

- 把 Phase 13-16 已產生的 retrieval eval output、rerank metadata 與 hybrid trace metadata，轉成可展示、可閱讀、可驗證的 frontend / report visibility。
- 17-01 已固定 trace UI contract；17-02 已加入 frontend trace panel；17-03 已改善 eval reporting；17-04 已完成 `v0.17.0` version bump、release docs sync 與 demo / eval smoke validation。
- 保留 baseline keyword demo 與 optional vector / `vector_rerank` / `hybrid` eval smoke 可重跑。

Phase 17 guardrails：

- 先執行 `17-01` contract，再開始 frontend 或 reporting implementation。
- Frontend trace panel 只能讀既有 response，不得為 UI 新增 backend endpoint 或改 API contract。
- Missing metadata 必須 graceful hidden 或顯示清楚 fallback state，不得讓 keyword baseline demo 因缺少 optional metadata 失效。
- 不讓 hybrid、vector retrieval、rerank 或 eval strategy default-on。
- 不實作 `hybrid_rerank`、production eval dashboard、LLM-as-judge、answer faithfulness、citation quality scoring、query rewriting 或 BM25 dependency，除非後續 ticket 明確要求。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 deployment 設定。

## MVP v0.18.0 Hybrid Rerank Planning Backlog

- [x] `tasks/phase-18-hybrid-rerank-planning/18-01-hybrid-rerank-boundary-contract.md`: 規劃 `hybrid_rerank` candidate flow、disabled-by-default 邊界、trace metadata 與 fallback states；文件 ticket，不 bump version。
- [x] `tasks/phase-18-hybrid-rerank-planning/18-02-hybrid-rerank-eval-dataset-plan.md`: 規劃 future `hybrid_rerank` eval dataset case 類型與 metrics 摘要使用方式；文件 ticket，不 bump version。
- [x] `tasks/phase-18-hybrid-rerank-planning/18-03-hybrid-rerank-trace-report-plan.md`: 規劃 future `hybrid_rerank` trace / report visibility 與 missing metadata behavior；文件 ticket，不 bump version。
- [x] `tasks/phase-18-hybrid-rerank-planning/18-04-phase-18-demo-release-plan.md`: 規劃 future `hybrid_rerank` demo validation 與 release sync checklist；文件 ticket，不 bump version。
- [x] Phase 18 planning validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no|release sync" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 18 goal：

- 只做 `hybrid_rerank` planning backlog，讓後續 implementation 能清楚區分 hybrid merge、rerank reordering、fallback metadata 與 demo / release validation。
- 本次規劃不修改 backend、frontend、sample data、eval runner、smoke script、版本號或 Docker Compose。
- 後續 implementation 已排入 Phase 19，目標版本號使用 `v0.19.0`。

Phase 18 guardrails：

- 18-01 到 18-04 都是 Markdown-only planning ticket，`Release Impact` 必須寫 `Version bump required: no`。
- 不實作 `hybrid_rerank` runtime、BM25 dependency、score fusion code、rerank invocation、backend API、frontend UI 或 production eval dashboard。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 deployment 設定。

18-01 boundary contract status：

- `hybrid_rerank` candidate flow 固定為 keyword branch + vector branch -> hybrid merge / dedupe -> optional rerank reordering。
- Strategy label 固定為 `hybrid_rerank`，後續 implementation 必須 explicit opt-in 且 disabled-by-default，不得改變 keyword baseline demo。
- Trace metadata 已規劃 run-level candidate counts、merge policy、dedupe key、rerank provider / model / status / latency、branch failures 與 fallback reason。
- Fallback states 已規劃 `vector_unavailable`、`vector_empty`、`merge_dedupe_partial`、`reranker_disabled` 與 `reranker_unavailable`。
- 18-01 validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過。

18-02 dataset plan status：

- Future dataset case types 已規劃 `lexical_heavy`、`semantic_heavy`、`branch_disagreement`、`rerank_improves_ordering`、`rerank_filters_distractor` 與 `rerank_fallback`。
- 後續 dataset update ticket 必須只使用公開虛構 sample documents；若既有 sample 不足，需停止並拆新 sample ticket。
- Metrics summary 邊界沿用 `fallback_count`、`trace_metadata_count`、`result_strategy_counts`、`fallback_reasons` 與既有 Hit Rate@K / MRR@K / Recall@K / latency / failure count。
- 18-02 validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|dataset|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過。

18-03 trace report plan status：

- Future visibility surfaces 已規劃 CLI summary、JSON output 與既有 frontend trace panel 的只讀顯示邊界。
- Report fields 已拆成 run-level、case-level 與 candidate-level，涵蓋 branch counts、merge policy、dedupe、rerank provider / status / score、fallback reason 與 candidate ordering。
- Missing metadata behavior 沿用 Phase 17：graceful hidden、`metadata unavailable` 或清楚 fallback state；不得把 branch score、merged score 與 rerank score 混成單一分數。
- 18-03 validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|trace|report|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過。

18-04 demo release plan status：

- Future validation checklist 已規劃 backend tests、frontend build、baseline demo smoke、baseline eval smoke、optional vector / `vector_rerank` / `hybrid` / future `hybrid_rerank` eval smoke 與 `git diff --check`。
- Future release sync files 已規劃 backend version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP；實作已順延到 Phase 19。
- Deferred items 已明確保留 production eval dashboard、Redis、NATS、worker、DB schema、auth、RBAC、deployment、LLM-as-judge、answer faithfulness、citation quality scoring、query rewriting 與 BM25 到後續 Phase。
- 18-04 validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no|release sync" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過。

## MVP v0.19.0 Hybrid Rerank Runtime Backlog

- [x] `tasks/phase-19-hybrid-rerank-runtime/19-01-hybrid-rerank-eval-provider.md`: 實作 disabled-by-default `hybrid_rerank` eval provider，流程為 keyword branch + vector branch -> hybrid merge / dedupe -> rerank reordering。
- [x] 19-01 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Set-Location 'C:/Users/USER/Desktop/DocuRAG'; ./scripts/test-backend.ps1"` 通過，`125 passed`（僅 pytest cache 權限警告）；`rg -n "hybrid_rerank|HybridRerank|rerank_fallback_reason|strategy_label" backend/app/services/evaluation.py backend/tests/test_evaluation.py TODO.md docs/ROADMAP.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-19-hybrid-rerank-runtime/19-02-hybrid-rerank-smoke-flag.md`: 將 `hybrid_rerank` 接入 eval runner CLI 與 `scripts/retrieval-eval-smoke.ps1 -RunHybridRerank`。
- [x] 19-02 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Set-Location 'C:/Users/USER/Desktop/DocuRAG'; ./scripts/test-backend.ps1"` 通過，`125 passed`（僅 pytest cache 權限警告）；baseline `scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional `scripts/retrieval-eval-smoke.ps1 -RunHybridRerank` 已進入 vector preflight，但本機 Qdrant collection `docurag_chunks_v1` / Docker daemon 未啟動而停止，需先啟動 Qdrant 並重跑 `scripts/qdrant-collection-smoke.ps1`；`rg -n "RunHybridRerank|hybrid_rerank|retrieval-eval-result-hybrid-rerank" scripts backend README.md sample-data/eval/README.md TODO.md docs/ROADMAP.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-19-hybrid-rerank-runtime/19-03-hybrid-rerank-trace-report-sync.md`: 補齊 `hybrid_rerank` trace / report visibility，確保 branch score、merged score 與 rerank score 可區分。
- [x] 19-03 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Set-Location 'C:/Users/USER/Desktop/DocuRAG'; ./scripts/test-backend.ps1"` 通過，`126 passed`（僅 pytest cache 權限警告）；baseline `scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional `scripts/retrieval-eval-smoke.ps1 -RunHybridRerank` 仍因本機 Qdrant collection / Docker daemon 未啟動停在 vector preflight；`rg -n "hybrid_rerank|merged_score|rerank_score|fallback_count|trace_metadata_count" README.md backend/README.md frontend/README.md sample-data/eval/README.md backend/app/services/evaluation.py backend/tests/test_evaluation.py TODO.md docs/ROADMAP.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-19-hybrid-rerank-runtime/19-04-hybrid-rerank-demo-release-sync.md`: 重跑 final validation，確認 baseline / optional smoke 狀態，並完成 `v0.19.0` release/version sync。
- [x] 19-04 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`126 passed`（僅 pytest cache 權限警告），backend editable package 已同步為 `docurag-agentops-backend==0.19.0`；`npm.cmd run build` 於 `frontend/` 通過；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/demo-smoke-test.ps1` 通過，health version `0.19.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；baseline `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional `-RunVector`、`-RunVectorRerank`、`-RunHybrid` 與 `-RunHybridRerank` 均已執行 preflight，但本機 Qdrant collection `docurag_chunks_v1` 不可用而停止，需先啟動 Qdrant 並重跑 `scripts/qdrant-collection-smoke.ps1`；backend version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `0.19.0`。

Phase 19 goal：

- 將 Phase 18 planning 中的 `hybrid_rerank` 從規格落地成 optional eval runner strategy。
- 保留 keyword baseline、`vector`、`vector_rerank` 與 `hybrid` 既有行為，不讓 `hybrid_rerank` default-on。
- 只把 `hybrid_rerank` 接入 evaluation / smoke / trace reporting，不接 production dashboard 或 default chat path。

Phase 19 guardrails：

- 先執行 `19-01` provider flow，再接 smoke flag、trace report sync 與 final release sync。
- 不接 `/rag/query`、frontend live chat、production eval dashboard、backend API endpoint 或 default retrieval path。
- 不新增 BM25 dependency、query rewriting、LLM-as-judge、answer faithfulness scoring、citation quality scoring、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、Agent runtime、VLM parser、PDF rendering、production OCR pipeline、K8s 或 deployment 設定。
- `19-04` 才允許 `v0.19.0` version bump；`19-01` 到 `19-03` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

## MVP v0.20.0 Interview MVP Packaging Backlog

- [x] `tasks/phase-20-interview-mvp-packaging/20-01-interview-demo-doc-refresh.md`: 更新 README / demo script / PRD / architecture 的面試 demo 敘事，對齊 `v0.17.0` runtime、`v0.18.0` planning-only 與 `v0.19.0` `hybrid_rerank` implementation 狀態；文件 ticket，不 bump version。
- [x] 20-01 validation：`rg -n "v0.17.0|v0.18.0|v0.19.0|Phase 20|interview MVP|面試" README.md docs/demo-script.md docs/PRD.md docs/architecture.md TODO.md docs/ROADMAP.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-20-interview-mvp-packaging/20-02-sample-eval-coverage-expansion.md`: 補齊公開虛構 sample documents 與 retrieval eval cases，目標至少 5 份 sample documents、20 筆 eval cases；不改 retrieval algorithm。
- [x] 20-02 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`127 passed`（僅 pytest cache 權限警告）；baseline `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=20`、Hit Rate@K `0.7`、MRR@K `0.475`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `62`；`rg -n "case_count|20|sample documents|demo-safe|synthetic" sample-data docs/ROADMAP.md TODO.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-20-interview-mvp-packaging/20-03-demo-media-and-readme-polish.md`: 補齊 README 5 到 10 分鐘面試導覽、截圖或 GIF 等 demo media；不新增 production UI 或 API。
- [x] 20-03 validation：`npm.cmd run build` 於 `frontend/` 通過；Browser 檢查 `http://localhost:5173` local frontend demo view 通過，並產出 `docs/demo-media/frontend-overview.png`、`docs/demo-media/frontend-trace.png` 與 `docs/demo-media/eval-summary.png`；`rg -n "screenshot|GIF|demo media|interview demo|面試" README.md docs/demo-script.md docs/ROADMAP.md TODO.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-20-interview-mvp-packaging/20-04-final-interview-mvp-validation.md`: 重跑 final validation，確認 baseline / optional smoke 狀態，並完成 `v0.20.0` release/version sync。
- [x] 20-04 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`127 passed`（僅 pytest cache 權限警告），backend editable package 已同步為 `docurag-agentops-backend==0.20.0`；`npm.cmd run build` 於 `frontend/` 通過；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/demo-smoke-test.ps1` 通過，health version `0.20.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；baseline `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=20`、Hit Rate@K `0.7`、MRR@K `0.475`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `62`；optional `-RunVector`、`-RunVectorRerank` 與 `-RunHybrid` 均已執行 preflight，但本機 Qdrant collection `docurag_chunks_v1` 不可用而停止，需先啟動 Qdrant 並重跑 `scripts/qdrant-collection-smoke.ps1`；backend version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `0.20.0`；`rg` 與 `git diff --check` 通過。

Phase 20 goal：

- 把已完成的受控 MVP 包裝成面試可展示版本，讓面試官能快速看懂 upload -> OCR -> RAG -> citation -> trace -> eval 的價值。
- 補齊 `goal.md` 成功標準中與面試展示直接相關的 sample coverage、eval coverage、demo script 與截圖 / GIF。
- 只做 demo readiness / packaging / validation，不把企業級 runtime scope 偷渡進來。

Phase 20 guardrails：

- 先執行 `20-01` 文件刷新，再做 sample/eval 擴充、demo media 與 final release sync。
- 不實作 production eval dashboard、BM25 dependency、query rewriting、LLM-as-judge、answer faithfulness scoring 或 citation quality scoring。
- 不新增 backend API、frontend route、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、Agent runtime、VLM parser、PDF rendering、production OCR pipeline、K8s 或 deployment 設定。
- `20-04` 才允許 `v0.20.0` version bump；`20-01` 到 `20-03` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

## MVP v0.20.1 Frontend Demo UI Polish

- [x] `tasks/phase-20-interview-mvp-packaging/20-05-frontend-demo-ui-polish.md`: 改善既有 Vue demo UI 的第一屏資訊層次、workflow 狀態、卡片 / 表格 / trace 視覺質感；不新增 route、API、外部依賴或 backend runtime。
- [x] 20-05 validation：`npm.cmd run build` 於 `frontend/` 通過；Browser 檢查 `http://localhost:5173/` local frontend demo view，desktop viewport 無 horizontal overflow；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-06-readme-demo-media-refresh.md`: 用 20-05 polish 後的 local frontend demo 與 baseline eval summary 重新覆蓋 README 引用的三張 demo 圖；不新增 route、API、外部依賴或 backend runtime。
- [x] 20-06 validation：`npm.cmd run build` 於 `frontend/` 通過；Browser 重新截取 `docs/demo-media/frontend-overview.png` 與 `docs/demo-media/frontend-trace.png`；baseline `scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=20`、Hit Rate@K `0.7`、MRR@K `0.475`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `62`；重新產生 `docs/demo-media/eval-summary.png`；`rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-07-frontend-zh-tw-copy-polish.md`: 將 frontend demo 的 hero、summary cards、workflow、panel、按鈕、表格、empty states、常見狀態與瀏覽器標題中文化；保留 API endpoint、JSON key、provider / model 名稱與技術 token 原文，不新增 route、API、外部依賴或 backend runtime。
- [x] 20-07 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend demo view 檢查標題、主要中文 panel、舊英文可見標籤與 desktop horizontal overflow 通過；ticket 指定 `rg` 已執行，剩餘命中僅 `listDocuments` / `refreshDocuments` 程式識別符；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-08-readme-zh-tw-demo-media-refresh.md`: 用 20-07 中文化後的 local frontend demo 重新覆蓋 README 引用的 `frontend-overview.png` 與 `frontend-trace.png`；不新增 README 圖片路徑、route、API、外部依賴或 backend runtime。
- [x] 20-08 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend demo view 重新截取 `docs/demo-media/frontend-overview.png` 與 `docs/demo-media/frontend-trace.png`，檢查中文標題 / panel / trace、舊英文可見標籤與 desktop horizontal overflow 通過；`rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-09-frontend-chat-first-demo.md`: 將 frontend demo 第一屏調整為客服式 RAG chat，upload / OCR / metadata 保留在同頁後台知識庫管理區；不新增 route、API、外部依賴或 backend runtime。
- [x] 20-09 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend demo view 檢查第一屏 chat-first、後台區塊仍可用、RAG query 後 answer / citations / trace / retrieved chunks 可見、desktop horizontal overflow 為 `0`；ticket 指定 `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-10-readme-chat-first-demo-refresh.md`: 更新 root README 的 chat-first recommended demo flow、前台 / 後台分工與 baseline / optional path 說明；不修改 frontend、backend、sample data 或 demo media。
- [x] 20-10 validation：ticket 指定 `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-11-frontend-minimal-chat-upload.md`: 將 frontend demo 收斂成兩個使用者可見入口：客服問答與文件上傳；OCR、indexing、document list、raw JSON、retrieval trace table 與 eval metrics 留在 backend API / CLI / smoke scripts。
- [x] 20-11 validation：`npm.cmd run build` 於 `frontend/` 通過；Browser 檢查 `http://localhost:5174/` local frontend demo view 只有客服問答與文件上傳，沒有 OCR panel、document list、metadata JSON、API response JSON、trace table，desktop horizontal overflow 為 `0`；ticket 指定 `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-12-default-llm-answer.md`: 將 local demo `/rag/query` 預設改為嘗試 Ollama `qwen3.5:4b` answer generation，Ollama 不可用時保留 retrieved OCR chunks fallback，並保留 `DOCURAG_LLM_PROVIDER=` 關閉 path。
- [x] 20-12 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`129 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 通過，answer source 為 `LLM unavailable fallback`、retrieval source 為 `keyword baseline`；ticket 相關 `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。

Phase 20.1 goal：

- 讓面試 demo 的 frontend 第一眼就是產品入口：使用者只看到客服式 RAG chat 與文件上傳，OCR、chunking、indexing、trace、raw JSON 與 eval metrics 都回到 backend API / CLI / smoke scripts。
- 只做展示質感與 README demo media 加分，不改 API contract、不新增功能範圍、不 bump version。

Phase 20.1 guardrails：

- 不新增 production eval dashboard、strategy comparison page、live eval runner、backend API、frontend route、外部依賴、DB、auth、Redis、NATS、worker、Agent runtime 或 deployment。
- 不改 retrieval algorithm、eval runner、smoke script、sample data 或 backend service。

## MVP v0.21.0 Real GPU OCR Interview Demo Path

- [x] `tasks/phase-21-real-gpu-ocr-demo/21-01-real-gpu-ocr-frontend-flow.md`: 將 frontend upload 預設改為 provider-selected `POST /documents/{document_id}/ocr` real GPU OCR-first，real OCR 失敗時保留已上傳文件並提供手動 mock OCR fallback。
- [x] 21-01 validation：`npm.cmd run build` 於 `frontend/` 通過；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`129 passed`（僅 pytest cache 權限警告）；baseline `scripts/demo-smoke-test.ps1` 通過，health version `0.21.0`、answer source `ollama/qwen3.5:4b`、retrieval source `keyword baseline`；以臨時 `DOCURAG_OCR_PROVIDER=paddleocr` backend 跑 `scripts/demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8012 -RunRealOcr` 通過，provider-selected OCR completed 且 metadata OK；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

Phase 21 goal：

- 讓面試主線不再看起來像 mock OCR demo；frontend upload 預設展示你已經有的 provider-selected PaddleOCR GPU flow。
- 保留 mock OCR 作為無 GPU / runtime 失敗時的明確手動 fallback，而不是靜默替代。
- 同步 `v0.21.0` 版本、README、backend README、frontend README、TODO、ROADMAP 與 demo script。

Phase 21 guardrails：

- 不修改 PaddleOCR provider、engine lifecycle、模型設定、OCR normalization 或 backend OCR API contract。
- 不新增 PDF rendering、image preprocessing、VLM parser、多頁 production OCR pipeline、DB、Auth、RBAC、Redis、NATS、worker、Agent runtime 或 deployment。

## MVP v0.22.0 RAG Query Hardening

- [x] `tasks/phase-22-rag-query-hardening/22-01-keyword-query-normalization.md`: 強化 `KeywordRagProvider` 的中文 tokenization 與 demo-safe alias，讓 `付款期限是什麼？` 可在 keyword baseline 命中 `Payment terms: Net 15`；同步修正 frontend / README 文案，不宣稱 backend 已有正式知識庫 ingestion / indexing pipeline。
- [x] 22-01 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`131 passed`（僅 pytest cache 權限警告）；`npm.cmd run build` 於 `frontend/` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，health version `0.22.0`、answer source `LLM unavailable fallback`、retrieval source `keyword baseline`；ticket `rg` 與 knowledge-base copy guard `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。

Phase 22 goal：

- 修正中文或近似問法無法觸發 RAG retrieval 的 demo 體感問題。
- 保留 default `/rag/query` 為 keyword baseline，不把 vector、hybrid、rerank 或 query rewrite 提前變成預設路徑。
- 同步 `v0.22.0` 版本、README、backend README、frontend README、TODO 與 ROADMAP。

Phase 22 guardrails：

- 不新增 embedding、Qdrant、BM25、rerank、hybrid retrieval、`hybrid_rerank` default chat path 或新外部依賴。
- 不新增 LLM-as-judge、answer faithfulness scoring、citation quality scoring、DB、Auth、RBAC、Redis、NATS、worker、PDF rendering、image preprocessing 或 production OCR pipeline。

## MVP v0.23.0 Viewer Chat / Admin Ingestion Role Split

- [x] `tasks/phase-23-role-split-demo/23-01-role-boundary-contract.md`: 固定 Phase 23 產品邊界，明確區分前台 Viewer Chat 與後台 Admin / Analyst Ingestion；文件 ticket，不 bump version。
- [x] `tasks/phase-23-role-split-demo/23-02-viewer-chat-only-surface.md`: 將 frontend 預設入口收斂為 Viewer Chat-only，不在前台主畫面顯示 upload / OCR / mock fallback。
- [x] `tasks/phase-23-role-split-demo/23-03-admin-ingestion-surface.md`: 建立明確的 Admin / Analyst 知識庫管理 surface，放置文件上傳、provider-selected OCR、狀態與手動 fallback。
- [x] `tasks/phase-23-role-split-demo/23-04-role-split-demo-release-sync.md`: 重跑 final validation，並在 Phase 23 完成時執行 `v0.23.0` release/version sync。
- [x] 23-01 validation：README、frontend README、demo script、architecture、ROADMAP 與 TODO 已固定 Viewer Chat / Admin Ingestion 產品邊界；文件明確說明 OCR 是 backend ingestion layer，不是前端直接對圖片聊天；保留 local JSON、local chunks、manual / explicit vector path、無正式 parser / worker / DB / auth 的限制；ticket `rg` 與 `git diff --check` 通過。
- [x] 23-02 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend 檢查首頁無文件上傳 / OCR / mock fallback controls，Viewer Chat query 後仍顯示 answer、answer source、retrieval source 與 citation summary；ticket `rg` 與 `git diff --check` 通過。
- [x] 23-03 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend 檢查 Viewer Chat 首屏無 upload / OCR controls，後台 Admin / Analyst ingestion surface 可看到文件上傳、provider-selected OCR flow、mock fallback 與 document / OCR / local chunks 狀態；baseline `scripts/demo-smoke-test.ps1` 通過；ticket `rg` 與 `git diff --check` 通過。
- [x] 23-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`131 passed`（僅 pytest cache 權限警告）；`npm.cmd run build` 於 `frontend/` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，health version `0.23.0`、answer source `LLM unavailable fallback`、retrieval source `keyword baseline`；Browser 檢查 Viewer Chat first、Admin / Analyst ingestion surface 分離，桌面與手機寬度無 horizontal overflow；ticket `rg` 與 `git diff --check` 通過。

Phase 23 goal：

- 將產品入口拆成兩條清楚路徑：Viewer 只進入 Chat 查詢已建立的知識庫；Admin / Analyst 才進入後台知識庫管理流程執行上傳、OCR 與 ingestion 狀態檢查。
- 修正目前 demo UI 把「查詢使用者」與「知識庫管理者」混在同一畫面的語意問題。
- 保留目前 local MVP 能力：backend upload、provider-selected OCR、local chunks、keyword baseline、citation 與 optional demo / eval paths。

Phase 23 guardrails：

- 不新增真實登入、RBAC、role guard、multi-user permission、PostgreSQL、Redis、NATS、worker、async queue 或 database schema。
- 不實作 VLM parser、PDF rendering、多頁 production OCR pipeline、automatic Qdrant indexing、default-on vector / hybrid / rerank chat path、Agent runtime 或 deployment。
- 不把 Admin / Analyst 後台入口說成正式權限系統；本階段只拆產品表面與 demo 工作流。
- `23-04` 才允許 `v0.23.0` version bump；`23-01` 到 `23-03` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

## MVP v0.24.0 VLM / Parser Minimal MVP

- [x] `tasks/phase-24-vlm-parser-mvp/24-01-parser-contract.md`: 固定 VLM-compatible parser contract，定義 OCR text -> invoice structured fields、parser status、source trace 與 fallback metadata；文件 ticket，不 bump version。
- [x] `tasks/phase-24-vlm-parser-mvp/24-02-invoice-parser-service.md`: 實作 deterministic invoice parser service，從既有 OCR text 抽取 invoice number、date、total amount、currency 等 MVP 欄位。
- [x] `tasks/phase-24-vlm-parser-mvp/24-03-document-fields-api.md`: 新增 `POST /documents/{document_id}/parse` 與 `GET /documents/{document_id}/fields`，並保存 parser result 到 local JSON metadata store。
- [x] `tasks/phase-24-vlm-parser-mvp/24-04-frontend-fields-surface.md`: 在 Admin / Analyst ingestion surface 顯示 parser status 與 structured fields 摘要，Viewer Chat 預設入口不顯示 parse / upload / OCR 操作。
- [x] `tasks/phase-24-vlm-parser-mvp/24-05-parser-demo-release-sync.md`: 重跑 final validation，補齊 parser demo 文件與 smoke，並在 Phase 24 完成時執行 `v0.24.0` release/version sync。

Phase 24 goal：

- 補上 JD 中「OCR / VLM 流程、複雜單據解析與結構化資料提取」的可展示切片。
- 先完成 VLM-compatible contract 與 deterministic invoice parser fallback，讓 demo 可穩定展示 OCR -> structured fields。
- 保留 future VLM / LLM parser 替換位置，但不把真正 vision model runtime 塞進第一個 parser MVP。

Phase 24 guardrails：

- 不新增真正 VLM、Ollama vision call、OpenAI-compatible VLM、LLM parser 或新外部依賴。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、Agent runtime、K8s 或 deployment 設定。
- 不修改 PaddleOCR provider、OCR model、OCR preprocessing、RAG retrieval、eval runner、Qdrant indexing 或 default chat path。
- 不實作人工修正欄位、欄位版本紀錄、audit log、表格完整重建、PDF rendering、多頁 production OCR pipeline 或 production parser dashboard。
- 不把 structured fields 接成 SQL query tool、Agent tool 或 default vector metadata filtering。
- `24-05` 才允許 `v0.24.0` version bump；`24-01` 到 `24-04` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

24-01 contract status：

- 已在 `docs/api.md` 與 `docs/architecture.md` 固定 `DocumentFields`、`ExtractedField`、`ParserResult`、parser status、source trace、fallback metadata、`POST /documents/{document_id}/parse` 與 `GET /documents/{document_id}/fields` 草案。
- Parser source 明確區分 Phase 24 MVP 的 deterministic invoice parser fallback、future text-only LLM parser 與 future VLM parser；目前不宣稱 production VLM parser，也不 bump version。
- [x] 24-01 validation：`rg -n "v0.24.0|Phase 24|Parser|VLM-compatible|DocumentFields|ExtractedField|fallback_reason" README.md TODO.md docs/ROADMAP.md docs/api.md docs/architecture.md tasks/phase-24-vlm-parser-mvp/24-01-parser-contract.md` 通過；`git diff --check` 通過（僅顯示 Windows `LF will be replaced by CRLF` 提示）。

24-02 parser service status：

- 已新增 `DocumentFields`、`ExtractedField`、`ParserResult` 與 `ParserStatus` schema，並建立 `DeterministicInvoiceParser` 作為 future VLM / LLM parser 的 fallback。
- Parser 只使用既有 OCR text / OCR lines，保留 `source_text`、`source_page`、`source_bbox`、`confidence`、`parser_source` 與 `fallback_reason`；缺欄位會回傳 missing metadata，不硬填假值。
- Unit tests 已覆蓋 sample invoice OCR text、missing field、中文標籤、TWD / 千分位金額與 OCR 未完成失敗案例；本 ticket 不新增 parse API、frontend UI、外部依賴或 version bump。
- [x] 24-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`135 passed`（僅 pytest cache 權限警告）；`rg -n "DocumentFields|ExtractedField|ParserResult|document_parser|fallback_reason" backend/app backend/tests TODO.md docs/ROADMAP.md tasks/phase-24-vlm-parser-mvp/24-02-invoice-parser-service.md` 通過；`git diff --check` 通過。

24-03 fields API status：

- 已新增 `POST /documents/{document_id}/parse` 與 `GET /documents/{document_id}/fields`，並將 parser result 保存到既有 local JSON metadata store 的 `parser_result`。
- `ProcessingStatus` 已加入 parser step，`ProcessingJobType.PARSER` 記錄明確 parse request；parser failure 不覆蓋 OCR / indexing 狀態，也不觸發 vector indexing、RAG ingestion、Qdrant upsert 或 eval run。
- API tests 已覆蓋 pending fields lookup、未 OCR parse failure、OCR 後 parse、保存後 fields lookup、storage reload 後 lookup、document not found 與 missing fields metadata。
- [x] 24-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`143 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 通過，health version `0.23.0`、answer source `ollama/qwen3.5:4b`、retrieval source `keyword baseline`；`rg -n "/parse|/fields|ParserResult|DocumentFields|fallback_reason" backend/app backend/tests docs/api.md TODO.md docs/ROADMAP.md tasks/phase-24-vlm-parser-mvp/24-03-document-fields-api.md` 通過；`git diff --check` 通過。

24-04 frontend fields surface status：

- 已在 Admin / Analyst ingestion surface 顯示 parser status、欄位解析操作、structured fields 摘要、confidence、source text、missing fields 與 failed parser state。
- Viewer Chat 預設入口仍只提供 RAG query，不顯示 upload、OCR、parse 或 ingestion 操作；UI 不宣稱 production VLM parser 或正式 RBAC。
- `frontend/README.md` 已補充 Phase 24 deterministic parser frontend slice 與 structured fields / `GET /fields` 檢查方式，並保留 production VLM parser / worker / DB 非目標說明。
- [x] 24-04 validation：`npm.cmd run build` 通過；Browser 檢查 `http://localhost:5173` desktop 與 390px mobile 通過，Viewer Chat first 不顯示 parse / upload / OCR 操作，Admin / Analyst ingestion surface 可觸發欄位解析並顯示 `AUR-2026-051`、vendor、total、confidence 與 source text，且無 horizontal overflow；`rg -n "structured fields|欄位解析|Parser|parse|fields|Viewer Chat|Admin / Analyst" frontend/src frontend/README.md TODO.md docs/ROADMAP.md tasks/phase-24-vlm-parser-mvp/24-04-frontend-fields-surface.md` 通過；`git diff --check` 通過。

24-05 parser demo release sync status：

- 已完成 `v0.24.0` version sync：backend package / app version、frontend package / lock / fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 已同步。
- `README.md`、`backend/README.md`、`frontend/README.md`、`docs/demo-script.md`、`TODO.md` 與 `docs/ROADMAP.md` 已補齊 parser demo wording；文件明確說明 Phase 24 是 deterministic parser MVP / VLM-compatible contract，不是 production VLM parser、LLM parser、worker、DB、Auth/RBAC、Agent runtime 或 deployment。
- `scripts/demo-smoke-test.ps1` 已加入 upload -> OCR mock -> parser -> fields lookup -> baseline RAG query 驗證，並檢查 `/health` version `0.24.0`、parser source、invoice number、vendor、total、currency 與 source text。
- [x] 24-05 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`143 passed`（僅 pytest cache 權限警告）；`npm.cmd run build` 通過；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/demo-smoke-test.ps1` 通過，health version `0.24.0`、parser fields `AUR-2026-051` / `1248.5 USD`、answer source `LLM unavailable fallback`、retrieval source `keyword baseline`；Browser 檢查 `http://localhost:5173` desktop 與 390px mobile 通過，Viewer Chat first 不顯示 parse / upload / OCR，Admin / Analyst ingestion surface 顯示 parser status、欄位解析操作、`AUR-2026-051` 與 structured fields 摘要，且無 horizontal overflow；`rg -n "v0.24.0|Phase 24|Parser|structured fields|欄位解析|VLM-compatible|DocumentFields|ExtractedField" README.md backend/README.md frontend/README.md docs/demo-script.md docs/ROADMAP.md TODO.md backend/app frontend/src tasks/phase-24-vlm-parser-mvp` 通過；`git diff --check` 通過。

## MVP v0.25.0 Agent Tool-use Minimal MVP

- [x] `tasks/phase-25-agent-tool-use-mvp/25-01-agent-boundary-contract.md`: 固定 Agent MVP boundary、allowlisted tools、deterministic planner、run / step / tool call / observation / final answer trace schema；文件 ticket，不 bump version。
- [x] `tasks/phase-25-agent-tool-use-mvp/25-02-agent-tool-adapters.md`: 實作 demo-safe allowlisted tool adapters：`get_document_fields`、`search_documents`、`summarize_invoice_fields`，只封裝既有 structured fields 與 retrieval 能力。
- [x] `tasks/phase-25-agent-tool-use-mvp/25-03-agent-run-api.md`: 新增 deterministic Agent run API，支援 `POST /agent/run` 與 `GET /agent/runs/{run_id}`，並輸出 plan、tool calls、observations、final answer 與 citations。
- [x] `tasks/phase-25-agent-tool-use-mvp/25-04-frontend-agent-trace-surface.md`: 在 demo UI 新增 Agent trace surface，展示 plan -> tool calls -> observations -> final answer + citations；Viewer Chat 預設入口保持不變。
- [x] `tasks/phase-25-agent-tool-use-mvp/25-05-agent-demo-release-sync.md`: 補齊 Agent demo validation、文件同步與 `v0.25.0` release/version bump。

Phase 25 goal：
- 補上 JD 中「AI Agent 架構、Skill / Tool-use 與 Task Planning」的 demo 證據。
- 把 Phase 24 structured fields、既有 RAG retrieval 與 citation 串成 deterministic tool-use flow。
- 讓 demo 展示 plan -> tool calls -> observations -> final answer + citations，並維持 production guardrails。

Phase 25 guardrails：
- 不新增 LLM autonomous planner、OpenAI function calling、Ollama planning call、streaming agent 或新外部依賴。
- 不新增任意 SQL、PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、role guard、project permission 或 multi-user isolation。
- 不允許 Agent 執行 delete、reindex、file system command、shell command、任意 tool execution 或 destructive operation。
- 不修改 parser extraction、OCR provider、RAG ranking、eval runner、Qdrant indexing 或 default Viewer Chat path。
- 不把 Agent trace surface 說成 production Agent dashboard 或正式權限系統。
- `25-05` 才允許 `v0.25.0` version bump；`25-01` 到 `25-04` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

25-01 agent boundary contract status：

- 已在 `docs/api.md` 定義 Phase 25 Agent Tool-use contract：`AgentRun`、`AgentStep`、`AgentToolCall`、observation、final answer、citations、trace metadata 與 future `POST /agent/run` / `GET /agent/runs/{run_id}` endpoint boundary。
- 已在 `docs/architecture.md` 固定 Agent MVP 只能使用 deterministic planner 與 allowlisted read-only tools：`get_document_fields`、`search_documents`、`summarize_invoice_fields`。
- 文件明確禁止任意 SQL、任意工具執行、delete、reindex、shell / file system command、DB、RBAC、worker、Redis / NATS 與 production autonomous Agent 宣稱。
- 本 ticket 只改 Markdown，不 bump version；完整 runtime 與 `v0.25.0` release sync 留給 `25-02` 到 `25-05`。
- [x] 25-01 validation：`rg -n "v0.25.0|Phase 25|Agent|tool-use|get_document_fields|search_documents|summarize_invoice_fields|deterministic planner|allowlisted" README.md TODO.md docs/ROADMAP.md docs/api.md docs/architecture.md tasks/phase-25-agent-tool-use-mvp/25-01-agent-boundary-contract.md` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。

25-02 agent tool adapters status：

- 已新增 `backend/app/schemas/agent.py` 與 `backend/app/services/agent_tools.py`，固定 `AgentToolCall`、tool observation、tool status 與 allowlisted tool output shape。
- 已實作 read-only `get_document_fields`、`search_documents` 與 `summarize_invoice_fields` adapters，只讀既有 local JSON parser result 與既有 RAG / keyword retrieval path，不執行任意 SQL、delete、reindex、shell / file system command 或 destructive operation。
- Backend tests 已覆蓋有 fields、缺 parser result、search hit、search miss、tool error 與 deterministic invoice summary。
- 本 ticket 不新增 Agent run API、frontend UI、LLM planner、DB、RBAC、worker、Redis / NATS 或新外部依賴；完整 release sync 留給 `25-05`。
- [x] 25-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`149 passed`（僅 pytest cache 權限警告）；ticket 指定 `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

25-03 agent run API status：

- 已新增 `POST /agent/run` 與 `GET /agent/runs/{run_id}`，用 deterministic planner 串接 allowlisted `get_document_fields`、`search_documents` 與 `summarize_invoice_fields`。
- Agent run result 會保存到 local JSON metadata store `agent_runs.json`，lookup endpoint 只讀保存結果，不重跑 planner 或 tools。
- Backend tests 已覆蓋 successful run、missing parser fields、search fallback、run lookup、invalid document 與 missing run lookup。
- 本 ticket 不新增 frontend UI、LLM autonomous planner、OpenAI function calling、Ollama planning call、streaming、DB、RBAC、worker、Redis / NATS、destructive tools 或新外部依賴；完整 release sync 留給 `25-05`。
- [x] 25-03 validation：`python -m pytest backend/tests/test_agent.py -q` 通過，`6 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`155 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 通過，health version `0.24.0`、parser fields `AUR-2026-051` / `1248.5 USD`、RAG query OK；ticket 指定 `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

25-04 frontend agent trace surface status：

- 已在 Admin / Analyst ingestion surface 新增 Agent trace panel，可用 demo-safe task、document 與 query 呼叫 `POST /agent/run`。
- Agent trace surface 會顯示 plan、tool calls、observation、final answer、citations、trace metadata 與 fallback state；Viewer Chat 預設入口仍不顯示 upload、OCR、parse 或 Agent operations。
- 本 ticket 不新增 frontend route、auth / RBAC、role guard、project permission、LLM autonomous planner、streaming UI、worker、DB、tool console 或 production Agent dashboard。
- [x] 25-04 validation：`npm.cmd run build` 通過；Browser 檢查 `http://localhost:5176`（臨時 backend `http://127.0.0.1:8003`）通過，Viewer Chat first 不顯示 Agent trace / Run Agent / upload 操作，Admin / Analyst Agent trace surface 可執行成功 run 並顯示 final answer / citations / tool trace，fallback run 顯示 `no_retrieved_chunks`，desktop 1280px 與 mobile 390px 均無 horizontal overflow；ticket 指定 `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

25-05 agent demo release sync status：

- 已完成 `v0.25.0` version sync 實作：backend package / app version、frontend package / lock / fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 已同步。
- `scripts/demo-smoke-test.ps1` 已加入 upload -> OCR mock -> parser -> fields lookup -> Agent run -> Agent lookup -> baseline RAG query 驗證，並檢查 deterministic planner、`allowlisted_read_only` tool policy、三個 allowlisted tools、final answer 與 citations。
- `README.md`、`backend/README.md`、`frontend/README.md`、`docs/demo-script.md`、`TODO.md` 與 `docs/ROADMAP.md` 已補齊 Agent tool-use demo wording；文件明確說明 Phase 25 是 deterministic planner + allowlisted tools，不是 production autonomous Agent、LLM planner、任意 SQL、正式 RBAC、worker、DB 或 deployment。
- [x] 25-05 validation：backend tests 通過，`155 passed`（僅 pytest cache 權限警告）；frontend build 通過；baseline demo smoke 通過，health version `0.25.0`，Agent run / lookup OK，RAG query OK；Browser 桌面檢查通過，Viewer Chat first、Admin / Analyst ingestion Agent trace surface、`Run Agent` success 與無 horizontal overflow 已確認；本批 final `rg` 與 `git diff --check` 已重跑通過。

## MVP v0.26.0 Real VLM Parser Provider Spike

- [x] `tasks/phase-26-vlm-parser-provider-spike/26-01-vlm-provider-decision.md`: 固定 VLM provider env、input / output contract、fallback policy 與 Agent 承接方式；文件 ticket，不 bump version。
- [x] `tasks/phase-26-vlm-parser-provider-spike/26-02-vlm-input-resolver.md`: 新增 demo-safe image input resolver，只解析既有上傳檔案，不做 PDF rendering 或 VLM call。
- [x] `tasks/phase-26-vlm-parser-provider-spike/26-03-vlm-parser-adapter.md`: 新增 VLM-first `vlm_invoice` parser adapter，輸出沿用 Phase 24 `DocumentFields` schema。
- [x] `tasks/phase-26-vlm-parser-provider-spike/26-04-parser-source-comparison.md`: 在 API / trace 顯示 `deterministic_invoice` vs `vlm_invoice` 的 parser source、fallback reason、confidence 與 source input。
- [x] `tasks/phase-26-vlm-parser-provider-spike/26-05-vlm-parser-demo-release-sync.md`: 補齊 VLM parser demo validation、文件同步與 `v0.26.0` release/version bump。

Phase 26 goal：
- 補上 JD 中「多模態與 OCR：熟悉 VLM 與 OCR 流程，能處理複雜單據解析與結構化資料提取」的可展示切片。
- 承接 Phase 24 parser schema 與 Phase 25 Agent tool-use：VLM parser 產生 structured fields，Agent `get_document_fields` 讀取保存結果。
- 以 VLM-first provider spike 展示 provider boundary、fallback、trace 與 demo-safe validation；`deterministic_invoice` 只作 fallback / debug override，不再是 Phase 26 後的預設路徑。

Phase 26 guardrails：
- 不新增 production VLM parser、OpenAI SDK、streaming、function calling 或新外部依賴；Phase 26 的 default-on 只代表 demo parser path 預設 VLM-first。
- 不新增 PDF rendering、image preprocessing、layout analysis、多頁 production parser pipeline、table reconstruction、人工修正 workflow 或 parser dashboard。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、Agent permission model、K8s 或 deployment 設定。
- 不修改 Phase 25 Agent planner / tool allowlist；Agent 不直接呼叫 VLM，只透過 `get_document_fields` 消費 parser result。
- 不修改 RAG ranking、eval runner、Qdrant indexing 或 default Viewer Chat path。
- `26-05` 才允許 `v0.26.0` version bump；`26-01` 到 `26-04` 若未形成完整 release artifact，必須寫 `Version bump required: no`。
- 後續執行 Phase 26 runtime ticket 時，不得為了維持舊 demo 相容而讓 deterministic parser 繼續當預設；VLM provider unavailable / timeout / invalid response 時才 fallback。

26-01 VLM provider decision status：

- 已在 `docs/api.md` 定義 `DOCURAG_VLM_PROVIDER`、`DOCURAG_VLM_BASE_URL`、`DOCURAG_VLM_MODEL`、`DOCURAG_VLM_TIMEOUT_SECONDS`、`DOCURAG_VLM_MIN_CONFIDENCE` 與 `DOCURAG_PARSER_SOURCE`。
- 已在 `docs/api.md` / `docs/architecture.md` 固定 VLM-first parser input / output contract、fallback chain、confidence metadata 與 Agent `get_document_fields` 承接方式。
- 本 ticket 只改 Markdown，不 bump version；完整 runtime 與 `v0.26.0` release sync 留給 `26-02` 到 `26-05`。

26-02 VLM input resolver status：

- 已新增 `VlmInputResolver` / `VlmInputDescriptor` building block，從既有 document upload metadata 解析 `data/uploads/` 內的 demo-safe `.png` / `.jpg` / `.jpeg`。
- Resolver 對 `unsupported_file`、`missing_file`、`unsafe_path` 與 `file_not_readable` 回傳明確 fallback reason，不呼叫 VLM、不改 `POST /documents/{document_id}/parse` 行為。
- Focused tests 已覆蓋 supported image、missing file、unsupported extension 與 unsafe path。

26-03 VLM parser adapter status：

- 已新增 VLM-first `VlmInvoiceParser`、Ollama-style local HTTP provider、disabled provider 與 parser dependency routing；`DOCURAG_PARSER_SOURCE=deterministic_invoice` 只作 explicit debug / validation override。
- VLM success 會輸出既有 `DocumentFields` / `ParserResult` schema，並標記 `parser_source=vlm_invoice`；provider unavailable、timeout、invalid response、missing fields 或低 confidence 時 fallback 到 `deterministic_invoice`。
- Focused tests 已覆蓋 VLM success、provider unavailable fallback、timeout / provider failure、invalid response、missing fields 與 explicit deterministic override。

26-04 parser source comparison status：

- Parser response trace 已可透過 `parser_route`、`fallback_chain`、`fallback_reason`、`deterministic_fallback_reason`、`confidence_summary` 與 source input metadata 區分 `vlm_invoice` vs `deterministic_invoice`。
- VLM fallback 時 top-level `ParserResult.fallback_reason` 顯示 VLM / resolver failure reason；deterministic fallback 自身 missing metadata 保留於 trace，不新增平行 schema。
- Backend tests 已覆蓋 VLM success trace、VLM fallback trace 與 explicit deterministic override trace；`frontend/README.md` 已補充這是 demo visibility，不是 production parser comparison dashboard。

26-05 VLM parser demo release sync status：

- 已同步 backend package / app version、frontend package / lock / fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `0.26.0`。
- `scripts/demo-smoke-test.ps1` 現在驗證 text input 的 VLM-first fallback path：`fallback_reason=unsupported_file`、`fallback_chain=vlm_invoice -> deterministic_invoice`，並確認 Agent `get_document_fields` observation 可讀到 parser source / fallback reason。
- 新增 `DOCURAG_VLM_PROVIDER=fake` demo / smoke stub，用於 image input 的 `vlm_invoice` success path；Agent tool contract 不變，仍只讀保存後的 parser result。
- README、backend README、frontend README、docs/demo-script.md、docs/api.md、docs/architecture.md、TODO 與 ROADMAP 已同步 Phase 26 demo 說法：這是 VLM-first provider spike，不是 production VLM parser。

## MVP v0.27.0 Aggressive Demo Defaults

- [x] `tasks/phase-27-aggressive-defaults/27-01-aggressive-demo-defaults.md`: 啟用 default `hybrid_rerank` RAG / Agent search、Ollama embedding、FastEmbed rerank adapter、frontend parser + vector indexing best-effort flow 與 `v0.27.0` release/version bump。

Phase 27 goal：
- 把已實作、已有 fallback、可驗證的進階 demo 能力改成預設路徑：`hybrid_rerank` RAG / Agent search、Ollama embedding、FastEmbed rerank adapter，以及 Admin ingestion 後的 parser + vector indexing best-effort flow。
- 讓 demo 開場就走最完整的先進路徑；本機模型、Qdrant 或 reranker 不可用時，回到 keyword evidence，並在 trace / UI 顯示原因。

Phase 27 guardrails：
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth / RBAC、OpenAI SDK、vLLM、production VLM parser、PDF rendering、K8s 或 deployment 設定。
- 不把 best-effort vector indexing 說成正式背景任務或 production ingestion pipeline。
- 不移除 keyword、deterministic parser 或 mock OCR；它們只作 fallback、manual override、debug path 或 validation path。

27-01 aggressive defaults status：

- Backend 預設已改為 `hybrid_rerank`，embedding 預設 Ollama，rerank 預設 FastEmbed adapter；`/rag/query` 與 Agent `search_documents` 使用同一個 RAG provider selection。
- `/rag/query` 已接上 `vector`、`vector_rerank`、`hybrid` 與 `hybrid_rerank` runtime provider；embedding、Qdrant 或 reranker 不可用時，會回到 keyword evidence 並保留 fallback metadata。
- Frontend 預設進入 Admin / Analyst ingestion surface；OCR 成功後會 best-effort 執行 parser 與 vector indexing，失敗時保留明確訊息，不阻斷主要 demo。
- README、backend README、frontend README、docs/demo-script.md、docs/api.md、docs/architecture.md、PRD、TODO、ROADMAP、Docker Compose、`.env.example` 與 demo smoke script 已同步 `v0.27.0` aggressive default 說法。
- [x] 27-01 validation：backend tests 通過，`166 passed`（僅 pytest cache 權限警告）；frontend build 通過；baseline demo smoke 通過，health version `0.27.0`、retrieval source `hybrid_rerank fallback: reranker_unavailable`；Browser 檢查 desktop 1280px 與 mobile 390px 預設皆為 Admin / Analyst ingestion surface，且無 horizontal overflow；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

## Release Verification Status

- [x] v0.0: repo structure、docs、tasks 已完成。
- [x] v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- [x] Python fallback: `scripts/check-dev-env.ps1` 與 `scripts/test-backend.ps1` 可透過 `pip.exe` 反推實際 `python.exe`。
- [x] Upload stub: pytest 與本機 HTTP 驗證皆通過。
- [x] Docker: `docker` CLI、Docker build 與 Docker Compose healthcheck 已驗證。
- [x] v0.2.0: Demo UI、backend CORS、Backend CI 與 Docker 驗證已完成。
- [x] v0.3.0: Document Local Storage、文件列表、文件詳情、frontend list UI 與 Docker Compose upload 驗證已完成。
- [x] v0.4.0: OCR Mock Pipeline、frontend OCR UI 與 Docker Compose OCR mock API 驗證已完成。
- [x] v0.5.0: Local RAG Baseline、frontend Chat UI 與 Docker Compose RAG API 驗證已完成。
- [x] v0.5.1: Demo Hardening、公開 sample data、demo seed script、API smoke test 與 Docker Compose demo 驗證已完成。
- [x] v0.6.0: Bridge Contracts、OCR provider interface、RAG provider interface、processing status、chunk citation schema 與 processing job contract。
- [x] v0.7.0: Real OCR Provider Spike 已完成；07-01 到 07-04 已執行，Docker validation 需待 Docker Desktop daemon 可用後重跑。
- [x] v0.8.0: PaddleOCR Runtime Stabilization 已完成；Python 3.12、PaddleOCR 2.10.0、PaddlePaddle 3.0.0 sample real OCR flow 已驗證。
- [x] v0.9.0: GPU Runtime 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.9.0`，本機 Python 3.12 + CUDA PaddlePaddle GPU runtime 與繁中 provider-selected OCR smoke 已通過。
- [x] v0.9.1: OCR Performance Hardening 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.9.1`，PaddleOCR startup preload、provider reuse、timing metadata、`cls=False` baseline 與 provider-selected real OCR smoke 已通過。
- [x] v0.10.0: LLM RAG Backlog 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.10.0`，Ollama `qwen3.5:4b` provider decision、最小 client、optional generation path、demo smoke `-RunLlm` 與 frontend answer source 已補齊。
- [x] v0.11.0: Vector RAG Backlog 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.11.0`，Ollama `qwen3-embedding:0.6b` embedding client、Qdrant local runtime / collection smoke、optional vector retrieval path、fallback trace metadata、demo smoke `-RunVector` 與 frontend retrieval source 已補齊。
- [x] v0.12.0: Vector Indexing Hardening 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.12.0`，manual vector indexing contract、同步 indexing service、`POST /documents/{document_id}/index/vector`、optional vector indexing smoke 與 fallback-safe vector retrieval 已補齊。
- [x] v0.13.0: Retrieval Evaluation Baseline 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.13.0`，公開 eval dataset、retrieval eval runner、baseline eval smoke、optional vector eval smoke 與 metrics output 已補齊。
- [x] v0.15.0: Rerank Runtime Spike 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.15.0`，FastEmbed provider decision、disabled-by-default rerank adapter、optional `vector_rerank` eval strategy、rerank trace metadata 與 baseline smoke 已補齊。
- [x] v0.16.0: Hybrid Retrieval Slice 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.16.0`，公開 eval dataset 擴充到 12 筆、optional `hybrid` eval strategy、hybrid trace metadata、baseline smoke 與 optional `-RunHybrid` smoke 已補齊。
- [x] v0.17.0: Retrieval Trace UI / Eval Visibility 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.17.0`，frontend trace panel、eval summary fallback / trace metadata reporting、baseline demo smoke、baseline eval smoke、optional `-RunVector` / `-RunVectorRerank` / `-RunHybrid` smoke 與 Browser trace UI 檢查已補齊。
- [x] v0.18.0: Hybrid Rerank Planning 已完成；本次只新增 Markdown planning tickets / TODO / ROADMAP，不 bump backend、frontend、health test 或 Docker Compose version。
- [x] v0.19.0: Hybrid Rerank Runtime 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `v0.19.0`，optional `hybrid_rerank` eval provider、`-RunHybridRerank` smoke flag、trace / report metadata、baseline demo smoke 與 baseline eval smoke 已補齊；optional vector-backed smoke 需待本機 Qdrant collection `docurag_chunks_v1` 可用後重跑。
- [x] v0.20.0: Interview MVP Packaging 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `v0.20.0`，demo script、sample / eval coverage、demo media、baseline demo smoke、baseline retrieval eval smoke 與 final validation 已補齊；optional vector-backed smoke 需待本機 Qdrant collection `docurag_chunks_v1` 可用後重跑。
- [x] v0.21.0: Real GPU OCR Interview Demo Path 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO、ROADMAP 與 demo script 已同步到 `v0.21.0`；frontend upload 已改為 provider-selected real OCR-first flow，mock OCR 只作手動 fallback；frontend build、backend tests、baseline demo smoke、real OCR smoke、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.22.0: RAG Query Hardening 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `v0.22.0`；keyword query normalization、CJK tokenization、demo-safe 中文 alias、backend tests、frontend build、baseline demo smoke、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.23.0: Viewer Chat / Admin Ingestion Role Split 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、frontend fallback version、demo script、architecture、TODO 與 ROADMAP 已同步到 `v0.23.0`；Viewer Chat-only 預設入口、Admin / Analyst ingestion surface、backend tests、frontend build、baseline demo smoke、Browser role split / overflow 檢查、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.24.0: VLM / Parser Minimal MVP 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、demo script、TODO 與 ROADMAP 已同步到 `v0.24.0`；deterministic invoice parser fallback、parse / fields API、local JSON parser result persistence、frontend structured fields surface、parser demo smoke、Browser structured fields / overflow 檢查、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.25.0: Agent Tool-use Minimal MVP 版本 / 文件 / smoke 實作已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、demo script、TODO 與 ROADMAP 已同步到 `v0.25.0`；deterministic planner、allowlisted tool adapters、Agent run / lookup API、frontend trace surface、Agent demo smoke、Browser desktop Agent trace / overflow 檢查、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.26.0: Real VLM Parser Provider Spike 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、demo script、TODO、ROADMAP、API 與 architecture 文件已同步到 `v0.26.0`；VLM-first parser provider boundary、demo-safe image input resolver、`vlm_invoice` adapter、parser source comparison、fake / stub success smoke、provider unavailable fallback 與 Agent `get_document_fields` consumption validation 已補齊。
- [x] v0.27.0: Aggressive Demo Defaults 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、demo script、TODO、ROADMAP、API、architecture、PRD 與 `.env.example` 已同步到 `v0.27.0`；default `hybrid_rerank` RAG / Agent search、Ollama embedding、FastEmbed rerank adapter、frontend parser + vector indexing best-effort flow、fallback-safe demo smoke 與 Browser default surface validation 已補齊。
