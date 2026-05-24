# 24-04 Frontend Fields Surface

## Goal

在 Admin / Analyst ingestion surface 顯示 parser structured fields，讓面試 demo 可以看到 OCR 後的 invoice JSON / 欄位摘要，而 Viewer Chat surface 維持只查詢知識庫。

## Scope

- 在既有 Admin / Analyst ingestion surface 加入「解析欄位」操作或狀態區。
- 顯示 parser status、document type、invoice number、vendor、issue date、total amount、currency 與 parser source。
- 顯示欄位層級 confidence / source text 的簡化資訊；詳細 raw JSON 可留在 backend API / CLI。
- Parser 尚未執行、失敗或欄位缺失時要有清楚狀態。
- Viewer Chat first surface 不得出現 parse / upload / OCR 操作。
- 更新 `frontend/README.md`、`TODO.md` 與 `docs/ROADMAP.md`。

## Out of Scope

- 不新增 frontend route、auth gate、role guard、i18n framework 或外部 UI 依賴。
- 不修改 backend parser algorithm 或 API contract。
- 不新增真正 VLM、LLM parser、worker、DB、Redis、NATS、Agent runtime 或 deployment。
- 不實作人工修正欄位、欄位版本紀錄、audit log、表格完整重建或 production parser dashboard。
- 不把 parser 結果接成 default RAG answer source 或 SQL query tool。

## Release Impact

- Target version: `v0.24.0`。
- Version bump required: no。
- 原因：本 ticket 完成 Phase 24 frontend slice；完整 release sync 留給 `24-05`。

## Files likely to change

- `frontend/src/App.vue`
- `frontend/src/api/client.ts`
- `frontend/src/styles.css`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Viewer Chat 預設入口不顯示 upload、OCR、parse 或 ingestion 操作。
- [ ] Admin / Analyst ingestion surface 可觸發 parse 並顯示 structured fields 摘要。
- [ ] Parser loading / success / failure / missing fields 狀態清楚。
- [ ] UI 不宣稱已完成 production VLM parser 或正式 RBAC。
- [ ] Desktop 與 mobile 檢查無 horizontal overflow。

## Validation

- `npm.cmd run build`
- Browser 檢查 local frontend：Viewer Chat first、Admin / Analyst ingestion surface 顯示 structured fields、桌面與手機寬度無 horizontal overflow。
- `rg -n "structured fields|欄位解析|Parser|parse|fields|Viewer Chat|Admin / Analyst" frontend/src frontend/README.md TODO.md docs/ROADMAP.md tasks/phase-24-vlm-parser-mvp/24-04-frontend-fields-surface.md`
- `git diff --check`
