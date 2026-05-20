# 00-01 - Repo Structure

## Goal

建立 DocuRAG AgentOps 後續開發需要的最小目錄邊界，讓 backend、frontend、docs、tasks、infra 與 sample data 有清楚位置。

## Scope

- 建立必要的 top-level 目錄或 placeholder Markdown。
- 只建立 repo 結構，不放入實作程式碼。
- 確認目錄命名與 README、ROADMAP 一致。

## Out of Scope

- 不建立 FastAPI app。
- 不建立 Vue app。
- 不安裝套件。
- 不建立 package manager 檔案。
- 不建立 Docker Compose 服務內容。
- 不實作 OCR、RAG、Qdrant、Redis、NATS 或 vLLM。

## Files likely to change

- `README.md`
- `TODO.md`
- `docs/`
- `tasks/`
- `backend/README.md`
- `frontend/README.md`
- `infra/README.md`
- `sample-data/README.md`

## Acceptance Criteria

- [ ] repo 有後續開發需要的最小目錄位置。
- [ ] 新增的 placeholder 都是 Markdown 或空目錄標記，不含程式碼。
- [ ] README 中的 repo structure 與實際目錄一致。
- [ ] 可以單獨 commit，不混入功能實作。

## Validation

- 列出 Markdown 與目錄結構，確認沒有新增程式碼或 package manager 檔案。
- 檢查 `git diff --stat` 只包含文件或 placeholder。
