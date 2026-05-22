# Backend

DocuRAG AgentOps backend MVP v0.11.0 是最小 FastAPI 服務，提供 healthcheck、文件本機上傳、metadata 保存、文件列表、文件詳情、OCR mock API、provider-selected OCR API、local RAG query API、demo seed script 與 API smoke test，並允許 local frontend 透過 CORS 呼叫。v0.6 bridge 先整理 provider contract，RAG 預設仍以 `KeywordRagProvider` 做 keyword retrieval 與 citation contract。v0.10.0 加入最小 Ollama `qwen3.5:4b` LLM client、可選 `/rag/query` generation path 與 demo smoke；v0.11.0 加入 disabled-by-default Ollama embedding client、optional Qdrant runtime 與 fallback-safe vector retrieval path。未設定 vector retrieval 或 LLM provider 時既有 `/rag/query` 預設仍是 deterministic keyword baseline。此階段不接資料庫、OpenAI API、vLLM、rerank、Redis、NATS、worker 或登入權限。

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

- `DOCURAG_LLM_PROVIDER` 未設定時，LLM provider 是 disabled，既有 `/rag/query` 仍回傳 deterministic keyword baseline。
- 設定 `DOCURAG_LLM_PROVIDER=ollama`、`DOCURAG_LLM_BASE_URL=http://127.0.0.1:11434` 與 `DOCURAG_LLM_MODEL=qwen3.5:4b` 後，可用 `OllamaLlmProvider` 呼叫 Ollama native `/api/generate`。
- client 使用 `stream=false`，讓回應維持單一 JSON 物件，方便 backend 測試與後續 RAG generation path 接入。
- `check_health()` 會呼叫 `/api/tags`，確認 service 可連線且目標模型出現在本機模型清單。
- 10-03 起 `/rag/query` 在 LLM provider enabled 且 retrieval 有命中 chunks 時，會用 query + retrieved chunks 組 prompt 產生回答；prompt 不包含未檢索內容。
- citations 與 retrieved chunks contract 保持不變，citation `trace_metadata` 會加上 `llm_provider`、`llm_model`、generation status、latency 與 token usage。
- Ollama 未啟動、模型不存在或 request timeout 時，answer 會明確標示 LLM generation unavailable，並 fallback 到 retrieved OCR chunks；不會讓模型捏造未檢索內容。
- `scripts/demo-smoke-test.ps1 -RunLlm` 會檢查 Ollama `/api/tags`、確認 `qwen3.5:4b` 存在，並要求 RAG answer source 為 `ollama/qwen3.5:4b`。

Phase 11 Ollama embedding client：

- `DOCURAG_EMBEDDING_PROVIDER` 預設未設定，embedding provider 為 disabled；既有 `/rag/query` 仍維持 keyword retrieval baseline。
- 設定 `DOCURAG_EMBEDDING_PROVIDER=ollama`、`DOCURAG_EMBEDDING_BASE_URL=http://127.0.0.1:11434` 與 `DOCURAG_EMBEDDING_MODEL=qwen3-embedding:0.6b` 後，`OllamaEmbeddingProvider` 會使用 native `POST /api/embed`。
- `DOCURAG_EMBEDDING_TIMEOUT_SECONDS` 預設為 `30`。
- `scripts/ollama-embedding-smoke.ps1` 可檢查 Ollama `/api/tags` 並呼叫 `/api/embed`，用於輸出本機實際 vector dimension。
- 2026-05-22 follow-up 本機 smoke 結果：Ollama service 可連線，已 pull `qwen3-embedding:0.6b`；`scripts/ollama-embedding-smoke.ps1` 通過並確認實際 vector dimension 為 `1024`。Mock HTTP tests 仍覆蓋 request / response / timeout / HTTP error / malformed response。
- 此 building block 預設 disabled，也不移除 optional `qwen3.5:4b` generation path。

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

2026-05-22 follow-up 本機 validation：Qdrant mock tests 通過；Docker Desktop 已啟動，Docker Compose 已啟動 `qdrant` service，`qdrant-collection-smoke.ps1` 通過並確認 `docurag_chunks_v1` collection，vector size `1024`、distance `Cosine`。這不改變既有 keyword RAG baseline 預設。

Phase 11 optional Vector RAG：

- `DOCURAG_RAG_RETRIEVAL_PROVIDER` 預設為 `keyword`；只有設定為 `vector` 時才會嘗試 embedding + Qdrant。
- Vector path 會在 query request 內以最小實作將 local chunks embed 後 upsert 到 Qdrant，再 embed query 並用 Qdrant search 取回 chunks。
- Embedding unavailable、Qdrant unavailable、collection mismatch、payload malformed 或 vector search 無結果時，response 會明確 fallback 到 keyword retrieval。
- Fallback 或成功狀態會寫入 citation `trace_metadata` 與 retrieved chunk `metadata`：`retrieval_provider`、`vector_retrieval_status`、`vector_store`、`qdrant_collection`、`embedding_provider`、`embedding_model` 與錯誤訊息或 vector score。
- LLM generation path 仍可接在 retrieved chunks 後；vector retrieval 成功時可由 `ollama/qwen3.5:4b` 生成回答，vector 失敗時仍可對 keyword fallback chunks 生成回答。

Phase 12 manual Vector Indexing：

- `POST /documents/{document_id}/index/vector` 會對單一已完成 OCR 且已有 chunks 的 document 執行手動同步 vector indexing。
- Endpoint 只在明確設定 `DOCURAG_EMBEDDING_PROVIDER=ollama` 且 Qdrant collection 可用時有機會成功；provider disabled、embedding failure、Qdrant unavailable 或 vector size mismatch 會回傳清楚錯誤。
- 成功 response 會包含 `indexed_chunk_count`、`point_ids`、`collection_name`、`vector_size`、`embedding_provider` 與 `embedding_model`。
- Empty chunks 會回傳 `status=skipped`，未完成 OCR 的 document 會回傳 `409`；upload / OCR 不會自動觸發 vector indexing。

```powershell
$env:DOCURAG_RAG_RETRIEVAL_PROVIDER="vector"
$env:DOCURAG_EMBEDDING_PROVIDER="ollama"
$env:DOCURAG_EMBEDDING_MODEL="qwen3-embedding:0.6b"
$env:DOCURAG_QDRANT_URL="http://127.0.0.1:6333"
$env:DOCURAG_QDRANT_COLLECTION="docurag_chunks_v1"
py -3.12 -m uvicorn app.main:app --reload
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunVector
```

## Local Storage

上傳 API 會將原始檔案保存到 repo root 的 `data/uploads/`，並將 metadata 寫入 `data/documents.json`。`filename` 會先安全化，避免 `../` 或 Windows path separator 造成 path traversal。

OCR mock API 會透過 `MockOcrProvider` 產生 deterministic OCR result，再由 `DocumentStorage` 將 OCR status、text、extracted fields、updated timestamp 與 local chunks 寫回同一份 `data/documents.json`。未執行 OCR 的文件會回傳 `pending` OCR status。

document metadata 會包含 `processing` contract，明確記錄 `upload`、`ocr`、`indexing`、`ready`、`failed_reason` 與 `updated_at`。upload 完成後 OCR / indexing 會保持 pending；mock OCR 成功後 OCR 與 indexing 會標記 completed 並進入 ready；provider 回傳 failed 時會保存 failed_reason，但不啟動 background worker 或 queue。

document metadata 也會保存 `processing_jobs` history 與 `latest_job` summary。同步 upload 會記錄 completed upload job；mock OCR 成功會記錄 completed OCR 與 local indexing job；provider failed 會記錄 failed OCR job。這些 job metadata 只是 contract，不代表已引入 worker、queue、Redis 或 NATS。

v0.5.1 chunks 由 OCR mock text 產生，每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。v0.6 chunk / citation schema 另外補齊 optional `page_number`、`bbox`、`confidence`、`source_type`、chunk `metadata` 與 citation `trace_metadata` 欄位；mock OCR chunk 只填 `source_type=ocr_mock` 與 metadata safe default，不產生真正 OCR bbox 或 confidence。v0.7 real OCR output 先正規化到 `OcrResult.lines`，再將 line-level page、bbox、confidence 與 metadata 寫入 `DocumentChunk`，讓 citations 與 retrieved chunks 不依賴 PaddleOCR 私有格式。`POST /rag/query` 預設透過 `KeywordRagProvider` 做本機 keyword retrieval，設定 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector` 時才改用 `VectorRagProvider` 嘗試 Ollama embedding + Qdrant search。對 `text/plain`、`.txt`、`.md`、`.csv` sample，OCR mock 會把上傳文字納入 deterministic mock OCR text，方便 demo query 引用具體欄位；這不是 rerank、hybrid search 或 eval runner。

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

`demo-smoke-test.ps1` 會驗證 `/health`、upload、OCR mock 與 `/rag/query`；預設要求 deterministic baseline answer source。`-RunLlm` 需要 backend 以 `DOCURAG_LLM_PROVIDER=ollama` 啟動，並要求 Ollama service 已載入 `qwen3.5:4b`。`seed-demo-data.ps1` 會上傳 `sample-data/documents/mock-invoice-aurora.txt`、執行 OCR mock、查詢 `payment due date Net 15`，並輸出 answer、citations、retrieved chunks。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunLlm
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
