# 30-03 RAG Vector Stale Filter Hardening

## Goal

修正 default `hybrid_rerank` 在 Qdrant collection 混有舊 demo / eval vectors 時，先用 `top_k` 取回 stale points、再被 backend 依目前 `data/documents.json` 的 document ids 過濾成空結果，導致明明 Qdrant 與 embedding 都可用，卻回報 `vector_unavailable` / `Vector search returned no chunks.` 的問題。

## Scope

- 讓 vector retrieval 查詢 Qdrant 時，優先限制在目前 backend 已載入、且有 chunks 的 `DocumentMetadata.document_id` 範圍內。
- 保留現有 `hybrid_rerank` flow：keyword branch + vector branch -> hybrid merge / dedupe -> FastEmbed rerank。
- 補強 stale Qdrant collection 測試：collection 內有不屬於目前文件清單的 points 時，stale points 不可消耗 `top_k`，也不可讓 vector branch 誤判為 unavailable。
- 保留既有 fallback 行為：embedding provider、Qdrant connection、collection missing、vector size mismatch 或真正沒有 matching vector result 時，仍要回傳清楚 fallback trace。
- 不要求使用者手動清空 Qdrant collection 才能跑 demo；runtime 應對 stale points 有韌性。

## Out of Scope

- 不新增 Qdrant cleanup API、delete endpoint、admin maintenance UI 或自動清 collection 行為。
- 不新增 production indexing worker、DB-backed ingestion pipeline、Redis、NATS、PostgreSQL schema、migration 或 queue。
- 不修改 embedding model、rerank model、score fusion algorithm、LLM prompt、Agent planner、built-in eval metrics 或 citation scoring。
- 不引入 BM25、query rewrite、LLM-as-judge、answer correctness scoring 或 production eval dashboard。
- 不 bump release version；本 ticket 是 `v0.29.0` 後續 focused hardening。

## Release Impact

- Target version: `v0.29.0` follow-up hardening。
- Version bump required: no。
- 原因：只補強既有 vector retrieval 的 document scope filtering 與 stale collection resilience，不更新 `/health` version、package version、Docker Compose `DOCURAG_VERSION` 或 release artifact。

## Files likely to change

- `backend/app/services/vector_store.py`
- `backend/app/services/rag.py`
- `backend/tests/test_vector_store.py`
- `backend/tests/test_rag.py`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-30-parser-ingestion-hardening/30-03-rag-vector-stale-filter-hardening.md`

## Acceptance Criteria

- [ ] `/rag/query` 使用 `hybrid_rerank` 時，Qdrant search 只回傳目前 backend document list 允許的 document ids，或等效確保 stale points 不會消耗 final vector `top_k`。
- [ ] Qdrant collection 內存在舊 eval / demo points 時，若目前文件已有 matching vector points，response 不得顯示 `fallback_state=vector_unavailable`。
- [ ] vector branch 成功時，retrieved chunk metadata 保留 `vector_retrieval_status=completed`、`qdrant_collection`、`embedding_provider`、`embedding_model` 與 `vector_score`。
- [ ] embedding / Qdrant runtime 真正不可用時，既有 fallback trace 與 keyword fallback 行為不變。
- [ ] 不新增 cleanup endpoint、DB schema、worker、queue 或 release version bump。

## Validation

- `python -m pytest backend/tests/test_vector_store.py backend/tests/test_rag.py -q`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- Optional local verification when Qdrant / Ollama embedding are available：建立或保留 stale Qdrant points，重新索引目前 `data/documents.json` 文件後，`/rag/query` 的 `hybrid_rerank` trace 不再出現 `Vector search returned no chunks.`。
- `rg -n "document_id|vector_unavailable|Vector search returned no chunks|hybrid_rerank|stale" backend/app backend/tests TODO.md docs/ROADMAP.md tasks/phase-30-parser-ingestion-hardening/30-03-rag-vector-stale-filter-hardening.md`
- `git diff --check`
