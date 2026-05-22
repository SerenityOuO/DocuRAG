# 10-01 Qwen3.5 Ollama Provider Decision

## Goal

依 `goal.md` 固定第一版本機大模型路線：LLM 使用 Ollama `qwen3.5:4b`，VLM 目標同樣使用 Ollama `qwen3.5:4b`，並把 Phase 10 的 RAG generation provider 決策收斂到可實作的設定。

## Scope

- 將第一版 LLM provider 選定為 `ollama`。
- 將第一版 RAG generation model 選定為 `qwen3.5:4b`。
- 記錄 `qwen3.5:4b` 也是後續 VLM / Parser 目標模型，但不在本 ticket 實作文件解析。
- 定義必要環境變數：
  - `DOCURAG_LLM_PROVIDER=ollama`
  - `DOCURAG_LLM_BASE_URL=http://127.0.0.1:11434`
  - `DOCURAG_LLM_MODEL=qwen3.5:4b`
  - `DOCURAG_VLM_PROVIDER=ollama`
  - `DOCURAG_VLM_MODEL=qwen3.5:4b`
- 明確記錄：vLLM 保留為後續 LLMOps / serving / latency 展示；第一版優先 Ollama `qwen3.5:4b`，以降低 Windows 本機整合成本與 RTX 5070 Ti 16GB VRAM 壓力。
- 記錄 OpenAI-compatible API 作為較大模型或替代 serving 的 fallback 方向。
- 記錄較新的大型 Qwen 系列可作為 fallback 方向，但未公開或未上架的 4B 型號不得寫入預設路線。

## Out of Scope

- 不實作 backend LLM client。
- 不下載或啟動 Ollama 模型。
- 不實作 VLM parser、PDF rendering、image preprocessing 或 JSON 欄位抽取。
- 不新增 embedding、Qdrant、rerank、worker、Redis、NATS、資料庫 schema、登入或權限。

## Release Impact

- Target version: `v0.10.0`。
- Version bump required: no，本 ticket 只做 Phase 10 provider decision。
- 完成後更新 TODO 與 ROADMAP，標示 Phase 10 尚未 release complete。

## Files likely to change

- `goal.md`
- `.env.example`
- `docs/ROADMAP.md`
- `docs/LOCAL_DEV_SETUP.md`
- `README.md`
- `TODO.md`

## Acceptance Criteria

- [ ] 文件明確列出第一版 LLM provider 是 Ollama。
- [ ] 文件明確列出第一版 LLM model 是 `qwen3.5:4b`。
- [ ] 文件明確列出 VLM 目標 model 是 `qwen3.5:4b`，且標示 VLM parser 另由後續 ticket 實作。
- [ ] 文件說明 Windows / RTX 5070 Ti / vLLM 限制與 fallback 策略。
- [ ] 後續 implementation ticket 可直接沿用 env vars。

## Validation

- `nvidia-smi`
- `ollama list`
- `ollama show qwen3.5:4b`
- `curl http://127.0.0.1:11434/api/tags`
- 文件 review。
