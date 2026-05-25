# 28-04 Demo Login Mode and Role Gates

## Goal

新增面試 demo 可展示的使用者登入模式，讓系統從「前端切換 Viewer / Admin surface」進一步變成「登入後依角色顯示功能」。這是 demo-safe login mode，不是完整 production Auth / RBAC / multi-tenant system。

`goal.md` 長期要求使用者登入、角色權限、organization / project access 與 API guard。Phase 28 先做最小可展示切片：demo accounts、login/logout/me API、frontend login page、role-gated UI 與基本 write API guard。

## Scope

- 新增 demo auth mode，預設可由 env 開關控制，例如 `DOCURAG_AUTH_MODE=demo` / `disabled`。
- 新增 demo users 設定，至少包含 Admin / Analyst / Viewer 三種角色；測試帳號不可使用真實密碼。
- 新增 Auth API：`POST /auth/login`、`POST /auth/logout`、`GET /auth/me`；`POST /auth/refresh` 可規劃但不強制實作。
- 使用 signed token、signed cookie 或等價 demo session；不可明文回傳密碼。
- Frontend 新增 login screen；登入成功後依角色顯示 Viewer Chat 或 Admin / Analyst ingestion surface。
- Viewer 不可看到或操作 upload、OCR、parse、vector index 等 ingestion action。
- Backend 對 write / ingestion 類 API 加上 demo role guard：upload、OCR、mock OCR、parse、vector index、download 規則需明確定義。
- 文件清楚說明此階段沒有 PostgreSQL users table、organization / project isolation、password reset、SSO、正式 audit log 或完整 RBAC。
- 新增 backend / frontend focused tests，驗證 login、me、logout、Viewer write API forbidden、Admin / Analyst allowed。

## Out of Scope

- 不新增 PostgreSQL schema、users table、password reset、email verification、SSO、OAuth、MFA 或正式 JWT refresh rotation。
- 不新增 organization / project CRUD、tenant isolation、project-level permission 或資料庫 metadata filtering；這些留給後續 Auth / Project phase。
- 不新增 Redis session store、NATS、worker、audit log pipeline、K8s 或 deployment hardening。
- 不把 frontend role gating 當成唯一安全機制；write API guard 必須在 backend 也驗證。
- 不允許 Viewer 透過 Agent 或 tool 呼叫繞過 upload / reindex 限制。

## Release Impact

- Target version: `v0.28.0`.
- Version bump required: yes when Phase 28 release sync is completed.
- 原因：新增登入入口、角色顯示、API guard 與 demo 使用流程，屬於明顯使用者可見行為。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/documents.py`
- `backend/app/api/routes/rag.py`
- `backend/app/main.py`
- `backend/app/schemas/auth.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_documents.py`
- `frontend/src/App.vue`
- `frontend/src/api/client.ts`
- `frontend/src/styles.css`
- `scripts/demo-smoke-test.ps1`
- `.env.example`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/demo-script.md`
- `docs/ROADMAP.md`
- `TODO.md`

## Acceptance Criteria

- [ ] Frontend 首次進入 demo 時顯示 login screen 或清楚的 demo auth state。
- [ ] Admin / Analyst 登入後可以操作 ingestion；Viewer 登入後只能查詢與查看，不可 upload / OCR / parse / index。
- [ ] Backend write API 對 Viewer 回傳 403 或等價 forbidden response。
- [ ] `GET /auth/me` 可回傳目前登入使用者與 role。
- [ ] 登出後 frontend 清除登入狀態，受保護操作不可繼續執行。
- [ ] 文件清楚說明這是 demo auth mode，不是正式 RBAC / tenant isolation。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Browser check for local frontend login flow: Admin / Analyst ingestion allowed, Viewer upload controls hidden or disabled, no horizontal overflow on desktop and mobile.
- `rg -n "DOCURAG_AUTH_MODE|/auth/login|/auth/me|demo auth|role guard|Viewer|Analyst|Admin|forbidden" backend/app backend/tests frontend/src README.md backend/README.md frontend/README.md docs/api.md docs/architecture.md docs/demo-script.md TODO.md docs/ROADMAP.md tasks/phase-28-document-sources-auth-mode`
- `git diff --check`
