# 17-03 Eval Result Report Summary

## Goal

改善 retrieval eval runner / smoke 的結果摘要，讓 keyword、vector、`vector_rerank` 與 `hybrid` metrics 更適合 demo、README 摘錄與後續比較。此 ticket 不建立 dashboard，也不新增資料庫。

## Scope

- 擴充 eval result summary，清楚輸出 strategy、case count、Hit Rate@K、MRR@K、Recall@K、latency、failure count 與 fallback count。
- 在可行範圍內輸出 candidate trace / fallback summary，協助判斷 vector、rerank 或 hybrid branch failure。
- 保持現有 baseline keyword eval smoke 指令可重跑；optional vector / `vector_rerank` / `hybrid` 仍需 explicit flag 與 local preflight。
- 補充 eval dataset / smoke 文件，說明 metrics 如何解讀與哪些 optional runtime 不可用時會被略過或 fallback。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 17 status。

## Implementation Notes

- `RetrievalEvalSummary` 已新增 `case_count`、`fallback_count`、`trace_metadata_count`、`result_strategy_counts` 與 `fallback_reasons`。
- CLI summary 會直接輸出 strategy、case count、Hit Rate@K、MRR@K、Recall@K、latency、failure count、fallback count、trace metadata count 與 result strategy counts。
- `retrieval-eval-smoke.ps1` 已檢查新增 summary 欄位，並在 smoke 結尾輸出 failure / fallback / trace metadata summary。
- `sample-data/eval/README.md` 已補充 summary metrics 解讀、optional runtime preflight 與 fallback 欄位用途。
- Optional vector / `vector_rerank` / `hybrid` 仍只在 explicit flag 與 local preflight 可用時執行；本 ticket 未新增 API、dashboard 或外部依賴。

## Out of Scope

- 不新增 production eval dashboard、frontend comparison page 或 API endpoint。
- 不新增 LLM-as-judge、answer faithfulness、citation quality scoring、`hybrid_rerank` 或 query rewriting。
- 不新增 eval dataset 真實資料；若需要新 sample document，必須另拆 ticket 並確認資料是公開虛構。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC 或 deployment 設定。

## Files likely to change

- `backend/app/services/evaluation.py`
- `backend/tests/test_evaluation.py`
- `scripts/retrieval-eval-smoke.ps1`
- `sample-data/eval/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-17-retrieval-trace-ui/17-03-eval-result-report-summary.md`

## Acceptance Criteria

- [x] Eval summary 包含 strategy、case count、Hit Rate@K、MRR@K、Recall@K、latency 與 failure count。
- [x] Optional branch fallback / unavailable 狀態可在 summary 中被辨識。
- [x] Baseline keyword eval smoke 在無 Ollama embedding、Qdrant 或 FastEmbed runtime 時仍可執行。
- [x] Optional vector / `vector_rerank` / `hybrid` summary 只在 explicit flag 與 preflight 可用時執行。
- [x] 既有 Phase 13-16 eval metrics contract 不被破壞。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional vector / vector_rerank / hybrid eval smoke commands must be run when local preflight is available.
- `git diff --check`

## Release Impact

- Target version: `v0.17.0`。
- Version bump required: no。
- 原因：本 ticket 只改善 eval reporting visibility，尚未完成整個 Phase 17 release sync；版本同步留到 Phase 17 release ticket。
