# 01-01 - Backend Healthcheck

## Goal

建立 backend 最小可執行入口，提供 `/health` 作為後續開發與 Docker 驗證基準。

## Scope

- 建立最小 FastAPI backend app。
- 新增 `/health` endpoint。
- 新增最小測試或手動驗證說明。
- 保持 implementation thin，不加入任何業務模組。

## Out of Scope

- 不實作登入、權限或 session。
- 不建立資料庫 schema 或 migration。
- 不接 Redis、NATS、Qdrant 或 vLLM。
- 不實作 document upload。
- 不建立 frontend。

## Files likely to change

- `backend/README.md`
- `backend/app/main.py`
- `backend/tests/test_health.py`
- `backend/pyproject.toml`

## Acceptance Criteria

- [ ] backend app 可以啟動。
- [ ] `GET /health` 回傳健康狀態。
- [ ] healthcheck 測試或手動驗證可重現。
- [ ] commit 只包含 backend healthcheck 所需檔案。

## Validation

- 執行 backend healthcheck 測試。
- 手動 request `/health`，確認回應符合 ticket 定義。
