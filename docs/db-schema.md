# Database Schema Draft

MVP 初期可以先使用 fixture 或 in-memory repository。正式資料表會在 Phase 01 起逐步落地。

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
