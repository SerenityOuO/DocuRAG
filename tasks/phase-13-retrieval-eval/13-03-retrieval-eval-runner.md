# 13-03 Retrieval Evaluation Runner

## Goal

新增本機 retrieval evaluation runner，讀取 Phase 13 eval dataset，執行既有 `/rag/query` 或 backend retrieval service，輸出 keyword / optional vector retrieval 的 per-query result 與 summary metrics。

## Scope

- 新增最小 eval runner service 或 script，優先重用既有 backend / smoke script pattern。
- Runner 可在 keyword baseline 下執行，不依賴 Ollama embedding 或 Qdrant。
- Optional vector mode 必須明確設定 env，並要求先完成 manual vector indexing 或由 runner 明確呼叫 manual indexing API。
- 計算 `Hit Rate@K`、`MRR@K`、`Recall@K`、平均 latency、failure count。
- 輸出可讀 summary 與 machine-readable JSON，例如 `data/eval/retrieval-eval-result.json` 或 stdout JSON。
- 單元測試覆蓋 metric calculation、missing expected evidence、empty retrieval、vector unavailable fallback。
- 更新 `TODO.md` 中對應 checklist。

## Out of Scope

- 不新增 rerank。
- 不新增 hybrid search。
- 不新增 LLM-as-judge 或 answer quality evaluation。
- 不新增 API endpoint 或 frontend UI。
- 不新增 Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不讓 eval runner 在 backend startup、upload、OCR 或 `/rag/query` 自動執行。

## Release Impact

- Target version: `v0.13.0`。
- Version bump required: no。
- 原因：此 ticket 新增 eval runner building block，但 Phase 13 release / version sync 留到 `13-04`。

## Files likely to change

- `backend/app/services/evaluation.py`
- `backend/tests/test_evaluation.py`
- `scripts/retrieval-eval-smoke.ps1`
- `sample-data/eval/retrieval-eval.json`
- `TODO.md`

## Acceptance Criteria

- [ ] Keyword baseline eval 可在無 Qdrant / embedding 時執行。
- [ ] Optional vector eval 可在明確 env 與 manual indexing 後執行。
- [ ] Summary metrics 包含 Hit Rate@K、MRR@K、Recall@K、latency 與 failure count。
- [ ] Metric calculation 有單元測試。
- [ ] 不改 upload、OCR、manual indexing 或 `/rag/query` 預設行為。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- baseline retrieval eval smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- optional vector retrieval eval smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVector`
- `git diff --check`
