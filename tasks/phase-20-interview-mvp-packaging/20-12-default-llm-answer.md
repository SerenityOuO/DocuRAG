# 20-12 Default LLM Answer

## Goal

讓本機 demo 的 `/rag/query` 在沒有額外設定 `DOCURAG_LLM_PROVIDER` 時，預設嘗試使用 Ollama `qwen3.5:4b` 產生回答；若 Ollama service、model 或 request timeout 不可用，仍清楚 fallback 到既有 retrieved OCR chunks，不中斷 demo。

## Scope

- 將 backend `Settings.llm_provider` 預設值調整為 `ollama`。
- 保留 `DOCURAG_LLM_PROVIDER=` 空值覆寫，讓使用者可以明確關閉 LLM generation。
- 更新 backend tests，避免一般 route test 真的呼叫本機 Ollama，並覆蓋 default-on provider selection。
- 更新 demo smoke script，讓預設模式接受 `ollama/qwen3.5:4b`、`LLM unavailable fallback` 或明確關閉時的 `deterministic baseline`。
- 更新 README、backend README、frontend README、TODO 與 ROADMAP 對預設 LLM 行為的描述。

## Out of Scope

- 不新增 OpenAI API、vLLM、streaming UI、VLM parser、PDF rendering、production OCR pipeline、Agent runtime 或新的 provider。
- 不改 retrieval algorithm、vector retrieval、rerank、hybrid、`hybrid_rerank`、eval runner 或 sample dataset。
- 不新增 Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、Docker service 或 deployment 設定。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 local demo 預設設定與驗證 patch，不產生新的 release artifact；既有 backend / frontend package version、health test version 與 Docker Compose `DOCURAG_VERSION` 不更新。

## Files likely to change

- `backend/app/core/config.py`
- `backend/tests/test_llm.py`
- `backend/tests/test_rag.py`
- `scripts/demo-smoke-test.ps1`
- `.env.example`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] 未設定 `DOCURAG_LLM_PROVIDER` 時，`get_rag_provider()` 會建立 `OllamaLlmProvider`。
- [x] `DOCURAG_LLM_PROVIDER=` 空值仍可關閉 LLM provider，保留 deterministic baseline path。
- [x] Ollama 不可用時 `/rag/query` 仍回傳 fallback answer、citations 與 retrieved chunks，不 hard fail。
- [x] `scripts/demo-smoke-test.ps1` 預設模式不會因 default-on LLM success / fallback 而誤判失敗；`-RunLlm` 仍要求真正 `ollama/qwen3.5:4b` 成功。
- [x] README / backend README / frontend README / TODO / ROADMAP 已同步說明 default-on Ollama 與 fallback 行為。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `rg -n "20-12|DOCURAG_LLM_PROVIDER|LLM unavailable fallback|default-on Ollama|deterministic baseline" README.md backend/README.md frontend/README.md TODO.md docs/ROADMAP.md tasks/phase-20-interview-mvp-packaging/20-12-default-llm-answer.md`
- `git diff --check`

## Validation Result

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`129 passed`（僅 pytest cache 權限警告）。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 通過，answer source 為 `LLM unavailable fallback`、retrieval source 為 `keyword baseline`。
- Ticket 相關 `rg` 通過。
- `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
