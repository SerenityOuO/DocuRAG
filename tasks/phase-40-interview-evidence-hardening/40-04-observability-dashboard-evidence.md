# Observability Dashboard Evidence

## Goal

建立 observability dashboard / query examples / screenshots 的面試證據，讓 Phase 39 的 Loki / Grafana 或 OpenSearch path 不只停留在架構文字。

## Scope

- 新增 observability evidence docs，包含 API log、worker log、RAG trace、retrieval latency、rerank latency、generation latency、eval metrics 的 dashboard / query examples。
- 若有 local dashboard，可保存 demo-safe screenshot 或 query result 範例。
- 補充 fallback / unavailable behavior，讓 observability stack 沒啟動時 app 仍可運作。
- 將 evidence 對齊 JD 中 ELK / Loki / logging system 與 ops monitoring 能力。

## Out of Scope

- 不新增 production alerting、SLO、incident workflow、distributed tracing 或 APM vendor integration。
- 不要求啟動完整 ELK / Loki stack 才能通過 baseline demo。
- 不修改 RAG ranking、Agent planner、OCR / parser behavior 或 worker runtime。
- 不新增大量 binary media；若需要截圖，使用 demo-safe 小檔並更新 README_DEV 說明。

## Release Impact

- Target version: `v0.40.0`
- Version bump required: no
- 原因：這是 Phase 40 evidence artifact ticket，版本同步留到 `40-05`。

## Files likely to change

- `docs/`
- `infra/`
- `outputs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-40-interview-evidence-hardening/40-04-observability-dashboard-evidence.md`

## Acceptance Criteria

- [ ] 有一份 observability evidence docs，包含 dashboard / query examples。
- [ ] Evidence 覆蓋 API log、worker log、RAG trace、latency 與 eval metrics。
- [ ] 若有截圖或 query result，必須是 demo-safe 且可在 README_DEV 找到說明。
- [ ] 文件明確標示這是 observability evidence，不是 production alerting stack。
- [ ] App 在 observability stack unavailable 時仍有 fallback / skip 說明。

## Validation

- `rg -n "observability evidence|Loki|Grafana|OpenSearch|dashboard|query example|RAG trace|eval metrics|latency" docs infra outputs README_DEV.md TODO.md tasks/phase-40-interview-evidence-hardening`
- `git diff --check`
