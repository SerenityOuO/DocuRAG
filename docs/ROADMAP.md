# Roadmap

本 roadmap 記錄 Phase 00 到 v0.12.0 的已交付切片，並追蹤下一階段 v0.13.0 backlog。後續每個 Phase 都必須對應明確版本號，避免 README / TODO / ROADMAP 出現 release 狀態脫節。

## Phase 00 - Bootstrap Documents and Tickets

Goal：建立可協作、可逐步開發的 repo 文件與 ticket 系統。

Deliverables：

- `README.md`
- `AGENTS.md`
- `TODO.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `tasks/_TEMPLATE.md`
- `tasks/phase-00-bootstrap/00-01-repo-structure.md`
- `tasks/phase-00-bootstrap/00-02-project-docs.md`

Acceptance：

- 所有 Phase 00 文件存在。
- README 說明專案目標、MVP 範圍與開發方向。
- AGENTS 說明小 ticket 開發流程。
- TODO 包含 Phase 00 到 v0.12.0 checklist。

## Phase 01 - Backend Bootstrap

Goal：建立 backend 最小可驗證入口，不實作業務功能。

Tickets：

- `tasks/phase-01-backend-bootstrap/01-01-backend-healthcheck.md`
- `tasks/phase-01-backend-bootstrap/01-02-backend-docker.md`

Expected Outcome：

- backend 有最小 `/health`。
- healthcheck 可以用測試或手動 request 驗證。
- Docker 邊界只包住 Phase 01 所需的 backend 啟動，不加入 Redis、NATS、Qdrant 或 vLLM。

## Phase 02 - Document Foundation

Goal：建立文件領域的最小 API 與 metadata contract。

Tickets：

- `tasks/phase-02-document-foundation/02-01-document-upload-api.md`
- `tasks/phase-02-document-foundation/02-02-document-metadata-schema.md`

Expected Outcome：

- 可以定義文件上傳 API 的 request / response 行為。
- 可以描述 document metadata 與狀態流轉。
- 不觸發 OCR、RAG、worker、Qdrant 或 Redis。

## Roadmap Guardrails

- Phase 00 只做文件與票券。
- Phase 01 只做 backend 啟動與 healthcheck。
- Phase 02 只做文件上傳與 metadata foundation。
- v0.4.0 只做 OCR mock pipeline，不接真正 OCR engine 或 async worker。
- v0.5.0 只做 local RAG baseline，不接 LLM、OpenAI API、Ollama、vLLM、embedding、Qdrant 或 rerank。
- v0.5.1 只做 demo hardening，不新增 Qdrant、embedding、rerank、真正 LLM、OpenAI API、Ollama、vLLM、Redis、NATS、PostgreSQL、登入或 RBAC。
- v0.6.0 只做 bridge contracts，不接真正 OCR、embedding、Qdrant、rerank、LLM、Redis、NATS、PostgreSQL、登入或 RBAC。
- v0.7.0 只做單一 local OCR provider spike，預設仍保留 mock provider，不接 queue、DB、Qdrant、embedding、rerank、LLM、Redis、NATS、登入或 RBAC。
- v0.8.0 只做 PaddleOCR runtime stabilization，不新增 PDF rendering、Qdrant、embedding、rerank、LLM、worker、DB、登入或 RBAC。
- v0.9.0 只做 PaddleOCR GPU runtime 與模型選擇 backlog，不接 LLM、embedding、Qdrant、worker、DB、登入或 RBAC。
- v0.9.1 只做 PaddleOCR engine lifecycle、backend startup preload、provider reuse、timing log、baseline 與小範圍 OCR 參數調校，不接 worker、Redis、NATS、資料庫 schema、PDF pipeline、登入或 RBAC。
- v0.10.0 只做 LLM RAG provider / client / demo smoke，不接 embedding、Qdrant、rerank、worker、DB、登入或 RBAC。
- v0.11.0 只做 vector RAG provider decision、embedding client、Qdrant local runtime 與 optional vector retrieval demo；保留 keyword RAG fallback，不實作 rerank、hybrid search、eval runner、worker、DB、登入或 RBAC。
- v0.12.0 只做 optional vector indexing contract、manual indexing service / API 與 demo smoke hardening；不實作 rerank、hybrid search、eval runner、worker、DB、登入或 RBAC。
- v0.13.0 只做 retrieval evaluation baseline、公開 eval dataset、metrics runner 與 demo smoke；不實作 rerank、hybrid search、LLM-as-judge、worker、DB、登入或 RBAC。
- `README.md` 的 Release Status 必須只列版本號；Phase 細節寫在本 roadmap。
- 每張 ticket 完成後才進下一張，不平行擴張範圍。

## v0.2.0 Demo UI Milestone

Goal：建立可面試展示的最小 UI，讓使用者能看到 backend health，並把檔案送到既有 `/documents/upload` stub。

Expected Outcome：

- GitHub Actions `Backend CI` 會在 push 與 pull request 執行 backend pytest。
- Vue 3 + Vite frontend 使用 `VITE_API_BASE_URL` 呼叫 backend。
- backend CORS 允許 `http://localhost:5173` 與 `http://127.0.0.1:5173`。
- Docker CLI、backend Docker build、Compose build、Compose up healthcheck 可驗證。
- 不新增 OCR、RAG、Qdrant、Redis、NATS、vLLM、登入、權限或資料庫 schema。

## v0.3.0 Document Local Storage Milestone

Goal：把文件上傳從 stub 升級為可驗證的本機 storage MVP，讓 demo 可以呈現「上傳後真的保存、可列出、可查詳情」。

Expected Outcome：

- `POST /documents/upload` 會將原始檔保存到 `data/uploads/`。
- document metadata 會保存到 `data/documents.json`。
- `GET /documents` 依 `created_at` 由新到舊回傳文件列表。
- `GET /documents/{document_id}` 回傳指定文件 metadata，找不到時回傳 404。
- frontend 在上傳成功後刷新文件列表，並可點選文件查看 metadata JSON。
- Docker Compose 掛載 repo root 的 `data/` 到 container `/app/data`，啟動後可通過 healthcheck 與 upload API 驗證。
- 不新增 OCR、RAG、Qdrant、Redis、NATS、vLLM、登入、權限、PostgreSQL、embedding、rerank 或 Agent。

## v0.4.0 OCR Mock Pipeline Milestone

Goal：建立可替換的 OCR mock pipeline，讓 demo 可以呈現「文件上傳後可執行 OCR、保存結果、前端顯示文字與欄位」。

Ticket：

- `tasks/phase-03-ocr-mock/03-01-ocr-mock-pipeline.md`

Expected Outcome：

- `POST /documents/{document_id}/ocr/mock` 對既有文件產生 deterministic mock OCR text 與 extracted fields。
- `GET /documents/{document_id}/ocr` 回傳 OCR status、text、extracted fields 與 updated timestamp。
- 未執行 OCR 的文件回傳 `pending` OCR status。
- OCR result 保存到 `data/documents.json` 的對應 document metadata。
- frontend 可在文件詳情執行 Run Mock OCR。
- frontend 顯示 OCR status、OCR text 與 extracted fields。
- 不新增 PaddleOCR、Tesseract、VLM、RAG、Qdrant、Redis、NATS、vLLM、登入、RBAC 或 PostgreSQL。

## v0.5.0 Local RAG Baseline Milestone

Goal：使用 v0.4.0 的 OCR mock text 作為知識來源，建立第一版可驗證的 local RAG baseline。

Ticket：

- `tasks/phase-05-rag-baseline/05-01-local-rag-baseline.md`

Expected Outcome：

- OCR mock 完成後會從 OCR text 產生 chunks，並保存到 local JSON metadata store。
- 每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。
- `POST /rag/query` 接收 `query` 與 `top_k`。
- local keyword retrieval 從 chunks 回傳 matched chunks、score、`document_id` 與 `chunk_id`。
- RAG response 包含 deterministic answer、citations 與 retrieved chunks。
- citations 指出 `document_id`、`filename` 與 `chunk_id`。
- frontend 新增 RAG chat，顯示 answer、citations 與 retrieved chunks。
- 不新增真正 LLM、OpenAI API、Ollama、vLLM、embedding、Qdrant、rerank、Redis、NATS、PostgreSQL、登入或 RBAC。

## v0.5.1 Demo Hardening Milestone

Goal：讓 v0.5.0 的 upload -> OCR mock -> local RAG -> citations 流程更適合 GitHub 與面試展示。

Ticket：

- `tasks/phase-05-rag-baseline/05-02-demo-hardening.md`

Expected Outcome：

- `sample-data/documents/` 提供公開虛構 sample documents，不包含真實個資或公司敏感資料。
- `scripts/seed-demo-data.ps1` 可自動上傳 sample、執行 OCR mock、執行 local RAG query，並輸出 answer、citations、retrieved chunks。
- `scripts/demo-smoke-test.ps1` 可重跑驗證 `/health`、upload、OCR mock 與 `/rag/query`。
- README 提供 5 分鐘 demo 指令、backend/frontend/Docker 啟動方式、範例問題與預期結果。
- `/health` 回傳 version `0.5.1`。
- demo 明確標示目前是 local keyword RAG baseline，不是 embedding、Qdrant、rerank 或 LLM。
- 不新增 Qdrant、embedding、rerank、真正 LLM、OpenAI API、Ollama、vLLM、Redis、NATS、PostgreSQL、登入或 RBAC。

## v0.6.0 Bridge Contracts Milestone

Goal：在真正 OCR / RAG provider 進場前，先把可替換邊界、處理狀態、chunk / citation metadata 與 processing job contract 打穩，避免後續接模型時重寫既有 API 與 frontend demo flow。

Tickets：

- `tasks/phase-06-bridge/06-01-ocr-provider-interface.md`
- `tasks/phase-06-bridge/06-02-rag-provider-interface.md`
- `tasks/phase-06-bridge/06-03-processing-status-contract.md`
- `tasks/phase-06-bridge/06-04-chunk-citation-schema.md`
- `tasks/phase-06-bridge/06-05-processing-job-contract.md`

Expected Outcome：

- OCR mock 已整理成最小 OCR provider / service 邊界，仍只保留 mock provider。
- local keyword RAG 已整理成最小 RAG provider / service 邊界，仍只保留 keyword provider。
- document processing status 已可清楚描述 upload、OCR、indexing、ready 與 failed 流轉。
- chunk 與 citation schema 已可承接 page、bbox、confidence 與 trace metadata，但不實作真正 OCR bbox 或 citation evaluation。
- processing job contract 已可記錄本機同步 job metadata，但不引入真正 worker、queue、Redis 或 NATS。
- 既有 upload -> OCR mock -> local RAG -> citations demo flow 保持可用。
- 不新增真正 OCR engine、embedding、Qdrant、rerank、LLM、OpenAI API、Ollama、vLLM、Redis、NATS、PostgreSQL、登入或 RBAC。

## v0.7.0 Real OCR Provider Spike Milestone

Goal：在 v0.6 bridge contracts 穩定後，挑選一個本機可驗證 OCR provider 做 spike；實作必須保留 mock fallback，並避免把 queue、DB、embedding 或 LLM 範圍提前拉進來。

Tickets：

- `tasks/phase-07-real-ocr-provider/07-01-ocr-provider-decision.md`
- `tasks/phase-07-real-ocr-provider/07-02-ocr-provider-adapter.md`
- `tasks/phase-07-real-ocr-provider/07-03-ocr-output-normalization.md`
- `tasks/phase-07-real-ocr-provider/07-04-real-ocr-demo-hardening.md`

Expected Outcome：

- 07-01 已選定 PaddleOCR 作為單一 Phase 07 OCR provider，並記錄安裝條件、明確失敗行為與 demo 風險。
- 07-02 已新增 `DOCURAG_OCR_PROVIDER` 設定與 provider-selected `POST /documents/{document_id}/ocr`，預設仍保持 mock demo 可用。
- 07-03 已新增 `OcrResult.lines` normalization，real OCR output 可映射到既有 `DocumentChunk`、processing status、processing job 與 citation trace contract。
- 07-04 已補齊 optional real OCR demo flow；沒有 real OCR dependency 的環境仍可用 mock path 重跑。
- 不新增 queue、Redis、NATS、Qdrant、embedding、rerank、LLM、PostgreSQL、登入或 RBAC。

Phase 07 provider decision：

- 選定 provider：`PaddleOCR`。
- 選定原因：Python backend 可直接 lazy import；輸出可包含 text、bbox 與 confidence，適合接到 v0.6 chunk / citation trace contract。
- 主要風險：依賴較重，首次 real OCR 可能需要模型下載；Docker 與 Windows 本機環境都需要在 07-04 清楚標記驗證條件。
- unavailable 行為：real provider endpoint 必須清楚失敗並更新 processing status / processing job metadata；不得靜默改跑 mock。既有 `POST /documents/{document_id}/ocr/mock` 繼續可用。
- adapter 狀態：07-02 已接入 lazy-import `PaddleOcrProvider`、`backend[real-ocr]` optional extra、`DOCURAG_INSTALL_REAL_OCR` Docker build arg 與 Compose `DOCURAG_OCR_PROVIDER` env；預設不安裝 real OCR dependency。
- normalization 狀態：07-03 已把 PaddleOCR line text、page、bbox、confidence 與 metadata 正規化到 `OcrTextLine`，並由 chunks、citations 與 retrieved_chunks 一致帶出 trace metadata。
- demo 狀態：07-04 已加入 `sample-ocr-invoice.png` 與 `-RunRealOcr` optional smoke / seed script；預設 validation 仍只要求 mock flow 可用。

## v0.8.0 PaddleOCR Runtime Stabilization Milestone

Goal：在 v0.7 real OCR spike 後，針對 PaddleOCR 環境問題建立可重現 baseline、修復 dependency / runtime 相容性，並驗證預設 PaddleOCR flow。

Tickets：

- `tasks/phase-08-paddleocr-runtime/08-01-paddleocr-environment-baseline.md`
- `tasks/phase-08-paddleocr-runtime/08-02-paddleocr-dependency-fix.md`
- `tasks/phase-08-paddleocr-runtime/08-03-paddleocr-default-flow-validation.md`

Expected Outcome：

- Windows 本機與 Docker 的 PaddleOCR 失敗點可被明確重現。
- `backend[real-ocr]` dependency 與安裝文件能支援受控初始化 PaddleOCR。
- provider-selected OCR 在預設 PaddleOCR flow 下可用 sample image 完成驗證。
- `DOCURAG_OCR_PROVIDER=mock` 仍可保留 demo-safe mock path。
- v0.8 決策：provider-selected `/ocr` 預設走 PaddleOCR，mock 需透過 `/ocr/mock` 或 `DOCURAG_OCR_PROVIDER=mock` 明確 override。
- 不新增 PDF rendering、image preprocessing、Qdrant、embedding、rerank、LLM、Redis、NATS、worker、資料庫 schema、登入或權限。

## v0.9.0 GPU Runtime Milestone

Goal：將 PaddleOCR real OCR runtime 收斂為 GPU-only，並固定 PP-OCRv4 mobile 中文 / 中英混合模型設定；mock path 仍是 demo-safe override。

Tickets：

- `tasks/phase-09-gpu-runtime/09-01-paddleocr-gpu-only-runtime.md`
- `tasks/phase-09-gpu-runtime/09-02-paddleocr-v4-mobile-chinese-model.md`

Expected Outcome：

- `backend[real-ocr]` 不再維護 CPU PaddleOCR baseline；provider-selected real OCR 會要求 CUDA Paddle build，非 CUDA build 明確回傳 `paddleocr_gpu_required`。
- PaddleOCR provider 預設 `lang=ch`、`ocr_version=PP-OCRv4`，並記錄 `PP-OCRv4_mobile_det`、`PP-OCRv4_mobile_rec`、`ch_ppocr_mobile_v2.0_cls` 與對應 cache / model directory。
- OCR line normalization 保留 line text、bbox、confidence 與 trace metadata，並額外帶出 OCR language、version 與模型資訊。
- 新增繁中 sample image `sample-data/documents/sample-ocr-zh-tw.png`；本機 Python 3.12.10 + CUDA PaddlePaddle GPU runtime 已完成驗證，實際辨識結果包含 `DocuRAG 繁中 OCR 測試`、`發票號碼：OCR-2026-009`、`客户：星河科技股份有限公司` 與 `總計 : NT$ 12,345`。
- PP-OCRv4 mobile recognition 主要驗證中文 / 中英數字；若繁中辨識不足，後續候選是 `chinese_cht_PP-OCRv3_rec`，本 milestone 不自動切換。
- 不新增 LLM、Ollama、vLLM、embedding、Qdrant、rerank、worker、Redis、NATS、資料庫 schema、登入或權限。

## v0.9.1 OCR Performance Hardening Milestone

Goal：先修 PaddleOCR GPU 模式每張圖過慢的核心原因，讓 backend 啟動時完成 engine preload，request path 重用 provider / engine，並用 timing baseline 收斂小範圍效能設定。

Tickets：

- `tasks/phase-09-gpu-runtime/09-03-paddleocr-engine-lifecycle-preload.md`
- `tasks/phase-09-gpu-runtime/09-04-paddleocr-performance-observability-tuning.md`

Expected Outcome：

- Backend startup path 可在 selected provider 為 PaddleOCR 時初始化 OCR engine，後續 provider-selected OCR request 不再每次 cold start。
- Mock OCR override path 仍可重跑 demo-safe flow，不觸發 PaddleOCR preload。
- PaddleOCR timing log / metadata 可觀察 engine preload、request engine load、inference、normalization 與 total duration。
- 文件已記錄 sample image baseline、`cls=True` / `cls=False`、warmup、圖片尺寸與少量推論參數對速度的影響。
- v0.9.1 預設 `DOCURAG_OCR_USE_ANGLE_CLS=false`、`DOCURAG_OCR_DET_LIMIT_SIDE_LEN=960`、`DOCURAG_OCR_REC_BATCH_NUM=6`。
- Phase 09 performance hardening 完成前，不開始 Phase 10 Qwen3 / Ollama / RAG demo ticket。
- 不新增 worker queue、Redis、NATS、資料庫 schema、登入、權限、PDF rendering、多頁 OCR pipeline 或 production-grade OCR tuning。

Baseline and decisions（2026-05-22，Windows / Python 3.12.10 / PaddleOCR 2.10.0 / `paddlepaddle-gpu==3.3.0` / RTX 5070 Ti）：

| Config | Sample | Image size | Engine init | First OCR | Second OCR | Lines |
|---|---|---:|---:|---:|---:|---:|
| `cls=True`, `det_limit_side_len=960` | `sample-ocr-invoice.png` | 760x260 | 4895.57 ms | 567.09 ms | 52.96 ms | 4 |
| `cls=True`, `det_limit_side_len=960` | `sample-ocr-zh-tw.png` | 1000x420 | 4895.57 ms | 90.27 ms | 65.28 ms | 4 |
| `cls=False`, `det_limit_side_len=960` | `sample-ocr-invoice.png` | 760x260 | 3749.86 ms | 84.18 ms | 39.81 ms | 4 |
| `cls=False`, `det_limit_side_len=960` | `sample-ocr-zh-tw.png` | 1000x420 | 3749.86 ms | 53.75 ms | 51.39 ms | 4 |
| `cls=False`, `det_limit_side_len=736` | `sample-ocr-invoice.png` | 760x260 | 3712.03 ms | 89.88 ms | 40.21 ms | 4 |
| `cls=False`, `det_limit_side_len=736` | `sample-ocr-zh-tw.png` | 1000x420 | 3712.03 ms | 71.28 ms | 51.14 ms | 4 |

Decision：`cls=False` 在兩張直立 sample 上保留相同行數與文字預覽，且首張推論明顯較快，因此採用為 v0.9.1 預設。`det_limit_side_len=736` 沒有穩定收益，保留 PaddleOCR mobile 預設 `960`。startup warmup 可降低第一張 request latency，但會讓 backend startup 依賴 sample image inference，本 milestone 不採用預設 warmup。

## v0.10.0 LLM RAG Backlog Milestone

Goal：在既有 keyword retrieval、citation contract 與 deterministic baseline 穩定後，加入可選 Ollama Qwen3.5 RAG generation demo；不得提前引入 embedding、Qdrant、rerank、worker、DB、登入或 RBAC。

Tickets：

- [x] `tasks/phase-10-llm-rag/10-01-qwen3-ollama-provider-decision.md`
- [x] `tasks/phase-10-llm-rag/10-02-ollama-qwen3-client.md`
- [x] `tasks/phase-10-llm-rag/10-03-qwen3-rag-generation.md`
- [x] `tasks/phase-10-llm-rag/10-04-qwen3-demo-smoke.md`

10-01 Provider decision：

- LLM provider：`DOCURAG_LLM_PROVIDER=ollama`。
- LLM endpoint：`DOCURAG_LLM_BASE_URL=http://127.0.0.1:11434`。
- RAG generation model：`DOCURAG_LLM_MODEL=qwen3.5:4b`。
- VLM / Parser target provider：`DOCURAG_VLM_PROVIDER=ollama`。
- VLM / Parser target model：`DOCURAG_VLM_MODEL=qwen3.5:4b`，但 VLM parser implementation 仍留給後續 ticket。
- vLLM 保留為後續 LLMOps / serving / latency 展示；v0.10.0 第一版不採用 vLLM。
- OpenAI-compatible API 保留為 fallback 設定，不是 v0.10.0 預設路線。
- 較新的大型 Qwen 系列可作為後續 fallback 候選；未公開或未上架的 4B 型號不寫入預設路線。

10-01 local validation（2026-05-22）：

- `nvidia-smi` 通過，GPU 為 NVIDIA GeForce RTX 5070 Ti。
- `ollama list` 與 `ollama show qwen3.5:4b` 目前因 `ollama` CLI 不在 PATH 而無法執行。
- `curl.exe http://127.0.0.1:11434/api/tags` 目前無法連線，表示本機 Ollama service 未回應。
- 以上為實際本機 generation 前置環境風險，不在 10-01 下載模型或啟動 service；10-02 client 測試以 mock HTTP / monkeypatch 覆蓋。

10-02 Client status：

- 已新增 backend LLM provider interface、disabled provider 與 Ollama native HTTP client。
- 未設定 `DOCURAG_LLM_PROVIDER` 時，provider 保持 disabled，既有 deterministic `/rag/query` baseline 不受影響。
- 設定 `DOCURAG_LLM_PROVIDER=ollama` 時，client 使用 `DOCURAG_LLM_BASE_URL`、`DOCURAG_LLM_MODEL=qwen3.5:4b` 與明確 timeout 呼叫 `POST /api/generate`，並設定 `stream=false`。
- `check_health()` 使用 `GET /api/tags` 判斷 Ollama service 與本機模型清單是否可用。
- 測試覆蓋成功回應、timeout、connection error、HTTP error、missing model 與 provider disabled。
- 2026-05-22 validation：backend test script 通過，`58 passed`；本機 `/api/tags` 仍因 Ollama service 未啟動而無法連線。

10-03 Generation status：

- `/rag/query` 仍先使用 existing keyword retrieval 與 citation contract。
- LLM provider 未設定時，回應保持 deterministic keyword baseline。
- LLM provider enabled 且 retrieval 有命中 chunks 時，generation prompt 只包含 user query 與 retrieved chunks，不加入未檢索內容。
- LLM success 時，answer 使用 `qwen3.5:4b` generation 結果；citations 與 retrieved chunks 保持對齊原 chunk metadata。
- citation `trace_metadata` 會記錄 `llm_provider=ollama`、`llm_model=qwen3.5:4b`、generation status、latency 與 token usage。
- LLM unavailable / timeout / model missing 時，answer 明確標示 LLM generation unavailable，並 fallback 到 retrieved OCR chunks，不產生誤導性回答。
- 2026-05-22 validation：backend test script 通過，`61 passed`；mock LLM client 測試覆蓋 prompt、成功生成、failure fallback、citation preservation 與 trace metadata。

10-04 Demo smoke status：

- `scripts/demo-smoke-test.ps1` 預設仍驗證 deterministic baseline answer source，確認 non-LLM demo 可重跑。
- `scripts/demo-smoke-test.ps1 -RunLlm` 會檢查 Ollama `/api/tags`、確認 `qwen3.5:4b` 存在，並要求 RAG answer source 為 `ollama/qwen3.5:4b`。
- frontend RAG result 會依 citation `trace_metadata` 顯示 `deterministic baseline`、`ollama/qwen3.5:4b` 或 `LLM unavailable fallback`。
- backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `v0.10.0`。
- 2026-05-22 validation：backend test script 通過，`61 passed`；`npm.cmd run build` 通過；baseline `scripts/demo-smoke-test.ps1` 通過並確認 answer source 為 `deterministic baseline`；follow-up 已安裝 Ollama 0.24.0、pull `qwen3.5:4b`，並以 LLM-enabled backend 跑通 `scripts/demo-smoke-test.ps1 -RunLlm`，確認 answer source 為 `ollama/qwen3.5:4b`。

## v0.11.0 Vector RAG Backlog Milestone

Goal：在 v0.10.0 LLM generation path 穩定後，逐步把 local keyword retrieval 擴充為可選 vector retrieval demo；第一階段只固定 embedding / vector store provider decision，後續再用小 ticket 接入 runtime。

Tickets：

- [x] `tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md`
- [x] `tasks/phase-11-vector-rag/11-02-ollama-embedding-client.md`
- [x] `tasks/phase-11-vector-rag/11-03-qdrant-local-runtime.md`
- [x] `tasks/phase-11-vector-rag/11-04-vector-retrieval-demo-smoke.md`

11-01 Provider decision：

- Embedding provider：Ollama native embedding API。
- Embedding endpoint：`DOCURAG_EMBEDDING_BASE_URL=http://127.0.0.1:11434`。
- Embedding model：`DOCURAG_EMBEDDING_MODEL=qwen3-embedding:0.6b`。
- Decision rationale：Ollama 官方 `qwen3-embedding` library 支援 `/api/embed`，`0.6b` tag 約 639MB，適合作為本機 demo 起點；Qwen3 Embedding 系列定位為 text embedding，且具 multilingual 能力，適合中英混合 OCR chunks。
- Vector store：Qdrant self-hosted Docker / Docker Compose。
- Qdrant endpoint：`DOCURAG_QDRANT_URL=http://127.0.0.1:6333`。
- Collection name：`docurag_chunks_v1`。
- Vector dimension：若本機 `qwen3-embedding:0.6b` 可用，11-02 以實際 `/api/embed` 回傳長度固定；若模型不可用，11-03 以可設定 env default 與 mock tests 保持 collection size 可重跑，不在 provider decision ticket 硬編碼。
- Payload metadata：`document_id`、`filename`、`chunk_id`、`source_type`、`page_number`、`ocr_provider`、`created_at`；project / organization filtering 留到 auth / project scope 排定後。

11-01 Guardrails：

- 不新增 embedding client、Qdrant dependency、Docker Compose service 或 runtime。
- 不改 `/rag/query` 預設行為，不移除 keyword RAG baseline。
- 不新增 rerank、hybrid search、eval runner、Redis、NATS、worker、DB、登入或 RBAC。
- Phase 11 runtime ticket 必須保留 deterministic baseline 與 LLM generation fallback，避免 vector path 不可用時中斷 demo。

11-01 validation：

- `rg -n "v0.11.0|phase-11|qwen3-embedding|Qdrant" TODO.md docs/ROADMAP.md tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md` 通過。
- `git diff --check` 通過。

11-02 Embedding client：

- 新增 `EmbeddingProvider` interface、`DisabledEmbeddingProvider` 與 `OllamaEmbeddingProvider`。
- `DOCURAG_EMBEDDING_PROVIDER` 預設未設定，embedding provider disabled，不改 `/rag/query` keyword baseline。
- `DOCURAG_EMBEDDING_PROVIDER=ollama` 時使用 `POST /api/embed`、`DOCURAG_EMBEDDING_BASE_URL=http://127.0.0.1:11434`、`DOCURAG_EMBEDDING_MODEL=qwen3-embedding:0.6b` 與 `DOCURAG_EMBEDDING_TIMEOUT_SECONDS=30`。
- `scripts/ollama-embedding-smoke.ps1` 可檢查 `/api/tags` 與 `/api/embed` 並輸出 vector dimension。
- 2026-05-22 follow-up：已透過 Ollama API pull `qwen3-embedding:0.6b`，`scripts/ollama-embedding-smoke.ps1` 通過並確認實際 vector dimension 為 `1024`。
- Qwen 官方 model card 記錄 `Qwen3-Embedding-0.6B` embedding dimension up to 1024；本機 smoke 已確認 `qwen3-embedding:0.6b` 與 `DOCURAG_QDRANT_VECTOR_SIZE=1024` 相符。
- Mock tests 覆蓋 successful embed、connection error、HTTP error、timeout、missing model health 與 malformed response。

11-03 Qdrant local runtime：

- Docker Compose 已新增 optional `qdrant` service，映射 `6333` / `6334`，使用 named volume `qdrant_storage`。
- Backend settings 已新增 `DOCURAG_QDRANT_URL=http://127.0.0.1:6333`、`DOCURAG_QDRANT_COLLECTION=docurag_chunks_v1`、`DOCURAG_QDRANT_VECTOR_SIZE=1024` 與 `DOCURAG_QDRANT_TIMEOUT_SECONDS=10`。
- 新增 `QdrantVectorStore.ensure_collection()`，只建立/檢查 collection，不掛到 backend startup 或 `/rag/query` 預設 path。
- 新增 `scripts/qdrant-collection-smoke.ps1`，用於檢查或建立 `docurag_chunks_v1`，distance 固定 `Cosine`。
- Mock tests 覆蓋 collection exists、create collection、vector size mismatch、connection error、timeout 與 malformed response。
- 2026-05-22 follow-up：已啟動 Docker Desktop、用 Docker Compose 啟動 Qdrant，並跑通 `scripts/qdrant-collection-smoke.ps1`；`docurag_chunks_v1` collection 已建立/確認，vector size `1024`、distance `Cosine`。

Next Candidate Milestone：

- v0.11.0 已完成 disabled-by-default embedding client building block、optional Qdrant local runtime、fallback-safe optional vector retrieval demo 與 release/version sync。
- Future Vector RAG hardening：後續若要做 persistent indexing、hybrid search、rerank 或 eval runner，必須另開 Phase ticket，不在 v0.11.0 回頭擴張。

11-04 Optional vector retrieval demo：

- 新增 `DOCURAG_RAG_RETRIEVAL_PROVIDER=keyword|vector`，預設 `keyword`，未設定時 `/rag/query` 行為維持 deterministic keyword baseline。
- `VectorRagProvider` 只在明確設定 `vector` 時啟用，會在 request 內以最小實作 embed local chunks、upsert Qdrant，再 embed query 並執行 vector search。
- Vector success 會在 citation trace metadata / retrieved chunk metadata 記錄 `retrieval_provider=vector`、`vector_retrieval_status=completed`、`vector_store=qdrant`、`qdrant_collection`、`embedding_provider`、`embedding_model` 與 `vector_score`。
- Embedding unavailable、Qdrant unavailable、collection missing、collection mismatch、payload malformed 或 vector search no result 時，會明確 fallback 到 keyword retrieval，answer 與 trace metadata 記錄 `vector_retrieval_status=failed` 與 error。
- Existing optional Ollama `qwen3.5:4b` generation path 保留，可接在 vector retrieved chunks 或 keyword fallback chunks 後。
- Frontend RAG result 追加 retrieval source pill：`keyword baseline`、`vector/qdrant` 或 `vector unavailable fallback`。
- `scripts/demo-smoke-test.ps1` 新增 `-RunVector`，會先檢查 Ollama embedding model 與 Qdrant availability，再要求 retrieval source 為 `vector/qdrant`。
- Backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `v0.11.0`。
- 2026-05-22 validation：backend test script 通過，`84 passed`；frontend `npm.cmd run build` 通過；baseline demo smoke 通過，answer source 為 `deterministic baseline`、retrieval source 為 `keyword baseline`。
- 2026-05-22 follow-up optional vector smoke：已在本機準備 Ollama `qwen3-embedding:0.6b` 與 Qdrant，並以 vector-enabled backend 跑通 `scripts/demo-smoke-test.ps1 -RunVector`；answer source 為 `deterministic baseline`，retrieval source 為 `vector/qdrant`。

## Release Verification

- v0.0: repo structure、docs、tasks 已完成。
- v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- v0.2.0: Demo UI、Backend CI、backend CORS、Docker build / Compose healthcheck 已完成。
- v0.3.0: Document Local Storage、文件列表、文件詳情、frontend list UI、Docker build / Compose healthcheck / Compose upload API 已完成。
- v0.4.0: OCR Mock Pipeline、OCR result persistence、frontend OCR UI、Docker build / Compose healthcheck / Compose upload / Compose OCR mock API 已完成。
- v0.5.0: Local RAG Baseline、chunking、keyword retrieval、RAG answer API、frontend Chat UI、Docker build / Compose healthcheck / Compose upload / Compose OCR mock / Compose RAG API 已完成。
- v0.5.1: Demo Hardening、公開 sample data、demo seed script、API smoke test、5 分鐘 README demo flow、Docker build / Compose demo smoke / seed script 已完成。
- v0.6.0: Bridge Contracts、OCR provider interface、RAG provider interface、processing status、chunk citation schema 與 processing job contract 已完成。
- v0.7.0: Real OCR Provider Spike 已完成；PaddleOCR real OCR path 是 optional spike，mock demo 仍為預設可攜 flow。
- v0.8.0: PaddleOCR Runtime Stabilization 已完成；Python 3.12、PaddleOCR 2.10.0、PaddlePaddle 3.0.0 sample real OCR flow 已驗證，provider-selected OCR 預設走 PaddleOCR。
- v0.9.0: GPU Runtime 已完成；PaddleOCR real OCR 收斂為 GPU-only，PP-OCRv4 mobile 中文 / 中英混合模型設定、模型目錄文件與繁中 sample 已補齊；本機 real OCR GPU validation、sample invoice 與繁中 provider-selected OCR smoke 已通過。
- v0.9.1: OCR Performance Hardening 已完成；backend startup preload、provider / engine reuse、OCR timing log / metadata、`cls=False` baseline、v0.9.1 version / README / TODO / ROADMAP 同步與 provider-selected real OCR smoke 已通過。
- v0.10.0: LLM RAG Backlog 已完成；Ollama `qwen3.5:4b` provider decision、最小 client、optional `/rag/query` generation path、demo smoke `-RunLlm`、frontend answer source、v0.10.0 version / README / TODO / ROADMAP 同步已完成。
- v0.11.0: Vector RAG Backlog 已完成；Ollama `qwen3-embedding:0.6b` embedding client、Qdrant local runtime / collection smoke、optional vector retrieval path、fallback trace metadata、demo smoke `-RunVector`、v0.11.0 version / README / TODO / ROADMAP 同步已完成。
- v0.12.0: Vector Indexing Hardening 已完成；manual vector indexing contract、同步 indexing service、`POST /documents/{document_id}/index/vector`、optional vector indexing smoke、fallback-safe vector retrieval 與 v0.12.0 version / README / TODO / ROADMAP 同步已完成。

## v0.12.0 Vector Indexing Hardening Backlog

Goal：把 Phase 11 的 request-time vector retrieval demo 收斂成明確、可重跑、可檢查的 local vector indexing flow。Phase 12 只做 manual / synchronous indexing hardening，不引入 worker、DB、rerank、hybrid search 或 eval runner。

Tickets：

- [x] `tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md`
- [x] `tasks/phase-12-vector-indexing/12-02-vector-indexing-service.md`
- [x] `tasks/phase-12-vector-indexing/12-03-vector-indexing-api.md`
- [x] `tasks/phase-12-vector-indexing/12-04-vector-indexing-demo-smoke.md`

Expected Outcome：

- 已完成 OCR 且已有 chunks 的 documents 可以被明確手動 index 到 Qdrant。
- Vector indexing 使用 stable point id，讓重跑 indexing 是 idempotent upsert。
- Qdrant payload metadata 保留 chunk / citation trace 所需欄位：`document_id`、`filename`、`chunk_id`、`text`、`source`、`source_type`、`page_number`、`bbox`、`confidence`、`created_at` 與 chunk metadata。
- Baseline keyword RAG 不依賴 Qdrant 或 embedding；optional vector indexing / retrieval 需明確 env 與手動 action。
- Optional vector demo smoke 會呈現 upload -> OCR -> chunks -> manual vector indexing -> vector retrieval query。
- External runtime unavailable 時有清楚錯誤或 fallback，不破壞 baseline demo。

12-01 Contract：

- Stable point id 固定為 `uuid5(NAMESPACE_URL, f"docurag:{document_id}:{chunk_id}")`，讓同一 chunk 重跑 indexing 時 upsert 到同一 Qdrant point。
- Collection 沿用 `docurag_chunks_v1`，distance 固定 `Cosine`，vector size 由 `DOCURAG_QDRANT_VECTOR_SIZE` 控制，預設 `1024`。
- Payload 必填 `document_id`、`filename`、`chunk_id`、`text`、`source`、`source_type` 與 `created_at`；若 chunk 有 `page_number`、`bbox`、`confidence` 與 `metadata`，必須保留。
- Payload trace 欄位需標示 `indexing_provider=vector`、`vector_store=qdrant`、`qdrant_collection`、`embedding_provider` 與 `embedding_model`，但不新增 project / organization filter。
- Empty chunks 應回傳 `status=skipped`；embedding disabled / unavailable、Qdrant unavailable、collection missing 或 vector size mismatch 應回傳清楚 failed result 或 HTTP error detail。
- Manual vector indexing 不修改 local document metadata，不由 upload、OCR 或 backend startup 自動觸發；keyword RAG baseline 與 Phase 11 vector retrieval fallback 仍保持可用。

12-02 Service status：

- 已新增 `VectorIndexingService`，對單一 document chunks 產生 stable point ids、Ollama embeddings 與 Qdrant points payload。
- Success result 會回傳 `indexed_chunk_count`、`point_ids`、collection、vector size、embedding provider / model。
- Empty chunks 回傳 `status=skipped`；embedding / Qdrant / collection mismatch / dimension mismatch 回傳 `status=failed`，不修改 local metadata。

12-03 API status：

- 已新增 `POST /documents/{document_id}/index/vector`，只對已完成 OCR 的單一 document 執行 manual vector indexing。
- Document not found 回傳 404；OCR 未完成回傳 409；provider disabled 或 Qdrant failure 回傳 503 與明確 detail。
- API 不新增 frontend 大改、batch indexing、worker、DB，也不讓 upload / OCR 自動觸發 vector indexing。

12-04 Demo smoke status：

- `scripts/demo-smoke-test.ps1 -RunVector` 會 preflight Ollama embedding model、Qdrant service 與 `docurag_chunks_v1` collection。
- Optional vector smoke flow 已改為 upload -> OCR mock -> manual vector indexing -> vector retrieval query。
- Vector retrieval path 不再 query-time upsert local chunks，只查詢 Qdrant 中已 manual indexed 的 chunks；失敗仍 fallback 到 keyword retrieval。
- Backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `v0.12.0`。

Out of Scope：

- 不實作 rerank。
- 不實作 hybrid search。
- 不實作 eval runner。
- 不新增 Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不讓 vector indexing 或 vector retrieval 成為 default-on path。

## v0.13.0 Retrieval Evaluation Baseline Backlog

Goal：在 keyword retrieval、optional vector retrieval 與 manual vector indexing 穩定後，建立第一版本機 retrieval evaluation baseline。Phase 13 只做公開 eval dataset、metrics contract、runner 與 demo smoke，讓後續 rerank / hybrid search 有可量化比較基準。

Tickets：

- [x] `tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md`
- [x] `tasks/phase-13-retrieval-eval/13-02-retrieval-eval-dataset.md`
- [x] `tasks/phase-13-retrieval-eval/13-03-retrieval-eval-runner.md`
- [ ] `tasks/phase-13-retrieval-eval/13-04-retrieval-eval-demo-smoke.md`

Expected Outcome：

- `sample-data/eval/` 有最小公開 retrieval eval dataset，使用既有虛構 sample documents。
- Eval case contract 包含 `query`、`top_k`、expected document / chunk hints、expected terms 與 tags。
- Runner 可輸出 per-query results 與 summary metrics。
- Summary metrics 至少包含 `Hit Rate@K`、`MRR@K`、`Recall@K`、平均 latency 與 failure count。
- Baseline keyword eval 不依賴 Qdrant 或 embedding。
- Optional vector eval 需明確 env、manual vector indexing 與 Qdrant runtime。
- Phase 13 demo smoke 能展示 keyword baseline metrics 與 optional vector metrics。

13-01 Contract：

- 固定 eval dataset schema、metrics 定義、strategy labels 與 result output contract。
- Strategy labels 第一版只包含 `keyword`、`vector` 與 vector unavailable fallback；不引入 hybrid 或 rerank。
- Result output 需同時支援人可讀 summary 與 machine-readable JSON。
- Dataset schema 以 JSON array 表示，每筆 case 包含 `id`、`query`、`top_k`、`expected_document_filenames`、`expected_chunk_hints`、`expected_terms` 與 `tags`；optional `notes` 與 `expected_source_types` 只作補充，不可綁死 runtime。
- Metrics 定義固定為 `Hit Rate@K`、`MRR@K`、`Recall@K`、`latency_ms` 與 `failure_count`；keyword baseline 必須可在沒有 Ollama embedding 或 Qdrant 時執行。
- Result JSON 至少包含 `run_id`、`created_at`、`strategy`、`dataset_path`、`summary`、`results` 與 `environment`，其中 `environment` 不得記錄 secret。
- 本 contract ticket 不 bump version；`v0.13.0` release/version sync 留到 `13-04`。

13-02 Dataset：

- 新增 retrieval eval dataset，至少涵蓋 invoice 與 contract / support sample。
- Dataset 不包含真實個資或公司敏感資料。
- Dataset schema 需有最小測試或文件驗證，避免後續 runner 讀取格式漂移。

13-03 Runner：

- 新增本機 runner 或 script，計算 `Hit Rate@K`、`MRR@K`、`Recall@K`、latency 與 failure count。
- Keyword baseline 可直接執行。
- Optional vector eval 需明確檢查 Ollama embedding model、Qdrant collection 與 manual vector indexing。

13-04 Demo smoke：

- 補齊 baseline retrieval eval smoke 與 optional vector retrieval eval smoke。
- 完成 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 的 `v0.13.0` release sync。

Out of Scope：

- 不實作 rerank。
- 不實作 hybrid search。
- 不實作 LLM-as-judge、answer faithfulness 或 citation quality scoring。
- 不新增 Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不讓 eval runner、vector retrieval 或 vector indexing 成為 default-on path。
