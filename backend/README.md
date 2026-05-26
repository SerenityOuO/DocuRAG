# Backend

DocuRAG AgentOps backend MVP v0.29.0 是最小 FastAPI 服務，提供 healthcheck、文件本機上傳、metadata 保存、文件列表、文件詳情、`.txt` direct ingestion、text-native PDF ingestion、OCR mock API、provider-selected OCR API、VLM-first invoice parser spike、OCR / VLM evidence alignment、deterministic invoice parser fallback、parse / fields API、Agent run / lookup API、manual vector indexing API、local RAG query API、demo auth API、built-in RAG eval API、retrieval evaluation runner、FastEmbed rerank adapter、hybrid / `hybrid_rerank` runtime provider、demo seed script 與 API smoke test，並允許 local frontend 透過 CORS 呼叫。v0.27.0 起 backend 採 aggressive demo defaults：`DOCURAG_RAG_RETRIEVAL_PROVIDER=hybrid_rerank`、`DOCURAG_EMBEDDING_PROVIDER=ollama`、`DOCURAG_RERANK_PROVIDER=fastembed`。v0.27.1 起 VLM parser request 會同時帶原始圖片與 compact OCR context；欄位值可對回 OCR line / bbox，未命中時會標示 evidence unmatched / unavailable。v0.28.0 已固定 `image_ocr`、`text_upload`、`pdf_text` 與 `pdf_scanned_pending_ocr` 的上傳分流；目前 runtime 已支援 `.txt` 直接建立 `text_upload` chunks，也會用 `pypdf` 抽取 text-native PDF 文字層建立 `pdf_text` chunks。v0.29.0 新增 `POST /eval/rag/built-in`，讓 Admin / Analyst 執行固定 `hybrid_rerank` 的 10 張 synthetic 中文發票 retrieval benchmark；後續 focused hardening 也讓 Ollama VLM adapter 可處理 `response` / `thinking` / fenced JSON、金額字串與 line item alias，並補強 RAG vector stale filtering 與 Ollama generation latency guardrails。`DOCURAG_AUTH_MODE=demo` 會啟用 demo login / me / logout 與 write API role guard，Admin / Analyst 可操作 ingestion 與 built-in eval，Viewer 只能查詢與下載。`/rag/query` 與 Agent `search_documents` 會優先使用 hybrid rerank；Ollama embedding、Qdrant 或 FastEmbed runtime 不可用時，會 fallback 到 keyword evidence 並寫入 trace。LLM provider 未覆寫時仍預設嘗試 Ollama `qwen3.5:4b` generation，Ollama 不可用或回空 final response 時 fallback 到 retrieved chunks。此階段不接資料庫、OpenAI API、vLLM、production VLM / LLM parser、production eval dashboard、自訂 eval dataset、Redis、NATS、worker、batch upload API、正式登入權限、production autonomous Agent、LLM planner、任意 SQL 或 production indexing pipeline。

## Install

```powershell
cd backend
py -3.12 -m pip install -e ".[dev]"
```

## Run

```powershell
cd backend
py -3.12 -m uvicorn app.main:app --reload
```

Healthcheck：

```powershell
curl http://127.0.0.1:8000/health
```

Upload：

```powershell
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@sample-data/documents/mock-invoice-aurora.txt"
```

Document list：

```powershell
curl http://127.0.0.1:8000/documents
```

Document detail：

```powershell
curl http://127.0.0.1:8000/documents/{document_id}
```

Document download：

```powershell
curl -OJ http://127.0.0.1:8000/documents/{document_id}/download
```

Run mock OCR：

```powershell
curl -X POST http://127.0.0.1:8000/documents/{document_id}/ocr/mock
```

Run provider-selected OCR：

```powershell
curl -X POST http://127.0.0.1:8000/documents/{document_id}/ocr
```

OCR result：

```powershell
curl http://127.0.0.1:8000/documents/{document_id}/ocr
```

Run VLM-first parser：

```powershell
curl -X POST http://127.0.0.1:8000/documents/{document_id}/parse
```

Structured fields：

```powershell
curl http://127.0.0.1:8000/documents/{document_id}/fields
```

Run deterministic Agent：

```powershell
curl -X POST http://127.0.0.1:8000/agent/run `
  -H "Content-Type: application/json" `
  -d "{\"task\":\"Summarize invoice fields and cite payment terms.\",\"document_id\":\"{document_id}\",\"query\":\"payment terms\",\"top_k\":3}"
```

Agent run lookup：

```powershell
curl http://127.0.0.1:8000/agent/runs/{run_id}
```

Run built-in RAG eval：

```powershell
curl -X POST http://127.0.0.1:8000/eval/rag/built-in `
  -H "Content-Type: application/json"
```

Demo auth mode：

```powershell
$env:DOCURAG_AUTH_MODE="demo"
$env:DOCURAG_AUTH_DEMO_SECRET="change-this-local-demo-secret"
```

Demo auth endpoints：

```powershell
curl -X POST http://127.0.0.1:8000/auth/login `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"admin\",\"password\":\"demo-admin-pass\"}"
curl http://127.0.0.1:8000/auth/me -H "Authorization: Bearer {token}"
curl -X POST http://127.0.0.1:8000/auth/logout -H "Authorization: Bearer {token}"
```

Phase 28 demo auth boundary：

- Auth mode 預設為 `disabled`；只有 `DOCURAG_AUTH_MODE=demo` 時才要求 bearer token。
- Demo users 固定為 `admin` / `analyst` / `viewer`，只供本機面試 demo 與測試使用；API 不回傳 password。
- Admin / Analyst 可呼叫 upload、provider-selected OCR、mock OCR、parse 與 vector index；Viewer 對這些 ingestion write API 會收到 403 forbidden。
- Demo mode 下 download 需要登入，但 Admin / Analyst / Viewer 都可下載已存在文件。
- 這不是 PostgreSQL users table、正式 JWT refresh rotation、SSO、OAuth、MFA、tenant isolation、project permission、Redis session、audit log 或 production RBAC。

Phase 24 parser boundary：

- Parser MVP source 為 `deterministic_invoice`，只從既有 OCR text / OCR lines 抽取 demo-safe invoice fields。
- `ParserResult` 保存 `DocumentFields`、欄位 `confidence`、`source_text`、`source_page`、`source_bbox`、`parser_source` 與 `fallback_reason`。
- Parser missing fields 會回傳 `field_not_found` / `missing_fields` metadata，不產生假資料。
- Parser failure 只更新 `processing.parser` 與 parser job，不覆蓋 OCR / indexing 狀態，也不觸發 vector indexing、RAG ingestion、Qdrant upsert 或 eval run。
- 這是 VLM-compatible contract 與 deterministic fallback，不是真正 VLM parser、LLM parser、worker、DB schema 或 production parser pipeline。

Phase 25 Agent boundary：

- Agent planner 為 deterministic，不呼叫 LLM autonomous planner、OpenAI function calling 或 Ollama planning call。
- Tool policy 固定為 `allowlisted_read_only`，只允許 `get_document_fields`、`search_documents` 與 `summarize_invoice_fields`。
- `POST /agent/run` 會保存 `AgentRun` 到 local JSON metadata store；`GET /agent/runs/{run_id}` 只讀保存結果，不重跑 planner 或 tools。
- Agent trace 會顯示 plan、tool calls、observation、final answer、citations、planner route、tool policy 與 fallback count。
- 這不是 production autonomous Agent、Agent permission model、任意 SQL、shell / file system command、worker、Redis、NATS、DB-backed tool console 或 destructive tool execution。

Phase 28 Document Source Router contract：

- Source router 依 `file_type`、`content_type` 與 future detection result 選擇 `image_ocr`、`text_upload`、`pdf_text` 或 `pdf_scanned_pending_ocr`。
- `image_ocr` 沿用 provider-selected OCR，產生 OCR text / OCR lines / chunks；`ocr_mock` 只保留為手動 fallback 或 validation path，不是 `.txt` 的正式來源。
- `.txt` 目前已走 `text_upload` direct ingestion，直接讀 UTF-8 原文、做基本空白 normalization 並建立 chunks；OCR status 保持 pending，不標成 OCR completed。
- PDF 必須分成 text-native PDF 與 scanned PDF：`pdf_text` 代表已用 `pypdf` 抽到文字層並建立 chunks；`pdf_scanned_pending_ocr` 代表需要 PDF rendering / OCR pipeline，未完成前只能顯示 pending / unsupported。
- Normalized document text contract 至少保留 `document_id`、`source_type`、`text`、`page_number`、`bbox`、`confidence`、`metadata` 與 `created_at`，讓 RAG、Qdrant payload 與 Agent citations 不再永久綁死 OCR chunks。
- `POST /documents/{document_id}/index/vector` 可索引 `text_upload` 與 `pdf_text` chunks；Qdrant / embedding runtime 不可用時仍回傳清楚 fallback error。
- 本階段新增的 PDF dependency 僅限 `pypdf` text extraction，不新增 PDF rendering、scanned PDF OCR、worker、DB schema、正式 Auth / RBAC、Redis、NATS 或 deployment 設定。

Phase 29 built-in RAG eval boundary：

- `POST /eval/rag/built-in` 固定使用 `hybrid_rerank`，不接受 strategy request body，也不改 `/rag/query` 預設行為。
- Dataset 固定為 `sample-data/eval/built-in-rag-eval-zh-invoices.json`，對應 10 張 `sample-data/documents/zh-invoice-*.txt` synthetic 中文發票 fixture。
- Response 只為後台第一版 UI 提供 Hit Rate@K、MRR@K、平均延遲、Failure / Fallback、failed cases 與 fallback cases；完整 trace / ranking table 仍留在 eval runner 與 JSON output。
- Embedding、Qdrant 或 reranker runtime 不可用時，built-in eval 會保留 fallback metadata 並回到 keyword evidence，不讓 UI 靜默假裝完整 vector / rerank 成功。
- Demo auth mode 下 Admin / Analyst 可執行；Viewer 會收到 403 forbidden。
- 這不是 production eval dashboard、自訂 dataset 上傳、DB-backed eval history、LLM-as-judge、answer faithfulness scoring、OCR eval 或 VLM parser accuracy eval。

Phase 26 VLM parser provider spike：

- `POST /documents/{document_id}/parse` 預設走 VLM-first `vlm_invoice` route；`DOCURAG_PARSER_SOURCE=deterministic_invoice` 只作 explicit debug / validation override。
- `DOCURAG_VLM_PROVIDER=ollama` 會嘗試 local HTTP `/api/generate` vision-style request；request 包含 image base64 與 compact OCR context；`DOCURAG_VLM_PROVIDER=fake` 只供 demo smoke 驗證 success path；空字串或不可用 provider 會明確 fallback。
- Ollama request 使用 `stream=false` 與 `format=json`；adapter 可從 `response`、空 `response` 搭配 `thinking`、markdown fenced JSON 或文字中的第一個 JSON object 取出欄位 payload。
- VLM success 會保存既有 `DocumentFields` / `ParserResult` schema，並標記 `parser_source=vlm_invoice`；欄位值若能命中 OCR line，會保存 `source_text`、`source_page` 與 `source_bbox`，未命中則以 `evidence_unmatched` / `evidence_unavailable` 標示；fallback 會回到 `deterministic_invoice` 並保留 `fallback_reason` 與 `fallback_chain` trace。
- Agent contract 不變；`get_document_fields` 只讀保存後的 parser result，不直接呼叫 VLM，也不新增 tool allowlist。
- 這不是 production VLM parser、PDF rendering、多頁 parser pipeline、table reconstruction、人工修正 workflow、worker、DB schema 或 deployment 設定。

Phase 07 provider decision：

- 07-01 選定 `PaddleOCR` 作為第一個 real OCR spike provider。
- 07-02 已新增 provider-selected `POST /documents/{document_id}/ocr`；既有 `POST /documents/{document_id}/ocr/mock` 保持相容。
- 使用 `DOCURAG_OCR_PROVIDER=mock|paddleocr` 選擇 provider；v0.8 起預設為 `paddleocr`，`mock` 是明確 override。
- PaddleOCR adapter 採 lazy import，讓未安裝 real OCR dependency 的環境仍可跑 mock demo。
- real provider 不可用時不靜默 fallback 到 mock；real endpoint 應回傳清楚錯誤，並更新 processing status 與 processing job metadata。
- real OCR trace output 會正規化到 `OcrResult.lines`，再映射到 chunk page、bbox、confidence、metadata 與 RAG citation trace metadata。
- mock path 仍是 demo-safe path，可用 `/ocr/mock` 或 `DOCURAG_OCR_PROVIDER=mock` 明確啟用。

安裝 real OCR optional dependency：

```powershell
cd backend
py -3.12 -m pip install "paddlepaddle-gpu==3.3.0" -i https://www.paddlepaddle.org.cn/packages/stable/cu129/
py -3.12 -m pip install -e ".[dev,real-ocr]"
```

Phase 09 將 backend real OCR runtime 固定在 Python 3.12 + PaddlePaddle GPU CUDA build。非 CUDA build 會回傳 `paddleocr_gpu_required`，不會改跑 CPU 或 mock：

```powershell
py -3.12 -c "import paddle, paddleocr; print(paddle.__version__, paddleocr.__version__); print(paddle.device.is_compiled_with_cuda()); print(paddle.device.get_device()); paddle.utils.run_check()"
```

若使用 Python 3.13+ 啟動 `PaddleOcrProvider`，backend 會回傳 `paddleocr_python_unsupported`，提示改用 Python 3.12；不會改跑 mock。

PaddleOCR provider 預設模型設定：

| 設定 | 預設值 | 預期 cache / model directory |
|---|---|---|
| `DOCURAG_OCR_LANGUAGE` | `ch` | - |
| `DOCURAG_OCR_VERSION` | `PP-OCRv4` | - |
| `DOCURAG_OCR_DET_MODEL_NAME` | `PP-OCRv4_mobile_det` | `%USERPROFILE%\\.paddleocr\\whl\\det\\ch\\ch_PP-OCRv4_det_infer` |
| `DOCURAG_OCR_REC_MODEL_NAME` | `PP-OCRv4_mobile_rec` | `%USERPROFILE%\\.paddleocr\\whl\\rec\\ch\\ch_PP-OCRv4_rec_infer` |
| `DOCURAG_OCR_CLS_MODEL_NAME` | `ch_ppocr_mobile_v2.0_cls` | `%USERPROFILE%\\.paddleocr\\whl\\cls\\ch\\ch_ppocr_mobile_v2.0_cls_infer` |
| `DOCURAG_OCR_USE_ANGLE_CLS` | `false` | 直立 demo sample 不啟用 angle classifier |
| `DOCURAG_OCR_DET_LIMIT_SIDE_LEN` | `960` | 保留 PaddleOCR mobile 預設 detection 尺寸上限 |
| `DOCURAG_OCR_REC_BATCH_NUM` | `6` | 保留 PaddleOCR recognition 預設 batch |

可用 `DOCURAG_OCR_DET_MODEL_DIR`、`DOCURAG_OCR_REC_MODEL_DIR`、`DOCURAG_OCR_CLS_MODEL_DIR` 指向已下載模型目錄。PP-OCRv4 mobile recognition 以簡中 / 中英數字識別為主；繁中 sample 目前只記錄驗證結果與限制，不自動切到 `chinese_cht_PP-OCRv3_rec`。

v0.9.1 PaddleOCR lifecycle 與 timing：

- backend lifespan startup 會在 selected provider 為 `paddleocr` 時呼叫 `PaddleOcrProvider.preload()`，後續 `/documents/{document_id}/ocr` 重用同一個 process 內的 provider / engine。
- startup preload 失敗會記錄 error log 並中止啟動，不會靜默 fallback 到 mock。
- `/documents/{document_id}/ocr/mock` 仍使用獨立 `MockOcrProvider`，不觸發 PaddleOCR preload。
- OCR result `extracted_fields` 會包含 `timing_engine_preload_ms`、`timing_engine_load_ms`、`timing_inference_ms`、`timing_normalization_ms`、`timing_total_ms` 與 `engine_preloaded_before_request`。
- backend log 會輸出 PaddleOCR preload 與 OCR completed timing summary。

v0.9.1 本機 baseline（2026-05-22，Windows / Python 3.12.10 / PaddleOCR 2.10.0 / `paddlepaddle-gpu==3.3.0` / RTX 5070 Ti）：

| Config | Sample | Image size | Engine init | First OCR | Second OCR | Lines |
|---|---|---:|---:|---:|---:|---:|
| `cls=True`, `det_limit_side_len=960` | `sample-ocr-invoice.png` | 760x260 | 4895.57 ms | 567.09 ms | 52.96 ms | 4 |
| `cls=True`, `det_limit_side_len=960` | `sample-ocr-zh-tw.png` | 1000x420 | 4895.57 ms | 90.27 ms | 65.28 ms | 4 |
| `cls=False`, `det_limit_side_len=960` | `sample-ocr-invoice.png` | 760x260 | 3749.86 ms | 84.18 ms | 39.81 ms | 4 |
| `cls=False`, `det_limit_side_len=960` | `sample-ocr-zh-tw.png` | 1000x420 | 3749.86 ms | 53.75 ms | 51.39 ms | 4 |
| `cls=False`, `det_limit_side_len=736` | `sample-ocr-invoice.png` | 760x260 | 3712.03 ms | 89.88 ms | 40.21 ms | 4 |
| `cls=False`, `det_limit_side_len=736` | `sample-ocr-zh-tw.png` | 1000x420 | 3712.03 ms | 71.28 ms | 51.14 ms | 4 |

決策：直立 demo sample 在 `cls=False` 下文字預覽與行數不變，且首張推論明顯較快，因此 v0.9.1 預設 `DOCURAG_OCR_USE_ANGLE_CLS=false`。`det_limit_side_len=736` 沒有穩定改善，保留 `960`。startup warmup 確實可把第一張圖的推論成本移到啟動階段，但會讓 backend 啟動依賴 sample image inference，本 patch 不採用預設 warmup。

Docker real OCR build 可用 build arg 開啟，預設不安裝 PaddleOCR：

```powershell
docker build --build-arg DOCURAG_INSTALL_REAL_OCR=true -t docurag-backend-real-ocr ./backend
```

Local RAG query：

```powershell
curl -X POST http://127.0.0.1:8000/rag/query `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"invoice\",\"top_k\":3}"
```

Phase 10 Ollama LLM RAG：

- `DOCURAG_LLM_PROVIDER` 未設定時，LLM provider 預設為 `ollama`，`/rag/query` 會在 retrieval 命中 chunks 後嘗試用 Ollama `qwen3.5:4b` 產生回答。
- 設定 `DOCURAG_LLM_PROVIDER=ollama`、`DOCURAG_LLM_BASE_URL=http://127.0.0.1:11434` 與 `DOCURAG_LLM_MODEL=qwen3.5:4b` 後，可明確用 `OllamaLlmProvider` 呼叫 Ollama native `/api/generate`；若要關閉 LLM provider，可設定 `DOCURAG_LLM_PROVIDER=`。
- client 使用 `stream=false`，讓回應維持單一 JSON 物件，方便 backend 測試與後續 RAG generation path 接入。
- Phase 30 hardening 起，Ollama `/api/generate` 預設帶 `think=false` 與 `options.num_predict=512`，避免 thinking-capable model 在 demo RAG answer generation 時輸出大量 hidden thinking 或無界生成；debug 時可用 `DOCURAG_LLM_THINK=true` 或 `DOCURAG_LLM_NUM_PREDICT=<tokens>` 明確覆寫。
- `check_health()` 會呼叫 `/api/tags`，確認 service 可連線且目標模型出現在本機模型清單。
- 10-03 起 `/rag/query` 在 LLM provider enabled 且 retrieval 有命中 chunks 時，會用 query + retrieved chunks 組 prompt 產生回答；prompt 不包含未檢索內容。
- citations 與 retrieved chunks contract 保持不變，citation `trace_metadata` 會加上 `llm_provider`、`llm_model`、generation status、latency、token usage、`llm_think` 與 `llm_num_predict`。
- Ollama 未啟動、模型不存在、request timeout、malformed response 或 final response 為空時，answer 會明確標示 LLM generation unavailable，並 fallback 到 retrieved OCR chunks；不會讓模型捏造未檢索內容。
- `scripts/demo-smoke-test.ps1 -RunLlm` 會檢查 Ollama `/api/tags`、確認 `qwen3.5:4b` 存在，並要求 RAG answer source 為 `ollama/qwen3.5:4b`。

Phase 11 Ollama embedding client：

- Phase 11 到 v0.26.0 期間，`DOCURAG_EMBEDDING_PROVIDER` 預設未設定，embedding provider 為 disabled；v0.27.0 起預設改為 `ollama`，供 aggressive demo defaults 優先嘗試 vector / hybrid retrieval。
- 設定 `DOCURAG_EMBEDDING_PROVIDER=ollama`、`DOCURAG_EMBEDDING_BASE_URL=http://127.0.0.1:11434` 與 `DOCURAG_EMBEDDING_MODEL=qwen3-embedding:0.6b` 後，`OllamaEmbeddingProvider` 會使用 native `POST /api/embed`。
- `DOCURAG_EMBEDDING_TIMEOUT_SECONDS` 預設為 `30`。
- `scripts/ollama-embedding-smoke.ps1` 可檢查 Ollama `/api/tags` 並呼叫 `/api/embed`，用於輸出本機實際 vector dimension。
- 2026-05-22 follow-up 本機 smoke 結果：Ollama service 可連線，已 pull `qwen3-embedding:0.6b`；`scripts/ollama-embedding-smoke.ps1` 通過並確認實際 vector dimension 為 `1024`。Mock HTTP tests 仍覆蓋 request / response / timeout / HTTP error / malformed response。
- 此 building block 在 Phase 11 起先作 optional adapter；v0.27.0 起成為預設 adapter selection，runtime 不可用時仍 fallback，不移除 optional `qwen3.5:4b` generation path。

Phase 11 Qdrant local runtime：

- `DOCURAG_QDRANT_URL` 預設 `http://127.0.0.1:6333`。
- `DOCURAG_QDRANT_COLLECTION` 預設 `docurag_chunks_v1`。
- `DOCURAG_QDRANT_VECTOR_SIZE` 預設 `1024`，對應本機 `qwen3-embedding:0.6b` smoke 確認的實際 vector dimension；外部 runtime 不可用時仍可用 mock tests 與明確 env 重跑。
- `DOCURAG_QDRANT_TIMEOUT_SECONDS` 預設 `10`。
- `QdrantVectorStore.ensure_collection()` 只建立或檢查 collection，不會被 backend startup 或 `/rag/query` 預設 path 呼叫。
- `scripts/qdrant-collection-smoke.ps1` 會檢查或建立 `docurag_chunks_v1`，distance 固定 `Cosine`。

```powershell
docker-compose -f infra/docker-compose.yml up -d qdrant
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\qdrant-collection-smoke.ps1
docker-compose -f infra/docker-compose.yml down
```

2026-05-22 follow-up 本機 validation：Qdrant mock tests 通過；Docker Desktop 已啟動，Docker Compose 已啟動 `qdrant` service，`qdrant-collection-smoke.ps1` 通過並確認 `docurag_chunks_v1` collection，vector size `1024`、distance `Cosine`。v0.27.0 起這條能力已成為 aggressive demo default 的優先路徑；runtime 不可用時仍 fallback。

Phase 11 optional Vector RAG：

- `DOCURAG_RAG_RETRIEVAL_PROVIDER` v0.27.0 起預設為 `hybrid_rerank`；若要回到舊 keyword baseline，可設定為 `keyword`。若要只展示純 vector，可設定為 `vector`。
- Vector path 只會 embed query 並用 Qdrant search 取回已索引 chunks；`POST /documents/{document_id}/index/vector` 才會負責將 local chunks embed 後 upsert 到 Qdrant。Phase 30 hardening 起 Qdrant search payload 會用目前 backend 已載入且有 chunks 的 document ids 做 filter，避免舊 demo / eval vectors 消耗 `top_k` 後再被 Python 端過濾成空結果。
- Embedding unavailable、Qdrant unavailable、collection mismatch、payload malformed 或 vector search 無結果時，response 會明確 fallback 到 keyword retrieval。
- Fallback 或成功狀態會寫入 citation `trace_metadata` 與 retrieved chunk `metadata`：`retrieval_provider`、`vector_retrieval_status`、`vector_store`、`qdrant_collection`、`embedding_provider`、`embedding_model` 與錯誤訊息或 vector score。
- LLM generation path 仍可接在 retrieved chunks 後；vector retrieval 成功時可由 `ollama/qwen3.5:4b` 生成回答，vector 失敗時仍可對 keyword fallback chunks 生成回答。

Phase 12 manual Vector Indexing：

- `POST /documents/{document_id}/index/vector` 會對單一已完成 OCR 且已有 chunks 的 document 執行手動同步 vector indexing。
- Endpoint 預設使用 `DOCURAG_EMBEDDING_PROVIDER=ollama`，且 Qdrant collection 可用時有機會成功；provider disabled、embedding failure、Qdrant unavailable 或 vector size mismatch 會回傳清楚錯誤。
- 成功 response 會包含 `indexed_chunk_count`、`point_ids`、`collection_name`、`vector_size`、`embedding_provider` 與 `embedding_model`。
- Empty chunks 會回傳 `status=skipped`，未完成 OCR 的 document 會回傳 `409`；backend upload / OCR endpoint 本身不啟動 worker，frontend v0.27.0 後台 ingestion 會在 OCR 成功後 best-effort 呼叫此 API。
- Phase 28 source router contract 將目前圖片 runtime 路由標為 `image_ocr`，而 vector payload 來源仍可保留 `source_type=ocr_image`：OCR lines / chunks 是 Qdrant payload 的文字來源，payload 至少保留 `document_id`、`filename`、`chunk_id`、`source_type`、`content_source`、`page_number`、`created_at` 與 future `project_id` / `tenant_id` metadata 位置。
- `.txt` 檔已走 `text_upload` direct chunks，不需要假裝經過 OCR；text-native PDF 已走 `pdf_text` extraction；scanned PDF 在 PDF rendering / OCR pipeline 完成前只能標為 `pdf_scanned_pending_ocr`，不得宣稱已可索引。
- VLM structured fields 不會在本 contract 自動寫入 retrieval chunks；若未來要索引欄位，需要另開 field-indexing policy ticket。

```powershell
$env:DOCURAG_RAG_RETRIEVAL_PROVIDER="hybrid_rerank"
$env:DOCURAG_EMBEDDING_PROVIDER="ollama"
$env:DOCURAG_EMBEDDING_MODEL="qwen3-embedding:0.6b"
$env:DOCURAG_RERANK_PROVIDER="fastembed"
$env:DOCURAG_QDRANT_URL="http://127.0.0.1:6333"
$env:DOCURAG_QDRANT_COLLECTION="docurag_chunks_v1"
py -3.12 -m uvicorn app.main:app --reload
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunVector
```

Phase 13 retrieval evaluation baseline：

- `sample-data/eval/retrieval-eval.json` 使用公開虛構 invoice 與 support contract sample。
- `app.services.evaluation` 會讀取 eval cases、建立本機 sample chunks、執行 keyword 或 optional vector retrieval，並輸出 per-query results 與 summary metrics。
- Summary metrics 包含 `Hit Rate@K`、`MRR@K`、`Recall@K`、平均 latency 與 failure count。
- Baseline keyword eval 不依賴 Ollama embedding 或 Qdrant。
- Optional vector eval 必須明確設定 embedding / Qdrant env；smoke 會先檢查 Ollama `qwen3-embedding:0.6b`、`docurag_chunks_v1` collection，並透過 `POST /documents/{document_id}/index/vector` 做 manual indexing API preflight。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVector
```

Eval result JSON 預設輸出到 `.tmp/retrieval-eval-result-keyword.json`、`.tmp/retrieval-eval-result-vector.json`、`.tmp/retrieval-eval-result-vector-rerank.json`、`.tmp/retrieval-eval-result-hybrid.json` 或 `.tmp/retrieval-eval-result-hybrid-rerank.json`，不寫入 production storage，也不在 backend startup、upload、OCR 或 `/rag/query` 自動執行。

Phase 15 optional vector rerank eval：

- `DOCURAG_RERANK_PROVIDER` v0.27.0 起預設為 `fastembed`；FastEmbed runtime 採 lazy import，不可用時會保留 candidates 並留下 fallback metadata。
- `vector_rerank` strategy 先執行既有 vector retrieval，再對 vector candidates 呼叫 rerank adapter；vector retrieval 失敗時保留原 keyword fallback，不會對 fallback chunks 再 rerank。
- Rerank unavailable、disabled、timeout 或 malformed scores 會保留原 vector candidates，並在 retrieved chunk metadata / citation trace metadata 記錄 `rerank_enabled=false`、`rerank_status` 與 `rerank_fallback_reason`。
- FastEmbed runtime 採 lazy import；尚未安裝 optional rerank runtime 時 baseline keyword eval 與 optional vector eval 不受影響。
- `vector_rerank` 不代表 hybrid search、BM25、score fusion、dataset JSON expansion 或 frontend trace UI 已完成。

```powershell
$env:DOCURAG_RERANK_PROVIDER="fastembed"
$env:DOCURAG_RERANK_MODEL="BAAI/bge-reranker-base"
$env:DOCURAG_RERANK_TOP_K="5"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVectorRerank
```

Phase 16 optional hybrid eval：

- `sample-data/eval/retrieval-eval.json` 已擴充到 12 筆公開虛構 eval cases，並覆蓋 lexical mismatch、multi-evidence、near-duplicate、cross-document ambiguity 與 numeric / table lookup tags。
- `hybrid` strategy 可透過 env 接入 `/rag/query`，eval runner 仍可用來量化比較。
- Hybrid eval 使用 existing keyword branch + optional vector branch，依 deterministic `rank_based_fusion` merge / dedupe candidates，並保留 branch rank、branch score、merged score、dedupe count 與 fallback reason。
- Vector branch unavailable 時會 fallback 到 keyword-only candidates；此 fallback 會留在 chunk / citation trace metadata，不讓 baseline eval 失敗。
- `hybrid` 不代表 `hybrid_rerank`、BM25 dependency、frontend trace UI、eval dashboard 或 answer faithfulness scoring 已完成。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybrid
```

Phase 19 / 27 hybrid rerank：

- `hybrid_rerank` strategy 已在 v0.27.0 接入 `/rag/query` 與 Agent search default path；eval runner 仍可用來量化比較，不代表 production eval dashboard。
- `hybrid_rerank` 先重用 `hybrid` 的 keyword + vector branch merge / dedupe candidates，再對 hybrid candidates 呼叫 rerank adapter。
- `-RunHybridRerank` 沿用 vector preflight、manual vector indexing API preflight 與 rerank fallback behavior；FastEmbed runtime 不可用時會保留 hybrid candidates 並記錄 `rerank_status` / `rerank_fallback_reason`。
- 輸出 `.tmp/retrieval-eval-result-hybrid-rerank.json`，summary 會保留 `fallback_count`、`fallback_reasons`、`trace_metadata_count` 與 `result_strategy_counts`。
- Candidate metadata 會區分 branch score、merge score 與 rerank score：`keyword_score` / `vector_score` 是 branch score，`merged_score` / `merged_rank` 是 hybrid merge 結果，`rerank_score` / `rerank_rank` 是 reranker 結果，`final_score_source` 說明目前排序使用哪一種分數。
- 缺少 optional metadata 時維持可讀 fallback state，例如 `vector_unavailable`、`reranker_disabled` 或 `reranker_unavailable`，不讓 keyword baseline 或 baseline eval 因 metadata 缺失失敗。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybridRerank
```

## Local Storage

上傳 API 會將原始檔案保存到 repo root 的 `data/uploads/`，並將 metadata 寫入 `data/documents.json`。`filename` 會先安全化，避免 `../` 或 Windows path separator 造成 path traversal。

OCR mock API 會透過 `MockOcrProvider` 產生 deterministic OCR result，再由 `DocumentStorage` 將 OCR status、text、extracted fields、updated timestamp 與 local chunks 寫回同一份 `data/documents.json`。未執行 OCR 的文件會回傳 `pending` OCR status。

document metadata 會包含 `processing` contract，明確記錄 `upload`、`ocr`、`indexing`、`ready`、`failed_reason` 與 `updated_at`。圖片 upload 完成後 OCR / indexing 會保持 pending；`.txt` direct ingestion 與 text-native PDF extraction 會直接完成 local indexing；mock OCR 成功後 OCR 與 indexing 會標記 completed 並進入 ready；provider 回傳 failed 時會保存 failed_reason，但不啟動 background worker 或 queue。

document metadata 也會保存 `processing_jobs` history 與 `latest_job` summary。同步 upload 會記錄 completed upload job；mock OCR 成功會記錄 completed OCR 與 local indexing job；provider failed 會記錄 failed OCR job。這些 job metadata 只是 contract，不代表已引入 worker、queue、Redis 或 NATS。

v0.5.1 chunks 由 OCR mock text 產生，每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。v0.6 chunk / citation schema 另外補齊 optional `page_number`、`bbox`、`confidence`、`source_type`、chunk `metadata` 與 citation `trace_metadata` 欄位；mock OCR chunk 只填 `source_type=ocr_mock` 與 metadata safe default，不產生真正 OCR bbox 或 confidence。v0.7 real OCR output 先正規化到 `OcrResult.lines`，再將 line-level page、bbox、confidence 與 metadata 寫入 `DocumentChunk`，讓 citations 與 retrieved chunks 不依賴 PaddleOCR 私有格式。v0.27.0 起 `POST /rag/query` 預設透過 `HybridRerankRagProvider` 嘗試 keyword + vector merge 與 rerank；設定 `DOCURAG_RAG_RETRIEVAL_PROVIDER=keyword` 可回到舊 keyword baseline。v0.28.0 起 `.txt` 直接產生 `source_type=text_upload` chunks，text-native PDF 產生 `source_type=pdf_text` chunks，不再把 direct text path 包成 mock OCR；v0.29.0 built-in RAG eval 會用 `eval_fixture` chunks 建立 synthetic 中文發票 benchmark。`hybrid_rerank` 不是 LLM-as-judge 或 answer quality evaluation，也不代表 production indexing pipeline 已完成。

可用環境變數覆寫資料目錄：

```powershell
$env:DOCURAG_DATA_DIR="C:/tmp/docurag-data"
```

runtime 檔案不會提交到 Git：

- `data/uploads/*`
- `data/documents.json`

repo 只保留 `data/uploads/.gitkeep` 作為資料夾 placeholder。

## Test

從 repo root 執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1
```

或在 Python 環境已準備好後手動執行：

```powershell
cd backend
py -3.12 -m pytest
```

## Demo Scripts

先啟動 backend，再從 repo root 執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1
```

`demo-smoke-test.ps1` 預設仍驗證 `/health`、upload、OCR mock、parser、Agent 與 `/rag/query`，作為無 GPU / 無 Qdrant 環境可重跑的 API baseline；frontend upload 主線則改用 provider-selected `/ocr`。預設模式接受 `ollama/qwen3.5:4b`、`LLM unavailable fallback` 或明確關閉 LLM 時的 `deterministic baseline` answer source，也接受 `hybrid_rerank`、`hybrid`、`vector_rerank`、`vector/qdrant`、`vector unavailable fallback` 或 `keyword baseline` retrieval source，因為外部 runtime 不可用時會保留 fallback trace。`-RunLlm` 仍要求 Ollama service 已載入 `qwen3.5:4b`，並要求 RAG answer source 為 `ollama/qwen3.5:4b`。`-RunVector` 需要 backend 以 vector / embedding / Qdrant env 啟動，會先呼叫 `POST /documents/{document_id}/index/vector`，再確認 retrieval source 屬於 vector-backed path。`seed-demo-data.ps1` 會上傳 `sample-data/documents/mock-invoice-aurora.txt`、執行 OCR mock、查詢 `payment due date Net 15`，並輸出 answer、citations、retrieved chunks；加上 `-RunRealOcr` 時會額外驗證 real OCR sample。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunLlm
```

Retrieval eval smoke 不需要啟動 frontend；baseline mode 也不需要 Qdrant 或 embedding：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1
```

Optional vector retrieval eval 需要 Ollama embedding、Qdrant collection 與 vector-enabled backend。它會先做 manual vector indexing API preflight，再跑本機 eval runner；optional `vector_rerank` eval 另可用 `-RunVectorRerank` 驗證 rerank metadata 或 fallback metadata：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVector
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVectorRerank
```

Real OCR demo 只在 backend 已用 Python 3.12 安裝 CUDA PaddlePaddle wheel 與 `.[dev,real-ocr]` 時使用。v0.8 起 provider-selected `/ocr` 預設走 PaddleOCR；Phase 09 起缺少 GPU dependency 或不是 CUDA build 時，`-RunRealOcr` smoke 會明確失敗，mock smoke / seed flow 可透過 `/ocr/mock` 或 `DOCURAG_OCR_PROVIDER=mock` 重跑：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1 -RunRealOcr
```

optional sample image 包含 `sample-data/documents/sample-ocr-invoice.png` 與 `sample-data/documents/sample-ocr-zh-tw.png`，內容皆為自造虛構資料。

## Docker

```powershell
docker build -t docurag-backend ./backend
docker run --rm -p 8000:8000 docurag-backend
```

或使用 repo 內的 Compose：

```powershell
docker compose -f infra/docker-compose.yml up --build
```

背景啟動後驗證：

```powershell
docker compose -f infra/docker-compose.yml up -d
curl http://127.0.0.1:8000/health
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1
docker compose -f infra/docker-compose.yml down
```

## Environment Check

從 repo root 執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1
```

如果 Python 或 Docker 不可用，依 `docs/LOCAL_DEV_SETUP.md` 修復本機工具後再重跑測試。

v0.9.1 PaddleOCR GPU baseline 可用同一支腳本分段檢查 NVIDIA CLI、CUDA Paddle build、`paddle.utils.run_check()`、model cache / engine initialization、sample image OCR 與 OCR timing：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr
```

2026-05-21 Windows 本機以 Python 3.12.10、PaddleOCR 2.10.0 與 PaddlePaddle 3.0.0 完成 v0.8 CPU baseline；Phase 09 已移除 CPU baseline。2026-05-22 已以 Python 3.12.10、PaddleOCR 2.10.0、`paddlepaddle-gpu==3.3.0` 與 CUDA 12.9 runtime wheel 完成 GPU baseline；v0.9.1 timing baseline 採用 `cls=False`、`det_limit_side_len=960` 與 startup preload / provider reuse。

## Release Status

- v0.1.0: FastAPI backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- Python: `scripts/test-backend.ps1` 可透過 `pip.exe` 反推實際 `python.exe` 並建立/使用 `.venv`。
- v0.2.0: backend CORS、Docker image build、Compose build 與 Compose healthcheck 已納入驗證。
- v0.3.0: document local storage、metadata JSON、list/detail/download API 與 Compose upload 驗證已完成。
- v0.4.0: OCR mock API、OCR result persistence、pytest、Docker build 與 Compose OCR mock API 驗證已完成。
- v0.5.0: local chunking、keyword retrieval、RAG answer API、pytest、Docker build 與 Compose RAG API 驗證已完成。
- v0.5.1: demo sample data、seed script、API smoke test、pytest、Docker build 與 Compose demo 驗證已完成。
- v0.6.0: Bridge Contracts、OCR provider interface、RAG provider interface、processing status、chunk citation schema 與 processing job contract 已完成。
- v0.7.0: Real OCR Provider Spike、PaddleOCR adapter、provider-selected OCR endpoint、trace normalization 與 optional real OCR demo hardening 已完成。
- v0.8.0: PaddleOCR Runtime Stabilization、Python 3.12 runtime guard、PaddleOCR 2.10.0 / PaddlePaddle 3.0.0 dependency baseline 與 sample real OCR flow 已完成。
- v0.9.0: GPU Runtime、PaddlePaddle GPU-only guard、PP-OCRv4 mobile 中文 / 中英混合模型設定與模型目錄文件已完成；本機 Python 3.12 + CUDA PaddlePaddle GPU runtime、sample invoice 與繁中 provider-selected OCR smoke 已通過。
- v0.9.1: OCR Performance Hardening、backend startup preload、provider / engine reuse、OCR timing log / metadata、`cls=False` baseline 與文件版本同步已完成。
- v0.10.0: LLM RAG Backlog、Ollama `qwen3.5:4b` provider decision、最小 client、optional `/rag/query` generation path、demo smoke `-RunLlm`、frontend answer source 與文件版本同步已完成。
- v0.11.0: Vector RAG Backlog、Ollama `qwen3-embedding:0.6b` embedding client、Qdrant local runtime / collection smoke、optional vector retrieval path、fallback trace metadata、demo smoke `-RunVector` 與文件版本同步已完成。
- v0.12.0: Vector Indexing Hardening、manual vector indexing contract、同步 indexing service、`POST /documents/{document_id}/index/vector`、optional vector indexing smoke 與文件版本同步已完成。
- v0.13.0: Retrieval Evaluation Baseline、公開 eval dataset、retrieval eval runner、Hit Rate@K / MRR@K / Recall@K / latency / failure count metrics、baseline eval smoke 與 optional vector eval smoke 已完成。
- v0.15.0: Rerank Runtime Spike、FastEmbed provider decision、disabled-by-default rerank adapter、optional `vector_rerank` eval strategy、rerank trace metadata 與文件版本同步已完成。
- v0.16.0: Hybrid Retrieval Slice、12 筆公開 eval dataset、optional `hybrid` eval strategy、hybrid trace metadata、baseline eval smoke 與 optional `-RunHybrid` smoke 已完成。
- v0.17.0: Retrieval Trace UI / Eval Visibility、eval summary fallback / trace metadata reporting、baseline demo smoke、baseline eval smoke 與文件版本同步已完成。
- v0.18.0: Hybrid Rerank Planning、Markdown-only planning tickets、TODO 與 ROADMAP 同步已完成，不 bump runtime version。
- v0.19.0: Hybrid Rerank Runtime、optional `hybrid_rerank` eval provider、`-RunHybridRerank` smoke flag、trace / report metadata、baseline demo smoke、baseline eval smoke 與文件版本同步已完成。
- v0.20.0: Interview MVP Packaging、demo script、sample / eval coverage、demo media、baseline final validation 與文件版本同步已完成。
- v0.21.0: Real GPU OCR Interview Demo Path、frontend upload provider-selected real OCR-first flow、manual mock OCR fallback、版本與文件同步已完成。
- v0.22.0: RAG Query Hardening、keyword query normalization、CJK tokenization、demo-safe 中文 alias、backend tests 與版本文件同步已完成。
- v0.23.0: Viewer Chat / Admin Ingestion Role Split、Viewer 前台查詢與 Admin / Analyst 後台 ingestion surface 分離、版本與文件同步已完成。
- v0.24.0: VLM / Parser Minimal MVP、deterministic invoice parser fallback、parse / fields API、local JSON parser result persistence、frontend structured fields surface、parser smoke validation 與版本文件同步已完成。
- v0.25.0: Agent Tool-use Minimal MVP、deterministic planner、allowlisted tool adapters、Agent run / lookup API、frontend trace surface、Agent demo smoke validation 與版本文件同步已完成。
- v0.26.0: Real VLM Parser Provider Spike、VLM-first `vlm_invoice` adapter、demo-safe image input resolver、fake / stub success smoke、provider unavailable fallback 與 Agent `get_document_fields` consumption validation 已完成。
- v0.27.0: Aggressive Demo Defaults、default `hybrid_rerank` RAG / Agent search、Ollama embedding、FastEmbed rerank adapter、frontend parser + vector indexing best-effort flow 與 fallback-safe smoke validation 已完成。
- v0.27.1: OCR / VLM Evidence Alignment 已完成；VLM request 帶 image + OCR context，欄位結果會保存 OCR evidence 或標示 evidence unmatched / unavailable，RAG / vector indexing 仍使用 OCR chunks。
- v0.28.0: Document Sources / Demo Auth Mode 已完成；`.txt` direct `text_upload` chunks、text-native PDF `pdf_text` chunks、scanned PDF pending state、demo login / me / logout API、Admin / Analyst write access 與 Viewer forbidden guard 已完成。
- v0.29.0: Built-in RAG Eval Admin Surface 已完成；新增 `POST /eval/rag/built-in`、10 張 synthetic 中文發票 fixture、固定 `hybrid_rerank` summary metrics、fallback cases 明細與 demo auth Viewer forbidden guard。
- v0.29.0 follow-up hardening: Ollama VLM response parsing 已支援 `response` / `thinking` / fenced JSON、金額字串、confidence label 與 line item alias；frontend 後台檔案選擇可多選並逐檔走既有 ingestion flow；`hybrid_rerank` vector branch 會用 document-scoped Qdrant filter 避免 stale vectors，Ollama RAG generation 預設帶 `think=false` 與 `options.num_predict=512`，不 bump version。
