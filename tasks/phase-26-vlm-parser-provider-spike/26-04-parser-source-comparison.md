# 26-04 Parser Source Comparison

## Goal

讓 API / demo trace 能清楚比較 `deterministic_invoice` 與 `vlm_invoice` parser source，顯示 fallback reason、confidence 與欄位來源，讓 Phase 26 的 VLM provider spike 可被面試 demo 解釋。

## Scope

- 擴充 parser result / fields response 的 trace metadata，使 `parser_source`、`fallback_reason`、confidence summary 與 source input type 更清楚。
- 若 VLM 成功，API response 顯示 `vlm_invoice` source 與欄位層級 confidence / source text。
- 若 VLM fallback，API response 顯示 fallback chain，例如 `vlm_invoice -> deterministic_invoice` 與 failure reason。
- 在 backend tests 中覆蓋 VLM success trace、VLM fallback trace 與 deterministic-only trace。
- 必要時更新 `docs/api.md` 與 frontend README / demo wording，但不做新的 production dashboard。

## Out of Scope

- 不新增新的 parser schema；仍沿用 Phase 24 `DocumentFields` / `ParserResult`。
- 不新增 frontend route、production parser comparison dashboard、人工修正 workflow 或欄位版本紀錄。
- 不修改 VLM provider adapter 的核心呼叫邏輯；adapter runtime 留在 `26-03`。
- 不修改 Agent planner / tools；Agent 只讀保存後的 parser result。
- 不新增 DB、worker、Redis、NATS、Auth、RBAC、K8s 或 deployment 設定。

## Release Impact

- Target version: `v0.26.0`。
- Version bump required: no。
- 原因：本 ticket 完成 parser source visibility slice；完整 release sync 留給 `26-05`。

## Files likely to change

- `backend/app/schemas/`
- `backend/app/services/`
- `backend/tests/`
- `docs/api.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Parser response 可區分 `deterministic_invoice` 與 `vlm_invoice`。
- [ ] VLM fallback 時可看到明確 fallback chain / reason。
- [ ] Confidence summary 與 source metadata 可被 API / smoke script 檢查。
- [ ] 文件明確說明這是 demo visibility，不是 production parser evaluation dashboard。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "parser_source|vlm_invoice|deterministic_invoice|fallback_reason|fallback chain|confidence|source input" backend/app backend/tests docs/api.md frontend/README.md TODO.md docs/ROADMAP.md tasks/phase-26-vlm-parser-provider-spike/26-04-parser-source-comparison.md`
- `git diff --check`
