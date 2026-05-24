# 26-01 VLM Provider Decision

## Goal

固定 Phase 26 Real VLM Parser Provider Spike 的產品與技術邊界，決定 VLM parser provider contract、env 設定、輸入 / 輸出格式、fallback policy 與 demo guardrails；本 ticket 只做規格與文件，不實作 runtime。

## Scope

- 定義 Phase 26 的目標：在 Phase 24 `DocumentFields` / `ParserResult` schema 上新增 disabled-by-default `vlm_invoice` provider path。
- 定義 provider env contract，例如 `DOCURAG_VLM_PROVIDER`、`DOCURAG_VLM_BASE_URL`、`DOCURAG_VLM_MODEL`、`DOCURAG_VLM_TIMEOUT_SECONDS`。
- 定義 VLM parser input contract：只接受既有上傳檔案中的 demo-safe image path / metadata，不做完整 PDF rendering。
- 定義 output contract：VLM output 必須正規化成既有 `DocumentFields` / `ExtractedField` / `ParserResult`，保留 `parser_source=vlm_invoice`、confidence、source trace 與 fallback metadata。
- 定義 fallback policy：VLM disabled、timeout、unsupported file、invalid JSON 或 confidence too low 時，回到 Phase 24 deterministic parser，不覆蓋既有 OCR / parser 狀態。
- 定義 Agent 承接方式：Phase 25 `get_document_fields` contract 不變，只讀保存後的 parser result。

## Out of Scope

- 不實作 VLM HTTP client、image resolver、parser adapter、API endpoint 或 frontend UI。
- 不新增真正 default-on VLM parser、OpenAI vision call、Ollama vision call、function calling、streaming 或新外部依賴。
- 不新增 PDF rendering、image preprocessing、layout analysis、多頁 production parser pipeline、table reconstruction 或 human correction workflow。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、Agent permission model、K8s 或 deployment 設定。
- 不修改 Phase 25 Agent planner / tool contract，不讓 Agent 直接呼叫 VLM。

## Release Impact

- Target version: `v0.26.0` planning backlog。
- Version bump required: no。
- 原因：本 ticket 只固定 VLM provider decision 與 contract；runtime、demo 與 release sync 留給 `26-02` 到 `26-05`。

## Files likely to change

- `docs/api.md`
- `docs/architecture.md`
- `docs/ROADMAP.md`
- `TODO.md`

## Acceptance Criteria

- [ ] 文件明確定義 Phase 26 VLM provider env、input、output、fallback 與 trace contract。
- [ ] 文件說明 `vlm_invoice` 必須輸出既有 `DocumentFields` schema，不新增平行欄位 schema。
- [ ] 文件說明 Phase 25 Agent tool contract 不變，Agent 只透過 `get_document_fields` 讀 parser result。
- [ ] 文件不宣稱已完成 production VLM parser、PDF rendering、worker、DB、RBAC 或 autonomous Agent。

## Validation

- `rg -n "v0.26.0|Phase 26|VLM provider|vlm_invoice|DOCURAG_VLM|DocumentFields|ParserResult|fallback|Agent|get_document_fields" README.md TODO.md docs/ROADMAP.md docs/api.md docs/architecture.md tasks/phase-26-vlm-parser-provider-spike/26-01-vlm-provider-decision.md`
- `git diff --check`
