# Retrieval Regression CI Report

## Goal

新增可重跑的 retrieval regression report，讓 RAG 策略變更後能比較 baseline 與 current metrics。

## Scope

- 擴充或新增 regression report script / artifact，輸出 baseline vs current 的 Hit Rate@K、MRR@K、Recall@K、latency 與 fallback summary。
- 報告需保留 strategy、dataset version、provider availability 與 skip reason。
- 規劃 CI 使用方式，但保持本地可手動執行。
- 文件說明 regression threshold 與未通過時的解讀方式。

## Out of Scope

- 不新增 production monitoring、資料庫 eval history、排程任務或外部 dashboard。
- 不強制 CI 啟動 Qdrant、Ollama、FastEmbed 或 GPU runtime。
- 不把 optional runtime unavailable 視為硬失敗；必須記錄 skip reason。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 41 report / validation artifact ticket，版本同步留到 `41-05`。

## Files likely to change

- `scripts/`
- `sample-data/eval/`
- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-41-rag-quality-regression-datasetops/41-03-retrieval-regression-ci-report.md`

## Acceptance Criteria

- [x] Regression report 可比較 baseline 與 current retrieval metrics。
- [x] Report 包含 dataset version、strategy、provider availability 與 skip reason。
- [x] 文件說明 local / CI 使用方式與 threshold 解讀。

## Completion Notes

- 新增 `scripts/retrieval-regression-report.ps1`，預設執行 CI-safe keyword regression report，不要求 Qdrant、Ollama、FastEmbed 或 GPU runtime。
- 新增 `sample-data/eval/retrieval-regression-baseline.json`，固定 Phase 41 keyword baseline metrics、provider availability、skip reason 與 threshold。
- 更新 `sample-data/eval/README.md`、`docs/ROADMAP.md`、`README_DEV.md` 與 `TODO.md`。
- 本 ticket 不 bump version，不新增 production monitoring、DB eval history、排程任務、外部 dashboard，也不把 optional runtime unavailable 視為硬失敗。

## Validation

- Regression report smoke command。
- `rg -n "regression report|baseline vs current|dataset version|provider availability|skip reason|threshold" scripts sample-data docs README_DEV.md TODO.md tasks/phase-41-rag-quality-regression-datasetops`
- `git diff --check`
