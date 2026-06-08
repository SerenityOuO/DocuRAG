# JD Evidence Matrix

## Goal

建立 JD 條目到 DocuRAG 專案證據的對照表，讓面試官可以快速看到每個能力如何被文件、demo、測試或截圖驗證。

## Scope

- 新增 JD evidence matrix 文件。
- 對照 AI Core、Software / System Architecture、Inference & Ops 三大類能力。
- 每列至少包含 JD keyword、專案證據、demo path、validation command、目前邊界與下一步。
- 標示哪些能力是 completed、demo-safe、research-only 或 future backlog。
- Matrix 必須逐條覆蓋 JD 原文能力：RAG / embedding tuning / chunking / vector DB、rerank / Hit Rate / MRR、VLM / OCR、SFT / synthetic data、Agent planning、FastAPI / Vue、RBAC / logs / SQL / NoSQL、NATS / gRPC boundary、Redis、vLLM / Ollama、GPU / NPU / KV cache、Docker / K8s。
- 每列必須有「面試說法」欄位，用一句白話說明這個證據實際代表什麼能力。
- 每列必須有 honesty boundary，區分 completed、demo-safe、research-only、skip-safe、future backlog 或 not covered。
- Matrix 結尾要有 gap summary，列出仍未補齊或刻意不做的項目，例如 production autoscaling、multi-cluster K8s、production SSO、real NPU profiling。

## Out of Scope

- 不新增 runtime、dependency、測試程式、截圖或 demo media，除非只是引用既有 artifacts。
- 不誇大 production readiness，不把未完成 roadmap 寫成已完成。
- 不修改 backend / frontend version。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 45 portfolio artifact ticket，版本同步留到 `45-05`。

## Files likely to change

- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-45-production-readiness-portfolio-pack/45-01-jd-evidence-matrix.md`

## Acceptance Criteria

- [x] JD evidence matrix 覆蓋 AI Core、System Architecture、Inference & Ops。
- [x] 每列包含 project evidence、demo / validation path 與 honesty boundary。
- [x] 文件清楚區分 completed、demo-safe、research-only 與 future backlog。
- [x] Matrix 逐條覆蓋 JD 原文能力，不只用大分類概括。
- [x] 每列包含 JD keyword、project evidence、demo command、file path、status、面試說法、honesty boundary 與 next action。
- [x] Gap summary 誠實列出 not covered / intentionally out of scope 的項目。

## Validation

- `rg -n "JD evidence matrix|AI Core|System Architecture|Inference|RAG|Embedding|SFT|synthetic data|VLM|OCR|Agent|RBAC|NATS|Redis|vLLM|KV cache|K8s|completed|demo-safe|research-only|skip-safe|future backlog|honesty boundary|gap summary" docs README_DEV.md TODO.md tasks/phase-45-production-readiness-portfolio-pack`
- `git diff --check`

## Completion Notes

- Added `docs/jd-evidence-matrix.md`.
- Matrix covers AI Core, Software / System Architecture and Inference & Ops evidence rows with JD keyword, project evidence, demo command, file path, status, interview wording, honesty boundary and next action.
- Gap summary explicitly separates `not covered`, `future backlog`, `research-only`, `demo-safe` and `completed`.
- No runtime, dependency, test program, screenshot, demo media or version bump was added.
