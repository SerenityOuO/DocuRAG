# 27-02 OCR / VLM Evidence Alignment

## Goal

讓 Phase 27 demo 的 OCR / VLM 配合方式對齊實務流程：

1. OCR 產生可搜尋文字層。
2. VLM 看圖片，也參考 OCR 文字。
3. VLM 輸出欄位 JSON。
4. 系統把欄位值對回 OCR line / bbox。
5. RAG 使用 OCR chunks。
6. Agent 同時使用 structured fields 與 document chunks。

本 ticket 是 `v0.27.1` patch hardening，目標是把既有 VLM-first parser 從「只看圖片、OCR 只當前置門檻」調整成「圖片 + OCR evidence」的 demo path。這不是 production VLM parser 或完整版面理解系統。

## Scope

- 在 VLM parser request 中加入 compact OCR context，例如 OCR lines、page number、bbox 與 confidence 摘要；VLM 仍必須接收原始圖片。
- 保留既有 VLM JSON 欄位輸出 schema，不新增平行 parser schema。
- 新增或整理欄位 evidence matching：VLM 回傳欄位值後，嘗試在 OCR lines 中找到對應文字，並補上 `source_text`、`source_page`、`source_bbox` 與 trace metadata。
- 未找到 evidence 時要清楚記錄 fallback / evidence state，不可靜默宣稱欄位已對齊 OCR 來源。
- 保留 deterministic parser fallback；VLM provider unavailable、timeout、invalid response、missing fields 或 low confidence 時仍可回到 OCR text based parser。
- RAG / vector indexing 仍使用 OCR chunks，不把 VLM fields 自動混入 retrieval corpus。
- Agent planner / tool allowlist 不變；透過 validation 確認 Agent 同時讀取 `get_document_fields` structured fields 與 `search_documents` OCR chunks。
- 更新 README、backend README、frontend README、docs/api.md、docs/architecture.md、docs/demo-script.md、TODO.md 與 docs/ROADMAP.md 的說法，避免把 OCR / VLM 說成互不相關或完全替代。

## Out of Scope

- 不新增 production VLM parser、OpenAI SDK、function calling、streaming、LLM planner 或新的模型供應商。
- 不新增 PDF rendering、多頁 parser pipeline、image preprocessing、layout analysis、table reconstruction 或人工修正 workflow。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth / RBAC、K8s 或 deployment 設定。
- 不修改 PaddleOCR model selection、OCR engine lifecycle、GPU dependency policy 或 OCR provider API contract。
- 不修改 RAG ranking、hybrid merge、rerank algorithm、Qdrant collection schema 或 eval metrics definition。
- 不允許 Agent 新增任意 SQL、任意 tool execution、delete、reindex、shell command、file system command 或 destructive tools。

## Release Impact

- Target version: `v0.27.1`。
- Version bump required: yes when this ticket is implemented.
- 原因：VLM input、parser trace、field source grounding 與 demo 說法都會改變使用者可觀察行為，完成時應作為 Phase 27 patch release。

## Files likely to change

- `backend/app/services/document_parser.py`
- `backend/app/services/vlm_input.py`
- `backend/app/schemas/documents.py`
- `backend/tests/test_document_parser.py`
- `backend/tests/test_agent.py`
- `scripts/demo-smoke-test.ps1`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/demo-script.md`
- `docs/ROADMAP.md`
- `TODO.md`

## Acceptance Criteria

- [ ] OCR completed document 保留可搜尋 OCR text / OCR lines / chunks，且 RAG response 仍能引用 OCR chunks。
- [ ] VLM request 同時包含原始圖片與 compact OCR context；trace metadata 可看出 VLM 是否收到 OCR evidence。
- [ ] VLM success path 仍輸出既有 `DocumentFields` / `ParserResult` schema，且 `parser_source=vlm_invoice`。
- [ ] VLM 欄位值若能對回 OCR line，欄位結果必須包含 `source_text`、`source_page`、`source_bbox` 或等價 trace metadata。
- [ ] VLM 欄位值若不能對回 OCR line，結果必須清楚標示 evidence unmatched / unavailable，不可假造 page 或 bbox。
- [ ] Deterministic fallback path 仍可用 OCR text / OCR lines 產生欄位結果。
- [ ] Agent run 仍固定使用 `get_document_fields` -> `search_documents` -> `summarize_invoice_fields`，並能在 trace 中看出 structured fields 與 OCR chunks 都被使用。
- [ ] 文件說法明確區分：OCR 是文字層 / retrieval evidence，VLM 是欄位理解 / parser，兩者不是互相替代。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- 若使用 fake VLM provider，需驗證 image + OCR context success path。
- `rg -n "ocr context|OCR context|source_bbox|source_page|evidence|vlm_invoice|get_document_fields|search_documents" backend/app backend/tests README.md backend/README.md frontend/README.md docs/api.md docs/architecture.md docs/demo-script.md TODO.md docs/ROADMAP.md tasks/phase-27-aggressive-defaults`
- `git diff --check`
