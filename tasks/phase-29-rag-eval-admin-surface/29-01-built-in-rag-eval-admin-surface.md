# 29-01 Built-in RAG Eval Admin Surface

## Goal

在「後台知識庫管理」新增一個標題為「測試RAG」的內建基準測試區塊，讓 Admin / Analyst 可以用固定 `hybrid_rerank` 策略執行 demo-safe retrieval benchmark，並只呈現第一版需要的核心指標：Hit Rate@K、MRR@K、平均延遲與 Failure / Fallback。

同時把既有「Agent 執行紀錄」改成可摺疊區塊，避免後台頁面一次攤開過多 trace 細節。

## Scope

- 新增後台「測試RAG」frontend surface，放在「後台知識庫管理」內。
- RAG 測試策略固定為 `hybrid_rerank`，不提供策略下拉選單。
- UI 只顯示以下 summary metrics：
  - `Hit Rate@K`
  - `MRR@K`
  - `average_latency_ms`
  - `failure_count` / `fallback_count`
- 可提供簡短狀態文字，說明 eval dataset、case count、目前 strategy 與 fallback 狀態。
- 若需要明細，僅用摺疊方式呈現 failed / fallback cases，不在主畫面做完整 dashboard。
- 新增或包裝 backend API，重用既有 retrieval eval runner，固定執行內建 `hybrid_rerank` baseline。
- 內建 benchmark 使用 demo-safe synthetic 中文發票 fixture：
  - 共 10 張發票。
  - 供應商分布：`NVDLA` 1 張、`GOOGLE` 1 張、`OpenAI` 1 張、`Intel` 3 張、`DocuRAG` 4 張。
  - 每張發票使用不同版面 / 欄位順序 / 文字呈現風格，日期與金額皆不同，幣別皆為台幣。
  - 若使用真實品牌名稱作為 vendor label，內容必須明確是 synthetic demo invoice，不可使用真實公司稅號、logo、地址、交易資料或任何敏感資訊。
- Eval cases 以固定 query + expected evidence 定義，例如供應商、發票號碼、日期、總金額、稅額或付款條件；每筆 case 必須可由 fixture 文件中的明確文字支撐。
- 更新 frontend `Agent 執行紀錄` 區塊為可摺疊 `<details>` 或等價交互。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 29 checklist / guardrails。

## Out of Scope

- 不新增策略選擇 UI；第一版只跑 `hybrid_rerank`。
- 不顯示 Recall@K、trace metadata count、result strategy counts、完整排名表、圖表 dashboard 或歷史趨勢。
- 不新增自訂 eval dataset 上傳、編輯器、case builder 或使用者可保存的 eval runs。
- 不把 built-in benchmark 改成 production eval dashboard。
- 不新增 LLM-as-judge、answer faithfulness scoring、citation quality scoring、回答正確性評分或人工標註流程。
- 不測 OCR 準確率、版面分析、PDF rendering、多頁 OCR 或 VLM parser 準確率；中文發票 fixture 在本 ticket 中只作 retrieval evidence benchmark。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、正式 RBAC、tenant isolation、SSO、OAuth、MFA、K8s 或 deployment 設定。
- 不改 `/rag/query` 預設行為、不改 rerank algorithm、不改 embedding model、不改 Qdrant collection schema。
- 不讓 eval runner 在 upload、OCR、parse、vector index 或一般 chat query 時自動執行。

## Release Impact

- Target version: `v0.29.0`.
- Version bump required: yes.
- 原因：此 ticket 會新增後台使用者可見的 RAG 測試 surface 與 backend eval API，並調整 Agent trace UI 呈現，需要形成明確 demo release。

## Files likely to change

- `backend/app/api/routes/rag.py` 或新增 `backend/app/api/routes/eval.py`
- `backend/app/main.py`
- `backend/app/services/evaluation.py`
- `backend/tests/test_evaluation.py`
- `backend/tests/test_eval_dataset.py`
- `sample-data/documents/`
- `sample-data/eval/retrieval-eval.json`
- `sample-data/eval/README.md`
- `frontend/src/api/client.ts`
- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/demo-script.md`
- `docs/ROADMAP.md`
- `TODO.md`

## Acceptance Criteria

- [x] 後台知識庫管理內出現「測試RAG」區塊。
- [x] 「測試RAG」只執行 `hybrid_rerank` 內建基準測試，不提供策略選擇。
- [x] 測試結果顯示 Hit Rate@K、MRR@K、平均延遲、Failure / Fallback。
- [x] 內建中文發票 fixture 共 10 張，供應商分布符合 `NVDLA` 1、`GOOGLE` 1、`OpenAI` 1、`Intel` 3、`DocuRAG` 4，日期 / 金額皆不同且幣別皆為台幣。
- [x] 每個 eval case 都有 expected evidence，且可由 fixture 文件文字明確支撐。
- [x] Runtime 不可用時，`hybrid_rerank` fallback 狀態清楚呈現，不讓 UI 靜默假裝完整 vector / rerank 成功。
- [x] Agent 執行紀錄改成可摺疊，收合時仍可看到標題與目前狀態。
- [x] Viewer role 在 demo auth mode 下不顯示或不可操作後台「測試RAG」與 Agent 操作。
- [x] README / docs 明確說明這是 built-in retrieval benchmark，不是 production eval dashboard、OCR eval 或 LLM-as-judge。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybridRerank`
- Browser check for local frontend: Admin / Analyst 後台可執行「測試RAG」、summary metrics 正確顯示、Agent 執行紀錄可展開 / 收合、desktop 與 mobile width 無 horizontal overflow。
- Demo auth Browser check: Viewer 看不到或不能操作「測試RAG」與 Agent 操作；Admin / Analyst 可操作。
- `rg -n "測試RAG|hybrid_rerank|Hit Rate@K|MRR@K|fallback_count|Agent 執行紀錄" frontend/src backend/app sample-data docs TODO.md tasks/phase-29-rag-eval-admin-surface`
- `git diff --check`

## Validation Result

- `python -m pytest backend/tests/test_evaluation.py backend/tests/test_eval_dataset.py backend/tests/test_evaluation_api.py -q` 通過：`27 passed, 1 warning`。
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過：`191 passed, 1 warning`（pytest cache 權限警告）。
- `npm.cmd run build` 通過，frontend package version 為 `0.29.0`。
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1 -RunHybridRerank -ApiBaseUrl http://127.0.0.1:8019` 通過；使用 temporary auth-disabled backend 驗證，因既有 `127.0.0.1:8000` demo auth 對 smoke script 回 `401`。結果包含 `case_count=20`、`hit_rate_at_k=0.65`、`mrr_at_k=0.575`、`failure_count=0`、`fallback_count=0`。
- Browser validation 通過：Admin 可執行「測試RAG」，顯示 `10 cases`、Hit Rate@K `100%`、MRR@K `1.00`、Failure / Fallback `0 / 10`；Agent 執行紀錄預設收合且可展開；desktop `1280px` 與 mobile `390px` 無 horizontal overflow。
- Demo auth Viewer validation 通過：Viewer 只看到前台查詢，不顯示或不可操作「測試RAG」與 Agent 操作。
- `rg -n "測試RAG|hybrid_rerank|Hit Rate@K|MRR@K|fallback_count|Agent 執行紀錄" frontend/src backend/app sample-data docs TODO.md tasks/phase-29-rag-eval-admin-surface` 通過。
- `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
