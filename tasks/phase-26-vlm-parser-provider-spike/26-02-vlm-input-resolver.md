# 26-02 VLM Input Resolver

## Goal

新增 Phase 26 VLM-first parser 的最小 input resolver，讓預設優先的 VLM adapter 可以從既有上傳文件中取得 demo-safe image input；本 ticket 不呼叫 VLM，不改 parser output。

## Scope

- 實作最小 VLM input resolver building block，從既有 document metadata / uploaded file path 解析可用 image input。
- 只支援已存在於 `data/uploads/` 的 demo-safe image file，例如 `.png` / `.jpg` / `.jpeg`。
- unsupported file type、missing file、path traversal 風險或檔案不可讀時，回傳明確 failure reason。
- Resolver output 必須包含 `document_id`、normalized file path / bytes reference、mime type、input source 與 fallback reason。
- 補 backend tests 覆蓋 supported image、missing file、unsupported extension 與 unsafe path。
- 保留 Phase 24 deterministic parser 作為後續 VLM adapter 的 fallback building block；本 ticket 不改 `POST /documents/{document_id}/parse` 行為。

## Out of Scope

- 不實作 PDF rendering、multi-page image extraction、image preprocessing、deskew、layout detection 或 OCR accuracy tuning。
- 不呼叫 VLM、Ollama、OpenAI-compatible endpoint 或任何外部服務。
- 不新增 frontend UI、API endpoint、worker、queue、DB schema、Redis、NATS、Auth、RBAC 或 deployment 設定。
- 不修改 Agent planner / tools；Agent 仍只透過 parser result 消費 structured fields。

## Release Impact

- Target version: `v0.26.0`。
- Version bump required: no。
- 原因：本 ticket 只新增 VLM input resolver building block；完整 VLM parser demo / release sync 留給 `26-05`。

## Files likely to change

- `backend/app/services/`
- `backend/tests/`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] VLM input resolver 可對支援的 image upload 回傳可交給 adapter 的 input descriptor。
- [ ] 不支援或不可讀的檔案會回傳明確 failure reason，不丟出未處理例外。
- [ ] Resolver 不會讀取 upload root 以外的路徑。
- [ ] Backend tests 覆蓋 success / failure / unsafe path cases。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "VlmInput|vlm input|input resolver|unsupported_file|unsafe path|DOCURAG_VLM" backend/app backend/tests TODO.md docs/ROADMAP.md tasks/phase-26-vlm-parser-provider-spike/26-02-vlm-input-resolver.md`
- `git diff --check`
