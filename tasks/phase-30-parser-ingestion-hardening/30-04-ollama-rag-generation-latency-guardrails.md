# 30-04 Ollama RAG Generation Latency Guardrails

## Goal

修正 default `/rag/query` 在使用 Ollama `qwen3.5:4b` generation 時，因 thinking-capable model 預設輸出大量 `thinking` tokens 或無上限生成，導致 Viewer Chat 單次 RAG 回答可能等待數十秒到 87 秒以上的問題。完成後，RAG generation 應保留 source-grounded answer 能力，但預設延遲要適合本機面試 demo。

## Scope

- 在 Ollama LLM provider request 中加入 demo-safe generation guardrails：
  - 預設關閉 thinking，例如 request payload 帶 `think=false`。
  - 預設限制 generation 長度，例如 `options.num_predict=512`。
- 將上述設定暴露為 backend settings / env，讓本機 debug 可明確 override；預設值必須偏向低延遲 demo。
- 保留現有 `/rag/query` prompt、structured field evidence、citations、trace metadata 與 fallback 行為。
- 在 LLM trace metadata 中保留足夠資訊，讓使用者能判斷 generation 是否使用 thinking、num_predict 或其他 output limit。
- 補上單元測試，驗證 Ollama `/api/generate` payload 帶有 latency guardrails，且 provider 回傳 `thinking` / 空 `response` 時不會讓 RAG 等待無界生成。
- 更新 README / README_DEV / backend README 或 docs 中的本機 demo 說明，提醒 5070 Ti 等 GPU 仍可能因 thinking tokens 慢，預設 guardrails 是為了 demo latency。

## Out of Scope

- 不更換預設 LLM model，不新增 OpenAI API、vLLM、server-side streaming、frontend streaming UI 或 chat token streaming。
- 不修改 retrieval ranking、Qdrant filtering、rerank algorithm、structured field evidence prompt 或 Agent planner。
- 不新增 production latency dashboard、metrics database、Redis cache、worker、queue、rate limit 或 request cancellation API。
- 不把 thinking 內容顯示到 Viewer Chat；Viewer 仍只看 final answer、answer source、retrieval source 與 citations。
- 不 bump release version；本 ticket 是 `v0.29.0` 後續 focused hardening。

## Release Impact

- Target version: `v0.29.0` follow-up hardening。
- Version bump required: no。
- 原因：只補強既有 Ollama generation request 的 demo latency guardrails 與文件說明，不更新 `/health` version、package version、Docker Compose `DOCURAG_VERSION` 或 release artifact。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/services/llm.py`
- `backend/tests/test_llm.py`
- `backend/tests/test_rag.py`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `tasks/phase-30-parser-ingestion-hardening/30-04-ollama-rag-generation-latency-guardrails.md`

## Acceptance Criteria

- [ ] 未覆寫 env 時，Ollama `/api/generate` request payload 會帶 `think=false` 或等效設定，避免 `qwen3.5:4b` 預設產生大量 hidden thinking。
- [ ] 未覆寫 env 時，Ollama `/api/generate` request payload 會限制 output token 數，例如 `options.num_predict=512`。
- [ ] 可用 env 明確 override thinking 與 num_predict，供 debug / model behavior comparison 使用；文件需說明 override 是手動路徑，不是 demo default。
- [ ] `/rag/query` 使用 LLM generation 時，citations trace metadata 可看出 generation guardrail 設定或至少看出 `llm_generation_status`、model、latency 與 output limit。
- [ ] Ollama generation provider unavailable、timeout、empty response 或 malformed response 時，既有 fallback 到 retrieved evidence 的行為不變。
- [ ] 不新增 streaming UI、OpenAI API、vLLM、DB、worker、queue 或 release version bump。

## Validation

- `python -m pytest backend/tests/test_llm.py backend/tests/test_rag.py -q`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- Optional local latency verification when Ollama is available：以 `DOCURAG_LLM_PROVIDER=ollama`、`DOCURAG_LLM_MODEL=qwen3.5:4b` 啟動 backend，對已索引文件執行 `/rag/query`，確認 trace 中 LLM generation 完成且不再因大量 thinking tokens 等待數十秒。
- `rg -n "llm.*think|num_predict|qwen3.5|Ollama|latency guardrail|DOCURAG_LLM" backend/app backend/tests README.md README_DEV.md backend/README.md docs/ROADMAP.md TODO.md tasks/phase-30-parser-ingestion-hardening/30-04-ollama-rag-generation-latency-guardrails.md`
- `git diff --check`

## References

- Ollama Thinking documentation: `https://docs.ollama.com/capabilities/thinking`
- Ollama Generate API documentation: `https://docs.ollama.com/api/generate`
- Ollama Modelfile parameter reference for `num_predict`: `https://docs.ollama.com/modelfile`
