# 10-02 OpenAI-Compatible LLM Client

## Goal

新增最小 OpenAI-compatible LLM client，讓 backend 可以呼叫本機大模型服務，但不立即改變既有 `/rag/query` 預設行為。

## Scope

- 新增 LLM provider interface 與 OpenAI-compatible HTTP client。
- 使用 `DOCURAG_LLM_BASE_URL`、`DOCURAG_LLM_MODEL` 等 env vars 設定本機服務。
- 新增明確 timeout、錯誤訊息與 health check helper。
- 增加測試覆蓋成功回應、timeout / connection error 與 provider disabled。
- 保持現有 deterministic RAG baseline 預設可用。

## Out of Scope

- 不接雲端 OpenAI API key。
- 不實作 streaming。
- 不接 embedding、Qdrant、rerank、worker、Redis、NATS、資料庫 schema、登入或權限。
- 不改 frontend UI。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/services/llm.py`
- `backend/tests/test_llm.py`
- `docs/LOCAL_DEV_SETUP.md`
- `backend/README.md`

## Acceptance Criteria

- [ ] 未設定 LLM provider 時，backend 測試與既有 RAG flow 不受影響。
- [ ] 設定 OpenAI-compatible endpoint 時，client 可送出 chat completion request。
- [ ] 錯誤狀態回傳 actionable message，不吞錯也不假裝 deterministic answer 是 LLM answer。
- [ ] 測試覆蓋成功與失敗路徑。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- 以 mock HTTP server 或 monkeypatch 驗證 chat completion request / response。
