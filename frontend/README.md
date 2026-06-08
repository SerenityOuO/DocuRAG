# DocuRAG AgentOps Frontend

目前 frontend package 與 fallback label 已同步到 `0.46.0`。Phase 46 的 Admin Document Delete Flow 讓 Admin / Analyst 可在後台資料匯入狀態刪除文件；frontend 不新增 production deletion dashboard、restore workflow、approval workflow、audit UI 或 Agent destructive tool surface。

最小 Vue 3 + Vite demo UI 目前已拆成前台 Viewer Chat 與後台 Admin / Analyst Ingestion 兩個 surface。v0.27.0 起預設先打開後台 Admin / Analyst Ingestion，讓 demo 第一眼呈現上傳、provider-selected OCR、VLM-first parser、Agent trace 與 best-effort Qdrant vector indexing。v0.27.1 起 backend VLM parser 會同時使用原始圖片與 OCR context，欄位結果可在 API / smoke trace 中看到 OCR evidence mapping 或 unmatched 狀態。Phase 28 Document Source Router contract 已明確標記 upload flow 應分成 `image_ocr`、`text_upload`、`pdf_text` 與 `pdf_scanned_pending_ocr`；目前 UI 對 `.txt` 會跳過 OCR 並顯示直接文字匯入，對 text-native PDF 會顯示 `pdf_text` ready，對 scanned / mixed PDF 可透過 API / smoke 驗證 page image OCR result 與 `pdf_page_ocr` chunks。v0.29.0 起後台新增「測試RAG」，Admin / Analyst 可直接執行固定 `hybrid_rerank` 的 10 張 synthetic 中文發票 built-in benchmark，並只看 Hit Rate@K、MRR@K、平均延遲與 Failure / Fallback；Agent 執行紀錄改成可摺疊。v0.31.0 起 backend 支援 opt-in PostgreSQL metadata repository，但 frontend surface 不新增 DB 管理頁或 production tenant UI。v0.32.0 起 frontend role surface 對齊 formal Auth / RBAC guard：Admin / Analyst 可使用 ingestion、built-in eval 與 Agent write surface，Viewer 只能查詢；未登入且 backend 要求 formal auth 時，UI 會顯示 locked panel。v0.34.0 起 frontend version / fallback label 已同步 scanned PDF OCR baseline；PDF rendering、page OCR chunks、parser / RAG handoff 由 backend API 與 smoke script 驗證，frontend 不新增 production layout review UI。v0.35.0 起 frontend version / fallback label 已同步 RAG indexing quality release；chunking strategy、Qdrant payload filter、reindex 與 stale cleanup 由 backend API 與 smoke script 驗證。v0.36.0 起 frontend version / fallback label 已同步 eval dashboard release；後台 Strategy comparison panel 可查看 Hit Rate@K、MRR@K、Recall@K、failure / fallback cases、trace metadata coverage 與 rerank before / after rank / score。v0.37.0 起 frontend version / fallback label 已同步 inference ops release；OpenAI-compatible / vLLM path 由 backend env、local docs 與 smoke script 驗證，frontend 不新增 production inference dashboard。v0.38.0 起 frontend version / fallback label 已同步 Agent runtime hardening；後台 Agent trace 會顯示 planner fallback、permission decision、tool tier、side-effect policy 與 fallback reason。v0.40.0 起 frontend version / fallback label 已同步 JD evidence hardening；Embedding / SFT、KV cache / TOPS inference hardware benchmark 與 observability dashboard evidence 由 docs / backend / infra artifacts 驗證，不新增 production training UI、production inference dashboard 或 production alerting UI。v0.42.0 起 frontend version / fallback label 已同步 inference gateway / capacity planning release；provider routing、timeout guardrails 與 capacity planning report 由 backend trace、docs 與 smoke script 驗證，frontend 仍不新增 token streaming UI 或 production inference ops dashboard。v0.43.0 起 frontend version / fallback label 已同步 AgentOps governance / secure tool runtime release；tool permission、approval state 與 Agent replay / eval 由 backend trace、docs、sample-data 與 smoke script 驗證，frontend 不新增 production autonomous Agent dashboard 或 external side-effect tool UI。v0.44.0 起 frontend version / fallback label 已同步 Document Intelligence QA / human review loop release；後台 structured fields surface 會顯示 field confidence、evidence state、source text / page / bbox，Admin / Analyst 可保存 demo-safe correction / golden label，parser field accuracy eval 由 backend smoke 與 sample-data report 驗證。v0.45.0 起 frontend version / fallback label 已同步 final interview portfolio pack；JD evidence matrix、system walkthrough、demo scenario pack 與 risk / tradeoff report 由 docs 驗證，不新增新的 frontend surface。v0.46.0 起後台資料匯入狀態新增「刪除文件」，成功後即時移除列表紀錄，失敗會在該列顯示錯誤。若 backend 以 `DOCURAG_AUTH_MODE=demo` 啟動，UI 會先顯示 demo login screen，Admin / Analyst 可進後台 ingestion，Viewer 只能使用前台查詢且後台入口 disabled。Viewer Chat 可切換使用，只查詢後端已建立的文件知識庫，並顯示 answer、answer source、retrieval source 與 citation summary。OCR detail、raw JSON、retrieval trace table 與完整 eval trace 可由 backend API、smoke scripts 或 CLI 檢查，不屬於 Viewer Chat 主流程；production-grade durable worker / production DB pipeline 尚未實作。backend 預設使用 `hybrid_rerank` RAG / Agent search、Ollama embedding 與 FastEmbed rerank adapter；Ollama embedding、Qdrant 或 reranker 不可用時，UI 會顯示 fallback 狀態。這仍不是 production VLM parser、production annotation platform、full document image annotation UI、autonomous Agent dashboard、任意 SQL / shell / filesystem tool、Agent destructive tool、external side-effect tool、production deletion dashboard、restore workflow、LLM-as-judge、answer faithfulness、citation quality scoring、SSO、OAuth、MFA 或 production identity provider。

## Install

```powershell
cd frontend
npm.cmd install
```

## Run

```powershell
cd frontend
npm.cmd run dev
```

預設網址：

```text
http://localhost:5173
```

## API Base URL

前端會讀取 `VITE_API_BASE_URL`。未設定時預設使用：

```text
http://127.0.0.1:8000
```

PowerShell 設定範例：

```powershell
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
npm.cmd run dev
```

## Build

```powershell
cd frontend
npm.cmd run build
```

## Demo UI

### Agent Trace Surface

- Admin / Analyst / developer-oriented surface can call `POST /agent/run` with a demo-safe task, document and query.
- The Agent trace surface shows planner fallback, tool calls, observation, final answer, citations, permission decision, tool tier and fallback state.
- Admin / Analyst ingestion is the default demo surface in v0.27.0; Viewer Chat remains available as a separate front surface.
- This is a permission-guarded read-only tool-use demo surface, not a production autonomous Agent dashboard, arbitrary tool console, worker runtime or DB-backed tool console.

目前 UI 支援：

- 前台 Viewer Chat：輸入 query 與 top_k，呼叫 `POST /rag/query`，用來查詢已建立的 demo knowledge base。
- Demo login screen：當 backend 回報 `auth_mode=demo` 且尚未登入時，提供 Admin / Analyst / Viewer demo role 選擇與登入表單。
- Role-gated UI：Admin / Analyst 登入後可使用後台 ingestion、built-in eval 與 Agent write surface；Viewer 登入後只顯示查詢入口，後台知識庫管理按鈕 disabled，且不顯示 upload / OCR / parse / index、built-in eval 或 Agent write controls。
- Formal auth locked panel：當 backend 要求 formal auth 但 frontend 沒有 bearer token context 時，UI 只顯示受保護狀態與版本，不提供 ingestion / eval / Agent write 操作。
- 回答結果：顯示 answer、answer source、retrieval source 與簡化引用來源。
- 空知識庫狀態：以 Viewer 角度提示需先由後台知識庫管理流程建立資料，不在前台查詢畫面提供文件上傳或 OCR 操作。
- 後台 Admin / Analyst Ingestion：預設入口，檔案選擇器支援單檔或多檔；多檔時 frontend 會逐檔呼叫既有 `POST /documents/upload`、provider-selected `POST /documents/{document_id}/ocr`、best-effort `POST /documents/{document_id}/parse` 與 `POST /documents/{document_id}/index/vector`，並分檔顯示成功 / 失敗結果；real OCR 失敗時才提供手動 `POST /documents/{document_id}/ocr/mock` fallback。這不是 batch API、queue 或 background worker。
- 測試RAG：後台固定呼叫 `POST /eval/rag/built-in`，使用 `hybrid_rerank` 內建中文發票 benchmark，顯示 Hit Rate@K、MRR@K、平均延遲與 Failure / Fallback；fallback / failed cases 只在摺疊明細中呈現。
- Agent 執行紀錄：後台 Agent trace surface 可展開 / 收合，並顯示 planner fallback、permission decision、tool tier、side-effect policy 與目前狀態。
- Phase 28 / 34 source router runtime：frontend 遇到 `.txt` 會顯示 direct text path，跳過 provider-selected OCR，直接接 best-effort parser / vector indexing；text-native PDF 會顯示 `pdf_text` path 並接 best-effort parser / vector indexing；scanned / mixed PDF 由 backend render page images 並可透過 provider-selected OCR 建立 `pdf_page_ocr` chunks，詳細 page OCR result 留在 API / smoke 檢查。
- 欄位解析：OCR 完成後可在後台觸發 `POST /documents/{document_id}/parse`，並顯示 parser status、document type、invoice number、vendor、issue date、total amount、currency、confidence、source text、source page、source bbox、parser source 與 fallback reason；v0.27.1 起 VLM 欄位若可對回 OCR line 會保存 source text / page / bbox，無法對回時以 evidence unmatched / unavailable 標示；44-02 起這些 evidence metadata 會在 Admin / Analyst 後台以欄位卡片呈現，詳細 JSON 仍可由 `GET /documents/{document_id}/fields` 或 API docs 檢查。
- Phase 26 parser source comparison：API response 會透過 `parser_source`、`trace_metadata.fallback_chain`、`trace_metadata.fallback_reason`、`trace_metadata.confidence_summary` 與 source input metadata 區分 `vlm_invoice` 與 `deterministic_invoice`；frontend 仍只呈現 demo-friendly structured fields 摘要，不新增 production parser comparison dashboard。
- 後端健康：只顯示簡短連線狀態與版本，不顯示 raw health JSON。
- 工程細節：OCR text、extracted fields、document list、metadata JSON、retrieved chunks、trace metadata 與 eval metrics 改由 backend API、`scripts/demo-smoke-test.ps1`、`scripts/retrieval-eval-smoke.ps1` 或 API docs 檢查，不放在 frontend 主畫面；正式知識庫 ingestion / indexing pipeline 尚未實作。
- backend 預設嘗試 Ollama LLM provider；generation 成功時 answer source 顯示 `ollama/qwen3.5:4b`，Ollama 不可用時顯示 `LLM unavailable fallback`，若以 `DOCURAG_LLM_PROVIDER=` 明確關閉則顯示 `確定性基準回答`。
- backend 預設使用 `hybrid_rerank`；retrieval source 可能顯示 `hybrid_rerank`、`hybrid_rerank 備援：vector_unavailable`、`hybrid_rerank 備援：reranker_unavailable`、`vector/qdrant` 或舊 keyword baseline override。
- Viewer 在 demo auth mode 下看不到後台「測試RAG」與 Agent 操作；Admin / Analyst 才能操作。Viewer 直接呼叫 ingestion / eval / Agent write API 時也會收到 backend 403。

建議面試前先 seed demo knowledge base，讓前台客服聊天一打開就能問：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1
```

建議 demo query：

```text
payment due date Net 15
```

在 backend 已執行 `scripts/seed-demo-data.ps1` 後，RAG result 預期會引用 `mock-invoice-aurora.txt`；詳細 chunks 與 trace 可用 smoke script 或 API response 檢查。

目前 frontend 預設展示的是 Admin / Analyst ingestion + default `hybrid_rerank` RAG / Agent search + default-on Ollama answer generation path。backend 會優先嘗試 Ollama embedding、Qdrant 與 FastEmbed rerank；若 runtime 不可用，會 fallback 到 keyword retrieval 並保留 trace。未覆寫 `DOCURAG_LLM_PROVIDER` 時會把 retrieved chunks 與 query 交給 Ollama `qwen3.5:4b` 產生回答；Ollama 不可用時會明確 fallback，若要回到 deterministic baseline 可設定 `DOCURAG_LLM_PROVIDER=`。OCR 是 backend ingestion layer：上傳後由 backend provider-selected GPU-only PaddleOCR 產生 OCR result 與 local chunks；scanned / mixed PDF 會先 render page images，再建立 page-aware OCR chunks。若 dependency、Python 版本、CUDA build 或模型不可用，backend 會用清楚錯誤與 processing metadata 呈現，後台 ingestion flow 才顯示手動 mock fallback，不會靜默 fallback 到 mock。Parser 在 Phase 26 起預設為 VLM-first provider spike，success path 標記 `vlm_invoice`；Ollama `response` / `thinking` / fenced JSON 會先被正規化，provider unavailable、unsupported file、timeout 或 invalid response 才 fallback 到 `deterministic_invoice`；這不代表已完成 production VLM parser、layout understanding、table reconstruction、image preprocessing、streaming UI、batch upload worker 或 production indexing worker。

## Release Status

- v0.45.0: Final Interview Portfolio Pack 已完成；frontend package / lock / fallback label 已同步到 `0.45.0`，Phase 45 的 JD evidence matrix、system design walkthrough、demo scenario pack 與 risk / tradeoff report 由 docs、README / README_DEV 與 smoke scripts 驗證；frontend 不新增新的 runtime UI、production dashboard、external service integration、模型訓練或 paid API surface。Validation 已通過：frontend build、backend full test、demo smoke、Phase 45 evidence `rg` 與 `git diff --check`。
- v0.46.0: Admin Document Delete Flow 已完成；frontend package / lock / fallback label 已同步到 `0.46.0`，後台資料匯入狀態新增「刪除文件」按鈕與確認訊息，成功後即時移除列表紀錄。Validation 已通過：frontend build、focused backend document / auth / health tests、Phase 46 keyword `rg` 與 `git diff --check`。不新增 production deletion dashboard、restore workflow、approval workflow、audit UI、Agent destructive tool 或 Qdrant cleanup surface。
- v0.42.0: Inference Gateway / Capacity Planning 已完成；frontend package / lock / fallback label 已同步到 `0.42.0`，Phase 42 的 provider routing / fallback metadata、timeout guardrails 與 capacity planning report 由 backend / docs / smoke scripts 驗證；frontend 不新增 production inference dashboard、SSE / WebSocket streaming UI、autoscaling UI、paid API key UI 或 SLA surface。Validation 已通過：frontend build、backend full test、inference benchmark smoke skipped report、Phase 42 keyword `rg` 與 `git diff --check`。
- v0.43.0: AgentOps Governance / Secure Tool Runtime 已完成；frontend package / lock / fallback label 已同步到 `0.43.0`，Phase 43 的 tool permission policy、approval fail-closed gate 與 Agent replay / eval evidence 由 backend / docs / sample-data / smoke scripts 驗證；frontend 不新增 production autonomous Agent dashboard、任意 SQL / shell / filesystem tool、destructive tool、external side-effect tool、production approval workflow 或 production audit UI。Validation 已通過：frontend build、backend full test `269 passed, 1 warning`（pytest cache permission warning）、Agent replay smoke、Phase 43 keyword `rg` 與 `git diff --check`。
- v0.44.0: Document Intelligence QA / Human Review Loop 已完成；frontend package / lock / fallback label 已同步到 `0.44.0`，Phase 44 的 field confidence / evidence view、human correction / golden labels 與 parser field accuracy eval 已由 frontend surface、backend API、sample-data report 與 smoke scripts 驗證；frontend 不新增 production annotation platform、full document image annotation UI、layout analysis、table reconstruction、model training 或 production OCR accuracy tuning。Validation 已通過：frontend build、backend full test `270 passed, 1 warning`（pytest cache permission warning）、parser field accuracy smoke（field accuracy `0.6`、sample count `5`、missing / wrong / evidence mismatch 各 `1`）、Phase 44 keyword `rg` 與 `git diff --check`。
- Phase 44 follow-up: `44-02` Field Confidence and Evidence View 已完成；Admin / Analyst structured fields surface 會顯示 field confidence、evidence linked / unmatched / unavailable、source text、source page、source bbox、parser source 與 fallback reason。Validation 已通過：frontend build、headless Chrome desktop / mobile browser evidence surface、Phase 44 keyword `rg` 與 `git diff --check`。不 bump version，不新增人工修正寫入、golden labels、parser accuracy eval、OCR / VLM provider、parser ranking 變更或 full document image annotation UI。
- Phase 44 follow-up: `44-03` Human Correction and Golden Labels 已完成；Admin / Analyst structured fields surface 可在每個欄位保存 corrected value 與 reviewer reason，成功後顯示 latest golden label version，並可匯出 golden labels artifact。Viewer 維持 read-only，不能修改 correction。Validation 已通過：frontend build、correction / golden label smoke、Phase 44 keyword `rg` 與 `git diff --check`。不 bump version，不新增 production annotation workflow、multi-review、external labeling service、model training writeback 或 destructive edit / delete flow。
- Phase 44 follow-up: `44-04` Parser Field Accuracy Eval 已完成；`scripts/parser-field-accuracy-smoke.ps1` 可重跑 field accuracy / document accuracy / missing field / wrong value / evidence mismatch 報告，tracked report 放在 `sample-data/eval/parser-field-accuracy-report.json`。Validation 已通過：parser field accuracy smoke、Phase 44 keyword `rg` 與 `git diff --check`。不 bump version，不新增 RAG retrieval eval、LLM-as-judge、model training、production analytics dashboard 或 automatic parser correction。
- v0.41.0: RAG Quality Regression / DatasetOps 已完成；frontend package / lock / fallback label 已同步到 `0.41.0`，Phase 41 的 golden dataset metadata、retrieval regression report 與 chunking / indexing ablation report 由 backend / docs / sample-data / smoke scripts 驗證；frontend 不新增 production eval dashboard、LLM-as-judge、production monitoring UI 或 dataset labeling UI。Validation 已通過：frontend build、backend full test、retrieval regression report smoke、Phase 41 keyword `rg` 與 `git diff --check`。
- v0.20.0: Interview MVP Packaging 已完成；frontend build、local demo view 檢查、README demo media 與 release 文件同步已完成。
- v0.21.0: Real GPU OCR Interview Demo Path 已完成；frontend upload 預設走 provider-selected real GPU OCR，mock OCR 只作手動 fallback。
- v0.22.0: RAG Query Hardening 已完成；frontend contract 不變，backend keyword query normalization 支援中文 demo 問法命中。
- v0.23.0: Viewer Chat / Admin Ingestion Role Split 已完成；Viewer Chat-only 預設入口與後台知識庫管理 surface 已完成，版本與文件同步已完成。
- v0.24.0: VLM / Parser Minimal MVP 已完成；後台可觸發 deterministic invoice parser，顯示 structured fields 摘要、missing metadata 與 parser status，版本與文件同步已完成。
- v0.25.0: Agent Tool-use Minimal MVP 已完成；後台 Agent trace surface 可顯示 deterministic plan、allowlisted tool calls、observations、final answer、citations 與 fallback state，版本與文件同步已完成。
- v0.26.0: Real VLM Parser Provider Spike 已完成；後台 structured fields surface 可顯示 `vlm_invoice` / `deterministic_invoice` parser source 與 fallback metadata，Agent trace 仍只透過 `get_document_fields` 讀取保存結果。
- v0.27.0: Aggressive Demo Defaults 已完成；後台預設入口、OCR 後 best-effort parser + vector indexing、default `hybrid_rerank` retrieval source / fallback 顯示與版本文件同步已完成。
- v0.27.1: OCR / VLM Evidence Alignment 已完成；backend VLM parser 使用 image + OCR context，欄位結果可保留 OCR line / bbox evidence 或明確 unmatched 狀態。
- v0.28.0: Document Sources / Demo Auth Mode 已完成；UI 會依 `text_upload`、`pdf_text`、`pdf_scanned_pending_ocr` 顯示來源狀態，demo auth mode 會先顯示 login screen，Admin / Analyst 可使用 ingestion，Viewer 只能查詢。
- v0.29.0: Built-in RAG Eval Admin Surface 已完成；後台新增「測試RAG」固定 `hybrid_rerank` metrics，Agent 執行紀錄可摺疊，Viewer 不顯示後台測試與 Agent 操作。
- v0.31.0: PostgreSQL / Schema / Repository Foundation 已完成；frontend version / fallback label 已同步，DB-backed mode 仍由 backend env opt-in，不新增 production DB 管理 UI、RBAC 或 worker surface。
- v0.32.0: Formal Auth / RBAC / Tenant Boundary 已完成；frontend version / fallback label 已同步，Admin / Analyst / Viewer role surface 與 backend permission guard 對齊，Viewer 不顯示 ingestion / eval / Agent write controls；不新增 SSO、OAuth、MFA、Redis session、worker、deployment hardening 或 production login runtime。
- v0.33.0: Redis + NATS Worker Pipeline 已完成；frontend version / fallback label 已同步，worker task status 由 backend `/tasks` API 與 smoke script 驗證；不新增 production worker dashboard、autoscaling 或 deployment hardening。
- v0.34.0: Production OCR / Scanned PDF Pipeline 已完成；frontend version / fallback label 已同步，scanned PDF OCR baseline 由 backend API 與 smoke script 驗證；Browser desktop `1440px` / mobile `390px` 已確認 upload 與 OCR status surface 無 horizontal overflow。不新增 production layout review UI、table reconstruction 或 production worker dashboard。
- v0.35.0: RAG Indexing Quality Hardening 已完成；frontend package / lock / fallback version 已同步，chunking strategy、Qdrant payload filter、reindex 與 stale cleanup 由 backend API 與 smoke script 驗證。不新增 production eval dashboard、LLM-as-judge 或 production indexing worker。
- v0.36.0: Eval Dashboard / Rerank Analysis 已完成；frontend package / lock / fallback version 已同步，後台 Strategy comparison panel 可顯示 strategy metrics、failure / fallback cases、trace metadata coverage 與 rerank before / after rank / score。Chrome GUI DevTools desktop / mobile 已確認畫面可渲染；不新增 LLM-as-judge、answer faithfulness、citation quality scoring 或 production monitoring trend。
- v0.37.0: Inference Ops / vLLM Serving 已完成；frontend package / lock / fallback version 已同步，OpenAI-compatible / vLLM path 由 backend env、local docs 與 `scripts/inference-benchmark-smoke.ps1` 驗證；frontend 不新增 production inference dashboard、streaming UI、model registry 或 secret vault。
- v0.38.0: Agent Runtime Hardening 已完成；frontend package / lock / fallback version 已同步，後台 Agent trace surface 可顯示 planner fallback、permission decision、tool tier、side-effect policy 與 fallback reason；frontend 不新增 production autonomous Agent dashboard、任意 SQL / shell / filesystem tool、destructive tool 或 production approval workflow。
- v0.39.0: Deployment / Observability / Fine-tuning Track 已完成；frontend package / lock / fallback label 已同步到 `0.39.0`，K8s baseline、Loki / Grafana observability path 與 fine-tuning research artifacts 由 backend / infra / docs / smoke scripts 驗證；frontend 不新增 production deployment dashboard、production alerting UI 或 production training UI。
- v0.40.0: JD Evidence Hardening 已完成；frontend package / lock / fallback label 已同步到 `0.40.0`，Phase 40 的 Embedding / SFT evidence、inference hardware benchmark evidence 與 observability dashboard evidence 由 backend / infra / docs / smoke scripts 驗證；frontend 不新增 production training UI、production inference dashboard、production observability dashboard、production alerting UI 或 production guarantee。Validation 已通過：frontend build、backend full test、baseline demo smoke、Phase 40 evidence `rg`、release `rg` 與 `git diff --check`。
