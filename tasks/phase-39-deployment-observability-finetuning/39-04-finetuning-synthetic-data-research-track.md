# Fine Tuning Synthetic Data Research Track

## Goal

Define a research-only fine-tuning / synthetic data / embedding tuning track that produces demo-safe artifacts and evaluation templates without creating a production training pipeline.

## Scope

- Add a synthetic data generation plan covering invoice, contract and report schema extraction use cases.
- Add SFT, embedding tuning and reranker tuning notebook / docs skeletons that explain expected data formats.
- Add research artifacts: dataset card, SFT JSONL sample, embedding positive / negative pairs, reranker pairwise samples, evaluation table and risk notes.
- Ensure the evaluation table includes Hit Rate@K, MRR@K, Recall@K, parser field accuracy, sample count, data source and skip reason.
- Document synthetic data privacy, label leakage and overfit risks with mitigation notes.
- Mark the whole track as research-only and explicitly not connected to production runtime.
- Update README_DEV, ROADMAP and TODO.

## Out of Scope

- Do not run long training jobs, download large models or add GPU training dependencies.
- Do not connect any fine-tuned model to production inference paths.
- Do not add dataset privacy workflow automation, model registry, deployment automation, new backend runtime, frontend runtime, worker, K8s service, external account, API key or paid-service credential.
- Do not change OCR, parser, RAG, Agent, Auth / RBAC, inference provider, embedding or reranker runtime behavior.

## Release Impact

- Target version: `v0.39.0`
- Version bump required: no
- Reason: this is a Phase 39 research artifact ticket; version sync remains deferred to `39-05`.

## Files likely to change

- `docs/`
- `fine-tuning/`
- `sample-data/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-39-deployment-observability-finetuning/39-04-finetuning-synthetic-data-research-track.md`

## Acceptance Criteria

- [x] Synthetic data plan covers invoice, contract and report examples.
- [x] Notebook / docs skeleton explains SFT, embedding tuning and reranker tuning data formats.
- [x] Artifact includes dataset card, SFT JSONL, embedding positive / negative pairs and reranker pairwise samples.
- [x] Evaluation table includes Hit Rate@K, MRR@K, Recall@K, parser field accuracy, sample count and skip reason.
- [x] Documentation explains synthetic data privacy, label leakage, overfit and mitigation.
- [x] Documentation clearly marks the track as research-only and not connected to production runtime.
- [x] Validation does not require downloading large models or running training.

## Validation

- `rg -n "SFT|synthetic data|embedding tuning|reranker tuning|positive|negative|JSONL|research-only|fine-tuning|field accuracy|Hit Rate|MRR|Recall|privacy|leakage|overfit" docs fine-tuning sample-data README_DEV.md TODO.md tasks/phase-39-deployment-observability-finetuning`
- `git diff --check`

## Status

- Completed. Added a research-only `fine-tuning/` artifact pack with dataset card, notebook skeleton and local evaluation template.
- Added sample SFT JSONL, embedding positive / negative pairs and reranker pairwise JSONL under `sample-data/fine-tuning/`.
- Documented privacy, label leakage and overfit risks, plus skip reasons for runs that are not executed locally.
- Release Impact: Version bump required: no. Version sync remains deferred to `39-05`.

## Validation Result

- Passed: ticket `rg`.
- Passed: JSONL parse sanity check.
- Passed: `git diff --check`.
