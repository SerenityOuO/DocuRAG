# Phase 01 - Auth / RBAC / Project Core

## Goal

建立面試展示最重要的企業應用骨架：登入、角色、組織與專案隔離。

## Completion Criteria

- Demo user 可以登入。
- API 可以取得目前使用者。
- 不同角色有不同權限。
- Viewer 不能建立或修改 project。
- 使用者只能看到自己 organization 的 projects。

## Tickets

### P01-T01 - Define auth domain schemas

- Goal：建立 user / org / role 資料模型。
- Scope：User、Organization、Membership schema。
- Out of Scope：OAuth、SSO。
- Files likely to change：`backend/app/models/*`、`backend/app/schemas/*`。
- Acceptance Criteria：角色 enum 清楚。
- Validation：Unit test schema。

### P01-T02 - Implement demo login API

- Goal：讓 demo 可登入。
- Scope：`/auth/login`、`/auth/me`、`/auth/logout`。
- Out of Scope：Redis session。
- Files likely to change：`backend/app/api/auth.py`、`backend/app/services/auth_service.py`。
- Acceptance Criteria：demo user 可登入。
- Validation：API test。

### P01-T03 - Add RBAC guard

- Goal：API 層可檢查權限。
- Scope：role guard、project access helper。
- Out of Scope：複雜 policy engine。
- Files likely to change：`backend/app/core/security.py`、`backend/app/services/auth_service.py`。
- Acceptance Criteria：Viewer 被拒絕寫入操作。
- Validation：Unit/API test。

### P01-T04 - Implement project API

- Goal：建立 project core。
- Scope：list / create / detail project。
- Out of Scope：delete、archive、billing。
- Files likely to change：`backend/app/api/projects.py`、`backend/app/services/project_service.py`、`backend/app/repositories/project_repository.py`。
- Acceptance Criteria：只能看同 organization project。
- Validation：API test。

### P01-T05 - Frontend login and project pages

- Goal：串起登入與 project 切換。
- Scope：Login、Projects、auth store、api client。
- Out of Scope：完整設計系統。
- Files likely to change：`frontend/src/pages/*`、`frontend/src/api/*`、`frontend/src/stores/*`。
- Acceptance Criteria：可登入並看到 project list。
- Validation：Manual browser check。
