# v0.7.0 OCR Provider Decision Spike

## Goal

選定 Phase 07 要接入的第一個可本機驗證 OCR provider，並把 provider 的安裝條件、fallback 行為、輸出 contract 與 demo 風險寫清楚，讓後續 ticket 不在實作時臨時擴張範圍。

## Scope

- 比較 2 到 3 個本機 OCR / VLM parser 候選，例如 Tesseract、PaddleOCR 或其他輕量方案。
- 只選定一個 Phase 07 spike provider，並說明為什麼適合目前 repo。
- 定義 provider 不可用時的 fallback 行為，必須保留現有 `mock` provider 與 API 相容。
- 更新 README、backend README、frontend README、TODO 與 ROADMAP 的 Phase 07 說明。
- 不修改 backend / frontend source code。

## Out of Scope

- 不安裝 OCR library。
- 不實作 OCR adapter。
- 不新增 PDF rendering、image preprocessing、queue、worker、Redis、NATS、Qdrant、embedding、rerank、LLM、PostgreSQL、登入或 RBAC。
- 不更改 API response schema。

## Files likely to change

- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-07-real-ocr-provider/07-01-ocr-provider-decision.md`

## Acceptance Criteria

- [ ] 文件清楚列出 OCR provider 候選與取捨。
- [ ] 文件選定單一 Phase 07 spike provider。
- [ ] 文件明確描述 provider unavailable fallback，保留 `mock` provider。
- [ ] 文件明確標示 Phase 07 仍不接 queue、DB、Qdrant、embedding、LLM 或權限系統。
- [ ] TODO 與 ROADMAP 更新 Phase 07 狀態。

## Validation

- `git diff --check`
- `git status --short --branch`
