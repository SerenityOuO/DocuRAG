# Golden Dataset Changelog

This dataset changelog records why RAG golden dataset metadata changes. It is demo-safe documentation only and does not change retrieval ranking, eval runner logic, dataset upload API, frontend editor, database schema or production labeling workflow.

## phase41_golden_metadata_v1

Date: 2026-06-08

Files:

- `sample-data/eval/golden-dataset-metadata.json`
- `sample-data/eval/retrieval-eval.json`
- `sample-data/eval/built-in-rag-eval-zh-invoices.json`

Reason:

- Promote existing demo-safe eval cases into a versioned golden dataset boundary for Phase 41 RAG quality regression / DatasetOps.
- Keep runtime eval datasets unchanged so existing backend tests, smoke scripts and built-in benchmark paths continue to read the same JSON schema.
- Add case version, source document version, expected evidence mapping, expected answer outline and case tags without adding a new production labeling workflow.

Dataset changelog notes:

- `retrieval-eval.json` remains the public retrieval regression dataset and keeps its existing 20 synthetic cases.
- `built-in-rag-eval-zh-invoices.json` remains the Admin / Analyst built-in benchmark dataset and keeps its existing 10 synthetic Chinese invoice cases.
- Expected evidence is still defined by each runtime case's `expected_document_filenames`, `expected_chunk_hints` and `expected_terms`.
- Future case additions must update this changelog with the case version, source document version, reason for the new case and whether it changes regression gate expectations.

Data safety:

- All cases are demo-safe synthetic data.
- Do not add real personal data, real customer files, real vendor records, external downloaded documents, private company material or paid-service output.
- If a sample uses a real brand-like vendor label, it must stay a synthetic fixture label and must not include real tax ids, addresses, logos, transactions or payment data.
