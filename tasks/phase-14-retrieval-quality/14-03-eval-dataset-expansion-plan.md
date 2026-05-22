# 14-03 Eval Dataset Expansion Plan

## Goal

規劃 retrieval eval dataset 的擴充方向，讓後續 rerank / hybrid search 可以用更有鑑別度的 case 比較品質。此 ticket 只做文件規劃，不改資料集 JSON。

## Scope

- 定義 Phase 14 dataset expansion 原則，例如公開虛構資料、可重跑、可解釋、避免敏感資訊。
- 規劃要新增的 case 類型，例如 lexical mismatch、multi-evidence、near-duplicate chunks、cross-document ambiguity。
- 定義每種 case 的 expected evidence 描述方式，避免綁死未來 runtime 或資料庫 id。
- 規劃 quality gates，例如 dataset schema validation、minimum case count、tag coverage。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 14 dataset planning 說明。

## Out of Scope

- 不修改 `sample-data/eval/retrieval-eval.json`。
- 不新增 sample documents、PDF、image 或真實業務資料。
- 不新增 backend tests、runner logic、API endpoint 或 frontend UI。
- 不新增 rerank、hybrid search、LLM-as-judge、answer faithfulness 或 citation quality scoring。
- 不新增外部依賴、Redis、NATS、worker、async queue 或 PostgreSQL schema。

## Release Impact

- Target version: `v0.14.0`。
- Version bump required: no。
- 原因：本 ticket 只規劃 dataset expansion，不新增資料集內容、不改 runtime，也不形成 release artifact。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md`

## Expansion Plan

### Dataset expansion principles

後續 dataset expansion 應遵守以下原則：

- 只使用公開、虛構、可提交到 repo 的 sample data；不得加入真實合約、發票、個資或敏感業務資料。
- 每個 case 都必須可重跑，並能用 Phase 13 eval runner 的 Hit Rate@K、MRR@K、Recall@K、latency 與 failure count 比較。
- Query、expected answer 與 expected evidence 都必須可解釋，讓失敗案例能回推是 lexical、semantic、ranking 或 ambiguity 問題。
- Expected evidence 不應綁死未來資料庫 id；可以用 document fixture name、document type、field/value、page hint、evidence description 與 tag 表示。
- Dataset schema 應維持向後相容；真正新增 JSON items 必須由後續 implementation / dataset ticket 執行。

### Planned eval case types

| Case type | Purpose | Expected evidence design |
|---|---|---|
| lexical mismatch | 測試 query 與 chunk 詞彙不完全相同時，retrieval 是否能找到語意相關 evidence。 | 用同義詞、縮寫或改寫問法描述問題；expected evidence 記錄目標 document fixture、欄位名稱、標準值與可接受片段描述，不只依賴 exact keyword。 |
| multi-evidence | 測試回答需要兩個以上 evidence chunks 才完整成立的情境。 | expected evidence 使用 required evidence set，列出每個必要 fact、來源文件描述與欄位/段落提示；future gold chunks 可多筆，但 planning 不先寫入 JSON。 |
| near-duplicate chunks | 測試相似 chunks 之間的 ranking 與去重能力。 | expected evidence 描述可區分的 vendor、日期、版本、金額或條款差異，並記錄 distractor evidence 的特徵，方便未來分析誤召回。 |
| cross-document ambiguity | 測試不同文件都有相近詞彙時，retrieval 是否能依 query 條件鎖定正確文件。 | expected evidence 必須包含 disambiguation cues，例如 document type、fixture name、party/vendor、日期或金額條件；避免只寫模糊答案。 |
| numeric / table lookup | 測試金額、數量、稅額、日期等結構化資訊是否被正確召回。 | expected evidence 記錄 normalized value、原始文字提示與欄位名稱，未來可對 OCR / parser / chunking 造成的格式差異做標記。 |

### Quality gates

後續真正擴充 dataset JSON 前，至少應滿足：

- Schema validation 必須通過，且新增欄位若非必需應放在 `metadata`。
- 第一版擴充建議至少新增 `12` 個 cases，且 lexical mismatch、multi-evidence、near-duplicate chunks、cross-document ambiguity 每類至少 `2` 個。
- 每個 item 必須有 `metadata.difficulty` 或等價 tag，並標示 case type。
- 每個 item 都必須有 expected evidence 描述，避免只有 expected answer。
- Dataset 不得包含真實個資、真實公司敏感資訊或不可公開文件內容。
- 擴充後必須能跑 baseline keyword eval；optional vector eval 仍需明確 env 與 Qdrant preflight，不可 default-on。

本 ticket 不修改 `sample-data/eval/retrieval-eval.json`；上述內容只是 future dataset ticket 的 planning input。

## Acceptance Criteria

- [x] Dataset expansion 原則已記錄。
- [x] 至少四種 future eval case 類型已定義。
- [x] 每種 case 都說明 expected evidence 設計方式。
- [x] Quality gates 已記錄，並明確避免敏感資料。
- [x] 明確標示此 ticket 不修改資料集 JSON。

## Validation

- `rg -n "dataset expansion|lexical mismatch|multi-evidence|near-duplicate|cross-document" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md`
- `git diff --check`
