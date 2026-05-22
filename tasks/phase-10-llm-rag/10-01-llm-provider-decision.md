# 10-01 LLM Provider Decision

## Goal

選定第一個本機大模型 serving 方式，讓 DocuRAG 可以從 deterministic local keyword answer 進入可驗證的 LLM-based RAG generation。

## Scope

- 依使用者指定的大模型、RTX 5070 Ti 16GB VRAM、Windows 本機環境與 GPU runtime 條件，比較 Ollama、LM Studio / OpenAI-compatible server、llama.cpp server、vLLM on WSL2 / Docker。
- 明確記錄 vLLM 不支援原生 Windows；若選 vLLM，必須走 WSL2 或 Docker。
- 選定第一個 provider contract，優先支援 OpenAI-compatible HTTP API，降低後續替換成本。
- 定義必要環境變數，例如 `DOCURAG_LLM_PROVIDER`、`DOCURAG_LLM_BASE_URL`、`DOCURAG_LLM_MODEL`、timeout 與 max tokens。
- 記錄不接雲端 API key 的本機 demo-safe 預設。

## Out of Scope

- 不實作 backend LLM client。
- 不修改 RAG answer API 行為。
- 不新增 embedding、Qdrant、rerank、worker、Redis、NATS、資料庫 schema、登入或權限。
- 不下載或轉換模型權重。

## Files likely to change

- `docs/ROADMAP.md`
- `docs/LOCAL_DEV_SETUP.md`
- `README.md`
- `TODO.md`

## Acceptance Criteria

- [ ] 選定第一個 local LLM provider 與 fallback 策略。
- [ ] 文件說明 Windows / GPU / vLLM 限制。
- [ ] 文件列出啟動本機模型服務所需的 endpoint、model name 與 env vars。
- [ ] 後續 implementation ticket 可依本 ticket 直接開始。

## Validation

- `nvidia-smi`
- 本機模型服務的 `/v1/models` 或等效 health check。
- 文件 review。
