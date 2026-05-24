# 26-03 VLM Parser Adapter

## Goal

實作 VLM-first `vlm_invoice` parser adapter，透過 Phase 26 input resolver 呼叫可設定的 VLM provider，並將 VLM 欄位抽取結果正規化為既有 `DocumentFields` / `ParserResult` schema。

## Scope

- 新增最小 VLM parser adapter，Phase 26 後 parser 預設先嘗試 `vlm_invoice`。
- 設定 VLM provider 預設值與 timeout guardrail；provider unavailable 或未回應時必須明確 fallback，不可讓 demo 卡死。
- Adapter 使用 Phase 26 input resolver 取得 demo-safe image input。
- 定義 VLM prompt / response parsing 的最小邊界：要求 provider 回傳 JSON object，欄位對齊 invoice number、vendor、issue date、total amount、tax amount、currency 與 line item summary。
- 將 provider response 正規化成既有 `DocumentFields`、`ExtractedField` 與 `ParserResult`，並標記 `parser_source=vlm_invoice`。
- VLM timeout、provider unavailable、invalid JSON、missing required fields 或 low confidence 時，回到 deterministic parser fallback，保留 `fallback_reason`。
- `deterministic_invoice` 可保留為 explicit debug / validation override，但不得再作為未設定 VLM 時的預設解析路徑。
- 補 backend tests 使用 fake provider / stub，不要求本機真的啟動 VLM。

## Out of Scope

- 不新增 production-grade VLM parser；Phase 26 的 default-on 只限 VLM-first demo path 與 fallback trace。
- 不新增 OpenAI SDK、Ollama package、外部依賴、streaming、function calling 或 autonomous Agent planner。
- 不新增 PDF rendering、image preprocessing、多頁 parser pipeline、table reconstruction、human correction 或 parser dashboard。
- 不修改 Agent tool contract、RAG ranking、Qdrant indexing、eval runner、Viewer Chat default path、DB、worker、Redis、NATS、Auth 或 RBAC。

## Release Impact

- Target version: `v0.26.0`。
- Version bump required: no。
- 原因：本 ticket 新增 VLM-first parser adapter；完整 demo / version sync 留給 `26-05`。

## Files likely to change

- `backend/app/core/`
- `backend/app/services/`
- `backend/app/schemas/`
- `backend/tests/`
- `docs/api.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Parser 預設行為會先嘗試 `vlm_invoice`，不再以 `deterministic_invoice` 作為預設路徑。
- [ ] 設定 fake / stub VLM provider 時，adapter 可產生 `parser_source=vlm_invoice` 的 `ParserResult`。
- [ ] VLM provider unavailable / timeout 時會 fallback 到 `deterministic_invoice`，並保留 `fallback_reason`。
- [ ] Invalid provider response 會明確 fallback，不產生假欄位。
- [ ] Backend tests 覆蓋 VLM success、provider unavailable fallback、timeout / provider failure、invalid JSON、missing fields 與 explicit deterministic override。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "vlm_invoice|DOCURAG_VLM_PROVIDER|VlmParser|DocumentFields|ParserResult|fallback_reason|deterministic_invoice" backend/app backend/tests docs/api.md TODO.md docs/ROADMAP.md tasks/phase-26-vlm-parser-provider-spike/26-03-vlm-parser-adapter.md`
- `git diff --check`
