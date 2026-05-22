# 14-04 Phase 14 Demo and Release Plan

## Goal

規劃 Phase 14 / `v0.14.0` 的 demo、validation 與 release 文件同步方式，確保後續若實作 rerank / hybrid search 時能用 Phase 13 eval baseline 做可重跑比較。此 ticket 只做計畫，不執行 release sync。

## Scope

- 規劃 future rerank / hybrid demo smoke 的 preflight 順序與 expected output。
- 定義 future validation checklist，包含 backend tests、frontend build、baseline eval、optional strategy eval 與 `git diff --check`。
- 規劃 release sync checklist，列出若未來完成 v0.14.0 runtime release 時需要同步的檔案。
- 明確記錄 Phase 14 planning 完成後，真正 runtime implementation 需另開後續 ticket。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 14 release planning 狀態。

## Out of Scope

- 不修改 backend version、frontend package version、frontend fallback version、health test 或 Docker Compose `DOCURAG_VERSION`。
- 不新增或修改 demo smoke script。
- 不新增 rerank、hybrid search、eval runner capability、API endpoint 或 frontend UI。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不 push tag 或建立 release note。

## Release Impact

- Target version: `v0.14.0`。
- Version bump required: no。
- 原因：本 ticket 只規劃 future demo / release checklist，不完成 runtime release；實際版本同步需等 future implementation ticket 明確要求。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md`

## Demo and Release Plan

### Future demo smoke preflight

後續若另開 implementation ticket 實作 rerank / hybrid search，demo smoke 應先確認以下 preflight。此處只規劃順序，不修改 script：

1. 確認 backend tests 通過，且 keyword baseline 不需要外部 runtime。
2. 確認 baseline `scripts/demo-smoke-test.ps1` 仍能輸出 `deterministic baseline` 與 `keyword baseline`。
3. 確認 baseline `scripts/retrieval-eval-smoke.ps1` 可輸出 keyword Hit Rate@K、MRR@K、Recall@K、latency 與 failure count。
4. 若 future strategy 需要 vector branch，先完成 Qdrant collection preflight 與 manual vector indexing preflight。
5. 若 future strategy 需要 reranker，先檢查 reranker provider / model availability，且確認 disabled-by-default 設定未破壞 baseline。
6. 執行 optional strategy eval，例如 future `vector_rerank`、`hybrid` 或 `hybrid_rerank`，並輸出 strategy label、metrics、latency 與 fallback reason。
7. 對照 Phase 13 baseline metrics，記錄是否改善 Hit Rate@K、MRR@K、Recall@K，或是否造成 latency / failure count regression。

Expected output 應至少包含：

- `strategy_label`
- Hit Rate@K / MRR@K / Recall@K / average latency / failure count
- rerank 或 hybrid trace metadata 是否存在
- fallback reason 是否可讀
- keyword baseline 是否仍可單獨執行

### Future validation checklist

Future runtime implementation ticket 若完成 rerank / hybrid search，至少應執行：

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`（於 `frontend/`）
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional strategy eval smoke，需明確列出 env、external runtime preflight 與 fallback 行為。
- `git diff --check`

若 implementation 未修改 frontend，可在 ticket 中說明不跑 frontend build 的理由；若修改 demo script，必須補充 script-level smoke validation。

### Future release sync checklist

若後續 ticket 明確完成 `v0.14.0` runtime release，才需要同步以下檔案；本 ticket 不執行：

- backend version
- frontend `package.json` / `package-lock.json` version
- frontend fallback version
- health test expected version
- Docker Compose `DOCURAG_VERSION`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

Release Status 只能列版本號；Phase 細節仍放在 `docs/ROADMAP.md`。除非 ticket 或使用者明確要求 tag，否則不得 push tag 或建立 release note。

### Future implementation boundary

Phase 14 planning 完成後，不代表可以直接實作 rerank / hybrid runtime。後續至少應另開 ticket 分別處理：

- Rerank provider / model client implementation。
- Hybrid merge policy / dedupe rule implementation。
- Eval dataset JSON expansion。
- Demo smoke script support for optional strategies。
- Frontend trace presentation（若需要）。

每張 future ticket 仍必須明確 Scope、Out of Scope、Validation 與 Release Impact，並保留 keyword baseline fallback。

## Acceptance Criteria

- [x] Future demo smoke preflight 順序已記錄。
- [x] Future validation checklist 已記錄。
- [x] Future release sync checklist 已記錄。
- [x] 明確標示此 ticket 不執行 version bump 或 release sync。
- [x] 明確標示 runtime implementation 需另開後續 ticket。

## Validation

- `rg -n "v0.14.0|demo smoke|release sync|Version bump required: no|future implementation" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md`
- `git diff --check`
