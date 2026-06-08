# DocuRAG K8s Baseline

This folder contains Phase 39 baseline manifests for local review and dry-run validation. They are deployment artifacts, not a production operations package.

## Files

- `docurag-baseline.yaml`: Namespace, ConfigMap, Secret template, API, frontend, worker placeholder, Qdrant, Redis and NATS baseline manifests.
- `hpa-optional.yaml`: optional HPA example for API scaling shape only.

## Local Validation

Offline YAML shape check:

```powershell
python -c "import yaml, pathlib; files=[pathlib.Path('infra/k8s/docurag-baseline.yaml'), pathlib.Path('infra/k8s/hpa-optional.yaml')]; docs=[]; [docs.extend([doc for doc in yaml.safe_load_all(path.read_text(encoding='utf-8')) if doc]) for path in files]; assert all(doc.get('apiVersion') and doc.get('kind') and doc.get('metadata', {}).get('name') for doc in docs); print(f'parsed {len(docs)} Kubernetes YAML documents')"
```

With an available Kubernetes context:

```powershell
kubectl apply --dry-run=client --validate=false -f .\infra\k8s
```

Use `--validate=false` so the manifest shape can be checked without requiring a live cluster OpenAPI schema. Some newer `kubectl` versions still perform API discovery even for client dry-run; if no cluster context is available, the offline YAML check above is the local fallback. A real cluster validation should use the cluster's policy and admission controls.

## Rollout

This baseline expects immutable image tags in real use. Replace the sample `0.38.0` image tags during release sync or deployment packaging.

```powershell
kubectl apply -f .\infra\k8s\docurag-baseline.yaml
kubectl -n docurag rollout status deployment/docurag-api
kubectl -n docurag rollout status deployment/docurag-frontend
kubectl -n docurag rollout status deployment/docurag-worker
```

Config changes should update a pod-template annotation such as `docurag.io/config-checksum` so a rollout is triggered intentionally. Readiness probes are the rollout gate for API and frontend examples.

## Rollback

```powershell
kubectl -n docurag rollout history deployment/docurag-api
kubectl -n docurag rollout undo deployment/docurag-api
```

Failed rollout triage should start with:

```powershell
kubectl -n docurag describe deployment/docurag-api
kubectl -n docurag get pods
kubectl -n docurag logs deployment/docurag-api
```

## Boundary

- Secret values are placeholders only. Do not commit production secrets, API keys or database URLs.
- `emptyDir` volumes are demo-safe and not durable storage.
- The worker deployment is a placeholder because the current worker skeleton is smoke-oriented, not a production worker loop. It has no Service because it does not expose inbound traffic.
- The HPA manifest is optional and not backed by large-scale load testing.
- This folder does not include Ingress, TLS automation, Helm, GitOps, service mesh, production database deployment or enterprise secret manager integration.
