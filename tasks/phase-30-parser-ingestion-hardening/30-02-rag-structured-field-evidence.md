# 30-02 RAG Structured Field Evidence Hardening

## Goal

讓 `/rag/query` 在已檢索到文件 chunk 時，也能把同一文件已保存的 invoice structured fields 當成 read-only evidence 放入回答上下文，避免欄位面板已有 `total_amount`，但 Viewer Chat / RAG 回答因 retrieved chunks 沒包含金額而誤判資訊不足。

## Scope

- 補強 keyword query normalization，讓「總共多少」、「發票總共多少」、「發票金額」、「應付金額」等中文問法更容易命中發票金額 chunk。
- 在 `KeywordRagProvider` 產生回答時，針對 retrieved chunks 對應的文件讀取已保存 `ParserResult.fields`。
- structured fields 只作為 prompt / fallback answer 的 read-only evidence，不轉成 retrieval chunks、不寫入 Qdrant、不改變 ranking。
- field evidence 只附加已解析且有值的 invoice MVP 欄位：vendor、invoice number、issue date、total amount、tax amount、currency。
- 補上 backend tests，驗證 LLM prompt 會包含 retrieved chunk 對應的 structured amount evidence。

## Out of Scope

- 不新增 field indexing policy、dedupe key、Qdrant payload schema 或 production indexing pipeline。
- 不新增 DB schema、migration、Redis、NATS、worker、batch API、正式 RBAC 或 deployment 設定。
- 不改 Agent planner / tool allowlist，不讓 Agent 直接呼叫 VLM 或任意工具。
- 不做 LLM-as-judge、answer correctness scoring、citation quality scoring 或 production eval dashboard。
- 不 bump release version；本 ticket 是 v0.29.0 後續 focused hardening。

## Release Impact

- Target version: `v0.29.0` follow-up hardening。
- Version bump required: no。
- 原因：只補強既有 RAG prompt evidence 與 query normalization，不改 `/health` version、package version、Docker Compose `DOCURAG_VERSION` 或 release artifact。

## Files likely to change

- `backend/app/services/rag.py`
- `backend/tests/test_rag.py`
- `TODO.md`
- `tasks/phase-30-parser-ingestion-hardening/30-02-rag-structured-field-evidence.md`

## Acceptance Criteria

- [x] `/rag/query` 的 LLM prompt 在 retrieved chunks 對應文件已有 parsed fields 時，包含 structured invoice fields evidence。
- [x] structured field evidence 包含 `total_amount` 與 `currency`，讓「總共多少」類問題不只依賴 OCR chunk 是否剛好含金額。
- [x] 沒有 parsed fields 時維持原本 retrieved chunks-only 行為。
- [x] 不把 structured fields 寫入 chunks、Qdrant 或新的 schema。
- [x] 補上中文總額問法 alias，降低「總共多少」查詢只命中 supplier chunk 的機率。

## Validation

- `python -m pytest backend/tests/test_rag.py -q`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "structured field|Structured fields|總共多少|發票總共|llm_prompt_field_evidence_count" backend/app backend/tests TODO.md tasks/phase-30-parser-ingestion-hardening`
- `git diff --check`

## Validation Result

- `python -m pytest backend/tests/test_rag.py -q` 通過，`21 passed`（僅 pytest cache 權限警告）。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`194 passed`（僅 pytest cache 權限警告）。
- Ticket `rg` 通過。
- `git diff --check` 通過。
