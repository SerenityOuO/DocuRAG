# Human Correction and Golden Labels

## Goal

新增 demo-safe human correction / golden labels flow，讓 Analyst 可以修正欄位並把結果保存為後續 parser eval 的標準答案。

## Scope

- 新增 correction data model 或 local metadata path，保存 corrected value、reviewer、reason、version 與 timestamp。
- 新增或文件化 correction API / UI，依 ticket scope 選擇最小可驗證做法。
- 將 corrected fields 匯出為 golden labels artifact，供 `44-04` parser field accuracy eval 使用。
- 保留 project access / role guard，Viewer 不可修改 correction。

## Out of Scope

- 不新增 production annotation workflow、多人審核、版本衝突解決或外部 labeling service。
- 不把 correction 自動回寫到 model training 或 production parser prompt。
- 不新增 destructive edit / delete flow。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 44 correction artifact ticket，版本同步留到 `44-05`。

## Files likely to change

- `backend/`
- `frontend/`
- `docs/`
- `sample-data/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-44-document-intelligence-qa-human-review/44-03-human-correction-and-golden-labels.md`

## Acceptance Criteria

- [ ] Analyst / Admin 可保存 demo-safe corrected fields 或 golden label artifact。
- [ ] Viewer 無法修改 correction。
- [ ] Golden labels 包含 field name、corrected value、source document 與 version metadata。

## Validation

- Backend tests。
- Frontend build if UI changes。
- Correction / golden label smoke。
- `rg -n "human correction|corrected value|golden labels|reviewer|version|field accuracy" backend frontend docs sample-data README_DEV.md TODO.md tasks/phase-44-document-intelligence-qa-human-review`
- `git diff --check`
