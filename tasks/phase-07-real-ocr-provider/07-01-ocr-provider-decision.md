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

## Decision

Phase 07 的 real OCR spike provider 選定 `PaddleOCR`。

候選取捨：

| Candidate | 優點 | 風險 / 不選原因 |
|---|---|---|
| PaddleOCR | Python 生態可直接接入 FastAPI backend；可回傳文字、bbox 與 confidence，貼近 v0.6 chunk / citation trace contract；適合 07-03 做 output normalization。 | 依賴較重，第一次執行可能需要下載模型；Windows / Docker 環境需要額外安裝與驗證。 |
| Tesseract | 成熟、離線、資源需求較低；適合簡單 OCR。 | 需要系統層 binary 與語言包，Windows / Docker 安裝差異較明顯；bbox / confidence 輸出仍需額外整理。 |
| EasyOCR | Python package 接入相對直接，也能回傳 bbox 與 confidence。 | 依賴同樣偏重，對目前 repo 沒有比 PaddleOCR 更明確的 contract 優勢；不作為 Phase 07 第一個 provider。 |

PaddleOCR 被選中是因為它最符合本階段的目標：做一個本機可驗證、能產出文字與 trace metadata 的 OCR provider spike，同時不把 queue、DB、embedding 或 LLM 範圍帶進來。

## Provider Behavior

- 預設 provider 仍是 `mock`，既有 demo 與 `POST /documents/{document_id}/ocr/mock` 必須維持可用。
- 07-02 會新增 `POST /documents/{document_id}/ocr` 作為 provider-selected OCR endpoint；當設定選擇 real provider 時才走 PaddleOCR。
- PaddleOCR 必須 lazy import，避免未安裝 real OCR dependency 時破壞既有 mock demo。
- 當 real provider 不可用、模型下載失敗、輸入格式不支援或執行 OCR 失敗時，real endpoint 採明確失敗，不靜默 fallback 到 mock。
- real provider 失敗時應更新 document processing status 與 processing job metadata，並回傳清楚錯誤訊息；mock path 仍可手動執行並保持相容。
- PaddleOCR output normalization 留給 07-03，目標是映射到既有 `OcrResult`、`DocumentChunk`、page、bbox、confidence 與 trace metadata contract。

## Guardrails

Phase 07 只做單一 local OCR provider spike。即使接入 PaddleOCR，也不新增 queue、worker、Redis、NATS、Qdrant、embedding、rerank、LLM、OpenAI API、Ollama、vLLM、PostgreSQL、登入、權限或 RBAC。

## Files likely to change

- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-07-real-ocr-provider/07-01-ocr-provider-decision.md`

## Acceptance Criteria

- [x] 文件清楚列出 OCR provider 候選與取捨。
- [x] 文件選定單一 Phase 07 spike provider。
- [x] 文件明確描述 provider unavailable fallback，保留 `mock` provider。
- [x] 文件明確標示 Phase 07 仍不接 queue、DB、Qdrant、embedding、LLM 或權限系統。
- [x] TODO 與 ROADMAP 更新 Phase 07 狀態。

## Validation

- `git diff --check`
- `git status --short --branch`
