# 12-01 Vector Indexing Contract

## Goal

固定 Phase 12 / `v0.12.0` 的 local vector indexing contract，讓後續 implementation ticket 有明確邊界。此 ticket 只做文件規劃，不新增 runtime。

## Scope

- 定義 Phase 12 的 vector indexing 目標與 release boundary。
- 固定 Qdrant point id、collection、vector size、payload metadata 與 indexing trace metadata contract。
- 定義 indexing failure / fallback 行為。
- 明確保留 keyword RAG baseline 與 optional Ollama `qwen3.5:4b` generation path。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 12 backlog。

## Out of Scope

- 不新增或修改 backend 程式碼。
- 不新增 indexing API。
- 不新增 persistent indexing runtime。
- 不實作 rerank、hybrid search 或 eval runner。
- 不新增 Redis、NATS、worker、PostgreSQL schema、登入或 RBAC。
- 不新增 VLM parser、PDF rendering 或 production OCR pipeline。
- 不讓 vector retrieval 成為 default-on path。

## Release Impact

- Target version: `v0.12.0`。
- Version bump required: no。
- 原因：本 ticket 只建立 Phase 12 contract 與 backlog，不完成 runtime release；版本同步留到 `12-04`。

## Phase 12 Contract

Phase 12 只把 Phase 11 的 request-time vector retrieval demo 收斂成手動、同步、可重跑的 local vector indexing flow。Keyword RAG 仍是預設 baseline；只有明確設定 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector`、`DOCURAG_EMBEDDING_PROVIDER=ollama`，且手動呼叫 indexing API 後，vector demo 才會依賴 Qdrant。

Indexing target：

- Collection：`docurag_chunks_v1`，沿用 Phase 11 Qdrant collection。
- Vector size：`DOCURAG_QDRANT_VECTOR_SIZE`，預設 `1024`，對應 `qwen3-embedding:0.6b`。
- Distance：`Cosine`。
- Embedding provider：`DOCURAG_EMBEDDING_PROVIDER=ollama`。
- Embedding model：`DOCURAG_EMBEDDING_MODEL=qwen3-embedding:0.6b`。

Stable point id：

- Point id 必須由 chunk identity deterministically 產生，避免重跑 indexing 時重複新增 points。
- 規則：`uuid5(NAMESPACE_URL, f"docurag:{document_id}:{chunk_id}")`。
- 同一 document chunk 重跑 indexing 只能 upsert 同一 point id。

Payload metadata：

- 必填：`document_id`、`filename`、`chunk_id`、`text`、`source`、`source_type`、`created_at`。
- 選填但需保留：`page_number`、`bbox`、`confidence`。
- Chunk metadata 需原樣保留在 `metadata`，並額外補上 safe trace 欄位：`ocr_provider`、`indexing_provider=vector`、`vector_store=qdrant`、`qdrant_collection`、`embedding_provider`、`embedding_model`。
- 不新增 organization / project filtering；project / auth scope 留到後續已排定 ticket。

Indexing result / trace metadata：

- Success result 至少包含 `document_id`、`status=completed`、`indexed_chunk_count`、`skipped_chunk_count`、`point_ids`、`collection_name`、`vector_size`、`embedding_provider`、`embedding_model`。
- Empty chunks 回傳 `status=skipped` 與清楚 reason，不呼叫 embedding 或 Qdrant upsert。
- Provider disabled、embedding failure、Qdrant unavailable、collection missing、dimension mismatch 或 upsert failure 回傳 `status=failed` 或 HTTP error detail；不得修改 local document metadata，也不得影響 keyword RAG baseline。

Failure / fallback 行為：

- Manual indexing API 可以明確失敗，讓 demo smoke 顯示 preflight / runtime error。
- `/rag/query` 預設仍走 keyword baseline。
- Vector retrieval failure 仍使用 Phase 11 fallback：回到 keyword retrieval，並在 citation / retrieved chunk trace metadata 記錄 `vector_retrieval_status=failed`。
- 不允許 upload、OCR 或 backend startup 自動觸發 vector indexing。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md`

## Acceptance Criteria

- [x] Phase 12 goal、scope 與 guardrails 已記錄。
- [x] Qdrant point id 與 payload metadata contract 已記錄。
- [x] Vector indexing failure / fallback 行為已記錄。
- [x] Phase 12 backlog 已加入 `TODO.md` 與 `docs/ROADMAP.md`。
- [x] 明確標示此 ticket 不 bump version。

## Validation

- `rg -n "v0.12.0|phase-12|Vector Indexing|docurag_chunks_v1" TODO.md docs/ROADMAP.md tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md`
- `git diff --check`
