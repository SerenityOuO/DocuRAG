# 16-03 Hybrid Eval Strategy Integration

## Goal

在 Phase 16 dataset expansion 完成後，新增 disabled-by-default optional `hybrid` eval strategy，讓本機 retrieval eval runner 可以比較 `keyword`、`vector`、`vector_rerank` 與 `hybrid`。此 ticket 只接 eval runner path，不改 `/rag/query` 預設行為。

## Scope

- 新增 optional `hybrid` eval strategy label，預設不啟用，僅由 eval runner / smoke flag 明確指定。
- Hybrid strategy 使用既有 keyword branch 與 optional vector branch 產生 candidates，並依 `16-01` contract 做 deterministic merge / dedupe。
- Vector branch unavailable 時，保留 keyword-only fallback，並在 result / chunk metadata 記錄 fallback reason。
- 保留 citation / retrieved chunk metadata，不破壞 Phase 13 metrics 與 Phase 15 rerank trace metadata。
- 更新 retrieval eval smoke script，新增 optional `-RunHybrid` 或等價明確 flag。
- 補齊 backend tests，覆蓋 success、vector branch fallback、dedupe、trace metadata 與 baseline keyword 不受影響。

## Implementation Notes

- `hybrid` 已加入 retrieval eval runner strategy choices，預設仍為 `keyword`。
- `HybridEvalProvider` 只存在於 eval runner path；不接 `/rag/query` 或 frontend。
- Merge policy 固定為 `rank_based_fusion`，使用 existing keyword branch 與 optional vector branch。
- Dedupe key 優先使用 `document_id:chunk_id`，並保留 branch rank、branch score、merged score、dedupe count 與 fallback metadata。
- Vector branch unavailable 時回到 keyword-only candidates，chunk / citation trace 會記錄 `branch_failures="vector"` 與 `fallback_reason`，且不把 optional branch fallback 算成 eval failure。
- `scripts/retrieval-eval-smoke.ps1 -RunHybrid` 已加入 explicit optional smoke flag。

## Out of Scope

- 不把 hybrid strategy 接到 `/rag/query`、frontend UI 或 default demo path。
- 不實作 `hybrid_rerank`、BM25 dependency、LLM-as-judge、answer faithfulness、citation quality scoring 或 eval dashboard。
- 不新增外部 dependency、Docker service、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 frontend trace UI。
- 不改變 existing `keyword`、`vector` 或 `vector_rerank` strategy 的預設行為。

## Release Impact

- Target version: `v0.16.0`。
- Version bump required: no。
- 原因：本 ticket 新增 Phase 16 optional eval strategy building block，但 release/version sync 留到 `16-04`，以避免前置 implementation ticket 提前 bump version。

## Files likely to change

- `backend/app/services/evaluation.py`
- `backend/app/services/rag.py`
- `backend/tests/test_evaluation.py`
- `scripts/retrieval-eval-smoke.ps1`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-16-hybrid-retrieval/16-03-hybrid-eval-strategy-integration.md`

## Acceptance Criteria

- [x] Eval runner 支援 explicit `hybrid` strategy，且預設仍是 keyword baseline。
- [x] Hybrid strategy 會 merge / dedupe keyword 與 vector candidates，並保留 trace metadata。
- [x] Vector branch unavailable 時會 fallback 到 keyword-only result，不讓 baseline eval 失敗。
- [x] Tests 覆蓋 hybrid success、fallback、dedupe 與 baseline safety。
- [x] Optional hybrid smoke flag 已文件化或實作，且不要求沒有 vector runtime 的環境必跑。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional hybrid eval smoke command must be run when local vector preflight is available.
- `git diff --check`
