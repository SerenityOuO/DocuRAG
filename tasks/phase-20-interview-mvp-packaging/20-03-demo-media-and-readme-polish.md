# 20-03 Demo Media and README Polish

## Goal

補齊面試展示素材，讓 README 與 demo 文件能用截圖或 GIF 直接展示 UI、RAG citation trace 與 eval summary，降低面試官理解成本。

## Scope

- 新增或更新 README 的面試導覽段落，整理 5 到 10 分鐘 demo 順序。
- 產出並放置 demo 截圖或 GIF，至少覆蓋 frontend health / document flow、RAG answer + citation、retrieval trace panel 與 eval summary。
- 更新 `docs/demo-script.md`，引用新增的截圖 / GIF 或文件位置。
- 若使用 Browser / Playwright 產生截圖，只針對 local dev target，不新增 production UI route。
- 媒體檔必須是 repo 可接受大小，且不得包含真實個資、公司敏感資料或本機 token。

## Out of Scope

- 不重設 UI 設計系統，不大改 frontend layout。
- 不新增 production eval dashboard、export UI、live eval runner 或 backend API。
- 不實作 Auth、RBAC、DB、Redis、NATS、worker、Agent runtime、`hybrid_rerank` runtime 或 deployment。
- 不新增外部依賴，除非後續 ticket 明確要求並通過確認。

## Release Impact

- Target version: `v0.20.0` interview MVP packaging backlog。
- Version bump required: no。
- 原因：本 ticket 補齊 demo media / README polish；完整 Phase 20 release sync 留到 `20-04`。

## Files likely to change

- `README.md`
- `docs/demo-script.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `docs/` 或 `sample-data/` 底下的 demo media assets

## Acceptance Criteria

- [ ] README 有清楚的 5 到 10 分鐘 interview demo path。
- [ ] 至少有一組截圖或 GIF 展示 frontend trace / citation / eval 可觀測性。
- [ ] Demo media 不包含真實敏感資料或本機 secrets。
- [ ] 文件能區分 baseline demo、optional vector / rerank / hybrid eval，以及尚未實作的 `hybrid_rerank` runtime。

## Validation

- `npm.cmd run build`（於 `frontend/`）
- Browser 檢查 local frontend demo view 可正常顯示。
- `rg -n "screenshot|GIF|demo media|interview demo|面試" README.md docs/demo-script.md docs/ROADMAP.md TODO.md`
- `git diff --check`
