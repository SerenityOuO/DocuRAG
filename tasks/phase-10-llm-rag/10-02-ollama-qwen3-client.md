# 10-02 Ollama Qwen3 LLM Client

## Goal

新增最小 Ollama LLM client，讓 backend 可以呼叫本機 `qwen3:8b`，但不立即改變既有 `/rag/query` 預設行為。

## Scope

- 新增 LLM provider interface 與 Ollama HTTP client。
- 以 `DOCURAG_LLM_PROVIDER=ollama` 啟用 provider。
- 使用 `DOCURAG_LLM_BASE_URL` 與 `DOCURAG_LLM_MODEL=qwen3:8b` 設定本機服務。
- 優先支援 Ollama native generate / chat API；若使用 OpenAI-compatible `/v1/chat/completions`，需在文件中明確記錄。
- 新增明確 timeout、錯誤訊息與 health check helper。
- 增加測試覆蓋成功回應、timeout / connection error 與 provider disabled。
- 保持現有 deterministic RAG baseline 預設可用。

## Out of Scope

- 不接雲端 OpenAI API key。
- 不實作 streaming。
- 不實作 `qwen3-vl:8b` VLM parser。
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
- [ ] 設定 `DOCURAG_LLM_PROVIDER=ollama` 與 `DOCURAG_LLM_MODEL=qwen3:8b` 時，client 可送出本機生成 request。
- [ ] Ollama 未啟動或模型不存在時，回傳 actionable message。
- [ ] 測試覆蓋成功與失敗路徑。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `curl http://127.0.0.1:11434/api/tags`
- 以 mock HTTP server 或 monkeypatch 驗證 Ollama request / response。
