# Phase 40 JD Evidence Plan

## Goal

新增 Phase 40 interview evidence hardening roadmap，補足完成 Phase 39 後仍可能被 JD 追問的三個證據缺口：Embedding / SFT 實驗、推論硬體 benchmark、observability dashboard / query examples。

## Scope

- 在 `TODO.md` 新增 Phase 40 `v0.40.0` version map 與 future ticket backlog。
- 在 `docs/ROADMAP.md` 新增 Phase 40 roadmap section，列出 ticket、expected outcome、guardrails 與 validation direction。
- 在 `README_DEV.md` 補充 Phase 40 是 JD evidence hardening，不是新 production runtime。
- 新增 Phase 40 後續小票，讓後續可逐張 ticket 實作證據 artifacts。

## Out of Scope

- 不新增 backend / frontend runtime。
- 不新增 SFT training dependency、下載大型模型、執行真實 training、啟動 vLLM、啟動 K8s 或新增 observability service。
- 不修改 Phase 31-39 的 scope，也不宣稱 Phase 40 已完成 JD 100% 對齊。
- 不更新 backend version、frontend package version、frontend fallback version、health test 或 Docker Compose `DOCURAG_VERSION`。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 40 planning ticket，只新增 future backlog 與文件說明，不改 runtime。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `tasks/phase-40-interview-evidence-hardening/40-01-phase-40-jd-evidence-plan.md`
- `tasks/phase-40-interview-evidence-hardening/40-02-embedding-sft-experiment-evidence.md`
- `tasks/phase-40-interview-evidence-hardening/40-03-inference-hardware-benchmark-evidence.md`
- `tasks/phase-40-interview-evidence-hardening/40-04-observability-dashboard-evidence.md`
- `tasks/phase-40-interview-evidence-hardening/40-05-phase-40-release-sync.md`

## Acceptance Criteria

- [x] `TODO.md` 包含 Phase 40 `v0.40.0` version map 與 pending ticket checklist。
- [x] `docs/ROADMAP.md` 包含 Phase 40 goal、tickets、expected outcome、guardrails 與 validation direction。
- [x] `README_DEV.md` 說明 Phase 40 是面試證據補強，不是 production runtime 擴張。
- [x] Phase 40 tickets 清楚拆成 evidence plan、Embedding / SFT evidence、Inference hardware benchmark evidence、Observability evidence 與 release sync。
- [x] 文件未新增 runtime dependency，也未宣稱 Phase 40 已完成。

## Validation

- `rg -n "Phase 40|v0.40.0|JD evidence|Embedding|SFT|KV cache|TOPS|observability|dashboard evidence" README_DEV.md TODO.md docs/ROADMAP.md tasks/phase-40-interview-evidence-hardening`
- `rg -n "Version bump required: no|Version bump required: yes|production runtime|research-only|benchmark evidence" tasks/phase-40-interview-evidence-hardening TODO.md docs/ROADMAP.md README_DEV.md`
- `git diff --check`

Validation result：

- Phase 40 keyword `rg` 通過，確認 `README_DEV.md`、`TODO.md`、`docs/ROADMAP.md` 與 Phase 40 tickets 都已包含 `v0.40.0`、JD evidence、Embedding / SFT、KV cache、TOPS 與 observability keywords。
- Release impact / guardrail `rg` 通過，確認 Phase 40 tickets 包含 `Version bump required`、production runtime guardrails、research-only 與 benchmark evidence 說明。
- `git diff --check` 通過，僅顯示 Windows LF/CRLF 提示。
