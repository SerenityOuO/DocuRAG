# K8s Manifest Baseline

## Goal

新增 basic K8s manifests，展示 DocuRAG 的 deployment boundary、health probes 與 resource request examples。

## Scope

- 新增 API、frontend、worker、Qdrant、Redis、NATS 等 basic manifest 或 template。
- 新增 ConfigMap / Secret template，不提交真實 secret。
- 加入 readiness / liveness probe 與 resource request examples。
- 補文件說明如何 dry-run / validate manifests。

## Out of Scope

- 不新增 production autoscaling、Ingress TLS automation、multi-cluster、Helm chart 或 GitOps pipeline。
- 不新增 enterprise secret manager 或 production database deployment。
- 不修改 app runtime 或 Docker image behavior。

## Release Impact

- Target version: `v0.39.0`
- Version bump required: no
- 原因：這是 Phase 39 deployment artifact ticket，版本同步留到 `39-05`。

## Files likely to change

- `infra/k8s/`
- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-39-deployment-observability-finetuning/39-02-k8s-manifest-baseline.md`

## Acceptance Criteria

- [ ] K8s manifests 包含 API / frontend / worker / supporting services 的 baseline。
- [ ] ConfigMap / Secret template 不包含真實 secret。
- [ ] Readiness / liveness probes 與 resource requests 有文件說明。
- [ ] Validation 至少包含 manifest lint / dry-run 指令或替代檢查。

## Validation

- K8s manifest dry-run / lint command。
- `rg -n "apiVersion|kind: Deployment|ConfigMap|Secret|readinessProbe|livenessProbe|resources" infra docs README_DEV.md TODO.md tasks/phase-39-deployment-observability-finetuning`
- `git diff --check`
