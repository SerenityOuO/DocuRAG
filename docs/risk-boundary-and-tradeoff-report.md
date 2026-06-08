# Risk Boundary And Tradeoff Report

這份 risk boundary report 用來誠實說明 DocuRAG 目前哪些能力已完成、哪些只是 demo-safe、哪些是 research-only，以及哪些仍屬 future production hardening。它和 [JD Evidence Matrix](./jd-evidence-matrix.md)、[System Design Walkthrough](./system-design-walkthrough.md)、[Demo Scenario Pack](./demo-scenario-pack.md) 互相對照：matrix 說明能力證據，walkthrough 說明資料流，scenario pack 說明展示路線，本文件專門回答「這樣做有什麼風險，為什麼現在先不做 production service」。

## Status Language

| Status | Meaning | Interview wording |
|---|---|---|
| completed | 已有主線 release、測試、smoke、文件或 artifact 可驗證 | 這部分可以展示，也能重跑 validation |
| demo-safe | 可本機展示，且有 fallback 或 skip-safe 行為，但不是 production runtime | 這是受控 demo path，不是 production guarantee |
| research-only | 只提供資料格式、研究證據或規劃，不接 runtime | 我可以說明方法，但沒有宣稱已訓練或部署 |
| skip-safe | optional runtime 不可用時會明確 skipped / fallback，不假裝成功 | unavailable 是可預期狀態，不是隱藏失敗 |
| future backlog | 已知道下一步，但還沒有有效 ticket 或不在本期 scope | 我知道 production 需要補什麼，但這次不提前做 |

## Risk Matrix

| Risk boundary | Current status | mitigation | Remaining gap | Next step / future backlog |
|---|---|---|---|---|
| data isolation | demo-safe | Formal auth mode 有 signed bearer guard、project access filtering、Viewer forbidden tests；Qdrant payload filter 可用 tenant / project / document / source 收斂查詢範圍 | 沒有 production identity provider、SSO / OAuth / MFA、完整 tenant lifecycle、audit retention 或 production session revocation | 定義 production identity provider、tenant lifecycle、audit retention 與 cross-tenant regression tests |
| production DB migration | demo-safe | Local JSON default 保持可重現；PostgreSQL repository 是 opt-in；migration script 從 local JSON 搬到 PostgreSQL，且沒有 destructive delete path | 沒有 production backup / restore、online migration、rollback runbook、data validation gate、schema drift monitoring | 另開 migration hardening ticket，要求 rollback / downgrade / data safety 規範 |
| worker durability | demo-safe | Redis / NATS 已展示 cache、rate limit、memory worker skeleton、task status API 和 worker smoke；worker unavailable 不會被包裝成 production async pipeline | 沒有 durable JetStream consumer、retry store、DLQ、idempotency key enforcement、worker autoscaling 或 production OCR / parser / indexing / eval queue | 補 durable worker contract、retry / DLQ schema、idempotency test、queue metrics |
| observability | demo-safe | API / RAG / eval / worker 可以輸出 JSONL trace；Loki / Grafana local profile 和 dashboard evidence 可回答 observability data shape | 沒有 production alerting、SLO、pager、incident workflow、distributed tracing、APM vendor、long-term retention | 補 production observability contract，定義 SLO、alert rule、retention、incident response |
| model latency | demo-safe / skip-safe | Ollama default、OpenAI-compatible / vLLM optional path 有 timeout guardrails、provider fallback metadata、benchmark skipped report 和 capacity planning | 沒有 production inference gateway、quota、circuit breaker、multi-GPU serving、SLA、billing / secret management 或 autoscaling controller | 補 inference gateway runtime / metrics / quota ticket，與 capacity planning report 對齊 |
| OCR / VLM accuracy | demo-safe | PaddleOCR-first flow、VLM-first parser、field confidence、OCR evidence mapping、human correction、golden labels 和 parser field accuracy smoke 可量化 missing / wrong / evidence mismatch | 沒有 production OCR accuracy tuning、layout analysis、table reconstruction、multi-review workflow、external labeling service 或 model training writeback | 補 annotation workflow / labeling governance / parser regression dataset，再考慮 training loop |
| Agent safety | completed / demo-safe | Agent tools 是 allowlisted read-only；tool permission metadata 有 risk tier、approval state、side-effect policy；future high-risk approval fail-closed；replay report 可檢查 evidence coverage | 沒有 production approval workflow、external side-effect tools、任意 SQL、shell、filesystem command、destructive tool、long-term audit store | 若要加 high-risk tool，必須先補 approval API、audit persistence、human confirmation UI 和 policy tests |

## Tradeoff Answers

### Why keep fallback paths?

Fallback 不是降低品質要求，而是讓 demo 在 optional runtime 不可用時仍能誠實展示系統邊界。RAG fallback 到 keyword evidence 時，citation 還是 grounded；VLM parser fallback 到 deterministic parser 時，trace 會留下 fallback reason；vLLM unavailable 時 benchmark 會 skipped，而不是假裝 serving 成功。

面試說法：

> 我保留 fallback，是為了讓 demo 可重現，也讓 unavailable runtime 變成可觀測狀態。production 當然需要更嚴格的 alert、retry 和 quality gate，但 MVP 階段先把失敗說清楚，比假裝全部成功更重要。

### Why not introduce production services earlier?

Production service 會帶來 secret、migration、monitoring、rollback、billing、incident workflow 和維運成本。如果 ticket 沒有明確要求，提前導入會讓 demo 失去可重現性，也讓風險被藏在 infrastructure 之下。DocuRAG 的策略是先用 local JSON、demo auth、optional Redis / NATS、optional vLLM 和 local observability profile 建立可驗證證據，再逐步替換成 production-grade service。

面試說法：

> 我不是不知道 production 需要 PostgreSQL、durable worker、observability 和 identity provider，而是刻意把它們拆成可驗證的小切片。這樣每次引入新的 production dependency 時，都能同時補 rollback、validation 和 boundary docs。

### Why local JSON before PostgreSQL?

Local JSON 讓每張 ticket 可以快速驗證，也方便檢查 OCR、parser、chunks、Agent runs 和 eval artifacts。PostgreSQL repository 已有 opt-in path，代表資料模型和 migration 方向不是空白，但 default 仍保留 local JSON 以維持本機 demo 穩定。

Tradeoff：

| Choice | Benefit | Risk |
|---|---|---|
| Local JSON default | 快速、透明、容易重跑 smoke | 不適合 multi-user、transaction、backup 或 long-term production operation |
| PostgreSQL opt-in | 可展示 schema / repository boundary | production migration、rollback、connection pool、backup 還沒完成 |

### Why sync API before durable workers?

OCR / parser / indexing 先保留同步 demo path，可以讓每張 ticket 的輸入輸出更容易驗證。Redis / NATS worker skeleton 用來展示 async architecture boundary，但不把它說成 durable production worker。

Tradeoff：

| Choice | Benefit | Risk |
|---|---|---|
| Sync demo path | 好測、好 debug、適合面試操作 | 長任務會阻塞，缺少 retry / DLQ / autoscaling |
| Durable worker future | 可承接 OCR / parser / indexing / eval job | 需要 idempotency、task store、monitoring、backpressure 和 failure policy |

## Interview Risk Answers

| Question | Short answer | Boundary to keep |
|---|---|---|
| 這能保證跨租戶資料隔離嗎？ | 現在能展示 role / project guard 和 metadata filter，但 production tenant isolation 還需要 identity provider、audit retention 和更完整 regression tests | 不說成 enterprise tenant isolation |
| migration 安全嗎？ | 目前 migration 是 local JSON to PostgreSQL 的 opt-in path，沒有 destructive delete；production migration 需要 rollback / backup / validation gate | 不連真實 production DB |
| worker 真的耐用嗎？ | 現在是 Redis / NATS demo-safe skeleton 和 task status，不是 durable JetStream pipeline | 不說成 production async OCR pipeline |
| observability 可以上線嗎？ | 現在能輸出 JSONL trace 並用 Loki / Grafana local profile 看資料形狀 | 不說成 production alerting / incident workflow |
| latency 怎麼處理？ | 目前有 timeout guardrails、fallback metadata、benchmark report 和 capacity planning | 不承諾 SLA、autoscaling 或 multi-GPU throughput |
| OCR / VLM accuracy 怎麼驗？ | Phase 44 已用 golden labels 和 parser field accuracy report 量化 missing / wrong / evidence mismatch | 不說成 production annotation / model training loop |
| Agent 會亂做事嗎？ | 目前 tools allowlist read-only，permission guard 和 approval fail-closed boundary 會擋高風險工具 | 不開放任意 SQL、shell、filesystem 或 destructive action |

## Production Hardening Backlog

| Area | Future hardening |
|---|---|
| data isolation | SSO / OAuth / MFA、tenant lifecycle、project membership audit、cross-tenant negative tests |
| migration | Alembic migration review、backup / restore runbook、online migration validation、rollback rehearsal |
| worker durability | JetStream durable consumer、retry / DLQ、idempotency store、worker autoscaling、queue metrics |
| observability | SLO、alert rules、pager / incident workflow、distributed tracing、retention policy |
| latency | inference gateway quota、circuit breaker、provider health, p95 / p99 dashboard、capacity test matrix |
| OCR / VLM accuracy | larger golden dataset、layout / table eval、multi-review correction workflow、label governance |
| Agent safety | production approval workflow、persistent audit store、human confirmation UI、external side-effect policy |

## What Not To Claim

- 不把 demo auth / formal bearer guard 說成 enterprise identity platform。
- 不把 local JSON default 說成 production database。
- 不把 Redis / NATS worker skeleton 說成 durable production worker pipeline。
- 不把 JSONL + local Loki / Grafana profile 說成 production observability stack。
- 不把 vLLM skipped report 說成 production inference gateway。
- 不把 parser field accuracy smoke 說成 production OCR / VLM accuracy guarantee。
- 不把 allowlisted read-only Agent tools 說成 production autonomous Agent。

## Closing

DocuRAG 的 production readiness 重點不是假裝所有 enterprise 能力都已完成，而是每個風險都有清楚 mitigation、剩餘缺口和下一步。這讓面試時可以誠實回答 tradeoff：目前成果足以展示 AI application engineering、RAG quality、Document Intelligence QA 和 AgentOps governance，但 production hardening 仍需要按 ticket-first workflow 逐步補齊。
