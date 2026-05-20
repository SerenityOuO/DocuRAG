# 01-02 - Backend Docker

## Goal

為 Phase 01 backend healthcheck 建立最小 Docker 啟動方式，讓服務可用容器驗證。

## Scope

- 建立 backend Dockerfile 或等效最小容器設定。
- 建立只啟動 backend healthcheck 的 Docker Compose 設定。
- 補充 README 中的容器啟動與驗證步驟。

## Out of Scope

- 不加入 PostgreSQL、Redis、NATS、Qdrant、vLLM 或 Ollama。
- 不建立 production Docker image 優化。
- 不建立 K8s manifests。
- 不建立 frontend container。
- 不實作業務 API。

## Files likely to change

- `backend/Dockerfile`
- `backend/.dockerignore`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`

## Acceptance Criteria

- [ ] 可以用 Docker 啟動 backend healthcheck。
- [ ] README 有明確啟動與驗證指令。
- [ ] Compose 檔只包含 Phase 01 所需服務。
- [ ] 沒有新增外部資料服務。

## Validation

- 執行 Docker 啟動指令。
- request `/health`，確認容器內服務回傳正常。
- 檢查 `git diff --stat` 沒有混入 Phase 02 或 AI pipeline 內容。
