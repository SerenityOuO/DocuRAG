# 23-01 Viewer Chat / Admin Ingestion Boundary Contract

## Goal

固定 Phase 23 的產品邊界：前台 Viewer 只進入 RAG Chat 查詢既有知識庫；後台 Admin / Analyst 才能操作文件上傳、OCR、ingestion 狀態與後續 indexing 入口，避免 demo UI 再把「問答使用者」與「知識庫管理者」混在同一個畫面。

## Scope

- 更新 README、frontend README、demo script、architecture / roadmap 文件中的 demo 敘事，明確區分：
  - Viewer Chat：問已建立的知識庫、看 answer、citation 與必要 trace summary。
  - Admin / Analyst Ingestion：上傳文件、觸發 backend provider-selected OCR、查看處理狀態與 local chunks / metadata debug link。
- 定義 Phase 23 frontend target surface：首頁或 `/chat` 為 Viewer Chat；上傳與 OCR 移到明確的後台知識庫管理入口。
- 明確說明目前 ingestion backend 仍是 local JSON + provider-selected OCR + local chunking；正式 parser、DB、worker 與 production indexing 仍未實作。
- 建立後續 tickets 的順序與 release guardrails。

## Out of Scope

- 不修改 frontend、backend、scripts、sample data、demo media 或版本號。
- 不新增登入、RBAC、Admin auth guard、project permission、PostgreSQL、Redis、NATS、worker、async queue 或 database schema。
- 不實作 VLM parser、PDF rendering、多頁 OCR、production OCR tuning、default-on vector indexing、hybrid retrieval、rerank chat path 或 Agent runtime。
- 不把 Admin / Analyst 後台入口包裝成真正權限系統；本 Phase 只做產品表面與 demo 邊界拆分。

## Release Impact

- Target version: `v0.23.0`
- Version bump required: no
- 原因：本 ticket 只固定 Phase 23 的產品邊界與後續 ticket 順序，不產生 runtime release artifact。

## Files likely to change

- `README.md`
- `frontend/README.md`
- `docs/demo-script.md`
- `docs/architecture.md`
- `docs/ROADMAP.md`
- `TODO.md`

## Acceptance Criteria

- [x] 文件明確寫出「前台 Viewer Chat」與「後台 Admin / Analyst Ingestion」是兩個不同產品入口。
- [x] 文件不再把 frontend upload 描述成 Viewer Chat 主線。
- [x] 文件說明 OCR 是 backend ingestion layer，不是前端直接對圖片聊天。
- [x] 文件保留現況限制：local JSON、local chunks、manual / explicit vector path、無正式 parser / worker / DB / auth。
- [x] Phase 23 ticket 順序與 `v0.23.0` release guardrails 已寫入 TODO / ROADMAP。

## Validation

- `rg -n "Phase 23|v0.23.0|Viewer Chat|Admin / Analyst|Ingestion|知識庫管理|前台|後台" README.md frontend/README.md docs/demo-script.md docs/architecture.md docs/ROADMAP.md TODO.md tasks/phase-23-role-split-demo/*.md`
- `git diff --check`
