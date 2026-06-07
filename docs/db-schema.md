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

- Local JSON remains the default demo fallback until a later ticket explicitly adds and validates DB-backed repository selection.
- DB-backed mode must be opt-in at first, for example by a future storage provider env, so existing interview demo data is not cut off in one commit.
- Migration from local JSON to DB should be a copy/import path before any default switch. The import should be idempotent by stable document id, chunk id and agent run id.
- Dual-write should not be introduced silently. If needed, it must be scoped to a repository adapter ticket with tests for consistency and failure behavior.
- Uploaded files remain filesystem artifacts during Phase 31; DB rows reference the stored filename/path and checksum metadata if available.
- Qdrant remains the vector store. PostgreSQL stores document/chunk/indexing metadata and does not replace Qdrant embeddings in Phase 31.

## Core Tables

### users

| Column | Type | Notes |
|---|---|---|
| id | UUID | User ID |
| email | string | Login email |
| password_hash | string | Hashed password |
| display_name | string | UI display name |
| is_active | bool | Active flag |
| created_at | datetime | Created time |

### organizations

| Column | Type | Notes |
|---|---|---|
| id | UUID | Organization ID |
| name | string | Organization name |
| created_at | datetime | Created time |

### memberships

| Column | Type | Notes |
|---|---|---|
| id | UUID | Membership ID |
| user_id | UUID | User ID |
| organization_id | UUID | Organization ID |
| role | string | admin / manager / analyst / viewer |

### projects

| Column | Type | Notes |
|---|---|---|
| id | UUID | Project ID |
| organization_id | UUID | Tenant boundary |
| name | string | Project name |
| description | text | Project description |
| created_by | UUID | Creator user ID |
| created_at | datetime | Created time |

## Document Tables

- documents
- document_pages
- document_chunks
- extracted_fields

## RAG / Eval Tables

- chat_sessions
- chat_messages
- eval_datasets
- eval_items
- eval_runs

## Security Notes

- 所有資料查詢都必須檢查 `organization_id`。
- Project-scoped API 必須檢查 `project_id` 是否屬於目前使用者的 organization。
- Viewer 不可建立、修改或刪除資料。
