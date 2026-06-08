# Embedding SFT Experiment Evidence

## Goal

建立 Embedding tuning / SFT / synthetic data 的面試證據 artifacts，讓 Phase 39 的 research track 從「有規劃」補強成「有可展示實驗設計與小型結果」。

## Scope

- 建立 `docs/` 或 `fine-tuning/` 下的 research report / notebook skeleton。
- 設計 invoice / contract / report 的 synthetic data generation format。
- 補充 SFT schema extraction、embedding tuning、reranker tuning 的資料格式、實驗步驟與 evaluation method。
- Report 至少包含 dataset card、SFT JSONL 範例、embedding positive / negative pairs、reranker pairwise samples、before / after eval table 與 risk notes。
- Synthetic data examples 至少覆蓋 invoice / contract / report 其中兩類；每類至少保留 2 筆 demo-safe sample。
- Before / after eval table 可以是 tiny experiment 或待跑 template，但欄位必須包含 Hit Rate@K、MRR@K、Recall@K、parser field accuracy、sample count 與 skip reason。
- 若實作小型實驗，必須使用可控小資料與明確 skip path，不下載大型模型或新增重型 dependency。
- 將結果連回 RAG eval 指標，例如 Hit Rate、MRR、Recall 或 parser field accuracy。

## Out of Scope

- 不執行完整 production training pipeline。
- 不下載大型模型、不新增 GPU training dependency、不新增 model registry。
- 不把 fine-tuned model 接到 production inference path。
- 不修改 backend / frontend runtime 或 default provider。

## Release Impact

- Target version: `v0.40.0`
- Version bump required: no
- 原因：這是 Phase 40 evidence artifact ticket，版本同步留到 `40-05`。

## Files likely to change

- `docs/`
- `fine-tuning/`
- `sample-data/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-40-interview-evidence-hardening/40-02-embedding-sft-experiment-evidence.md`

## Acceptance Criteria

- [x] 有一份可閱讀的 Embedding / SFT / synthetic data experiment report 或 notebook skeleton。
- [x] Report 清楚說明資料格式、實驗流程、evaluation method 與風險。
- [x] 至少包含 invoice / contract / report 其中兩類 synthetic data examples。
- [x] Report 包含 SFT JSONL、embedding positive / negative pair 與 reranker training pair 範例。
- [x] Before / after eval table 包含 Hit Rate@K、MRR@K、Recall@K、parser field accuracy、sample count 與 skip reason。
- [x] 文件說明如何避免 synthetic data overfit、label leakage 與 production document privacy 風險。
- [x] 文件明確標示 research-only，不接 production runtime。
- [x] Validation 不需要下載大型模型或執行長時間 training。

## Validation

- `rg -n "SFT|synthetic data|embedding tuning|reranker tuning|positive|negative|JSONL|research-only|field accuracy|Hit Rate|MRR|Recall|skip reason|overfit|privacy" docs fine-tuning sample-data README_DEV.md TODO.md tasks/phase-40-interview-evidence-hardening`
- `git diff --check`

## Status

- Completed. Added `fine-tuning/phase40-experiment-evidence.md` and `sample-data/fine-tuning/phase40-before-after-eval.csv`.
- Updated fine-tuning README / dataset card, README_DEV, TODO and ROADMAP.
- The report links SFT JSONL, embedding positive / negative pairs, reranker pairwise samples, invoice / contract / report synthetic data coverage, before / after eval fields, Hit Rate@K, MRR@K, Recall@K, parser field accuracy, sample count, skip reason, privacy, label leakage, overfit and research-only runtime boundaries.
- Release Impact: Version bump required: no. Version sync remains deferred to `40-05`.

## Validation Result

- Passed: ticket `rg`.
- Passed: `git diff --check`.
- No model download, no long-running training, no dependency, no backend / frontend runtime change and no production runtime connection were added.
