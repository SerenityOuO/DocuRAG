# 26-03 VLM Parser Adapter

## Goal

實作 disabled-by-default `vlm_invoice` parser adapter，透過 Phase 26 input resolver 呼叫可設定的 VLM provider，並將 VLM 欄位抽取結果正規化為既有 `DocumentFields` / `ParserResult` schema。

## Scope

- 新增最小 VLM parser adapter，只有在 `DOCURAG_VLM_PROVIDER` 明確設定時才啟用。
- Adapter 使用 Phase 26 input resolver 取得 demo-safe image input。
- 定義 VLM prompt / response parsing 的最小邊界：要求 provider 回傳 JSON object，欄位對齊 invoice number、vendor、issue date、total amount、tax amount、currency 與 line item summary。
- 將 provider response 正規化成既有 `DocumentFields`、`ExtractedField` 與 `ParserResult`，並標記 `parser_source=vlm_invoice`。
- VLM disabled、timeout、provider unavailable、invalid JSON、missing required fields 或 low confidence 時，回到 deterministic parser fallback，保留 `fallback_reason`。
- 補 backend tests 使用 fake provider / stub，不要求本機真的啟動 VLM。

## Out of Scope

- 不新增 default-on VLM parser；未設定 env 時仍走 deterministic parser。
- 不新增 OpenAI SDK、Ollama package、外部依賴、streaming、function calling 或 autonomous Agent planner。
- 不新增 PDF rendering、image preprocessing、多頁 parser pipeline、table reconstruction、human correction 或 parser dashboard。
- 不修改 Agent tool contract、RAG ranking、Qdrant indexing、eval runner、Viewer Chat default path、DB、worker、Redis、NATS、Auth 或 RBAC。

## Release Impact

- Target version: `v0.26.0`。
- Version bump required: no。
- 原因：本 ticket 新增 disabled-by-default VLM parser adapter；完整 demo / version sync 留給 `26-05`。

## Files likely to change

- `backend/app/core/`
- `backend/app/services/`
- `backend/app/schemas/`
- `backend/tests/`
- `docs/api.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] 未設定 `DOCURAG_VLM_PROVIDER` 時，parser 預設行為仍為 deterministic fallback。
- [ ] 設定 fake / stub VLM provider 時，adapter 可產生 `parser_source=vlm_invoice` 的 `ParserResult`。
- [ ] Invalid provider response 會明確 fallback，不產生假欄位。
- [ ] Backend tests 覆蓋 VLM success、disabled fallback、timeout / provider failure、invalid JSON 與 missing fields。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "vlm_invoice|DOCURAG_VLM_PROVIDER|VlmParser|DocumentFields|ParserResult|fallback_reason|deterministic_invoice" backend/app backend/tests docs/api.md TODO.md docs/ROADMAP.md tasks/phase-26-vlm-parser-provider-spike/26-03-vlm-parser-adapter.md`
- `git diff --check`
