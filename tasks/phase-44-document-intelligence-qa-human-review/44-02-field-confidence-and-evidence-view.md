# Field Confidence and Evidence View

## Goal

在 Admin / Analyst 文件解析結果中呈現欄位 confidence、evidence、source page 與 source bbox，讓 VLM / OCR 抽取結果可被檢查。

## Scope

- 擴充 structured fields surface 或 API response，顯示 confidence、source_text、source_page、source_bbox、parser_source 與 fallback reason。
- 對 evidence unavailable / unmatched 給出清楚 UI 或 trace 呈現。
- 補充測試與 Browser validation，確認 desktop / mobile 不溢出。
- 保留 Viewer Chat read-only 查詢主線，不把 QA surface 放到前台。

## Out of Scope

- 不新增人工修正寫入、不新增 golden labels、不新增 parser accuracy eval。
- 不新增新的 OCR / VLM provider 或改變 parser ranking。
- 不新增 full document image annotation UI。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 44 UI / evidence visibility ticket，版本同步留到 `44-05`。

## Files likely to change

- `backend/`
- `frontend/`
- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-44-document-intelligence-qa-human-review/44-02-field-confidence-and-evidence-view.md`

## Acceptance Criteria

- [ ] Admin / Analyst 可看到欄位 confidence 與 evidence metadata。
- [ ] Evidence unavailable / unmatched 狀態清楚可見。
- [ ] Browser validation 確認 desktop / mobile 無 horizontal overflow。

## Validation

- Backend tests if API changes。
- Frontend build。
- Browser validation。
- `rg -n "confidence|source_text|source_page|source_bbox|evidence_unmatched|evidence_unavailable" backend frontend docs README_DEV.md TODO.md tasks/phase-44-document-intelligence-qa-human-review`
- `git diff --check`
