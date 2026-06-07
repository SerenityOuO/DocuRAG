# Fine Tuning Synthetic Data Research Track

## Goal

新增 fine-tuning / synthetic data / embedding tuning 的 research track，展示模型優化理解，但不把它接成 production training pipeline。

## Scope

- 建立 synthetic data generation plan，支援 invoice / contract / report schema extraction use cases。
- 新增 SFT / embedding tuning / reranker tuning 的 notebook skeleton 或 docs。
- 定義資料格式、evaluation method、風險與不納入 production 的 guardrails。
- 更新 README_DEV / ROADMAP / TODO。

## Out of Scope

- 不執行真實 training、不下載大型模型、不新增 GPU training dependency。
- 不把 fine-tuned model 接到 production inference path。
- 不新增 dataset privacy workflow、model registry 或 deployment automation。

## Release Impact

- Target version: `v0.39.0`
- Version bump required: no
- 原因：這是 Phase 39 research artifact ticket，版本同步留到 `39-05`。

## Files likely to change

- `docs/`
- `fine-tuning/`
- `sample-data/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-39-deployment-observability-finetuning/39-04-finetuning-synthetic-data-research-track.md`

## Acceptance Criteria

- [ ] Synthetic data plan 覆蓋 invoice / contract / report examples。
- [ ] Notebook / docs skeleton 說明 SFT、embedding tuning 與 reranker tuning 的資料格式。
- [ ] 文件明確標示 research-only，不接 production runtime。
- [ ] Validation 不需要下載大型模型或執行 training。

## Validation

- `rg -n "SFT|synthetic data|embedding tuning|reranker tuning|research-only|fine-tuning" docs fine-tuning sample-data README_DEV.md TODO.md tasks/phase-39-deployment-observability-finetuning`
- `git diff --check`
