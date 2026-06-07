# Database Schema Draft

到 v0.29.0 / Phase 30 hardening 為止，DocuRAG 仍以 local JSON store 與 uploaded files 支撐 demo runtime；本文件是 Phase 31 起導入 PostgreSQL 的邊界與 migration policy，不代表目前已新增 DB schema、migration 檔或 repository runtime。

## Phase 31 PostgreSQL Boundary

Phase 31 的目標是把目前 local JSON store 中已存在且可驗證的資料域，逐步轉成 DB-backed contract。第一步只定義資料邊界、migration policy 與 fallback path；真正 schema、migration 檔與 repository adapter 需等後續 ticket 才能實作。

### Current Local JSON Store

| Local source | Current data | Future DB domain | Notes |
|---|---|---|---|
| `data/documents.json` | document metadata、stored filename、content type、processing status | `documents` | DB 保存 metadata 與 file reference；原始檔仍留在 `data/uploads` 或後續 object storage，不把 bytes 直接塞進 DB。 |
| `data/documents.json` | OCR status、OCR text、OCR lines、bbox、confidence、OCR trace metadata | `document_pages` / OCR block columns | Page-level OCR result 需可追蹤 provider、language、model version、timing 與 failure reason。 |
| `data/documents.json` | local chunks、source type、citation metadata、vector indexing trace | `document_chunks` / indexing metadata | `source_type` 需保留 `ocr_image`、`text_upload`、`pdf_text`、`pdf_scanned_pending_ocr` 等來源邊界。 |
| `data/documents.json` | parser result、invoice fields、field evidence、fallback chain | `extracted_fields` plus parser result metadata | Structured fields 必須保留 `parser_source`、confidence、source text/page/bbox 與 fallback reason。 |
| `data/documents.json` | processing jobs and latest job metadata | `processing_jobs` | 先記錄同步 processing state；Phase 33 worker ticket 才能擴成 queue-backed task status。 |
| `data/agent_runs.json` | deterministic Agent run、plan steps、tool calls、citations、final answer | `agent_runs` / `agent_steps` / `agent_tool_calls` | 仍是 read-only deterministic Agent；正式 planner / permission tiers 屬於 Phase 38。 |
| `sample-data/eval/*.json` | retrieval eval dataset and built-in benchmark fixtures | `eval_datasets` / `eval_items` | Phase 36 才做可管理 eval dashboard；Phase 31 只保留 schema direction。 |
| request-time eval output | built-in RAG eval result summary | `eval_runs` / `eval_run_items` | v0.29.0 built-in eval 目前不持久化 run history。 |

### Migration Policy

- Tooling policy: future runtime migrations should use Alembic with the backend DB stack selected in Phase 31 implementation tickets. This ticket does not add Alembic, SQLAlchemy, psycopg, migration files, or runtime imports.
- Naming policy: migration files should use an Alembic revision id with a readable slug such as `phase31_create_documents_tables`; release notes should reference the ticket id and target version.
- Execution policy: migrations run from `backend/` with `DATABASE_URL` set, using an explicit command such as `python -m alembic upgrade head` after the dependency and config ticket exists.
- Rollback policy: every migration must provide a downgrade path. Destructive changes must use expand / migrate / contract sequencing, with local JSON or DB backup verified before applying the contract step.
- Validation policy: each schema ticket must include migration upgrade / downgrade validation, targeted repository tests, and at least one fallback smoke path that proves local JSON demo mode still works unless the ticket explicitly changes the default.
- Release policy: only the Phase 31 release sync ticket may bump backend / frontend / Docker Compose version to `v0.31.0`.

### Local JSON Fallback And Migration Path

- Local JSON remains the default demo fallback. `31-04` adds validated opt-in DB-backed repository selection with `DOCURAG_REPOSITORY_PROVIDER=postgresql`.
- DB-backed mode remains opt-in, so existing interview demo data is not cut off in one commit.
- Migration from local JSON to DB should be a copy/import path before any default switch. The import should be idempotent by stable document id, chunk id and agent run id.
- Dual-write should not be introduced silently. If needed, it must be scoped to a repository adapter ticket with tests for consistency and failure behavior.
- Uploaded files remain filesystem artifacts during Phase 31; DB rows reference the stored filename/path and checksum metadata if available.
- Qdrant remains the vector store. PostgreSQL stores document/chunk/indexing metadata and does not replace Qdrant embeddings in Phase 31.

## Phase 31 Core Tables Contract

`31-03` 只定義 table contract。下列欄位、index 與 relationship 是後續 migration / repository ticket 的輸入，不代表目前已建立 PostgreSQL schema、Alembic migration、SQLAlchemy model 或 DB-backed repository runtime。

Phase 31 保留 `project_id` 作為 future project / tenant metadata，但不建立 `users`、`organizations`、`roles` 或 `memberships` table；正式 Auth / RBAC / tenant boundary 留給 Phase 32。所有 `project_id` 在本 contract 中都可為 `NULL`，以支援目前 single-user local JSON demo fallback。

### Type And Constraint Conventions

| Contract token | Future PostgreSQL shape | Notes |
|---|---|---|
| `text_id` | `text` or `uuid` selected by migration ticket | 目前 local JSON id 是 string；migration ticket 可決定是否轉 UUID。 |
| `json_data` | `jsonb` | 保存 OCR bbox、trace metadata、field value 或 raw payload。 |
| `timestamp` | `timestamptz` | 時間欄位以 UTC ISO timestamp 對齊目前 API / local JSON。 |
| `status_text` | `text` with application enum check | enum 值先由 API schema 定義，DB check constraint 留給 migration ticket。 |

### documents

Stores `DocumentMetadata` level data from `data/documents.json`.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `document_id` | `text_id` | yes | no | primary key | `DocumentMetadata.document_id` |
| `project_id` | `text_id` | no | yes | index | future project metadata; current API may be `null` |
| `filename` | `text` | yes | no | index | original filename |
| `stored_filename` | `text` | yes | no | unique or indexed | uploaded file reference under `data/uploads/` |
| `file_type` | `text` | yes | no | index | extension / normalized type |
| `content_type` | `text` | yes | no | none | upload MIME type |
| `size_bytes` | `integer` | yes | no | none | `size` |
| `status` | `status_text` | yes | no | index | `uploaded` / `processing` / `ready` / `failed` |
| `processing_status` | `json_data` | no | yes | none | upload / OCR / parser / indexing state snapshot |
| `latest_job_id` | `text_id` | no | yes | FK to `processing_jobs.job_id` when available | latest processing job |
| `created_at` | `timestamp` | yes | no | index | document creation time |
| `updated_at` | `timestamp` | no | yes | none | latest processing / OCR / parser update |

### document_pages

Stores page-level OCR text and OCR line trace. Image-only uploads can use `page_number=1`; text uploads may omit page rows unless a later repository ticket decides to materialize them.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `page_id` | `text_id` | yes | no | primary key | derived from `document_id` + page number |
| `document_id` | `text_id` | yes | no | FK to `documents.document_id`, index | OCR result owner |
| `project_id` | `text_id` | no | yes | index | copied from `documents.project_id` |
| `page_number` | `integer` | yes | no | unique with `document_id` | `OcrTextLine.page_number` or default page |
| `source_type` | `text` | yes | no | index | `ocr_image` / `pdf_text` / `text_upload` / `pdf_scanned_pending_ocr` |
| `ocr_status` | `status_text` | yes | no | index | `pending` / `running` / `completed` / `failed` |
| `ocr_text` | `text` | no | yes | optional full-text index later | `OcrResult.text` / page text |
| `ocr_lines` | `json_data` | no | yes | none | text, bbox, confidence, metadata array |
| `ocr_metadata` | `json_data` | no | yes | none | provider, model, language, timing, error trace |
| `created_at` | `timestamp` | yes | no | none | import / processing time |
| `updated_at` | `timestamp` | no | yes | none | `OcrResult.updated_at` |

Recommended indexes:

- `idx_document_pages_document_page` on `document_id, page_number`.
- `idx_document_pages_project_status` on `project_id, ocr_status`.

### document_chunks

Stores normalized retrieval chunks. Embeddings stay in Qdrant; PostgreSQL only tracks chunk metadata and indexing state.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `chunk_id` | `text_id` | yes | no | primary key | `DocumentChunk.chunk_id` |
| `document_id` | `text_id` | yes | no | FK to `documents.document_id`, index | chunk owner |
| `page_id` | `text_id` | no | yes | FK to `document_pages.page_id` | page-level OCR / PDF text source |
| `project_id` | `text_id` | no | yes | index | copied from `documents.project_id` |
| `text` | `text` | yes | no | optional full-text index later | `DocumentChunk.text` |
| `source` | `text` | yes | no | none | `DocumentChunk.source` |
| `source_type` | `text` | yes | no | index | `ocr_image` / `text_upload` / `pdf_text` / `eval_fixture` |
| `page_number` | `integer` | no | yes | index | citation page |
| `bbox` | `json_data` | no | yes | none | citation bbox |
| `confidence` | `double precision` | no | yes | none | OCR confidence when available |
| `metadata` | `json_data` | no | yes | none | retrieval / trace / vector indexing metadata |
| `created_at` | `timestamp` | yes | no | index | chunk creation time |

Recommended indexes:

- `idx_document_chunks_document_created` on `document_id, created_at`.
- `idx_document_chunks_project_source` on `project_id, source_type`.
- `idx_document_chunks_page` on `document_id, page_number`.

### extracted_fields

Stores flattened parser fields from `ParserResult.fields`. Line items may be represented by `field_group=line_items` and `field_index`.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `field_id` | `text_id` | yes | no | primary key | derived stable field id |
| `document_id` | `text_id` | yes | no | FK to `documents.document_id`, index | parser result owner |
| `project_id` | `text_id` | no | yes | index | copied from `documents.project_id` |
| `schema_version` | `text` | yes | no | index | `ParserResult.schema_version` |
| `parser_source` | `text` | yes | no | index | `deterministic_invoice` / `llm_invoice` / `vlm_invoice` |
| `parser_status` | `status_text` | yes | no | index | `pending` / `parsing` / `parsed` / `failed` |
| `field_group` | `text` | no | yes | index | `invoice_fields` / `line_items` |
| `field_name` | `text` | yes | no | index with `document_id` | field name such as `vendor_name` |
| `field_index` | `integer` | no | yes | none | line item index |
| `field_value` | `json_data` | no | yes | none | `ExtractedField.value` |
| `confidence` | `double precision` | no | yes | none | normalized confidence |
| `source_text` | `text` | no | yes | none | OCR / VLM evidence text |
| `source_page` | `integer` | no | yes | index | evidence page |
| `source_bbox` | `json_data` | no | yes | none | evidence bbox |
| `fallback_reason` | `text` | no | yes | none | missing / fallback reason |
| `trace_metadata` | `json_data` | no | yes | none | parser trace metadata |
| `updated_at` | `timestamp` | no | yes | none | `ParserResult.updated_at` |

Recommended indexes:

- `idx_extracted_fields_document_field` on `document_id, field_name`.
- `idx_extracted_fields_project_schema` on `project_id, schema_version`.

### processing_jobs

Stores current synchronous processing job history from `DocumentMetadata.processing_jobs`. Phase 33 can later connect this to queue-backed worker status.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `job_id` | `text_id` | yes | no | primary key | `ProcessingJob.job_id` |
| `document_id` | `text_id` | yes | no | FK to `documents.document_id`, index | job owner |
| `project_id` | `text_id` | no | yes | index | copied from `documents.project_id` |
| `job_type` | `text` | yes | no | index | upload / OCR / parser / indexing job type |
| `status` | `status_text` | yes | no | index | pending / running / completed / failed |
| `error_message` | `text` | no | yes | none | job failure message |
| `created_at` | `timestamp` | yes | no | index | job creation time |
| `updated_at` | `timestamp` | yes | no | none | latest job update |

### eval_datasets

Stores eval dataset metadata. Current built-in datasets come from `sample-data/eval/*.json`; this table is a future persistence contract only.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `dataset_id` | `text_id` | yes | no | primary key | stable dataset id |
| `project_id` | `text_id` | no | yes | index | future project metadata |
| `name` | `text` | yes | no | unique within project later | dataset name |
| `source_path` | `text` | no | yes | none | fixture path when imported |
| `description` | `text` | no | yes | none | dataset notes |
| `metadata` | `json_data` | no | yes | none | tags / fixture metadata |
| `created_at` | `timestamp` | yes | no | index | import time |

### eval_items

Stores retrieval eval cases.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `eval_item_id` | `text_id` | yes | no | primary key | `RetrievalEvalCase.id` |
| `dataset_id` | `text_id` | yes | no | FK to `eval_datasets.dataset_id`, index | parent dataset |
| `project_id` | `text_id` | no | yes | index | copied from dataset |
| `query` | `text` | yes | no | none | eval question |
| `top_k` | `integer` | yes | no | none | eval top K |
| `expected_document_filenames` | `json_data` | yes | no | none | expected documents |
| `expected_chunk_hints` | `json_data` | yes | no | none | expected chunk hints |
| `expected_terms` | `json_data` | yes | no | none | expected terms |
| `tags` | `json_data` | no | yes | none | case tags |
| `notes` | `text` | no | yes | none | case notes |

### eval_runs

Stores eval run summary. v0.29.0 built-in eval currently returns this at request time and does not persist run history.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `eval_run_id` | `text_id` | yes | no | primary key | `RetrievalEvalRun.run_id` / built-in response `run_id` |
| `dataset_id` | `text_id` | no | yes | FK to `eval_datasets.dataset_id` | parent dataset if persisted |
| `project_id` | `text_id` | no | yes | index | future project metadata |
| `strategy` | `text` | yes | no | index | keyword / vector / hybrid / hybrid_rerank |
| `case_count` | `integer` | yes | no | none | run case count |
| `summary` | `json_data` | yes | no | none | Hit Rate@K, MRR@K, latency, fallback metrics |
| `environment` | `json_data` | no | yes | none | provider / model / Qdrant / rerank trace |
| `created_at` | `timestamp` | yes | no | index | run time |

### eval_run_items

Stores per-case eval results.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `eval_run_item_id` | `text_id` | yes | no | primary key | derived stable id |
| `eval_run_id` | `text_id` | yes | no | FK to `eval_runs.eval_run_id`, index | parent run |
| `eval_item_id` | `text_id` | no | yes | FK to `eval_items.eval_item_id` | source case if persisted |
| `case_id` | `text` | yes | no | index | case id from output |
| `query` | `text` | yes | no | none | query snapshot |
| `top_k` | `integer` | yes | no | none | top K |
| `hit` | `boolean` | yes | no | index | retrieval hit state |
| `first_relevant_rank` | `integer` | no | yes | none | first relevant rank |
| `reciprocal_rank` | `double precision` | no | yes | none | per-case MRR component |
| `recall_at_k` | `double precision` | no | yes | none | per-case recall |
| `latency_ms` | `double precision` | no | yes | none | per-case latency |
| `retrieved_chunks` | `json_data` | no | yes | none | retrieved chunk output snapshot |
| `fallback_reasons` | `json_data` | no | yes | none | fallback reasons |
| `error` | `text` | no | yes | none | failure message |

### agent_runs

Stores deterministic Agent run records from `data/agent_runs.json`.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `agent_run_id` | `text_id` | yes | no | primary key | `AgentRun.run_id` |
| `project_id` | `text_id` | no | yes | index | future project metadata |
| `document_id` | `text_id` | no | yes | FK to `documents.document_id` | optional focused document |
| `status` | `status_text` | yes | no | index | pending / running / completed / failed |
| `task` | `text` | yes | no | none | requested task |
| `query` | `text` | no | yes | none | optional search query |
| `final_answer` | `json_data` | yes | no | none | `AgentFinalAnswer` |
| `citations` | `json_data` | no | yes | none | source citations snapshot |
| `trace` | `json_data` | no | yes | none | planner / policy trace |
| `created_at` | `timestamp` | yes | no | index | run creation time |
| `updated_at` | `timestamp` | yes | no | none | latest run update |

### agent_steps

Stores Agent plan steps.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `agent_step_id` | `text_id` | yes | no | primary key | `AgentStep.step_id` |
| `agent_run_id` | `text_id` | yes | no | FK to `agent_runs.agent_run_id`, index | parent run |
| `step_order` | `integer` | yes | no | unique with `agent_run_id` | `AgentStep.order` |
| `title` | `text` | yes | no | none | step title |
| `tool_name` | `text` | no | yes | index | allowlisted tool name |
| `status` | `status_text` | yes | no | index | pending / running / completed / failed |
| `input_summary` | `text` | no | yes | none | step input summary |
| `observation_summary` | `text` | no | yes | none | step observation summary |
| `fallback_reason` | `text` | no | yes | none | step fallback reason |

### agent_tool_calls

Stores detailed allowlisted tool calls. This table is included because `AgentRun.tool_calls` is persisted today even though `31-03` does not add runtime.

| Column | Type | Required | Nullable | Index / key | Maps from |
|---|---|---:|---:|---|---|
| `tool_call_id` | `text_id` | yes | no | primary key | derived stable id |
| `agent_run_id` | `text_id` | yes | no | FK to `agent_runs.agent_run_id`, index | parent run |
| `tool_name` | `text` | yes | no | index | allowlisted tool name |
| `status` | `status_text` | yes | no | index | completed / failed |
| `input_summary` | `text` | yes | no | none | call input summary |
| `output_summary` | `text` | no | yes | none | call output summary |
| `observation` | `json_data` | yes | no | none | `AgentToolObservation` |
| `output` | `json_data` | no | yes | none | summarized tool output |
| `citations` | `json_data` | no | yes | none | citations snapshot |
| `retrieved_chunks` | `json_data` | no | yes | none | retrieved chunk snapshot |
| `trace_metadata` | `json_data` | no | yes | none | call trace metadata |
| `error_message` | `text` | no | yes | none | failure message |

## Local JSON Mapping Summary

| Local JSON field | Phase 31 table |
|---|---|
| `DocumentMetadata.document_id`, filename, file metadata, status | `documents` |
| `DocumentMetadata.processing` | `documents.processing_status` |
| `DocumentMetadata.ocr.text`, `ocr.lines`, `ocr.extracted_fields`, `ocr.updated_at` | `document_pages` |
| `DocumentMetadata.chunks[]` | `document_chunks` |
| `DocumentMetadata.parser_result.fields` / `trace_metadata` | `extracted_fields` |
| `DocumentMetadata.processing_jobs[]` / `latest_job` | `processing_jobs` |
| `RetrievalEvalCase` fixture JSON | `eval_datasets` / `eval_items` |
| `RetrievalEvalRun` / built-in eval response | `eval_runs` / `eval_run_items` |
| `AgentRun.plan_steps[]` | `agent_steps` |
| `AgentRun.tool_calls[]` | `agent_tool_calls` |
| `AgentRun.final_answer`, citations, trace | `agent_runs` |

## Explicitly Deferred From Phase 31 Schema Contract

- No users, organizations, roles, memberships, password hashes, sessions or formal RBAC tables in `31-03`; those belong to Phase 32.
- No migration file, Alembic config, SQLAlchemy model, repository code, DB connection setting or production config change.
- No Qdrant payload index, Redis, NATS, worker, K8s or deployment schema in this ticket.
- No destructive migration or default switch away from local JSON fallback.

## Phase 32 Formal Auth / RBAC Schema Runtime

`32-02` adds the first runtime schema slice for formal Auth / RBAC / tenant boundary. The schema is created by `backend/app/repositories/auth_rbac.py` and the explicit migration command `scripts/migrate-auth-rbac-schema.py`. This is a PostgreSQL foundation only; endpoint permission guards remain scheduled for `32-03`, and frontend role surface / release sync remain scheduled for `32-04`.

### Migration Command

```powershell
python scripts/migrate-auth-rbac-schema.py --dry-run --seed-demo-users
python scripts/migrate-auth-rbac-schema.py --database-url $env:DOCURAG_DATABASE_URL --seed-demo-users
```

The migration statements are non-destructive and use `CREATE TABLE IF NOT EXISTS` / `CREATE INDEX IF NOT EXISTS`. Demo seed writes use idempotent upsert statements. The command does not connect to a production database unless the operator explicitly provides that URL.

### Phase 32 Auth Tables

| Table | Purpose | Required boundary |
|---|---|---|
| `users` | Formal local account record with `username`, optional `email`, `display_name`, `password_hash`, `disabled`, `auth_source` and JSON payload. | Passwords are stored only as hashes; disabled users stay persisted but must not receive active access in later guards. |
| `organizations` | Top-level tenant boundary. | Organization membership is required before project access can be granted. |
| `projects` | Project workspace owned by an organization. | Documents, eval runs, Agent runs and future Qdrant payload filters join through `project_id`. |
| `roles` | Canonical `viewer`, `analyst`, `admin` role definitions with permission payload. | Permission semantics follow `32-01` role matrix. |
| `memberships` | User-to-organization role relationship. | Disabled status blocks organization-level access in later guards. |
| `project_memberships` | User-to-project role relationship. | This is the project access source of truth for `32-03` backend guards. |

### Demo Seed Users

`32-02` defines local demo seed rows for `admin`, `analyst`, `viewer` and `disabled-viewer`. Seed password values are converted into deterministic `pbkdf2_sha256$iterations$salt$digest` hashes before persistence. These rows are for local validation of the formal schema foundation only.

Phase 28 demo auth mode is still preserved as an explicit fallback: `DOCURAG_AUTH_MODE=demo` continues to use fixed demo tokens for local validation, and `DOCURAG_AUTH_MODE=disabled` remains the default in `.env.example`. `32-02` does not replace `/auth/login`, does not add production login runtime, and does not complete all endpoint permission guards.
