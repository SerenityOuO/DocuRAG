# Chunking Strategy Runtime

## Goal

新增至少一條可驗證的 chunking strategy runtime，讓 RAG indexing 不再只依賴單一 demo chunking 方式。

## Scope

- 實作 fixed-size 與 semantic 或 parent-child 中至少一種進階 strategy。
- 讓 indexing request / config 可以明確選擇 strategy，並保存 chunking metadata。
- 補 backend tests，驗證不同 strategy 的 chunk output 與 metadata。
- 保留既有 demo fallback，不破壞現有 RAG smoke。

## Out of Scope

- 不新增 eval dashboard 或自動 strategy tuning。
- 不新增 LLM-based semantic segmentation，除非已在 ticket scope 明確選定且可 fallback。
- 不修改 OCR / parser / Agent planner。

## Release Impact

- Target version: `v0.35.0`
- Version bump required: no
- 原因：這是 Phase 35 runtime ticket，版本同步留到 `35-04`。

## Files likely to change

- `backend/app/services/`
- `backend/tests/`
- `docs/api.md`
- `TODO.md`
- `tasks/phase-35-rag-indexing-quality/35-02-chunking-strategy-runtime.md`

## Acceptance Criteria

- [x] Indexing flow 可選擇 chunking strategy。
- [x] Chunk metadata 保存 strategy name、token / char count、source type 與 page number。
- [x] Backend tests 覆蓋至少兩種 strategy 的 output 差異。
- [x] Existing demo smoke 不因新 strategy hard fail。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "chunking strategy|fixed|semantic|parent_child|chunk metadata" backend docs TODO.md tasks/phase-35-rag-indexing-quality`
- `git diff --check`

## Validation Result

- Passed: focused backend tests `60 passed` (`tests/test_vector_indexing.py tests/test_documents.py`)
- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` (`234 passed`, 1 pytest cache warning)
- Passed: `rg -n "chunking strategy|fixed|semantic|parent_child|chunk metadata" backend docs TODO.md tasks/phase-35-rag-indexing-quality`
- Passed: `git diff --check`（僅 Windows LF/CRLF 提示）
