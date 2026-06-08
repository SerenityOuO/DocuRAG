# Phase 40 Embedding / SFT Experiment Evidence

This report turns the Phase 39 research artifacts into interview-ready evidence. It is research-only: no model is trained, no large model is downloaded and no fine-tuned model is connected to the DocuRAG production runtime.

## Artifact Map

| Evidence need | Local artifact | Notes |
|---|---|---|
| Dataset card | `fine-tuning/dataset-card.md` | Documents intended use, labeling rules, metrics and risk notes. |
| Notebook skeleton | `fine-tuning/notebook-skeleton.md` | Re-runnable checklist without Jupyter or training dependency. |
| SFT JSONL | `sample-data/fine-tuning/sft-schema-extraction-sample.jsonl` | Schema extraction samples for invoice, contract and report. |
| Embedding positive / negative JSONL | `sample-data/fine-tuning/embedding-positive-negative-pairs.jsonl` | Query, positive evidence and negative evidence pairs. |
| Reranker pairwise JSONL | `sample-data/fine-tuning/reranker-pairwise-sample.jsonl` | Chosen / rejected candidate pairs with preference reasons. |
| Before / after eval table | `sample-data/fine-tuning/phase40-before-after-eval.csv` | Tiny experiment template with sample count, skip reason and metric columns. |

## Synthetic Data Coverage

The current demo-safe synthetic data covers three document families. Each family has at least two evidence samples when SFT, embedding tuning and reranker tuning artifacts are counted together.

| Document type | SFT samples | Embedding pairs | Reranker pairs | Evidence summary |
|---|---:|---:|---:|---|
| invoice | 1 | 1 | 1 | Invoice id, vendor, buyer, dates, amount, tax and line item evidence. |
| contract | 1 | 1 | 1 | Parties, effective date, term, renewal, termination notice, governing law and scope evidence. |
| report | 1 | 1 | 1 | KPI, parser field accuracy, risk and action evidence. |

## Data Format Evidence

SFT schema extraction uses one JSONL object per sample with `instruction`, `input`, normalized JSON `output`, `split` and `research_only=true`. The target output is compatible with parser field accuracy checks because it preserves structured field names and normalized values.

Embedding tuning uses `query`, `positive` and `negative` text. Positive evidence must answer the query; negative evidence should be plausible but materially less relevant. This keeps Hit Rate@K, MRR@K and Recall@K tied to retrieval quality instead of memorized labels.

Reranker tuning uses `query`, `chosen`, `rejected`, `preference` and `reason`. The pairwise format can be evaluated by checking whether the chosen candidate ranks ahead of the rejected candidate in a future local reranker experiment.

## Before / After Evaluation

This ticket does not run training. The table below is intentionally a tiny before / after template that can be updated after an explicit local experiment.

| stage | track | dataset_version | sample_count | Hit Rate@K | MRR@K | Recall@K | parser field accuracy | skip reason |
|---|---|---|---:|---|---|---|---|---|
| before_current_runtime | sft_schema_extraction | phase39-research-v1 | 3 | not_applicable | not_applicable | not_applicable | not_run | training_not_run_research_only |
| after_candidate_sft | sft_schema_extraction | phase40-evidence-template | 3 | not_applicable | not_applicable | not_applicable | pending | training_not_run_research_only |
| before_current_runtime | embedding_tuning | phase39-research-v1 | 3 | not_run | not_run | not_run | not_applicable | embedding_runtime_not_run |
| after_candidate_embedding | embedding_tuning | phase40-evidence-template | 3 | pending | pending | pending | not_applicable | training_not_run_research_only |
| before_current_runtime | reranker_tuning | phase39-research-v1 | 3 | not_run | not_run | not_run | not_applicable | reranker_runtime_not_run |
| after_candidate_reranker | reranker_tuning | phase40-evidence-template | 3 | pending | pending | pending | not_applicable | training_not_run_research_only |

## RAG Eval Linkage

- Hit Rate@K answers whether a query finds any expected evidence chunk in the top K results.
- MRR@K answers how early the first relevant evidence appears.
- Recall@K answers how much expected evidence is covered by retrieved candidates.
- parser field accuracy answers whether schema extraction returns exact or normalized field values.
- skip reason keeps the report honest when embedding tuning, reranker tuning or SFT training is not executed.

These metrics map back to DocuRAG's existing retrieval eval and parser evidence: retrieval quality uses Hit Rate, MRR and Recall; schema extraction quality uses parser field accuracy.

## Risk Notes

| Risk | Why it matters | Required control |
|---|---|---|
| privacy | Production documents, logs or credentials must never enter synthetic data. | Use fictional data only; reject secrets, bearer tokens, API keys, account ids and production database URLs. |
| label leakage | Queries that reveal the expected answer can inflate retrieval scores. | Keep answer-bearing text in positive evidence, not in query text, unless explicitly tagged as a leakage test. |
| overfit | Tiny templates can make metrics look better than real documents. | Split train / validation / holdout by template family and report repeated vendor, amount or clause patterns. |
| runtime drift | A research artifact can be mistaken for a production capability. | Keep this report research-only and disconnected from OCR, parser, RAG, Agent, embedding and reranker runtime defaults. |

## Validation

```powershell
rg -n "SFT|synthetic data|embedding tuning|reranker tuning|positive|negative|JSONL|research-only|field accuracy|Hit Rate|MRR|Recall|skip reason|overfit|privacy" docs fine-tuning sample-data README_DEV.md TODO.md tasks/phase-40-interview-evidence-hardening
git diff --check
```
