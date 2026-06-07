# DB Schema Contract

## Goal

建立 Phase 31 的 DB schema contract，固定 documents、pages、chunks、fields、eval runs 與 agent runs 的資料表設計，讓後續 migration ticket 可以照 contract 實作。

## Scope

- 定義 documents、document_pages、document_chunks、extracted_fields、eval_runs、eval_items、agent_runs、agent_steps 的 table contract。
- 定義欄位型別、required / nullable、index、foreign key 與保留的 tenant / project metadata 欄位。
- 對齊既有 API response 與 local JSON metadata，不擴張 user-facing behavior。
- 更新 `docs/db-schema.md`、architecture 與 TODO。

## Out of Scope

- 不建立 migration 檔或 repository code。
- 不新增 users / organizations / roles / memberships schema；正式 RBAC 留給 Phase 32。
- 不新增 Redis、NATS、worker、Qdrant payload index 或 K8s。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 schema contract 文件票，不改 runtime 或 release artifact。

## Files likely to change

- `docs/db-schema.md`
- `docs/architecture.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-31-enterprise-roadmap/31-03-db-schema-contract.md`

## Acceptance Criteria

- [ ] `docs/db-schema.md` 有 Phase 31 core tables 的欄位、index 與關聯說明。
- [ ] schema contract 保留 `project_id` / future tenant metadata 欄位，但不實作正式 RBAC。
- [ ] local JSON metadata 與 DB schema 的 mapping 清楚可追。
- [ ] 文件明確標示 schema contract 尚未等於 migration runtime。

## Validation

- `rg -n "document_pages|document_chunks|extracted_fields|eval_runs|agent_runs|project_id|Phase 31" docs TODO.md tasks/phase-31-enterprise-roadmap`
- `git diff --check`
