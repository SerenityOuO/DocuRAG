# 17-01 Retrieval Trace UI Contract

## Goal

固定 Phase 17 retrieval trace UI / eval visibility 的顯示 contract，讓後續 frontend 與 report work 可以一致呈現 keyword、vector、`vector_rerank` 與 `hybrid` metadata。此 ticket 是文件 ticket，只做 Markdown planning，不改 runtime。

## Scope

- 定義 frontend trace panel 應顯示的 retrieval strategy label、answer source、retrieval source、candidate count、latency 與 fallback state。
- 定義 candidate-level 顯示欄位，例如 rank、score、document id、chunk id、filename、source text preview 與 branch metadata。
- 規劃 `vector_rerank` metadata 顯示方式，包含 rerank provider、rerank status、rerank score 與 fallback reason。
- 規劃 `hybrid` metadata 顯示方式，包含 branch candidates、merge policy、dedupe count、branches、merged score 與 branch failures。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 17 planning 說明。

## Trace UI Contract

Phase 17 trace UI 只負責讀取既有 `/rag/query` response 與 retrieval eval output 中已存在的欄位，並把 metadata 轉成可閱讀的 frontend panel / eval summary。此 contract 不新增 response schema，也不要求 backend 為 UI 補欄位。

Run-level display：

- Strategy label：優先顯示 metadata 中的 `strategy_label`；缺少時依既有 `retrieval_source` / `answer_source` 推定為 `keyword` 或顯示 `unknown`。
- Answer source：顯示 deterministic baseline、LLM provider fallback 或其他既有 answer source label；缺少時顯示為未提供。
- Retrieval source：顯示 keyword baseline、vector、`vector_rerank`、`hybrid` 或 fallback source；不可讓 UI 暗示 optional strategy 已 default-on。
- Candidate count：顯示 retrieved chunks / candidates 數量；若 summary 有 branch count，另顯示 keyword、vector 與 merged candidate count。
- Latency：只顯示既有 `latency_ms`、rerank latency 或 eval summary latency；缺少時隱藏，不自行估算。
- Fallback state：顯示 provider unavailable、reranker disabled、vector branch failed、missing metadata 或 keyword-only fallback 等既有 reason。

Candidate-level display：

- 基本欄位：rank、score、document id、chunk id、filename 與 source text preview。
- Metadata 欄位：page number、bbox、confidence、provider metadata 與 trace metadata 可用時顯示；缺少時不讓 UI error。
- Branch metadata：若 candidate 來自 hybrid path，顯示 `branches`、keyword rank / score、vector rank / score、merged rank / score 與 dedupe key fallback。
- Text preview：優先使用 chunk text / citation text；長文字由 frontend 做 compact preview，不在 contract 要求新增 backend 欄位。

`vector_rerank` display：

- Run-level：顯示 rerank provider、model、status、input candidate count、rerank top K、rerank latency 與 fallback reason。
- Candidate-level：顯示 original rank、reranked rank、原始 retrieval score、rerank score 與 rerank fallback metadata。
- 若 reranker disabled / unavailable / timeout / malformed，保留原 candidates 顯示，並用 fallback state 標示，不把結果視為 UI failure。

`hybrid` display：

- Run-level：顯示 merge policy、dedupe key、keyword candidate count、vector candidate count、merged candidate count、deduped candidate count、branch failures 與 fallback reason。
- Candidate-level：顯示 final rank、merged score、branches、keyword rank / score、vector rank / score、dedupe key 與 dedupe key fallback。
- Vector branch unavailable 時顯示 keyword-only fallback；keyword baseline 不因 optional branch 失敗而被標示為整體失敗。

Missing metadata behavior：

- 既有 keyword baseline response 若沒有 strategy metadata，trace panel 應保持可讀，至少顯示 answer source、retrieval source、candidate count 與 retrieved chunk basic fields。
- 缺少 optional metadata 時採 graceful hidden 或明確顯示 `metadata unavailable`，不得 throw UI error 或顯示誤導性的成功狀態。
- UI 不自行推導 rerank score、merged score 或 branch failure；只呈現 response / eval output 已提供的值。

## Out of Scope

- 不修改 `backend/`、`frontend/`、`scripts/` 或 runtime code。
- 不新增 API endpoint、不改 `/rag/query` response schema、不接 eval runner 到 frontend。
- 不實作 production eval dashboard、LLM-as-judge、answer faithfulness、citation quality scoring 或 `hybrid_rerank`。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 deployment 設定。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md`

## Acceptance Criteria

- [x] Trace UI contract 已涵蓋 keyword、vector、`vector_rerank` 與 `hybrid` strategy。
- [x] Contract 已定義 run-level metadata、candidate-level metadata、fallback display 與 missing metadata 行為。
- [x] 明確標示此 ticket 不修改 runtime、不新增 API、不新增 frontend implementation。
- [x] `TODO.md` 與 `docs/ROADMAP.md` 已同步 Phase 17 planning 邊界。

## Validation

- `rg -n "v0.17.0|Phase 17|trace UI|hybrid|vector_rerank" TODO.md docs/ROADMAP.md tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md`
- `git diff --check`

## Release Impact

- Target version: `v0.17.0`。
- Version bump required: no。
- 原因：本 ticket 只固定 Phase 17 trace UI contract，不新增 runtime，也不形成 release artifact；實際版本同步留到 Phase 17 release ticket。
