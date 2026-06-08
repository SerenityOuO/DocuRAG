# Dataset Card: Phase 39 Research Synthetic Data

## Summary

- Dataset name: `docurag-phase39-synthetic-research`
- Dataset version: `phase39-research-v1`
- Status: research-only
- Intended use: document understanding research for SFT, embedding tuning and reranker tuning.
- Not intended use: production training, model registry upload, paid-service fine-tuning or production inference routing.

## Composition

| Slice | Current sample artifact | Document types |
|---|---|---|
| SFT JSONL | `sample-data/fine-tuning/sft-schema-extraction-sample.jsonl` | invoice, contract, report |
| embedding tuning pairs | `sample-data/fine-tuning/embedding-positive-negative-pairs.jsonl` | invoice, contract, report |
| reranker tuning pairs | `sample-data/fine-tuning/reranker-pairwise-sample.jsonl` | invoice, contract, report |
| Evaluation template | `sample-data/fine-tuning/evaluation-template.csv` | SFT / retrieval / reranker reporting |

All current records are small fictional samples designed to document format and evaluation expectations. They are not a statistically meaningful training dataset.

## Labeling Rules

- SFT outputs should use normalized JSON fields and avoid prose-only answers.
- Positive evidence must contain enough information to answer the query.
- Negative evidence should be plausible but materially less relevant than the positive candidate.
- Reranker pairwise samples should explain why the chosen candidate is preferred.
- Each record must include `research_only=true` or equivalent metadata.

## Metrics

| Metric | Track | Notes |
|---|---|---|
| Hit Rate@K | embedding tuning, reranker tuning | Measures whether at least one expected evidence item appears in top K. |
| MRR@K | embedding tuning, reranker tuning | Measures rank of the first relevant candidate. |
| Recall@K | embedding tuning, reranker tuning | Measures coverage of expected evidence terms or chunks. |
| parser field accuracy | SFT schema extraction | Measures exact or normalized field match against expected fields. |
| sample count | all tracks | Required for every report. |
| skip reason | all tracks | Required when training, evaluation or model download is skipped. |

## Risk Notes

| Risk | Impact | Mitigation |
|---|---|---|
| privacy | Real customer data could leak into examples. | Use fictional documents only; reject secrets, account ids, production logs and raw customer files. |
| label leakage | The answer may appear in the query or metadata. | Keep answer-bearing text in evidence, not in query; tag deliberate leakage tests. |
| overfit | Small templates can make metrics look better than real performance. | Split by template family, add holdout vendors and report repeated patterns. |
| unrealistic samples | Synthetic data may miss real layout or OCR noise. | Add OCR-noise variants only as separate research cases and label their source. |

## Release Boundary

This dataset card does not create a production training pipeline. It does not add dependencies, model artifacts, scheduled jobs, registry uploads, deployment automation or runtime provider changes.
