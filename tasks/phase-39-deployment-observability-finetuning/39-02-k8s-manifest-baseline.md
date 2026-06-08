# K8s Manifest Baseline

## Goal

新增 basic K8s manifests，展示 DocuRAG 的 deployment boundary、health probes 與 resource request examples。

## Scope

- 新增 API、frontend、worker、Qdrant、Redis、NATS 等 basic manifest 或 template。
- 新增 ConfigMap / Secret template，不提交真實 secret。
- 加入 readiness / liveness probe 與 resource request examples。
- 補文件說明如何 dry-run / validate manifests。
- Manifest 至少包含 backend API、frontend、worker skeleton、Qdrant、Redis、NATS 的 Deployment / Service 或清楚註明 deferred reason。
- 補充 rollout / rollback 基本說明，包含 image tag、config checksum、readiness gate 與 failed rollout 排查方式。
- 可選提供 HPA example，但必須標示為 optional scaling template，不宣稱已壓測大規模流量。

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

- [x] K8s manifests 包含 API / frontend / worker / supporting services 的 baseline。
- [x] ConfigMap / Secret template 不包含真實 secret。
- [x] Readiness / liveness probes 與 resource requests 有文件說明。
- [x] Backend / frontend / worker manifests 有 image tag、env config、readinessProbe、livenessProbe、resources requests / limits。
- [x] 文件說明 local validation、dry-run、rollout / rollback 與 optional HPA boundary。
- [x] Validation 至少包含 manifest lint / dry-run 指令或替代檢查。

## Validation

- K8s manifest dry-run / lint command。
- `rg -n "apiVersion|kind: Deployment|ConfigMap|Secret|readinessProbe|livenessProbe|resources|requests|limits|rollout|rollback|HPA|HorizontalPodAutoscaler" infra docs README_DEV.md TODO.md tasks/phase-39-deployment-observability-finetuning`
- `git diff --check`

## Status

- Completed. Added `infra/k8s/docurag-baseline.yaml` for namespace, ConfigMap, Secret template, API, frontend, worker placeholder, Qdrant, Redis and NATS baseline manifests.
- Added `infra/k8s/hpa-optional.yaml` as optional API HPA shape only; it does not claim production autoscaling or load-test coverage.
- Added `infra/k8s/README.md` with local lint, cluster dry-run, rollout / rollback, config checksum, readiness gate, failed rollout triage and boundary notes.
- Worker manifest has a deferred reason and no Service because the current worker skeleton does not expose inbound traffic.
- Release Impact: Version bump required: no. Sample image tags remain `0.38.0`; Phase 39 version sync remains deferred to `39-05`.

## Validation Result

- Passed: offline YAML lint parsed 15 Kubernetes YAML documents and confirmed each document has `apiVersion`, `kind` and `metadata.name`.
- Attempted: `kubectl apply --dry-run=client --validate=false -f .\infra\k8s`; local kubectl v1.34.1 failed before manifest validation because no Kubernetes API context was available and API discovery attempted `localhost:8080`.
- Passed: ticket `rg`.
- Passed: `git diff --check` and `git diff --cached --check`.
