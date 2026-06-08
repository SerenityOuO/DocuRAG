# Notebook Skeleton: SFT, Embedding and Reranker Research

This is a notebook-style checklist written as Markdown so it can be reviewed without installing Jupyter. It is research-only and intentionally contains no training command.

## 1. Load Local Artifacts

Inputs:

- `sample-data/fine-tuning/sft-schema-extraction-sample.jsonl`
- `sample-data/fine-tuning/embedding-positive-negative-pairs.jsonl`
- `sample-data/fine-tuning/reranker-pairwise-sample.jsonl`
- `sample-data/fine-tuning/evaluation-template.csv`

Checks:

- Every JSONL line parses as one object.
- Every object has a stable id, document type, source and `research_only=true`.
- No object contains bearer token, API key, production database URL or real customer identifier.

## 2. SFT Schema Extraction

Expected input fields:

- `instruction`
- `input`
- `output`
- `document_type`
- `split`

Expected output:

- JSON object with normalized fields for invoice, contract or report extraction.
- Parser field accuracy can be computed by comparing expected JSON keys and normalized values.

No action in this ticket:

- No model fine-tuning.
- No external API call.
- No production parser provider change.

## 3. Embedding Tuning

Expected input fields:

- `query`
- `positive`
- `negative`
- `document_type`
- `source`

Evaluation idea:

- Encode query and candidates in a future local experiment.
- Rank candidates and report Hit Rate@K, MRR@K and Recall@K.
- If the embedding runtime is unavailable, write `skip_reason=embedding_runtime_unavailable`.

## 4. Reranker Tuning

Expected input fields:

- `query`
- `chosen`
- `rejected`
- `preference`
- `reason`

Evaluation idea:

- Use existing retrieval candidates as inputs in a future local experiment.
- Compare chosen versus rejected order after reranking.
- Report Hit Rate@K, MRR@K, Recall@K and skip reason.

## 5. Report Table

Start from `sample-data/fine-tuning/evaluation-template.csv`.

Required columns:

- `track`
- `dataset_version`
- `sample_count`
- `Hit Rate@K`
- `MRR@K`
- `Recall@K`
- `parser_field_accuracy`
- `data_source`
- `skip_reason`
- `notes`

## 6. Guardrail Review

Before any future experiment:

- Confirm the dataset is synthetic data only.
- Confirm privacy review found no secrets or customer data.
- Confirm leakage checks do not put expected answers in queries.
- Confirm overfit risks are documented for small templates.
- Confirm the result remains research-only and disconnected from production runtime.
