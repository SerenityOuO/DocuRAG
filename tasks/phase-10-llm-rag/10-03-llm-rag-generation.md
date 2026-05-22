# 10-03 LLM-Based RAG Generation

## Goal

在既有 keyword retrieval 與 citations contract 上加入 LLM answer generation，讓 `/rag/query` 可以用 retrieved chunks 產生自然語言回答並保留 citation trace。

## Scope

- 在 `RagProvider` 邊界內新增 LLM generation path。
- Prompt 必須只使用 retrieved chunks 與 query，不把未檢索內容當成事實。
- 回應保留現有 `answer`、`citations`、`retrieved_chunks` contract。
- 設計 provider disabled / LLM unavailable 的明確錯誤或顯式 fallback 策略。
- 加入測試覆蓋 prompt assembly、citation preservation 與 LLM failure。

## Out of Scope

- 不新增 embedding、Qdrant 或 rerank。
- 不實作 streaming、多輪記憶、agent tool use 或 function calling。
- 不新增 worker queue、Redis、NATS、資料庫 schema、登入或權限。
- 不改 OCR pipeline。

## Files likely to change

- `backend/app/services/rag.py`
- `backend/app/services/llm.py`
- `backend/app/api/routes/rag.py`
- `backend/tests/test_rag.py`
- `docs/LOCAL_DEV_SETUP.md`
- `backend/README.md`

## Acceptance Criteria

- [ ] `/rag/query` 可在 LLM enabled 時使用 retrieved chunks 產生回答。
- [ ] citations 與 retrieved chunks 仍與原 chunk metadata 對齊。
- [ ] LLM unavailable 時不產生誤導性回答。
- [ ] 測試覆蓋 prompt、成功生成、失敗處理與 citation trace。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- 以本機模型服務或 mock LLM client 執行 RAG query smoke。
