# 18-03 Hybrid Rerank Trace Report Plan

## Goal

規劃 future `hybrid_rerank` trace / report visibility，讓後續 implementation 能在 CLI summary、JSON output 與既有 frontend trace panel 中清楚呈現 branch merge 與 rerank 結果，但本 ticket 不修改 UI 或程式碼。

## Scope

- 定義 future report fields：strategy label、branch counts、hybrid merge policy、rerank provider、rerank status、rerank score、fallback reason 與 candidate ordering。
- 規劃 frontend trace panel 後續只讀既有 response / result metadata 的顯示邊界，不新增 live eval dashboard。
- 說明 missing metadata 行為應沿用 Phase 17：graceful hidden、`metadata unavailable` 或清楚 fallback state。
- 只更新 Markdown 規劃文件與 checklist。

## Out of Scope

- 不修改 `frontend/src/App.vue`、CSS、backend eval runner、API response 或 smoke script。
- 不建立 production eval dashboard、strategy comparison page、export UI 或 live eval runner。
- 不實作 `hybrid_rerank`、BM25、LLM-as-judge、answer faithfulness 或 citation quality scoring。
- 不新增外部依賴、Redis、NATS、worker、DB、auth、RBAC 或 deployment 設定。

## Release Impact

- Target version: `v0.18.0` planning backlog。
- Version bump required: no。
- 原因：本 ticket 只規劃 trace / report display contract，不修改 frontend、backend 或 release artifact。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-18-hybrid-rerank-planning/18-03-hybrid-rerank-trace-report-plan.md`

## Acceptance Criteria

- [ ] 已列出 future `hybrid_rerank` trace / report 欄位。
- [ ] 已明確禁止 production eval dashboard 與 live eval runner。
- [ ] 已定義 missing metadata / fallback display 原則。
- [ ] Release Impact 明確寫 `Version bump required: no` 並說明原因。

## Validation

- `rg -n "v0.18.0|Phase 18|hybrid_rerank|trace|report|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md`
- `git diff --check`
