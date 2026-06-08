# Demo Scenario Pack

這份 demo scenario pack 用來把 DocuRAG 的最終面試展示拆成可選路線。面試時不需要每條都跑完，可以依追問方向選主線；每條主線都要先說清楚前置條件、操作步驟、預期畫面 / 輸出，以及 runtime unavailable 時的 fallback 解讀。

## Demo Map

| Path | When to use | Main evidence |
|---|---|---|
| RAG quality | 面試官關心檢索品質、評估指標、citation 和 trace | Viewer Chat、built-in RAG eval、retrieval regression report、chunking / indexing ablation |
| Document Intelligence QA | 面試官關心 OCR / VLM parser、欄位可信度、人工修正與 golden labels | Admin Ingestion、structured fields、field confidence、parser field accuracy report |
| AgentOps governance | 面試官關心 Agent tool-use 是否可控、可審計、可重播 | Agent trace、tool permission guard、approval fail-closed boundary、agent replay report |
| Inference Gateway / capacity planning | 面試官追問推論服務、vLLM、timeout、KV cache 或 GPU capacity | Inference benchmark smoke、capacity planning report、provider fallback metadata |
| Observability evidence | 面試官追問 logs、trace、dashboard、failure diagnosis | JSONL trace logs、Loki / Grafana local profile、observability dashboard evidence |
| K8s / deployment boundary | 面試官追問部署與 production readiness | K8s baseline manifests、Docker Compose config、risk boundary 說明 |

## Path 1 - RAG Quality

### 前置條件

| Requirement | Demo-safe option |
|---|---|
| Backend / frontend 可啟動 | 用 README / README_DEV 的本機啟動流程 |
| 已有 demo documents 或 synthetic eval data | 使用 repo 內 `sample-data/` 與既有 smoke scripts |
| Optional Qdrant / embedding / reranker runtime | 沒啟用也可以展示 keyword fallback 與 trace metadata |

### 操作步驟

1. 先用 Viewer Chat 問一個已建置知識庫可回答的問題，展示 answer source、retrieval source 和 citation summary。
2. 切到 Admin / Analyst 後台的 built-in RAG eval，執行固定 `hybrid_rerank` benchmark。
3. 展示 Hit Rate@K、MRR@K、Recall@K、latency、failure count、fallback count 和 trace metadata count。
4. 若面試官追問 regression，補充 `scripts/retrieval-regression-report.ps1` 與 `docs/chunking-indexing-ablation-report.md`。

### 預期畫面 / 輸出

| Surface | Expected result |
|---|---|
| Viewer Chat | 回答包含 citations，並標示 retrieval source |
| Built-in RAG eval | 顯示 retrieval metrics、failure / fallback summary |
| Regression report | 能說明 keyword baseline gate、strategy comparison 和 ablation evidence |

### fallback 解讀

- Qdrant、embedding 或 reranker 不可用時，RAG 不應 hard fail，會回到 keyword evidence 並保留 retrieval source / fallback reason。
- 這代表 demo 是可降級的，不代表 production retrieval quality 已被保證。
- 若結果低於預期，要說明這是 retrieval regression 會追的問題，而不是把單次回答包裝成品質保證。

## Path 2 - Document Intelligence QA

### 前置條件

| Requirement | Demo-safe option |
|---|---|
| Admin / Analyst 權限 | 使用 demo auth 或 formal auth guard 展示 role boundary |
| 可上傳 invoice / image / PDF / TXT sample | 使用 repo 內 sample 或本機 synthetic file |
| OCR / parser runtime | PaddleOCR / VLM 不可用時仍可展示 explicit fallback 與 deterministic parser |

### 操作步驟

1. 以 Admin / Analyst 進入 ingestion surface，上傳 sample document。
2. 執行 provider-selected OCR，觀察 OCR status、OCR text / chunks 或 fallback error。
3. 觸發 VLM-first parser，展示 structured fields、parser source、confidence、source text、source page / bbox。
4. 在 field confidence view 解釋 `linked`、`unmatched`、`unavailable` evidence state。
5. 保存一筆 demo-safe human correction，然後說明 golden labels export 如何供 parser field accuracy eval 使用。
6. 展示 `scripts/parser-field-accuracy-smoke.ps1` 的 report：field accuracy、document accuracy、missing field、wrong value、evidence mismatch。

### 預期畫面 / 輸出

| Surface | Expected result |
|---|---|
| Admin Ingestion | 文件狀態、OCR / parser 狀態與 structured fields 可被檢查 |
| Field QA view | 每個欄位有 confidence、evidence、fallback reason 或 correction metadata |
| Parser accuracy report | 用 golden labels 對照 parser output，量化 missing / wrong / evidence mismatch |

### fallback 解讀

- OCR provider 不可用時，mock OCR 只能作手動 fallback / validation path，不是 default success。
- VLM parser timeout、unavailable 或 invalid response 時，系統會回 deterministic parser 並記錄 fallback reason。
- Human correction 是 demo-safe append-only metadata，不是 production annotation workflow，也不回寫模型訓練。

## Path 3 - AgentOps Governance

### 前置條件

| Requirement | Demo-safe option |
|---|---|
| 已有 document fields 或 local chunks | 可先跑 Document Intelligence QA path 或使用既有 sample data |
| Admin / Analyst role | Viewer 應被 backend permission guard 擋下 write / agent-sensitive path |
| Agent replay artifact | 使用 repo 內 tracked replay sample 與 smoke report |

### 操作步驟

1. 在 Admin / Analyst surface 執行一個 Agent run，讓 Agent 使用 read-only allowlisted tools。
2. 展開 trace，說明 planner、tool calls、observation、final answer、citations 和 fallback state。
3. 指出每個 tool 的 risk tier、approval_required、approval_state、side-effect policy 與 permission decision。
4. 切換或說明 Viewer role 時，展示 Viewer 不能執行 ingestion / write / restricted action。
5. 若面試官追問 audit，展示 `scripts/agent-replay-smoke.ps1` 與 replay report 如何檢查 tool correctness、permission compliance 和 evidence coverage。

### 預期畫面 / 輸出

| Surface | Expected result |
|---|---|
| Agent trace | 能看見受控 planner、allowlisted tools、source-backed answer |
| Permission metadata | 能說清楚工具是否 read-only、是否需要 approval、是否有 side effect |
| Replay report | 能重播檢查 evidence coverage 與 policy compliance |

### fallback 解讀

- LLM planner 不可用、timeout 或輸出不合法時，會回 deterministic planner。
- Future high-risk tool 若需要 approval 但沒有 approved 狀態，會 fail closed。
- 這不是 production autonomous Agent，也不開放任意 SQL、shell、filesystem command 或 destructive tool。

## Optional Path - Inference Gateway / Capacity Planning

### 前置條件

| Requirement | Demo-safe option |
|---|---|
| Ollama local provider | 可用時展示 generation / VLM / embedding；不可用時展示 fallback |
| OpenAI-compatible / vLLM endpoint | optional，未啟用時使用 skipped benchmark report |
| Capacity planning docs | `docs/inference-capacity-planning-report.md` 與 hardware benchmark evidence |

### 操作步驟

1. 用 RAG query 或 inference benchmark smoke 說明 provider routing 與 timeout guardrails。
2. 展示 token、latency、throughput、KV cache / VRAM estimate 與 provider unavailable skip reason。
3. 把 OpenAI-compatible / vLLM path 說成 optional serving boundary，不說成 production inference gateway。

### 預期畫面 / 輸出

| Surface | Expected result |
|---|---|
| Inference benchmark smoke | 有 latency / token / throughput 或 clear skipped report |
| Capacity report | 能回答模型大小、VRAM、KV cache、concurrency 的取捨 |
| RAG generation metadata | Provider timeout 或 unavailable 有 fallback metadata |

### fallback 解讀

- vLLM endpoint 不存在時，skipped report 是正確結果，不是 demo failure。
- Paid API key 或 production secret 不需要也不應在 demo 中出現。
- 目前展示的是 routing / capacity planning 思路，不是 SLA、quota、billing 或 autoscaling controller。

## Optional Path - Observability Evidence

### 前置條件

| Requirement | Demo-safe option |
|---|---|
| Observability log path | 可用 `DOCURAG_OBSERVABILITY_LOG_PATH` opt-in 寫 JSONL |
| Local Loki / Grafana profile | optional，本機沒啟動也可看 docs evidence |
| Existing smoke scripts | API / RAG / eval / worker trace logs 可用 smoke 產生 |

### 操作步驟

1. 展示 JSONL trace log 的事件形狀：API request、RAG query、eval run、worker task。
2. 展示 `docs/observability-dashboard-evidence.md` 裡的 dashboard query 和 screenshot / report 說法。
3. 說明 failure diagnosis 會靠 correlation fields、request id、provider status、fallback reason。

### 預期畫面 / 輸出

| Surface | Expected result |
|---|---|
| JSONL logs | 能看到 structured event、latency、status、fallback reason |
| Loki / Grafana docs | 能說明 dashboard panel 和 query examples |
| Smoke output | 不因 observability path unavailable 讓主流程 hard fail |

### fallback 解讀

- 本機 observability 是 evidence path，不是 production alerting。
- 沒有 SLO、incident workflow、distributed tracing、APM vendor 或 long-term retention。
- 面試時可把它當成「我知道要觀測什麼」的證據，不把它說成 production monitoring stack。

## Optional Path - K8s / Deployment Boundary

### 前置條件

| Requirement | Demo-safe option |
|---|---|
| Docker Compose config | `infra/docker-compose.yml` 可說明本機依賴拓撲 |
| K8s baseline manifests | `infra/k8s/` 提供 namespace、config、secret template、service、deployment、probe 與 resource examples |
| Production risk explanation | 用 risk / tradeoff report 補足 production gap |

### 操作步驟

1. 先用 Docker Compose 說明 backend、frontend、Qdrant、Redis、NATS、observability profile 的本機關係。
2. 再用 K8s baseline 說明 probe、resource request / limit、worker placeholder、rollback docs。
3. 明確說：這是 deployment boundary evidence，不是 managed production deployment。

### 預期畫面 / 輸出

| Surface | Expected result |
|---|---|
| Compose config | 能看出 local runtime dependencies |
| K8s manifests | 能討論 readiness / liveness、resources、secret template 和 optional HPA shape |
| Boundary explanation | 不宣稱 multi-cluster、Ingress TLS、managed secret 或 production autoscaling |

### fallback 解讀

- 沒有 K8s cluster 時，不需要把 dry-run failure 包裝成錯誤；可直接看 manifests 和 README。
- Production deployment 仍需 Helm / GitOps / Ingress TLS / managed secrets / backup / incident workflow。
- 這條 optional path 只用於被追問 deployment 時補證據。

## Closing Script

> 我會把 DocuRAG 定位成一個可驗證的文件 AI 平台 demo，而不是 production SaaS。主線展示 RAG quality、Document Intelligence QA 和 AgentOps governance；optional path 用來回答 inference、observability 和 deployment 追問。每個 path 都有 fallback 解讀，避免把 unavailable runtime 說成成功，也避免把 demo-safe 能力誇大成 production guarantee。
