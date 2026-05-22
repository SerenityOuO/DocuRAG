# 20-01 Interview Demo Doc Refresh

## Goal

更新面試 demo 文件，讓 README、demo script、PRD 與 architecture 文件清楚反映目前已完成的 `v0.17.0` runtime、`v0.18.0` planning、`v0.19.0` `hybrid_rerank` implementation 狀態，以及 Phase 20 的面試 MVP 收斂方向。

## Scope

- 更新 `docs/demo-script.md`，移除已過期的 deferred items，改成 5 到 10 分鐘可講的 demo flow。
- 更新 `README.md` 的 Development Direction，說明 Phase 18 是 planning-only、Phase 19 是 `hybrid_rerank` implementation backlog、Phase 20 是 interview MVP packaging backlog。
- 視需要小幅更新 `docs/PRD.md` 與 `docs/architecture.md`，避免仍把已完成的 OCR / vector / rerank / eval 能力描述成未來項目。
- 保留目前受控 MVP 的 single-user / local-demo 邊界，不把文件寫成 production-ready 平台。

## Out of Scope

- 不修改 backend、frontend、sample data、eval dataset、smoke script 或 Docker Compose。
- 不實作 `hybrid_rerank` runtime、Agent、Auth、RBAC、PostgreSQL、Redis、NATS、worker、K8s 或 deployment。
- 不新增截圖、GIF 或媒體 assets；這些留給 `19-03`。
- 不 bump backend / frontend / Docker Compose version。

## Release Impact

- Target version: `v0.20.0` interview MVP packaging backlog。
- Version bump required: no。
- 原因：本 ticket 只同步文件敘事，不形成完整 release artifact；`v0.20.0` version sync 留到 `20-04`。

## Files likely to change

- `README.md`
- `docs/demo-script.md`
- `docs/PRD.md`
- `docs/architecture.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Demo script 能在 5 到 10 分鐘內講清楚目前已完成的 upload -> OCR -> RAG -> citation -> trace -> eval flow。
- [ ] 文件明確標示 Phase 18 是 `hybrid_rerank` planning-only，Phase 19 才是 `hybrid_rerank` runtime implementation。
- [ ] 文件不再把已完成的 optional OCR / vector / rerank / hybrid eval 全部列為 deferred。
- [ ] 仍明確說明 Auth、DB、Redis、NATS、worker、production eval dashboard 與 deployment 不在目前 MVP 內。

## Validation

- `rg -n "v0.17.0|v0.18.0|v0.19.0|Phase 20|interview MVP|面試" README.md docs/demo-script.md docs/PRD.md docs/architecture.md TODO.md docs/ROADMAP.md`
- `git diff --check`
