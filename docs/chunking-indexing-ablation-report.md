# Chunking / Indexing Ablation Report

此文件是 Phase 41 的 analysis artifact，用來說明如何比較 chunking / indexing policy 對 RAG 檢索品質的影響。它不新增 runtime、不調整 `/rag/query` 預設策略，也不宣稱尚未實測的策略勝率。

## Evidence Boundary

| Evidence status | Meaning | Current source |
|---|---|---|
| `measured` | 已由既有 eval / smoke 產生可重跑 metrics。 | `sample-data/eval/retrieval-regression-baseline.json` 的 keyword baseline。 |
| `pending_hypothesis` | 已定義比較方式與應收 metrics，但尚未完成受控實測。 | `sample-data/eval/chunking-indexing-ablation-template.json` 的 fixed-size / semantic / parent-child / indexing policy rows。 |
| `not_supported` | 目前 runtime 尚未支援，不能被列為勝率比較。 | `parent-child` chunking runtime。 |

目前唯一納入此報告的實測基準是 Phase 41 keyword regression baseline：Hit Rate@K `0.7`、MRR@K `0.475`、Recall@K `0.625`、average latency `0.35 ms`、failure count `0`、fallback count `0`。fixed-size、semantic、parent-child 與 payload index / reindex policy 的 row 都是待測模板，不能解讀為結果優劣。

## Policies To Compare

| Policy | Type | Comparison method | Required metrics | Current evidence |
|---|---|---|---|---|
| `fixed_size` / fixed-size vector indexing | Chunking baseline from Phase 35 | 用相同 golden dataset、相同 embedding provider、相同 Qdrant collection 與相同 retrieval strategy 重跑 indexing；與 `semantic` 比較 top K evidence 是否更穩定。 | Hit Rate@K、MRR@K、Recall@K、average latency、failure count、fallback count、trace metadata count。 | `pending_hypothesis` |
| `semantic` vector indexing | Chunking variant from Phase 35 | 只使用既有段落 / section boundary；若 fallback 到 fixed-size，必須記錄 `chunking_fallback_reason`，再與 fixed-size row 比較 metric delta。 | Hit Rate@K、MRR@K、Recall@K、average latency、failure count、fallback count、chunking fallback count。 | `pending_hypothesis` |
| `parent-child` indexing | Future chunking policy | 目前只能作為 contract row；若後續 ticket 實作 parent-child runtime，才可用 parent hit / child evidence mapping 做 ablation。 | Hit Rate@K、MRR@K、Recall@K、average latency、failure count、fallback count、parent-child trace coverage。 | `not_supported` |
| Qdrant payload filter + payload index | Indexing policy from Phase 35 | 在相同 query set 下比較有 tenant / project / document / source filters 與 payload index metadata 時的 correctness、latency 與 fallback；不得關閉安全邊界做 production tuning。 | Hit Rate@K、MRR@K、Recall@K、average latency、failure count、fallback count、filter skip / unavailable reason。 | `pending_hypothesis` |
| Stale vector cleanup + reindex | Index freshness policy from Phase 35 | 先建立舊 vectors，再用 `cleanup_stale=true` 或 project reindex 產生新 index run；比較 stale evidence 是否消失、latency 是否可接受。 | Hit Rate@K、MRR@K、Recall@K、average latency、failure count、fallback count、stale vector count、reindex status。 | `pending_hypothesis` |

## Metric Interpretation

- Hit Rate@K：看 expected evidence 是否仍出現在 top K，適合抓 chunking 或 stale vector 導致的 evidence 消失。
- MRR@K：看第一個 relevant evidence 的排名是否被推低，適合抓 semantic chunking 或 payload filter 對排序的影響。
- Recall@K：看多 evidence case 是否遺漏部分證據，適合比較 fixed-size 與 semantic 是否切碎或合併過度。
- Average latency：看 payload filter、payload index、reindex 後 collection 狀態是否讓查詢變慢；latency 只作 warning，不單獨判定品質勝負。
- Fallback count：看 Qdrant、embedding、reranker 或 metadata unavailable 是否讓 vector / hybrid path 回退，避免把 unavailable 當成策略失敗。
- Trace metadata count：看 chunking strategy、chunking version、filter、fallback reason、score source 是否足以解釋結果。

## Phase Linkage

Phase 35 提供這份報告的 runtime 邊界：`fixed_size` 與 `semantic` chunking strategy、Qdrant payload filter、payload index、document stale vector cleanup 與 project reindex。`parent_child` 目前仍不是 runtime strategy。

Phase 36 提供 strategy comparison 的 metrics shape：Hit Rate@K、MRR@K、Recall@K、average latency、failure count、fallback count、trace metadata coverage，以及 failure / fallback case detail。

Phase 41 提供可版本化的 golden dataset、keyword regression baseline、baseline vs current report 與 pass / warn / fail gate。chunking / indexing ablation 的結果必須沿用 Phase 41 dataset version 與 strategy snapshot，否則不能和 baseline 比較。

## Qdrant Policy Impact

Qdrant payload filter 主要影響 correctness：tenant / project / document / source scope 可以避免 cross-project 或 stale evidence 混入結果。若 filter 缺失，Hit Rate@K 可能表面不降，但 evidence 可能來自錯誤範圍，因此 trace metadata 必須標出 filter scope。

Payload index 主要影響 latency 與可操作性：filter 欄位有 payload index 時，document / project scoped 查詢更可預期；沒有 payload index 時，查詢可能變慢或在大型 collection 上不穩。此 ticket 只記錄比較方法，不做 production Qdrant tuning。

Stale vector cleanup 主要影響品質：舊 chunk 若未清掉，semantic 或 fixed-size 重切後可能仍命中過期 evidence。Ablation report 應記錄 stale vector count、cleanup status 與 reindex status，並在 stale evidence 仍出現時標為 regression candidate。

Reindex 主要影響 freshness 與成本：document reindex 可用於單檔策略切換，project reindex 可用於全專案策略比較；兩者都必須保留 index run metadata，避免把不同 chunking_version 的結果混在同一個 comparison row。

## Reporting Rule

只有 `evidence_status=measured` 的 row 可以被寫成實測結果。`pending_hypothesis` row 只能描述預期觀察點與必填欄位；`not_supported` row 只能說明缺少 runtime，不能納入勝率或 release gate。
