# 30-01 VLM Response and Multi Upload Hardening

## Goal

修正本機 Ollama VLM parser 常見回覆格式造成的 `vlm_invalid_response` fallback，並讓後台知識庫管理的檔案選擇支援多檔，前端依序執行既有 upload / OCR / parser / vector indexing 流程。

## Scope

- 加強 `vlm_invoice` adapter 對 Ollama `/api/generate` 實際回覆的解析容錯。
- 支援 markdown fenced JSON、`thinking` 欄位中的 JSON、數字字串、`confidence=high/medium/low` 與 line item `total` / `total_price` / `subtotal` alias。
- 保持 `DocumentFields` / `ExtractedField` / `ParserResult` 既有 schema，不新增平行 schema。
- 後台 Admin / Analyst ingestion file input 改成可選多個檔案。
- 多檔上傳由 frontend 依序呼叫現有 API；每個檔案仍走既有 source router、provider-selected OCR、VLM-first parser 與 best-effort vector indexing。
- 更新 focused backend tests、frontend build validation 與相關文件紀錄。

## Out of Scope

- 不新增 async worker、queue、Redis、NATS、DB schema、batch upload API 或 production indexing pipeline。
- 不新增 OpenAI SDK、vLLM serving、streaming、function calling 或 production VLM parser dashboard。
- 不新增 PDF rendering、image preprocessing、多頁 parser pipeline、table reconstruction 或人工修正 workflow。
- 不修改 Agent planner / tool allowlist、RAG ranking、Qdrant indexing service 行為或 demo auth role model。
- 不 bump release version；這是 v0.29.0 之後的 focused hardening ticket。

## Release Impact

- Target version: `v0.29.0` follow-up hardening。
- Version bump required: no。
- 原因：本 ticket 只強化現有 parser adapter 與 frontend ingestion ergonomics，不形成完整 release sync，不修改 `/health` version、package version 或 Docker Compose `DOCURAG_VERSION`。

## Files likely to change

- `backend/app/services/document_parser.py`
- `backend/tests/test_document_parser.py`
- `frontend/src/App.vue`
- `README.md`
- `README_DEV.md`
- `frontend/README.md`
- `backend/README.md`
- `docs/api.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `tasks/phase-30-parser-ingestion-hardening/30-01-vlm-response-and-multi-upload-hardening.md`

## Acceptance Criteria

- [x] Ollama 回傳 fenced JSON 時，parser 可抽出 JSON object，不再 fallback 成 `vlm_invalid_response`。
- [x] Ollama 回傳 JSON 在 `thinking` 欄位、`response` 為空時，parser 可抽出 JSON object。
- [x] VLM payload 中金額數字字串會正規化為 number，`confidence` 常見文字等級會正規化為 `0` 到 `1`。
- [x] VLM line item 的 `total` / `total_price` / `subtotal` alias 會映射到既有 `amount` 欄位。
- [x] 後台檔案選擇支援多檔，submit 後依序處理每個檔案，並顯示整批完成 / 部分失敗摘要。
- [x] 單檔既有 mock OCR fallback 行為仍可用；多檔遇到個別 OCR 失敗時不阻斷整批後續檔案。
- [x] 不新增 worker、DB schema、batch API 或 production parser dashboard。

## Validation

- `python -m pytest backend/tests/test_document_parser.py -q`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Browser check local frontend：後台 file input 可選多檔、upload button 狀態合理、桌面與手機寬度無明顯 overflow。
- `rg -n "vlm_invalid_response|extract_invoice_fields|multi|multiple|selectedFiles|VLM Response and Multi Upload" backend/app backend/tests frontend/src frontend/README.md backend/README.md TODO.md tasks/phase-30-parser-ingestion-hardening`
- `git diff --check`

## Validation Result

- `python -m pytest backend/tests/test_document_parser.py -q` 通過，`15 passed`（僅 pytest cache 權限警告）。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`193 passed`（僅 pytest cache 權限警告）。
- `npm.cmd run build` 通過。
- Browser check 通過：`1280x900` 與 `390x844` 皆確認後台 file input `multiple=true`、未選檔 upload button disabled、horizontal overflow `0`。
- Ticket `rg` 通過。
- `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
