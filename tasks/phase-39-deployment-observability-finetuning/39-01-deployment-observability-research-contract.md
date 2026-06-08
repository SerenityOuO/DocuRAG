# Deployment Observability Research Contract

## Goal

定義 Phase 39 deployment / observability / fine-tuning track 的邊界，將 LLMOps / MLOps 加分能力拆成可驗證但不誇大 production 的項目。

## Scope

- 定義 K8s baseline scope：Deployment、Service、ConfigMap / Secret template、health probes、resource requests。
- 定義 observability scope：API log、worker log、RAG trace、eval metrics，並選定 Loki / Grafana 或 OpenSearch path。
- 定義 fine-tuning / synthetic data / embedding tuning 的 research-only scope。
- 更新 docs、TODO、ROADMAP 與 README_DEV。

## Out of Scope

- 不新增 K8s manifests、observability runtime 或 notebook。
- 不宣稱 production autoscaling、multi-cluster deployment、enterprise SSO 或 production training pipeline。
- 不修改 backend / frontend runtime。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 39 contract ticket，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-39-deployment-observability-finetuning/39-01-deployment-observability-research-contract.md`

## Acceptance Criteria

- [x] 文件定義 K8s、observability 與 research track 的 scope。
- [x] 明確標示 production autoscaling 與 production training pipeline 不在 scope。
- [x] Fine-tuning / synthetic data 只作 research track，不影響 main runtime。
- [x] 文件列出 Phase 39 ticket 執行順序。

## Status

- Completed Phase 39 Markdown-only contract in `docs/architecture.md`, `docs/ROADMAP.md`, `README_DEV.md` and `TODO.md`.
- Selected Loki + Grafana as the default observability path; OpenSearch remains an alternative path, not the default for this Phase.
- Defined K8s baseline scope as Deployment, Service, ConfigMap / Secret template, health probes and resource request examples only.
- Defined fine-tuning / synthetic data / embedding tuning as research-only artifacts that do not change main runtime defaults.
- Release boundary remains explicit: no K8s manifests, observability runtime, notebook, dependency, production autoscaling, multi-cluster deployment or production training pipeline.

## Validation

- Passed: `rg -n "K8s|observability|Loki|Grafana|OpenSearch|fine-tuning|synthetic data|Phase 39" docs README_DEV.md TODO.md tasks/phase-39-deployment-observability-finetuning`
- Passed: `git diff --check`（僅 Windows LF/CRLF 提示）。
