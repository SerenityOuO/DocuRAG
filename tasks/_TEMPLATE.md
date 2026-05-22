# Ticket Template

## Goal

說明這張 ticket 要完成的單一結果。

## Scope

- 條列本 ticket 允許修改或完成的內容。
- 保持小範圍，讓 Codex 一次可以完成。

## Out of Scope

- 條列本 ticket 明確不處理的內容。
- 若工作超出這裡，應停止並拆新 ticket。

## Release Impact

- Target version: `v0.x.0` 或 `none`。
- Version bump required: yes/no。
- 若需要 bump version，確認同步更新 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、TODO 與 ROADMAP。
- 若不需要 bump version，說明原因，避免 Phase 完成後版本號與文件狀態脫節。

## Files likely to change

- `path/to/file`

## Acceptance Criteria

- [ ] 可驗收條件 1。
- [ ] 可驗收條件 2。

## Validation

- 說明完成後要跑的檢查、測試或人工驗證。
