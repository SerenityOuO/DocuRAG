# 17-02 Frontend Retrieval Trace Panel

## Goal

在既有 RAG result UI 中加入 compact retrieval trace panel，讓 demo 使用者可以看見 answer source、retrieval source、strategy metadata、candidate trace 與 fallback reason。此 ticket 只讀既有 response，不新增 backend API。

## Scope

- 在現有 frontend RAG result 區塊新增 retrieval trace panel / table，顯示既有 response 中可取得的 metadata。
- 顯示 keyword baseline、optional vector、`vector_rerank` 與 `hybrid` metadata；缺少 metadata 時 graceful hidden 或顯示清楚 fallback state。
- 保留既有 upload、OCR、document list、RAG chat 與 deterministic baseline flow。
- 更新 frontend README、`TODO.md` 與 `docs/ROADMAP.md` 的 Phase 17 status。

## Out of Scope

- 不修改 backend API 或 response schema；不得為了 UI 新增 endpoint。
- 不接 live eval runner、不做 eval dashboard、不做 strategy comparison page。
- 不實作 `hybrid_rerank`、BM25 dependency、LLM-as-judge、answer faithfulness 或 citation quality scoring。
- 不新增外部 UI library、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、deployment 設定或 Docker service。

## Files likely to change

- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `frontend/src/api/client.ts`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-17-retrieval-trace-ui/17-02-frontend-retrieval-trace-panel.md`

## Acceptance Criteria

- [ ] RAG result UI 可顯示 answer source 與 retrieval source。
- [ ] Retrieved chunks / candidates 可顯示 rank、score、document id、chunk id、filename 與 text preview。
- [ ] 若 response 帶有 rerank metadata，UI 可顯示 rerank provider、rerank status、rerank score 或 fallback reason。
- [ ] 若 response 帶有 hybrid metadata，UI 可顯示 merge policy、branches、branch ranks、merged score、dedupe count 或 branch failure。
- [ ] Missing metadata 不造成 UI error，baseline keyword demo 仍可使用。

## Validation

- `npm.cmd run build`（於 `frontend/`）
- 若本機 dev server 可用，使用 Browser 檢查 RAG result UI 不重疊、不破版，且 baseline result 仍可讀。
- `git diff --check`

## Release Impact

- Target version: `v0.17.0`。
- Version bump required: no。
- 原因：本 ticket 只新增 frontend trace visibility，尚未完成整個 Phase 17 release sync；版本同步留到 Phase 17 release ticket。
