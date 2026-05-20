# Phase 00 - Repository Bootstrap

## Goal

建立可開工的 repo 骨架，讓 backend、frontend、docs、infra 與 tasks 有明確邊界。

## Completion Criteria

- README 說清楚專案目的與 MVP 範圍。
- Backend 有 `/health` skeleton。
- Frontend 有可開啟的 Dashboard skeleton。
- `.env.example` 有最小必要設定。
- `infra/docker-compose.yml` 有 support services skeleton。

## Tickets

### P00-T01 - Define README MVP narrative

- Goal：建立專案第一印象。
- Scope：README 專案定位、MVP、demo flow。
- Out of Scope：完整技術文件。
- Files likely to change：`README.md`。
- Acceptance Criteria：3 分鐘內可理解專案價值。
- Validation：Manual check README。

### P00-T02 - Add minimal docs skeleton

- Goal：建立文件落點。
- Scope：architecture / api / db-schema / demo-script 初版。
- Out of Scope：完整規格細節。
- Files likely to change：`docs/*`。
- Acceptance Criteria：每份文件有目的與待補方向。
- Validation：Manual check docs。

### P00-T03 - Backend health skeleton

- Goal：建立 API 起點。
- Scope：FastAPI app、`/health`、基本設定。
- Out of Scope：DB、auth、worker。
- Files likely to change：`backend/app/main.py`、`backend/app/core/config.py`、`backend/pyproject.toml`。
- Acceptance Criteria：`/health` 回傳 OK。
- Validation：`pytest` 或 manual curl。

### P00-T04 - Frontend app skeleton

- Goal：建立前端起點。
- Scope：Vue app、router、Dashboard placeholder。
- Out of Scope：完整 UI、API 串接。
- Files likely to change：`frontend/package.json`、`frontend/src/*`。
- Acceptance Criteria：首頁可開啟。
- Validation：`npm run dev` manual check。

### P00-T05 - Infra skeleton

- Goal：保留部署擴充位置。
- Scope：`.env.example`、compose skeleton。
- Out of Scope：完整 app containers、K8s。
- Files likely to change：`.env.example`、`infra/docker-compose.yml`。
- Acceptance Criteria：設定名稱清楚，不含真實 secret。
- Validation：Manual check。
