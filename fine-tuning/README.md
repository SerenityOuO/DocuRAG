# Fine-tuning Research Artifacts

This folder is a research-only Phase 39 artifact pack. It defines how DocuRAG could evaluate SFT, synthetic data, embedding tuning and reranker tuning later, without running training, downloading large models or connecting any fine-tuned model to production runtime.

## Scope

| Track | Purpose | Artifact |
|---|---|---|
| SFT schema extraction | Teach a future model to return structured invoice, contract and report fields. | `sample-data/fine-tuning/sft-schema-extraction-sample.jsonl` |
| embedding tuning | Prepare query/document positive and negative pairs for retrieval tuning. | `sample-data/fine-tuning/embedding-positive-negative-pairs.jsonl` |
| reranker tuning | Prepare pairwise chosen/rejected examples for reranker tuning. | `sample-data/fine-tuning/reranker-pairwise-sample.jsonl` |
| Evaluation | Track retrieval and parser outcomes without running model training. | `sample-data/fine-tuning/evaluation-template.csv` |

## Synthetic Data Plan

The first research dataset stays small and synthetic. It should cover:

| Document type | Example target fields | Notes |
|---|---|---|
| Invoice | invoice id, vendor, buyer, due date, currency, subtotal, tax, total, line items. | Use public fictional vendors and values only. |
| Contract | parties, effective date, term, renewal, termination notice, governing law, service scope. | Keep clauses short and avoid copying real contracts. |
| Report | report id, period, owner, KPI values, risks, actions, status. | Use synthetic operational summaries, not real business reports. |

Future expansion should split train / validation / holdout by document id and template family. Do not let the same generated document appear in both training and evaluation.

## Data Formats

SFT JSONL uses one JSON object per line:

```json
{"sample_id":"sft-invoice-001","document_type":"invoice","instruction":"Extract schema fields as JSON.","input":"Synthetic document text...","output":{"invoice_id":"AUR-2026-051"},"split":"train","research_only":true}
```

Embedding tuning JSONL uses explicit positive and negative evidence:

```json
{"pair_id":"emb-invoice-001","query":"When is Aurora invoice due?","positive":"Payment terms: Net 15. Due date: 2026-06-30.","negative":"The contract renews monthly.","label":"positive_negative_pair","research_only":true}
```

Reranker tuning JSONL uses pairwise chosen / rejected candidates:

```json
{"pair_id":"rerank-invoice-001","query":"Aurora invoice total","chosen":"Total: 1248.50 USD.","rejected":"Termination notice: 30 days.","preference":"chosen_is_more_relevant","research_only":true}
```

## Evaluation Template

Every experiment report should include:

| Column | Meaning |
|---|---|
| `track` | `sft`, `embedding`, `reranker` or `combined`. |
| `dataset_version` | Dataset card version, for example `phase39-research-v1`. |
| `sample_count` | Number of examples used in the local run. |
| `Hit Rate@K` | Retrieval hit rate for query/evidence tasks. |
| `MRR@K` | Mean reciprocal rank for retrieval tasks. |
| `Recall@K` | Expected evidence recall for retrieval tasks. |
| `parser_field_accuracy` | Exact or normalized field accuracy for schema extraction. |
| `skip_reason` | Required when training or evaluation is not run. |

## Guardrails

- research-only: these artifacts do not change OCR, parser, RAG, Agent, Auth / RBAC, embedding, reranker or inference runtime.
- privacy: do not add real customer documents, production logs, bearer tokens, API keys, account identifiers or paid-service credentials.
- leakage: expected answers must not be embedded in query text unless the case is explicitly tagged as a leakage test.
- overfit: keep holdout templates separate from train templates and report repeated vendor / amount patterns.
- cost: validation must not download large models, run long training jobs or require external accounts.

## Validation

```powershell
rg -n "SFT|synthetic data|embedding tuning|reranker tuning|positive|negative|JSONL|research-only|fine-tuning|field accuracy|Hit Rate|MRR|Recall|privacy|leakage|overfit" docs fine-tuning sample-data README_DEV.md TODO.md tasks/phase-39-deployment-observability-finetuning
git diff --check
```
