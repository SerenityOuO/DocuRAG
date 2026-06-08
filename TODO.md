# TODO

本 checklist 追蹤 DocuRAG AgentOps 目前的 Phase 00 到 v0.45 final portfolio pack backlog。每張 ticket 完成後應可單獨 commit，並更新對應項目。

## Release Version Map

已完成舊 ticket 不回填 `Release Impact`；從目前 release 修正與後續 backlog 起，Phase 與版本號必須明確對應：

- Phase 08 -> `v0.8.0`
- Phase 09 -> `v0.9.0`
- Phase 09 performance hardening -> `v0.9.1`
- Phase 10 -> `v0.10.0`
- Phase 11 -> `v0.11.0`
- Phase 12 -> `v0.12.0`
- Phase 13 -> `v0.13.0`
- Phase 14 -> `v0.14.0`
- Phase 15 -> `v0.15.0`
- Phase 16 -> `v0.16.0`
- Phase 17 -> `v0.17.0`
- Phase 18 -> `v0.18.0`
- Phase 19 -> `v0.19.0`
- Phase 20 -> `v0.20.0`
- Phase 21 -> `v0.21.0`
- Phase 22 -> `v0.22.0`
- Phase 23 -> `v0.23.0`
- Phase 24 -> `v0.24.0`
- Phase 25 -> `v0.25.0`
- Phase 26 -> `v0.26.0`
- Phase 27 -> `v0.27.0`
- Phase 27 evidence hardening -> `v0.27.1` when `27-02` is implemented
- Phase 28 -> `v0.28.0`
- Phase 29 -> `v0.29.0`
- Phase 30 hardening -> no version bump unless a later release sync ticket is created
- Phase 31 -> `v0.31.0`
- Phase 32 -> `v0.32.0`
- Phase 33 -> `v0.33.0`
- Phase 34 -> `v0.34.0`
- Phase 35 -> `v0.35.0`
- Phase 36 -> `v0.36.0`
- Phase 37 -> `v0.37.0`
- Phase 38 -> `v0.38.0`
- Phase 39 -> `v0.39.0`
- Phase 40 -> `v0.40.0`
- Phase 41 -> `v0.41.0`
- Phase 42 -> `v0.42.0`
- Phase 43 -> `v0.43.0`
- Phase 44 -> `v0.44.0`
- Phase 45 -> `v0.45.0`

後續 ticket 若完成整個 Phase，必須同步更新版本號、README / README_DEV、TODO、ROADMAP 與 validation 狀態；若不 bump version，ticket 必須明確寫原因。

目前已完成優先順序：

1. `tasks/phase-09-gpu-runtime/09-03-paddleocr-engine-lifecycle-preload.md` 已完成。
2. `tasks/phase-09-gpu-runtime/09-04-paddleocr-performance-observability-tuning.md` 已完成。
3. `tasks/phase-10-llm-rag/10-01-qwen3-ollama-provider-decision.md` 已完成，只固定 Ollama `qwen3.5:4b` provider decision 與 env 文件。
4. `tasks/phase-10-llm-rag/10-02-ollama-qwen3-client.md` 已完成，只新增最小 Ollama client building block，未改變既有 `/rag/query` deterministic baseline 預設。
5. `tasks/phase-10-llm-rag/10-03-qwen3-rag-generation.md` 已完成，只在 retrieved chunks 與 query 上加入可選 generation path。
6. `tasks/phase-10-llm-rag/10-04-qwen3-demo-smoke.md` 已完成，補齊 demo smoke、UI answer source 與 `v0.10.0` release/version sync。
7. `tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md` 已完成，只固定 Phase 11 embedding / Qdrant provider decision 與 backlog，不新增 runtime。
8. `tasks/phase-11-vector-rag/11-02-ollama-embedding-client.md` 已完成，只新增 disabled-by-default Ollama embedding client。
9. `tasks/phase-11-vector-rag/11-03-qdrant-local-runtime.md` 已完成，只新增 optional Qdrant local runtime / collection smoke。
10. `tasks/phase-11-vector-rag/11-04-vector-retrieval-demo-smoke.md` 已完成，補齊 optional vector retrieval path、fallback trace metadata、demo smoke 與 `v0.11.0` release/version sync。
11. `tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md` 已完成，固定 manual vector indexing contract 與 guardrails。
12. `tasks/phase-12-vector-indexing/12-02-vector-indexing-service.md` 已完成，新增同步 vector indexing service / helper。
13. `tasks/phase-12-vector-indexing/12-03-vector-indexing-api.md` 已完成，新增手動 vector indexing API。
14. `tasks/phase-12-vector-indexing/12-04-vector-indexing-demo-smoke.md` 已完成，補齊 optional vector indexing smoke 與 `v0.12.0` release/version sync。
15. `tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md` 已完成，固定 retrieval evaluation contract。
16. `tasks/phase-13-retrieval-eval/13-02-retrieval-eval-dataset.md` 已完成，新增公開 retrieval eval dataset。
17. `tasks/phase-13-retrieval-eval/13-03-retrieval-eval-runner.md` 已完成，新增本機 retrieval eval runner。
18. `tasks/phase-13-retrieval-eval/13-04-retrieval-eval-demo-smoke.md` 已完成，補齊 retrieval eval smoke 與 `v0.13.0` release/version sync。

下一步優先順序：

1. `tasks/phase-14-retrieval-quality/14-01-rerank-provider-decision.md` 已完成，固定 Phase 14 retrieval quality planning boundary。
2. `tasks/phase-14-retrieval-quality/14-02-retrieval-quality-contract.md` 已完成，規劃 future rerank / hybrid trace contract。
3. `tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md` 已完成，規劃 eval dataset 擴充方向。
4. `tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md` 已完成，規劃 future demo / validation / release checklist。
5. `tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md` 已完成，選定 FastEmbed + `BAAI/bge-reranker-base` 作為 disabled-by-default `vector_rerank` runtime spike 起點。
6. `tasks/phase-15-rerank-runtime/15-02-rerank-provider-adapter.md` 已完成，新增 disabled-by-default FastEmbed rerank adapter building block。
7. `tasks/phase-15-rerank-runtime/15-03-vector-rerank-eval-integration.md` 已完成，將 optional `vector_rerank` 接入 retrieval eval runner。
8. `tasks/phase-15-rerank-runtime/15-04-rerank-demo-release-sync.md` 已完成，補齊 rerank demo / eval smoke 文件並完成 `v0.15.0` release/version sync。
9. `tasks/phase-16-hybrid-retrieval/16-01-hybrid-retrieval-contract.md` 已完成，固定 optional `hybrid` retrieval contract、merge policy、dedupe key 與 fallback trace metadata。
10. `tasks/phase-16-hybrid-retrieval/16-02-eval-dataset-expansion-json.md` 已完成，公開 retrieval eval dataset 已擴充到 12 筆並覆蓋 Phase 16 retrieval quality case tags。
11. `tasks/phase-16-hybrid-retrieval/16-03-hybrid-eval-strategy-integration.md` 已完成，將 optional `hybrid` 接入 retrieval eval runner 並新增 explicit `-RunHybrid` smoke flag。
12. `tasks/phase-16-hybrid-retrieval/16-04-hybrid-demo-release-sync.md` 已完成，補齊 hybrid demo / eval smoke 並執行 `v0.16.0` release/version sync。
13. `tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md` 已完成，固定 retrieval trace UI / eval visibility contract。
14. `tasks/phase-17-retrieval-trace-ui/17-02-frontend-retrieval-trace-panel.md` 已完成，在既有 RAG result UI 實作 frontend trace panel。
15. `tasks/phase-17-retrieval-trace-ui/17-03-eval-result-report-summary.md` 已完成，改善 eval result summary 與 fallback visibility。
16. `tasks/phase-17-retrieval-trace-ui/17-04-trace-ui-demo-release-sync.md` 已完成，補齊 trace UI / eval visibility demo validation 並執行 `v0.17.0` release/version sync。
17. `tasks/phase-18-hybrid-rerank-planning/18-01-hybrid-rerank-boundary-contract.md` 已完成，固定 `hybrid_rerank` planning boundary、candidate flow、trace metadata 與 fallback states。
18. `tasks/phase-18-hybrid-rerank-planning/18-02-hybrid-rerank-eval-dataset-plan.md` 已完成，規劃 future eval dataset case 類型、demo-safe 資料邊界與 metrics 摘要使用方式。
19. `tasks/phase-18-hybrid-rerank-planning/18-03-hybrid-rerank-trace-report-plan.md` 已完成，規劃 future trace / report visibility、report fields 與 missing metadata behavior。
20. `tasks/phase-18-hybrid-rerank-planning/18-04-phase-18-demo-release-plan.md` 已完成，規劃 future demo validation、release sync checklist 與 deferred items。
21. `tasks/phase-19-hybrid-rerank-runtime/19-01-hybrid-rerank-eval-provider.md` 已完成，實作 optional `hybrid_rerank` eval provider，將 hybrid candidates 交給 rerank service 重新排序。
22. `tasks/phase-19-hybrid-rerank-runtime/19-02-hybrid-rerank-smoke-flag.md` 已完成，新增 eval runner / smoke script 的 explicit `hybrid_rerank` strategy 與 `-RunHybridRerank` flag。
23. `tasks/phase-19-hybrid-rerank-runtime/19-03-hybrid-rerank-trace-report-sync.md` 已完成，補齊 `hybrid_rerank` trace / report visibility 與文件解讀。
24. `tasks/phase-19-hybrid-rerank-runtime/19-04-hybrid-rerank-demo-release-sync.md`：重跑 final validation，並在 Phase 19 完成時執行 `v0.19.0` release/version sync。
25. `tasks/phase-20-interview-mvp-packaging/20-01-interview-demo-doc-refresh.md`：更新面試 demo 文件，對齊目前已完成 runtime、Phase 18 planning-only 與 Phase 19 `hybrid_rerank` implementation 狀態。
26. `tasks/phase-20-interview-mvp-packaging/20-02-sample-eval-coverage-expansion.md`：補齊公開 sample data 與 retrieval eval dataset 覆蓋率，目標至少 5 份 sample documents 與 20 筆 eval cases。
27. `tasks/phase-20-interview-mvp-packaging/20-03-demo-media-and-readme-polish.md`：補齊 README 面試導覽、截圖或 GIF 等 demo media。
28. `tasks/phase-20-interview-mvp-packaging/20-04-final-interview-mvp-validation.md`：重跑 final validation，並在 Phase 20 完成時執行 `v0.20.0` release/version sync。
29. `tasks/phase-21-real-gpu-ocr-demo/21-01-real-gpu-ocr-frontend-flow.md`：將 frontend upload 面試主線改為 provider-selected real GPU OCR-first，mock OCR 只保留為手動 fallback，並同步 `v0.21.0` release 文件與版本。
30. `tasks/phase-22-rag-query-hardening/22-01-keyword-query-normalization.md`：強化 default keyword RAG query normalization，讓中文 query 與 demo-safe alias 可命中英文 OCR chunks，並同步 `v0.22.0` release 文件與版本。
31. `tasks/phase-23-role-split-demo/23-01-role-boundary-contract.md`：固定 Viewer Chat 與 Admin / Analyst Ingestion 的產品邊界，讓前台只負責查詢既有知識庫，後台才操作 upload / OCR / ingestion。
32. `tasks/phase-23-role-split-demo/23-02-viewer-chat-only-surface.md`：將 frontend 預設入口收斂為 Viewer Chat-only，不在前台主畫面顯示 upload / OCR / mock fallback。
33. `tasks/phase-23-role-split-demo/23-03-admin-ingestion-surface.md`：建立明確 Admin / Analyst 後台知識庫管理 surface，承接 upload、provider-selected OCR、狀態與手動 fallback。
34. `tasks/phase-23-role-split-demo/23-04-role-split-demo-release-sync.md`：完成 `v0.23.0` release/version sync 與 final validation。
35. `tasks/phase-24-vlm-parser-mvp/24-01-parser-contract.md`：固定 VLM-compatible parser contract、invoice structured fields、parser status 與 fallback metadata；文件 / contract ticket，不 bump version。
36. `tasks/phase-24-vlm-parser-mvp/24-02-invoice-parser-service.md`：實作 deterministic invoice parser service，從既有 OCR text 抽取 demo-safe structured fields，作為 future VLM / LLM parser fallback。
37. `tasks/phase-24-vlm-parser-mvp/24-03-document-fields-api.md`：新增 parse / fields API，將 parser result 保存到 local JSON metadata store。
38. `tasks/phase-24-vlm-parser-mvp/24-04-frontend-fields-surface.md`：在 Admin / Analyst ingestion surface 顯示 structured fields 摘要，Viewer Chat 仍保持只查詢。
39. `tasks/phase-24-vlm-parser-mvp/24-05-parser-demo-release-sync.md`：補齊 parser demo validation，並在 Phase 24 完成時執行 `v0.24.0` release/version sync。
40. `tasks/phase-25-agent-tool-use-mvp/25-01-agent-boundary-contract.md` 已完成，固定 Agent MVP boundary、allowlisted tools、deterministic planner 與 trace schema；文件 / contract ticket，不 bump version。
41. `tasks/phase-25-agent-tool-use-mvp/25-02-agent-tool-adapters.md` 已完成，實作 `get_document_fields`、`search_documents` 與 `summarize_invoice_fields` allowlisted tool adapters。
42. `tasks/phase-25-agent-tool-use-mvp/25-03-agent-run-api.md` 已完成，新增 `POST /agent/run` 與 `GET /agent/runs/{run_id}`，用 deterministic planner 串接 allowlisted tools。
43. `tasks/phase-25-agent-tool-use-mvp/25-04-frontend-agent-trace-surface.md` 已完成，在 demo UI 顯示 Agent plan、tool calls、observations、final answer 與 citations。
44. `tasks/phase-25-agent-tool-use-mvp/25-05-agent-demo-release-sync.md` 已完成，版本 / 文件 / smoke / Browser validation 已補齊。
45. `tasks/phase-26-vlm-parser-provider-spike/26-01-vlm-provider-decision.md` 已完成，固定 VLM provider env、input / output contract、fallback policy 與 Agent 承接方式；文件 / contract ticket，不 bump version。
46. `tasks/phase-26-vlm-parser-provider-spike/26-02-vlm-input-resolver.md` 已完成，新增 demo-safe image input resolver，只解析既有上傳檔案，不做 PDF rendering 或 VLM call。
47. `tasks/phase-26-vlm-parser-provider-spike/26-03-vlm-parser-adapter.md` 已完成，新增 VLM-first `vlm_invoice` parser adapter，輸出沿用 Phase 24 `DocumentFields` schema。
48. `tasks/phase-26-vlm-parser-provider-spike/26-04-parser-source-comparison.md` 已完成，在 API / trace 顯示 `deterministic_invoice` vs `vlm_invoice` 的 parser source、fallback reason 與 confidence。
49. `tasks/phase-26-vlm-parser-provider-spike/26-05-vlm-parser-demo-release-sync.md` 已完成，補齊 VLM parser demo validation、版本 / 文件同步與 `v0.26.0` release sync。
50. `tasks/phase-27-aggressive-defaults/27-01-aggressive-demo-defaults.md` 已完成，啟用 default `hybrid_rerank` RAG / Agent search、Ollama embedding、FastEmbed rerank adapter、frontend parser + vector indexing best-effort flow 與 `v0.27.0` release sync。
51. `tasks/phase-27-aggressive-defaults/27-02-ocr-vlm-evidence-alignment.md` 已完成，讓 VLM parser request 帶 image + OCR context，並將 VLM 欄位結果對回 OCR line / bbox 或標示 evidence unmatched / unavailable；同步 `v0.27.1` patch release。
52. `tasks/phase-27-aggressive-defaults/27-03-vector-source-expansion-contract.md` 已完成，固定 `ocr_image`、`text_upload`、`pdf_text` 與 `pdf_scanned_pending_ocr` vector source contract；planning ticket，不 bump version。
53. `tasks/phase-30-parser-ingestion-hardening/30-01-vlm-response-and-multi-upload-hardening.md` 已完成，強化 Ollama VLM response parsing 與後台多檔依序 ingestion；focused hardening ticket，不 bump version。
54. `tasks/phase-30-parser-ingestion-hardening/30-03-rag-vector-stale-filter-hardening.md` 已完成，讓 default `hybrid_rerank` vector branch 以目前文件 document ids 查詢 Qdrant，避免 stale vectors 消耗 `top_k` 後誤報 `vector_unavailable`；focused hardening ticket，不 bump version。
55. `tasks/phase-30-parser-ingestion-hardening/30-04-ollama-rag-generation-latency-guardrails.md` 已完成，讓 Ollama RAG generation 預設帶 `think=false` 與 `options.num_predict=512`，並把 guardrail 寫入 citation trace；focused hardening ticket，不 bump version。
56. `tasks/phase-31-enterprise-roadmap/31-01-phase-31-to-39-roadmap-plan.md` 已完成，新增 Phase 31 到 Phase 39 的 enterprise / production roadmap planning；文件 ticket，不 bump version。
57. `tasks/phase-40-interview-evidence-hardening/40-01-phase-40-jd-evidence-plan.md` 已完成，新增 Phase 40 JD evidence hardening roadmap；文件 ticket，不 bump version。
58. `tasks/phase-31-enterprise-roadmap/31-02-postgresql-boundary-and-migration-policy.md` 已完成，固定 Phase 31 PostgreSQL boundary、migration policy 與 local JSON fallback / migration path；文件 ticket，不 bump version。
59. `tasks/phase-31-enterprise-roadmap/31-03-db-schema-contract.md` 已完成，固定 Phase 31 core tables schema contract 與 local JSON mapping；文件 ticket，不 bump version。
60. `tasks/phase-33-redis-nats-worker-pipeline/33-02-redis-cache-rate-limit-session-slice.md` 已完成，新增 opt-in Redis session cache、RAG query cache、rate limit、health fallback 與 Docker Compose redis profile；不 bump version。
61. `tasks/phase-33-redis-nats-worker-pipeline/33-03-nats-worker-skeleton-and-task-status.md` 已完成，新增 optional NATS helper、worker skeleton placeholder handlers、task status store / API 與 NATS worker smoke script；不 bump version。
62. `tasks/phase-33-redis-nats-worker-pipeline/33-04-worker-demo-smoke-and-release-sync.md` 已完成，新增 worker demo smoke script，並同步 `v0.33.0` backend / frontend / Docker Compose / health test / README / README_DEV / backend README / frontend README / TODO / ROADMAP。

## Phase 30 Parser / Ingestion Hardening

- [x] `tasks/phase-30-parser-ingestion-hardening/30-01-vlm-response-and-multi-upload-hardening.md`: 修正 VLM fenced JSON / thinking JSON / alias 欄位造成的 `vlm_invalid_response`，並讓後台知識庫管理支援多檔依序 upload / OCR / parser / vector indexing。
- Release Impact: Version bump required: no。此 ticket 是 v0.29.0 後的 focused hardening，不更新 backend / frontend / Docker version。
- [x] 30-01 validation：`python -m pytest backend/tests/test_document_parser.py -q` 通過，`15 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`193 passed`（僅 pytest cache 權限警告）；`npm.cmd run build` 通過；Browser 檢查 `1280x900` 與 `390x844` 皆確認 file input `multiple=true`、未選檔 upload button disabled、horizontal overflow `0`；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-30-parser-ingestion-hardening/30-03-rag-vector-stale-filter-hardening.md`: Qdrant search payload 支援 document-scoped filter，`VectorRagProvider` 以目前 backend document ids 查詢 vector branch，保留 stale collection resilience 與既有 fallback trace。
- Release Impact: Version bump required: no。此 ticket 是 v0.29.0 後的 focused hardening，不更新 backend / frontend / Docker version。
- [x] 30-03 validation：`python -m pytest backend/tests/test_vector_store.py backend/tests/test_rag.py -q` 通過，`32 passed`（僅 pytest cache 權限警告）；full backend validation 併入 30-04 本次 final validation。
- [x] `tasks/phase-30-parser-ingestion-hardening/30-04-ollama-rag-generation-latency-guardrails.md`: Ollama `/api/generate` 預設送出 `think=false` 與 `options.num_predict=512`，可由 `DOCURAG_LLM_THINK` / `DOCURAG_LLM_NUM_PREDICT` 覆寫，citation trace 會標示 `llm_think` 與 `llm_num_predict`。
- Release Impact: Version bump required: no。此 ticket 是 v0.29.0 後的 focused hardening，不更新 backend / frontend / Docker version。
- [x] 30-04 validation：`python -m pytest backend/tests/test_llm.py backend/tests/test_rag.py -q` 通過，`33 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`199 passed`（僅 pytest cache 權限警告）；兩張 ticket 的 `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

## Phase 31-39 Enterprise Completion Roadmap

- [x] `tasks/phase-31-enterprise-roadmap/31-01-phase-31-to-39-roadmap-plan.md`: 新增後續完成路線，將目前未完成的 DB、正式權限、Redis、NATS、worker、PDF OCR pipeline、RAG quality dashboard、vLLM、Agent runtime、K8s 與 fine-tuning 拆成 Phase 31 到 Phase 39；文件 ticket，不 bump version。

後續實作 ticket backlog：

Phase 31 `v0.31.0` - PostgreSQL / schema / repository foundation：
- [x] `tasks/phase-31-enterprise-roadmap/31-02-postgresql-boundary-and-migration-policy.md`: 盤點 local JSON store 資料域、對應 future DB domain、固定 migration policy 與 local JSON fallback / migration path；文件 ticket，不 bump version。
- [x] `tasks/phase-31-enterprise-roadmap/31-03-db-schema-contract.md`: 定義 `documents`、`document_pages`、`document_chunks`、`extracted_fields`、eval tables 與 Agent tables 的欄位、nullable、index / key、`project_id` future metadata 與 local JSON mapping；文件 ticket，不 bump version。
- [x] `tasks/phase-31-enterprise-roadmap/31-04-repository-adapter-and-migration-path.md`: 完成 opt-in local JSON / PostgreSQL repository selection、PostgreSQL metadata adapter、local JSON migration command、optional `backend[postgres]` dependency 與 backend repository tests；不 bump version。
- [x] `tasks/phase-31-enterprise-roadmap/31-05-phase-31-release-sync.md`: 完成 `v0.31.0` release sync，更新 backend / frontend / Docker Compose / health test / `.env.example` 版本與 README / README_DEV / backend README / frontend README / TODO / ROADMAP；不新增 Phase 32、worker 或 production deployment。

Phase 32 `v0.32.0` - Formal Auth / RBAC / tenant boundary：
- [x] `tasks/phase-32-auth-rbac-tenant-boundary/32-01-auth-rbac-contract.md`: 完成 Markdown-only formal Auth / RBAC / tenant boundary contract，定義 User / Organization / Project / Role / Membership / project access、Viewer / Analyst / Admin 權限矩陣與 API guard policy；不 bump version。
- [x] `tasks/phase-32-auth-rbac-tenant-boundary/32-02-users-orgs-project-membership-schema.md`: 完成正式 Auth / RBAC PostgreSQL schema foundation、non-destructive migration command、demo seed users / disabled user password hash persistence 與 backend tests；不 bump version。
- [x] `tasks/phase-32-auth-rbac-tenant-boundary/32-03-backend-permission-guards.md`: 完成 formal signed bearer token guard、project access filter、Analyst / Admin write guard、Viewer forbidden 與 formal / demo backend tests；不 bump version。
- [x] `tasks/phase-32-auth-rbac-tenant-boundary/32-04-frontend-role-surface-and-release-sync.md`: 完成 frontend role surface、Viewer UI / API write guard validation、`v0.32.0` backend / frontend / Docker Compose / health test 版本同步與 README / README_DEV / backend README / frontend README / TODO / ROADMAP release sync。

Phase 33 `v0.33.0` - Redis + NATS worker pipeline：
- [x] `tasks/phase-33-redis-nats-worker-pipeline/33-01-redis-nats-worker-contract.md`: 完成 Markdown-only Redis / NATS worker pipeline contract，定義 Redis responsibilities / boundaries、NATS / JetStream topics、event payload、task status lifecycle、retry / failure policy 與 idempotency key；不 bump version。
- [x] `tasks/phase-33-redis-nats-worker-pipeline/33-02-redis-cache-rate-limit-session-slice.md`: 完成 opt-in Redis backend slice，支援 session cache、RAG query cache、rate limit、health fallback 與 Docker Compose redis profile；不 bump version。
- [x] `tasks/phase-33-redis-nats-worker-pipeline/33-03-nats-worker-skeleton-and-task-status.md`: 完成 optional NATS publish / subscribe helper、worker skeleton placeholder handlers、local JSON task status store、`/tasks` API 與 smoke script；不 bump version。
- [x] `tasks/phase-33-redis-nats-worker-pipeline/33-04-worker-demo-smoke-and-release-sync.md`: 完成 worker demo smoke 與 `v0.33.0` release sync。

Phase 34 `v0.34.0` - Production OCR / scanned PDF pipeline：
- [x] `tasks/phase-34-production-ocr-scanned-pdf/34-01-scanned-pdf-ocr-contract.md`: 完成 scanned PDF OCR contract，定義 PDF source routing、page image、OCR block、page-level status、retry / failure reason 與 parser / indexing worker handoff；不 bump version。
- [x] `tasks/phase-34-production-ocr-scanned-pdf/34-02-pdf-rendering-page-image-pipeline.md`: 完成 demo-safe PDF rendering page image pipeline，scanned / mixed PDF 可產生 bounded PNG page images 與 metadata；逐頁 OCR 執行當時留到 `34-03`，不 bump version。
- [x] `tasks/phase-34-production-ocr-scanned-pdf/34-03-multipage-ocr-status-and-retry.md`: 完成 scanned / mixed PDF page image provider-selected OCR、page-level status / retry / failure reason、`pdf_page_ocr` chunks 與 scanned PDF OCR smoke；不 bump version。
- [x] `tasks/phase-34-production-ocr-scanned-pdf/34-04-scanned-pdf-demo-release-sync.md`: 完成 `v0.34.0` release sync，補上 scanned PDF demo smoke、版本同步、文件同步與 Browser surface validation。

Phase 35 `v0.35.0` - RAG indexing quality hardening：
- [x] `tasks/phase-35-rag-indexing-quality/35-01-indexing-quality-contract.md`: 完成 Phase 35 indexing quality contract，定義 chunking strategies、Qdrant payload / filter、reindex 與 stale vector cleanup；不 bump version。
- [x] `tasks/phase-35-rag-indexing-quality/35-02-chunking-strategy-runtime.md`: 完成 vector indexing `fixed_size` / `semantic` chunking strategy runtime、request body 與 metadata；不 bump version。
- [x] `tasks/phase-35-rag-indexing-quality/35-03-qdrant-payload-index-and-reindexing.md`: 完成 Qdrant payload index / filter runtime、document stale cleanup 與 project reindex API；不 bump version。
- [x] `tasks/phase-35-rag-indexing-quality/35-04-indexing-quality-demo-release-sync.md`: 完成 `v0.35.0` release sync，補上 indexing quality smoke、版本同步與文件同步。

Phase 36 `v0.36.0` - Eval dashboard / rerank analysis：
- [x] `tasks/phase-36-eval-dashboard-rerank-analysis/36-01-eval-dashboard-contract.md`: 完成 eval dashboard / rerank analysis contract；不 bump version。
- [x] `tasks/phase-36-eval-dashboard-rerank-analysis/36-02-eval-dataset-management.md`: 完成 eval dataset / eval item CRUD API、repository persistence、frontend management surface 與 permission boundary；不 bump version。
- [x] `tasks/phase-36-eval-dashboard-rerank-analysis/36-03-strategy-comparison-and-rerank-analysis.md`: 完成 strategy comparison eval run API、result persistence、frontend comparison panel 與 rerank analysis visibility；不 bump version。
- [x] `tasks/phase-36-eval-dashboard-rerank-analysis/36-04-eval-dashboard-release-sync.md`: 完成 `v0.36.0` release sync，補上 eval dashboard smoke、版本同步與文件同步。

36-01 Eval Dashboard Contract：
- 已完成。`docs/api.md` 已定義 future eval dataset、eval item、eval run、strategy comparison、failure / fallback cases 與 rerank analysis API / UI contract。
- `docs/architecture.md` 已固定 Phase 36 dashboard data flow：eval dataset -> eval run -> strategy comparison summary -> case detail -> rerank analysis。
- Metrics contract 包含 Hit Rate@K、MRR@K、Recall@K、Precision@K、average latency、failure count 與 fallback count；rerank analysis contract 包含 pre / post rerank rank、score、final score source、rerank status 與 trace metadata coverage。
- Validation 通過：ticket `rg` 與 `git diff --check`。
- Release Impact：Version bump required: no。這是 Markdown-only contract ticket，不新增 dashboard runtime、frontend UI、eval dataset persistence、LLM-as-judge、answer faithfulness、citation quality scoring、OCR eval、ranking algorithm 或 rerank provider。

36-02 Eval Dataset Management：
- 已完成。Backend 新增 `/eval/datasets` 與 `/eval/datasets/{dataset_id}/items` 管理 API，支援 dataset create / list / detail / update / delete，以及 item create / list / detail / update / delete。
- Local JSON 與 PostgreSQL metadata repository path 已保存 eval datasets / eval items；dataset delete 會同步移除其 items。
- Frontend 後台新增 Eval Dataset surface，可建立/更新/刪除 dataset，並管理 query、expected terms、document IDs、chunk IDs、tags 與 notes。
- Permission boundary：Admin / Analyst 可管理 eval datasets / items；Viewer 在 demo / formal auth write path 會收到 `403 forbidden`。
- Validation 通過：focused backend tests `15 passed`；backend full test `245 passed`；frontend build；Admin API CRUD；Viewer blocked API；Edge headless desktop / mobile DOM surface check；ticket `rg` 與 `git diff --check`。in-app Browser 控制工具因 Node REPL sandbox `spawn setup refresh` 錯誤不可用，改用 Edge headless DOM 檢查。
- Release Impact：Version bump required: no。版本同步留到 `36-04`；本 ticket 不新增 strategy comparison dashboard、LLM-as-judge、answer faithfulness、OCR eval、citation quality scoring 或 retrieval / rerank runtime behavior。

36-03 Strategy Comparison and Rerank Analysis：
- 已完成。Backend 新增 `/eval/runs`、`/eval/runs/{run_id}` 與 `/eval/runs/{run_id}/items`，可對 eval dataset 執行 keyword、vector、hybrid、vector_rerank、hybrid_rerank strategy comparison，並保存 eval run summary、case result、failure / fallback cases 與 rerank analysis payload。
- Eval run 會保存 strategy config、Hit Rate@K、MRR@K、Recall@K、average latency、failure count、fallback count、trace metadata coverage 與 fallback reasons；vector-backed runtime unavailable 時會保留 fallback cases，不把 fallback 偽裝成完整成功。
- Frontend 後台新增 Strategy comparison panel，顯示 metrics table、Top K、strategy set、failure / fallback cases、trace metadata count、fallback reasons，以及 rerank before / after rank、score、final score source 與 rerank status。
- Validation 通過：targeted backend tests `8 passed, 26 deselected`；eval dashboard smoke `7 passed, 27 deselected`；backend full test `246 passed`；frontend build；Edge headless desktop / mobile screenshot check；ticket `rg`；`git diff --check`。pytest cache warning 與 Edge registry usage stats warning 為本機工具環境提示。
- Release Impact：Version bump required: no。版本同步留到 `36-04`；本 ticket 不新增 LLM-as-judge、answer faithfulness、citation quality scoring、production monitoring trend，也不更換 default retrieval provider 或 rerank model。

36-04 Eval Dashboard Phase 36 Release Sync：
- 已完成。backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 ticket 已同步到 `0.36.0`。
- `scripts/eval-dashboard-smoke.ps1` 覆蓋 eval dataset、strategy comparison、failure / fallback cases 與 rerank analysis path。
- Validation 已通過：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`246 passed`，1 pytest cache warning）、`npm.cmd run build`、`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\eval-dashboard-smoke.ps1`（`7 passed, 27 deselected`，1 pytest cache warning）、Chrome GUI DevTools desktop / mobile screenshot check、ticket `rg` 與 `git diff --check`。
- Release Impact：Version bump required: yes。Phase 36 已完成 `v0.36.0` eval dashboard / rerank analysis release；仍不包含 LLM-as-judge、answer faithfulness、citation quality scoring 或 production monitoring trend。

Phase 37 `v0.37.0` - Inference Ops / vLLM serving：
- [x] `tasks/phase-37-inference-ops-vllm/37-01-inference-provider-ops-contract.md`: 完成 inference provider ops contract；不 bump version、不新增 runtime。
- [x] `tasks/phase-37-inference-ops-vllm/37-02-openai-compatible-client-boundary.md`: 新增 OpenAI-compatible LLM client adapter，可透過 env 明確啟用；保留 Ollama default / fallback，不 bump version。
- [x] `tasks/phase-37-inference-ops-vllm/37-03-vllm-local-serving-and-benchmark-docs.md`: 新增 vLLM local / Docker serving guide 與 inference benchmark smoke，記錄 latency、tokens、throughput、KV cache / GPU memory estimate；vLLM unavailable 時寫入 skipped report 與 Ollama / deterministic fallback，不 bump version。
- [x] `tasks/phase-37-inference-ops-vllm/37-04-inference-ops-release-sync.md`: 完成 `v0.37.0` inference ops / vLLM serving release sync，更新 backend / frontend / Docker Compose / health test version 與 README / README_DEV / backend README / frontend README / TODO / ROADMAP；保留 vLLM 為 serving path / benchmark，不宣稱 production inference serving。

37-01 Inference Provider Ops Contract：
- 已完成。`docs/architecture.md` 已定義 Phase 37 inference provider router、Ollama / OpenAI-compatible / vLLM provider boundary、metrics boundary 與 fallback boundary。
- `docs/api.md` 已補上 provider trace metadata、prompt / completion tokens、latency、throughput、GPU memory estimate、KV cache estimate、timeout、malformed response 與 unavailable handling contract。
- 本 ticket 是 Markdown-only contract，不新增 OpenAI-compatible client runtime、vLLM server、dependency、Docker runtime、multi-GPU serving、autoscaling、K8s deployment、production inference gateway、RAG prompt 變更、Agent planner 變更或 VLM parser 行為變更。
- Validation 已通過：`rg -n "inference|vLLM|OpenAI-compatible|Ollama|KV cache|GPU memory|Phase 37" docs README_DEV.md TODO.md tasks/phase-37-inference-ops-vllm` 與 `git diff --check`。
- Release Impact：Version bump required: no。這是 Phase 37 contract ticket，版本同步留到 `37-04`。

37-02 OpenAI Compatible Client Boundary：
- 已完成。`DOCURAG_LLM_PROVIDER=openai_compatible` 可啟用 OpenAI-compatible LLM adapter，使用 `DOCURAG_LLM_BASE_URL`、`DOCURAG_LLM_MODEL`、`DOCURAG_LLM_TIMEOUT_SECONDS` 與可選 `DOCURAG_LLM_API_KEY` 呼叫 `{base_url}/chat/completions`。
- Provider success path 會回填 prompt tokens、completion tokens、total tokens、finish reason、provider request id、provider latency 與 tokens per second；timeout、malformed response 或 unavailable endpoint 會保留既有 RAG retrieved-chunks fallback，並在 trace metadata 標示 `llm_fallback_reason=provider_error`。
- Ollama default / fallback 未移除；本 ticket 不新增 OpenAI SDK dependency、vLLM server、VLM parser runtime、Agent planner 變更、RAG prompt 變更、production API key vault 或 production inference gateway。
- Validation 已通過：focused backend tests `39 passed`、backend full test `251 passed`（1 pytest cache warning）、ticket `rg` 與 `git diff --check`。
- Release Impact：Version bump required: no。這是 Phase 37 runtime slice，版本同步留到 `37-04`。

37-03 vLLM Local Serving and Benchmark Docs：

- 已完成。`docs/LOCAL_DEV_SETUP.md` 補上 vLLM Docker / OpenAI-compatible `/v1` local serving guide，並說明 hardware constraints、Ollama fallback 與 deterministic baseline。
- `scripts/inference-benchmark-smoke.ps1` 會呼叫 OpenAI-compatible `/chat/completions`，成功時記錄 latency、prompt tokens、completion tokens、total tokens、throughput、KV cache estimate 與 GPU memory estimate；endpoint unavailable 時寫入 `status=skipped` report。
- `.env.example` 與 `infra/docker-compose.yml` 補上 local OpenAI-compatible / vLLM env pass-through，但不新增 vLLM service，不把 vLLM 設成唯一 runtime。
- Validation 已通過：inference benchmark smoke、ticket `rg` 與 `git diff --check`。
- Release Impact：Version bump required: no。這是 Phase 37 ops / docs / smoke ticket，版本同步留到 `37-04`。

37-04 Inference Ops Phase 37 Release Sync：

- 已完成。backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 ticket 已同步到 `0.37.0` / `v0.37.0`。
- OpenAI-compatible provider boundary、vLLM local / Docker guide、inference benchmark smoke、latency / token / throughput / KV cache / GPU memory estimate 與 provider unavailable skip reason 已形成可展示 release。
- Release boundary 保持明確：vLLM 是 local serving path / benchmark，不是唯一 runtime、production inference gateway、multi-GPU serving、K8s autoscaling、model registry、OpenAI billing / secret vault、RAG ranking 變更、VLM parser schema 變更或 Agent planner。
- Validation 已通過：backend full test `251 passed`（1 pytest cache warning）、frontend build、baseline demo smoke、inference benchmark smoke（本機 vLLM endpoint unavailable 時產出 `status=skipped` report）、ticket `rg` 與 `git diff --check`。
- Release Impact：Version bump required: yes。Phase 37 已完成 `v0.37.0` inference ops / vLLM serving demonstration release。

Phase 38 `v0.38.0` - Agent runtime hardening：
- [x] `tasks/phase-38-agent-runtime-hardening/38-01-agent-runtime-permission-contract.md`: 定義 Agent planner provider boundary、deterministic fallback、tool permission tiers、project access guard、human confirmation requirement、trace fields 與 forbidden tool boundary；文件 ticket，不 bump version、不新增 runtime。
- [x] `tasks/phase-38-agent-runtime-hardening/38-02-llm-planner-provider-boundary.md`: 新增 `DOCURAG_AGENT_PLANNER_PROVIDER=llm_planner` runtime boundary、LLM plan JSON validation、timeout / invalid plan deterministic fallback 與 planner audit trace；不 bump version、不新增任意工具執行。
- [x] `tasks/phase-38-agent-runtime-hardening/38-03-tool-permission-guards-and-trace.md`: 為既有 Agent tools 補上 `read-only` tier / permission requirement、執行前 role / project / side-effect guard、permission trace metadata 與 frontend trace 顯示；不 bump version、不新增 destructive tool。
- [x] `tasks/phase-38-agent-runtime-hardening/38-04-agent-runtime-release-sync.md`: 完成 `v0.38.0` Agent runtime hardening release sync，更新 backend / frontend / Docker Compose / health test version 與 README / README_DEV / backend README / frontend README / TODO / ROADMAP；保留 Agent 只執行受控 read-only allowlisted tools，不允許 arbitrary SQL、shell、filesystem 或 destructive tools。

38-01 Agent Runtime Permission Contract Status：

- 已完成。`docs/architecture.md` 與 `docs/api.md` 已固定 Phase 38 planner boundary：`deterministic` 是 always-available fallback，future `llm_planner` 只能輸出 validated structured plan；timeout、invalid plan、unsafe tool selection、missing evidence 或 schema validation failure 都不得執行 unsafe tool。
- Tool tiers 已定義為 `read-only`、`write`、`admin`、`destructive`；permission guard 必須檢查 role、project access、tool allowlist、tool tier、input schema、target resource project 與 human confirmation state。
- Trace contract 已包含 plan、tool selection、permission decision、observation、reflection / fallback 與 final answer；文件也明確禁止任意 SQL、shell、filesystem command、arbitrary network tool、delete、drop table、destructive reindex、credential mutation 或 production database mutation。
- Release Impact：Version bump required: no。此 ticket 是 Phase 38 contract 文件，不改 backend / frontend runtime。

38-02 LLM Planner Provider Boundary Status：

- 已完成。`backend/app/services/agent_planner.py` 新增 deterministic planner 與 LLM planner provider boundary；`DOCURAG_AGENT_PLANNER_PROVIDER=deterministic` 保持預設安全路徑，`llm_planner` 才會透過既有 LLM provider 嘗試產生 JSON plan。
- LLM plan validation 只接受 `invoice_summary`、`document_question`、`unsupported_task` 與既有 allowlisted tools；unknown tool、unsafe route、missing `document_id` / query、invalid JSON / schema 都會在 tool execution 前 fallback。
- Agent trace 已記錄 `planner_provider`、`planner_attempted_provider`、`planner_status`、`plan_validation_status`、`planned_tools`、`planner_fallback_reason`、latency、model / token metadata 與 role / project metadata。
- Validation 已通過：focused Agent tests `9 passed`；backend full test `254 passed`（1 pytest cache warning）；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- Release Impact：Version bump required: no。此 ticket 是 Phase 38 runtime slice，版本同步留到 `38-04`。

38-03 Tool Permission Guards and Trace Status：

- 已完成。既有 Agent tools 已標記 `read-only` tool tier、`agent_run_tool_execution` permission requirement、`admin,analyst` required roles、`no_side_effects` side-effect policy 與 human confirmation `not_required` trace metadata。
- Agent run 在 tool execution 前會檢查 role、project context、tool tier 與 side-effect policy；Viewer role 會在 backend guard 被擋下，Analyst / Admin 或本地 disabled auth path 只會執行既有 allowlisted read-only tools。
- Agent trace 與 tool call trace metadata 已包含 `permission_decision`、`permission_reason`、`tool_tier`、`required_roles`、`project_access`、`side_effect_policy`、`human_confirmation_required` 與 `human_confirmation_status`；frontend Agent trace 會顯示 permission decision、阻擋工具、tool tier 與 side-effect policy。
- Validation 已通過：focused Agent tests `17 passed`（1 pytest cache warning）；backend full test `255 passed`（1 pytest cache warning）；frontend build；Chrome GUI Browser check desktop / mobile（Agent trace permission fields rendered，無 horizontal overflow）；ticket `rg`；`git diff --check`（僅 Windows LF/CRLF 提示）。
- Release Impact：Version bump required: no。此 ticket 是 Phase 38 runtime slice，版本同步留到 `38-04`。

38-04 Agent Runtime Phase 38 Release Sync：

- 已完成。backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 ticket 已同步到 `0.38.0` / `v0.38.0`。
- Phase 38 已形成可展示 release：受控 `llm_planner` provider boundary、deterministic fallback、read-only tool permission guard、Viewer forbidden path 與 Agent trace permission fields 均已納入驗證。
- Release boundary 保持明確：Agent 仍不允許 arbitrary autonomous execution、任意 SQL、shell、filesystem command、destructive tools、external browser control、production approval workflow 或 production audit dashboard。
- Validation 已通過：backend full test `255 passed, 1 warning`（pytest cache warning）、frontend build、Agent runtime smoke（health `0.38.0`、planner fallback `llm_planner_timeout`、Viewer 403、permission trace OK）、Browser Agent trace desktop / mobile（permission fields rendered，無 horizontal overflow）、ticket `rg` 與 `git diff --check`（僅 Windows LF/CRLF 提示）。
- Release Impact：Version bump required: yes。Phase 38 已完成 `v0.38.0` Agent runtime hardening release。

Phase 39 `v0.39.0` - Deployment / observability / fine-tuning track：
- [x] `tasks/phase-39-deployment-observability-finetuning/39-01-deployment-observability-research-contract.md`: 定義 Phase 39 K8s baseline、Loki + Grafana observability path、API / worker / RAG / eval trace logging boundary，以及 fine-tuning / synthetic data / embedding tuning research-only scope；文件 ticket，不 bump version、不新增 runtime。
- [x] `tasks/phase-39-deployment-observability-finetuning/39-02-k8s-manifest-baseline.md`: 新增 `infra/k8s/` baseline manifests，包含 API、frontend、worker placeholder、Qdrant、Redis、NATS、ConfigMap、Secret template、probes、resources、rollout / rollback docs 與 optional HPA template；不 bump version。
- [x] `tasks/phase-39-deployment-observability-finetuning/39-03-observability-stack-and-rag-trace-logs.md`: 新增 opt-in JSONL observability exporter、API / RAG / eval / worker events、Loki + Grafana local profile、Promtail config、LogQL query docs 與 observability smoke；不 bump version。
- [x] `tasks/phase-39-deployment-observability-finetuning/39-04-finetuning-synthetic-data-research-track.md`: 新增 research-only fine-tuning / synthetic data artifact pack，包含 dataset card、notebook skeleton、SFT JSONL、embedding positive / negative pairs、reranker pairwise samples 與 evaluation template；不 bump version。
- [x] `tasks/phase-39-deployment-observability-finetuning/39-05-phase-39-release-sync.md`: 完成 `v0.39.0` Phase 39 release sync，更新 backend / frontend / Docker Compose / `.env.example` / health test / K8s sample image tag 版本與 README / README_DEV / backend README / frontend README / TODO / ROADMAP；保留 production autoscaling、multi-cluster deployment、managed secret integration 與 production training pipeline 為未完成邊界。

39-01 Deployment Observability Research Contract Status：

- 已完成。`docs/architecture.md` 已定義 Phase 39 deployment / observability / fine-tuning research contract，將 K8s baseline 限定為 Deployment、Service、ConfigMap / Secret template、health probes 與 resource request examples。
- Observability path 已選定 Loki + Grafana；OpenSearch 保留為替代路線。Log / trace scope 包含 API log、worker log、RAG trace 與 eval metrics，並明確避免預設記錄 raw document text、prompt body、bearer token 或 secret。
- Fine-tuning / synthetic data / embedding tuning 僅作 research track，可產生 dataset card、experiment report 或 notebook skeleton；不執行長時間 training、不下載大型模型、不改 main runtime default。
- Release Impact：Version bump required: no。此 ticket 是 Phase 39 contract 文件，不新增 K8s manifest、observability runtime、notebook、dependency、backend / frontend runtime 或版本更新。

39-02 K8s Manifest Baseline Status：

- 已完成。`infra/k8s/docurag-baseline.yaml` 已新增 `docurag` namespace、ConfigMap、Secret template、backend API、frontend、worker placeholder、Qdrant、Redis 與 NATS baseline manifests。
- Backend / frontend / worker manifests 均包含 image tag、env config、readinessProbe、livenessProbe、resource requests / limits；worker 因目前 skeleton 無 inbound traffic，文件明確註記無 Service 與 deferred reason。
- `infra/k8s/hpa-optional.yaml` 僅作 optional API HPA shape，不宣稱 production autoscaling 或大規模壓測完成。
- 文件已補充 local YAML lint、cluster dry-run、rollout / rollback、config checksum、readiness gate、failed rollout triage 與 boundary。
- Validation 已通過：offline YAML lint（15 個 K8s YAML documents，均有 `apiVersion` / `kind` / `metadata.name`）、ticket `rg` 與 `git diff --check` / `git diff --cached --check`。`kubectl apply --dry-run=client --validate=false -f .\infra\k8s` 已嘗試，但本機無 Kubernetes API context，kubectl v1.34.1 在 API discovery 階段連 `localhost:8080` 失敗。
- Release Impact：Version bump required: no。此 ticket 是 deployment artifact baseline；sample image tag 已由 `39-05` release sync 更新到 `0.39.0`。

39-03 Observability Stack and RAG Trace Logs Status：

- 已完成。新增 `DOCURAG_OBSERVABILITY_LOG_PATH` opt-in JSONL exporter；未設定或寫入失敗時 app 不 hard fail。
- API request middleware 會匯出 route、method、status code、request_id、trace_id 與 latency；`/rag/query` 匯出 RAG trace 摘要，不記 raw query、document text、prompt body、token 或 secret。
- Eval endpoints 匯出 Hit Rate@K、MRR@K、average latency、failure count、fallback count 與 trace metadata count；worker task store 匯出 queued / running / succeeded / failed lifecycle。
- `infra/observability/` 已新增 Loki / Promtail / Grafana opt-in path、JSON label config 與 LogQL query examples，覆蓋 API p95 latency、error rate、worker failures、retrieval / rerank / generation latency、fallback count、Hit Rate 與 MRR。
- Validation 已通過：backend full test `260 passed, 1 warning`（pytest cache permission warning）、observability smoke `5 passed, 1 warning`、`docker-compose -f .\infra\docker-compose.yml --profile observability config`（通過但本機 Docker config 權限 warning）、ticket `rg` 與 `git diff --check`。
- Release Impact：Version bump required: no。此 ticket 是 Phase 39 observability runtime / docs slice；版本已由 `39-05` release sync 統一更新到 `v0.39.0`。

39-04 Fine Tuning Synthetic Data Research Track Status：

- 已完成。`fine-tuning/` 已新增 research-only artifact pack，包含 synthetic data plan、dataset card、notebook skeleton、evaluation template、privacy / leakage / overfit 風險與 mitigation。
- `sample-data/fine-tuning/` 已新增 SFT schema extraction JSONL、embedding positive / negative pairs、reranker pairwise samples 與 evaluation CSV，覆蓋 invoice、contract、report examples。
- Evaluation template 明確保留 Hit Rate@K、MRR@K、Recall@K、parser field accuracy、sample count、data source 與 skip reason。
- Validation 已通過：ticket `rg`、JSONL parse sanity check 與 `git diff --check`。
- Release Impact：Version bump required: no。此 ticket 是 Phase 39 research artifact slice，不執行 training、不下載大型模型、不新增 dependency、不接 production runtime；版本已由 `39-05` release sync 統一更新到 `v0.39.0`。

39-05 Phase 39 Release Sync Status：

- 已完成。backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、K8s sample image tag、README、README_DEV、backend README、frontend README、TODO、ROADMAP、demo smoke expected version 與 ticket 已同步到 `0.39.0` / `v0.39.0`。
- Validation 已通過：backend full test `260 passed, 1 warning`（pytest cache permission warning）、frontend build、baseline demo smoke（health `0.39.0`，本機 Qdrant unavailable 時 keyword fallback 符合預期）、K8s offline YAML lint `15 documents`、observability smoke `5 passed, 1 warning`、Docker Compose observability profile config（Docker config permission warning，但 config 解析成功）、research artifact `rg`、JSONL parse sanity check、release `rg` 與 `git diff --check`。
- `kubectl apply --dry-run=client --validate=false -f .\infra\k8s` 已嘗試；本機無 Kubernetes API context，kubectl 在 API discovery 階段連 `localhost:8080` 失敗。此環境限制已記錄，offline YAML lint 通過。
- Release Impact：Version bump required: yes。Phase 39 已完成 `v0.39.0` deployment / observability / fine-tuning track release；不新增 production autoscaling、multi-cluster deployment、managed secret integration、production alerting / incident workflow 或 production training pipeline。

Phase 31-39 guardrails：

- Phase 31 已完成 `v0.31.0` release sync，Phase 32 已完成 `v0.32.0` release sync，Phase 33 已完成 `v0.33.0` Redis + NATS worker demo milestone release sync，Phase 34 已完成 `v0.34.0` scanned PDF OCR baseline release sync，Phase 35 已完成 `v0.35.0` RAG indexing quality release sync，Phase 36 已完成 `v0.36.0` eval dashboard / rerank analysis release sync，Phase 37 已完成 `v0.37.0` inference ops / vLLM serving release sync，Phase 38 已完成 `v0.38.0` Agent runtime hardening release sync，Phase 39 已完成 `v0.39.0` deployment / observability / fine-tuning track release sync，Phase 40 已完成 `v0.40.0` JD evidence hardening release sync，Phase 41 已完成 `v0.41.0` RAG quality regression / DatasetOps release sync，Phase 42 已完成 `v0.42.0` inference gateway / capacity planning release sync。
- 每個 Phase 仍必須依序先做 contract / migration / validation，再做 runtime 與 release sync。
- 不得在 Phase 31 提前實作 Redis、NATS、vLLM、K8s 或 fine-tuning；也不得在規劃 ticket 中新增外部依賴或 schema。
- Phase 完成且形成 release 時，才可同步 bump backend / frontend / health / Docker Compose version。

31-02 PostgreSQL Boundary and Migration Policy Status：

- 已完成。`docs/db-schema.md` 與 `docs/architecture.md` 已列出目前 local JSON store 的 document metadata、OCR results、chunks、parser fields、processing jobs、eval datasets / eval runs 與 Agent runs 對應的 future DB domain。
- Migration policy 已記錄 Alembic 工具方向、readable slug 命名、explicit execution、rollback / downgrade、validation 與 release sync 原則。
- Local JSON fallback / migration path 已明確保留；DB-backed mode 後續應先 opt-in 並用 idempotent import 遷移，不在本 ticket 切斷既有 demo。
- Validation 已通過：`rg -n "PostgreSQL|migration|local JSON|fallback|Phase 31" docs README_DEV.md TODO.md tasks/phase-31-enterprise-roadmap` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- Release Impact：Version bump required: no。本 ticket 不新增 PostgreSQL schema、migration 檔、repository runtime、正式 RBAC、Redis、NATS、worker、K8s 或 deployment 設定。

31-03 DB Schema Contract Status：

- 已完成。`docs/db-schema.md` 已定義 Phase 31 core tables 的欄位、required / nullable、index / key、FK direction 與 local JSON mapping。
- Contract 包含 `documents`、`document_pages`、`document_chunks`、`extracted_fields`、`processing_jobs`、`eval_datasets`、`eval_items`、`eval_runs`、`eval_run_items`、`agent_runs`、`agent_steps` 與 `agent_tool_calls`。
- Nullable `project_id` 已保留為 future project / tenant metadata；正式 users / organizations / roles / memberships schema 明確留到 Phase 32。
- Validation 已通過：`rg -n "document_pages|document_chunks|extracted_fields|eval_runs|agent_runs|project_id|Phase 31" docs TODO.md tasks/phase-31-enterprise-roadmap` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- Release Impact：Version bump required: no。本 ticket 不新增 migration 檔、database schema runtime、repository code、dependency、正式 RBAC、Redis、NATS、worker、K8s 或 deployment 設定。

31-04 Repository Adapter and Migration Path Status:
- 已完成 runtime repository selection：`DOCURAG_REPOSITORY_PROVIDER=local_json|postgresql`，預設仍是 local JSON，只有 PostgreSQL-backed mode 需要 `DOCURAG_DATABASE_URL`。
- 已新增 `PostgresDocumentRepository`，只做非破壞性 schema bootstrap 與 documents、chunks、parser fields、eval runs、Agent runs 的 upsert metadata writes；`LocalJsonDocumentRepository` 保留既有 local JSON fallback。
- 已新增 `scripts/migrate-local-json-to-postgresql.py` 作為明確 local JSON import command，並新增 `backend[postgres]` optional dependency 供 `psycopg[binary]` 使用。
- Validation passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` (`205 passed`, 1 pytest cache warning). Release Impact: Version bump required: no; `31-05` remains release sync.

31-05 Phase 31 Release Sync Status：
- 已完成 `v0.31.0` release sync：backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION` 與 `.env.example` 已同步到 `0.31.0`。
- README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 ticket 已同步 Phase 31 release 狀態；文件明確保留正式 RBAC、worker pipeline 與 production deployment 尚未完成的邊界。
- Validation 已通過：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`205 passed`，1 pytest cache warning）；`npm.cmd run build`；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`（health version `0.31.0`，local JSON fallback demo flow 通過，Qdrant unavailable vector indexing fallback 符合 local baseline）；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

32-01 Auth RBAC Contract Status：
- 已完成。`docs/api.md` 與 `docs/architecture.md` 已定義正式 Auth / RBAC / tenant boundary 的 User、Organization、Project、Role、Membership 與 project access domain contract。
- Viewer / Analyst / Admin 權限矩陣已固定：Viewer 只能讀取 / query / download 可存取 project；Analyst 可執行 ingestion、OCR、parser、indexing、built-in eval 與 deterministic Agent；Admin 另可管理 project metadata / memberships。
- API guard policy 已固定 authenticated read、ingestion write、admin / membership endpoint 與 cross-project denied behavior；demo auth 只保留為 local validation fallback，不宣稱 production RBAC。
- Release Impact：Version bump required: no。本 ticket 不新增 users / organizations schema、migration 檔、production login runtime、Redis session、SSO、OAuth、MFA、frontend role surface 或 backend runtime guard。
- Validation 已通過：`rg -n "Auth|RBAC|Viewer|Analyst|Admin|organization|project access|Phase 32" docs README_DEV.md TODO.md tasks/phase-32-auth-rbac-tenant-boundary`；`git diff --check`（僅 Windows LF/CRLF 提示）。

32-02 Users Orgs Project Membership Schema Status：
- 已完成。新增 `backend/app/repositories/auth_rbac.py`，以 PostgreSQL schema statements 建立 `users`、`organizations`、`projects`、`roles`、`memberships` 與 `project_memberships`。
- 新增 `scripts/migrate-auth-rbac-schema.py`，支援 `--dry-run` 與 `--seed-demo-users`；migration 使用 non-destructive `CREATE TABLE IF NOT EXISTS` / `CREATE INDEX IF NOT EXISTS` 與 seed upsert。
- Demo seed users 已包含 Admin / Analyst / Viewer / disabled Viewer，password 以 deterministic PBKDF2 hash 保存；Phase 28 `DOCURAG_AUTH_MODE=demo` 仍為 explicit local fallback，不被本 schema ticket 靜默替換。
- Release Impact：Version bump required: no。Endpoint permission guards、frontend role surface、Redis session、SSO、OAuth、MFA 與 production login runtime 仍留到後續 Phase 32 tickets。
- Validation 已通過：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`210 passed`，1 pytest cache warning）；`rg -n "users|organizations|memberships|roles|project access|DOCURAG_AUTH_MODE" backend docs TODO.md tasks/phase-32-auth-rbac-tenant-boundary`；`git diff --check`（僅 Windows LF/CRLF 提示）。

32-03 Backend Permission Guards Status：
- 已完成。新增 `DOCURAG_AUTH_MODE=formal` signed bearer token parsing，解析 current user、organization、active project 與 accessible project ids。
- Document upload、OCR、parse、vector index、built-in eval 與 Agent run 已接 Analyst / Admin write guard；Viewer 會收到 generic `403 forbidden`。
- Document list / detail / OCR result / fields / download、RAG query corpus、Agent search corpus 與 Agent run lookup 已依 project access filter / deny；cross-project denied response 不包含 target document id 或 project id。
- Release Impact：Version bump required: no。Frontend role surface 與 Phase 32 release sync 已由 `32-04` 完成；Redis session、SSO、OAuth、MFA 與 production login runtime 仍不在 Phase 32 範圍。
- Validation 已通過：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`216 passed`，1 pytest cache warning）；`rg -n "forbidden|permission|project access|Viewer|Analyst|Admin|tenant" backend docs TODO.md tasks/phase-32-auth-rbac-tenant-boundary`；`git diff --check`（僅 Windows LF/CRLF 提示）。

32-04 Frontend Role Surface and Release Sync Status：
- 已完成 `v0.32.0` release sync：backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION` 與 `.env.example` 已同步到 `0.32.0`。
- Frontend role surface 已對齊 backend guard：Admin / Analyst 可使用 ingestion、built-in eval 與 Agent write surface；Viewer 只能查詢，且 UI 與 API 都不能執行 ingestion / eval / Agent write。
- README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 ticket 已同步 Phase 32 release 狀態；文件明確保留 SSO、OAuth、MFA、Redis session、worker、deployment hardening 與 production login runtime 尚未完成的邊界。
- Validation 已通過：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`216 passed`，1 pytest cache warning）；`npm.cmd run build`；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`（health version `0.32.0`）；Browser 檢查 Admin / Analyst / Viewer desktop / mobile role surface 與 horizontal overflow 通過；Viewer API 403 檢查通過；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

33-01 Redis NATS Worker Contract Status：
- 已完成。`docs/architecture.md` 與 `docs/api.md` 已定義 Phase 33 Redis / NATS worker pipeline contract。
- Redis responsibilities 已限定為 session cache、query cache、rate limit、worker lock 與 short-term chat history；文件明確禁止把 Redis 當成 canonical store、permission source of truth 或跨 tenant cache。
- NATS / JetStream topics 已固定為 `document.uploaded`、`document.ocr.requested`、`document.parse.requested`、`document.index.requested` 與 `rag.eval.requested`，並定義 payload 不包含 file bytes、secret 或跨 project data。
- Task status lifecycle、retry / failure policy 與 deterministic idempotency key 已固定；本 ticket 不新增 runtime service、worker code、dependency、migration、deployment config、autoscaling 或 model behavior changes。
- Release Impact：Version bump required: no。

33-02 Redis Cache Rate Limit Session Slice Status：
- 已完成。新增 opt-in Redis runtime helper：`DOCURAG_REDIS_URL` 有設定且安裝 optional `backend[redis]` extra 時，backend 可 best-effort 使用 session cache、RAG query cache 與 rate limit。
- Redis 未設定、client 未安裝或連線不可用時，`/health` 會回報 `disabled` / `unavailable`，既有 demo API 不會 hard fail；rate limit fallback 會允許請求繼續。
- `/auth/login` 會 best-effort 以 token hash 寫入 session cache；`/rag/query` 會依 auth context、provider settings 與可見 document signature 建立 query cache key，並在 Redis 可用時套用 per-minute rate limit。
- Docker Compose 新增 optional `redis` profile，backend image 可用 `DOCURAG_INSTALL_REDIS=true` 安裝 Redis client；預設仍不啟動 Redis、不要求外部服務。
- 本 ticket 不新增 NATS、worker、async queue、distributed lock runtime、production session rotation、OAuth、MFA、enterprise auth，也不修改 OCR、parser、RAG ranking 或 Agent planner。
- Validation 已通過：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`221 passed`，1 pytest cache warning）；manual Redis health fallback check 通過（Redis client 未安裝時 `/health` 回 `redis: unavailable` 且 service `ok`）；ticket `rg` 與 `git diff --check` 通過。
- Release Impact：Version bump required: no；`v0.33.0` 版本同步留到 `33-04`。

33-03 NATS Worker Skeleton and Task Status：
- 已完成。新增 optional NATS runtime helper，`DOCURAG_NATS_URL=memory://` 可用於本機 smoke；真實 NATS client 收斂在 optional `backend[nats]` extra。
- 新增 `WorkerSkeleton` placeholder handlers，訂閱 `document.ocr.requested`、`document.parse.requested`、`document.index.requested` 與 `rag.eval.requested`，只回寫 task status，不執行 OCR / parser / indexing / eval 核心 model 行為。
- 新增 local JSON `worker_tasks.json` task status store 與 `GET /tasks` / `GET /tasks/{task_id}` API，狀態包含 `queued`、`running`、`succeeded`、`failed`、`retrying`、`cancelled`。
- Docker Compose 新增 optional `nats` profile，backend image 可用 `DOCURAG_INSTALL_NATS=true` 安裝 NATS client；預設仍不啟動 NATS、不要求外部服務。
- 本 ticket 不新增 production autoscaling、K8s、dead-letter dashboard、full observability stack、vLLM、OpenAI API、fine-tuning 或 Agent planner 變更。
- Validation 已通過：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`227 passed`，1 pytest cache warning）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\nats-worker-smoke.ps1`；ticket `rg` 與 `git diff --check` 通過。
- Release Impact：Version bump required: no；`v0.33.0` 版本同步留到 `33-04`。

33-04 Worker Demo Smoke and Phase 33 Release Sync：
- 已完成。新增 `scripts/worker-demo-smoke.ps1`，以 fake Redis client 驗證 session cache、query cache 與 rate limit path，並用 `DOCURAG_NATS_URL=memory://` 驗證 NATS worker skeleton publish / consume 與 `/tasks` task status API。
- backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 ticket 已同步到 `v0.33.0`。
- 這是 demo-safe async architecture milestone，不新增 production autoscaling、K8s、distributed tracing、full observability stack、vLLM、OpenAI API、fine-tuning pipeline，也不修改 OCR / parser / RAG / Agent model behavior。
- Validation 已通過：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`227 passed`，1 pytest cache warning）；`npm.cmd run build`；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\worker-demo-smoke.ps1`（health version `0.33.0`，Redis fake-client path `ok`，NATS memory worker 與 task status `succeeded`）；ticket `rg` 與 `git diff --check` 通過。

34-01 Scanned PDF OCR Contract：
- 已完成。`docs/architecture.md` 與 `docs/api.md` 已定義 Phase 34 PDF source routing：text-native PDF、scanned PDF、mixed PDF 與 invalid PDF。
- Page image、OCR block、page-level status、retry / failure reason 已固定；future runtime 應保留 page number、bbox、confidence、reading order、provider 與 failure metadata。
- OCR results 接 parser、chunks、vector indexing 與 Phase 33 worker task status 的 handoff 已定義，但本 ticket 不新增 PDF rendering runtime、OCR code、layout analysis、table reconstruction、human correction workflow 或 production accuracy tuning。
- Validation 已通過：`rg -n "scanned PDF|pdf_text|page image|OCR block|page-level|Phase 34" docs README_DEV.md TODO.md tasks/phase-34-production-ocr-scanned-pdf` 與 `git diff --check` 通過。
- Release Impact：Version bump required: no。`v0.34.0` 版本同步留到 `34-04`。

34-02 PDF Rendering Page Image Pipeline：
- 已完成。新增 `PyMuPDF` backend dependency 與 demo-safe PDF rendering service；scanned PDF 會 render 成 bounded PNG page images，metadata 保存 `path`、`width`、`height`、`dpi`、`checksum`、`page_number` 與 `source_type`。
- Text-native PDF 仍走既有 `pdf_text` chunks，不會產生 page images；mixed PDF 會保留 text pages 的 `pdf_text` chunks，並只為 scanned pages 建立 `pdf_mixed_pending_ocr` page images。
- Invalid / unsupported PDF 仍有明確 failure reason；PDF rendering dependency missing / render failed 會標示 `pdf_rendering` failed job。本 ticket 不執行 OCR、不新增 production storage、S3、K8s、autoscaling、layout analysis、table reconstruction、deskew tuning 或 image enhancement 深度調參。
- Validation 已通過：targeted backend tests `63 passed`；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`229 passed`，1 pytest cache warning）；ticket `rg` 與 `git diff --check` 通過。
- Release Impact：Version bump required: no。`v0.34.0` 版本同步留到 `34-04`。

34-03 Multipage OCR Status and Retry：
- 已完成。`POST /documents/{document_id}/ocr` 對 scanned / mixed PDF page images 執行 provider-selected OCR，並保存 page-level `ocr_text`、`ocr_blocks`、`ocr_attempts`、`ocr_provider`、`failure_reason` 與 `updated_at`。
- OCR 成功後會建立 `pdf_page_ocr` chunks，metadata 保留 `content_source=pdf_scanned_ocr`、page number、bbox / confidence 與 page image id；mixed PDF 會保留既有 `pdf_text` chunks，再接上掃描頁 OCR chunks。
- OCR 失敗會標示 `ocr_failed` 與 failure reason；retry 會增加 page attempts、移除舊 `pdf_page_ocr` chunks，避免重複污染 chunks 或 metadata。
- Validation 已通過：targeted backend tests `66 passed`；backend full tests `232 passed`；frontend build；`scripts/scanned-pdf-ocr-smoke.ps1`（`3 passed`）；ticket `rg` 與 `git diff --check` 通過。
- Release Impact：Version bump required: no。`v0.34.0` 版本同步留到 `34-04`。

34-04 Scanned PDF Demo and Phase 34 Release Sync：
- 已完成。backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 ticket 已同步到 `0.34.0`。
- 新增 scanned PDF demo smoke 覆蓋 PDF rendering、page image OCR chunks、parser 與 RAG handoff；focused backend tests 也確認 RAG route 使用同一份測試 storage，避免跨測試資料誤命中。
- Validation 已通過：focused backend tests `67 passed`；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`233 passed`，1 pytest cache warning）；`npm.cmd run build`；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\scanned-pdf-ocr-smoke.ps1`（`4 passed`）；Browser PDF upload / OCR status surface 檢查 desktop `1440px` 與 mobile `390px` 皆無 horizontal overflow；ticket `rg` 與 `git diff --check` 通過。
- Release Impact：Version bump required: yes。Phase 34 已完成 `v0.34.0` scanned PDF OCR baseline release；仍不包含 layout analysis、table reconstruction、human correction workflow、production OCR benchmark、production GPU scheduling 或 autoscaling。

35-01 Indexing Quality Contract：
- 已完成。`docs/architecture.md` 已定義 Phase 35 indexing quality contract：`fixed_size`、`semantic`、`parent_child` chunking 策略、Qdrant payload / tenant / project / document filter boundary、reindex document / project、stale vector cleanup 與 indexing audit metadata。
- `docs/api.md` 已補上未來 indexing request、Qdrant payload、reindex response 與 cleanup contract；本 ticket 不新增 runtime chunking、Qdrant index code、worker、eval dashboard、OCR、parser、Agent planner 或 Auth / RBAC 行為。
- Validation 已通過：`rg -n "chunking|semantic|parent-child|Qdrant payload|reindex|stale vector|Phase 35" docs README_DEV.md TODO.md tasks/phase-35-rag-indexing-quality`；`git diff --check`（僅 Windows LF/CRLF 提示）。
- Release Impact：Version bump required: no。這是 Phase 35 contract ticket，不改 runtime。

35-02 Chunking Strategy Runtime：
- 已完成。`POST /documents/{document_id}/index/vector` 可用 request body 選擇 `chunking_strategy=fixed_size|semantic`；不傳 body 仍使用 `fixed_size`，避免現有 demo hard fail。
- Vector indexing 會依 strategy 產生 indexing chunks，並在 payload metadata 保存 strategy name、`char_count`、`token_count`、`source_type`、`source_chunk_id`、`chunk_part_index` 與可用的 `page_number`。`semantic` 只使用既有段落 / section 邊界，邊界不足時 fallback 到 fixed windows。
- Backend tests 已覆蓋 `fixed_size` 與 `semantic` output 差異、metadata 與 API request flow；本 ticket 不新增 LLM segmentation、eval dashboard、OCR、parser 或 Agent planner 行為。
- Validation 已通過：focused backend tests `60 passed`；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`234 passed`，1 pytest cache warning）；`rg -n "chunking strategy|fixed|semantic|parent_child|chunk metadata" backend docs TODO.md tasks/phase-35-rag-indexing-quality`；`git diff --check`（僅 Windows LF/CRLF 提示）。
- Release Impact：Version bump required: no。版本同步留到 `35-04`。

35-03 Qdrant Payload Index and Reindexing：
- 已完成。`QdrantVectorStore` 會建立 payload indexes，並支援 tenant / project / document / source filters；vector payload 會保存 `tenant_id`、`project_id`、`content_source` 與 `chunk_type`。
- `POST /documents/{document_id}/index/vector` 可用 `cleanup_stale=true` 在成功 upsert 新 points 後刪除同文件舊 points；`POST /documents/index/vector/reindex` 可同步重跑可存取 project 範圍內的文件。
- Backend tests 與 smoke script 已覆蓋 payload index request、filter shape、project reindex、document stale cleanup 與 runtime unavailable 的既有 skipped / failed response；本 ticket 不新增 Redis / NATS worker、production eval dashboard、rerank algorithm、embedding model selection 或 LLM generation。
- Validation 已通過：focused backend tests `98 passed`；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\qdrant-reindex-cleanup-smoke.ps1`（`4 passed`，1 pytest cache warning）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`240 passed`，1 pytest cache warning）；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- Release Impact：Version bump required: no。版本同步留到 `35-04`。

35-04 Indexing Quality Demo and Phase 35 Release Sync：
- 已完成。backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 ticket 已同步到 `0.35.0`。
- 新增 `scripts/indexing-quality-smoke.ps1`，覆蓋 `fixed_size` / `semantic` chunking、Qdrant payload filter、project reindex 與 stale vector cleanup path。
- Validation 已通過：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`240 passed`，1 pytest cache warning）、`npm.cmd run build`、`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\indexing-quality-smoke.ps1`（`7 passed`，1 pytest cache warning）、ticket `rg` 與 `git diff --check`。
- Release Impact：Version bump required: yes。Phase 35 已完成 `v0.35.0` RAG indexing quality release；仍不包含 production eval dashboard、LLM-as-judge、rerank tuning 或 production indexing worker。
## Phase 40 Interview Evidence Hardening

- [x] `tasks/phase-40-interview-evidence-hardening/40-01-phase-40-jd-evidence-plan.md`: 新增 Phase 40 `v0.40.0` JD evidence hardening roadmap；文件 ticket，不 bump version。

Phase 40 `v0.40.0` - JD evidence hardening：
- [x] `tasks/phase-40-interview-evidence-hardening/40-02-embedding-sft-experiment-evidence.md`: 補齊 research-only Embedding / SFT experiment evidence report、before / after eval table、synthetic data coverage、skip reason 與 risk notes；不 bump version、不新增 runtime。
- [x] `tasks/phase-40-interview-evidence-hardening/40-03-inference-hardware-benchmark-evidence.md`: 補齊 inference hardware benchmark evidence report，整理 vLLM / Ollama / OpenAI-compatible matrix、KV cache、TOPS / NPU、VRAM、tokens/sec、latency 與 skip reason；不 bump version、不新增 runtime。
- [x] `tasks/phase-40-interview-evidence-hardening/40-04-observability-dashboard-evidence.md`: 補齊 observability dashboard evidence docs、Loki / Grafana query examples、Grafana dashboard JSON skeleton、log schema mapping 與 fallback / unavailable 說明；不 bump version、不新增 production alerting。
- [x] `tasks/phase-40-interview-evidence-hardening/40-05-phase-40-release-sync.md`: 完成 `v0.40.0` release sync，更新 backend / frontend / Docker Compose / `.env.example` / health test / K8s sample image tag / demo smoke expected version，並同步 README / README_DEV / backend README / frontend README / TODO / ROADMAP；保留 production training、production inference autoscaling、production alerting / incident workflow 與 production guarantee 為未完成邊界。

40-05 Phase 40 Release Sync Status：
- 已完成。backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、K8s sample image tag、demo smoke expected version、README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 ticket 已同步到 `0.40.0` / `v0.40.0`。
- Phase 40 三個 JD evidence artifacts 已收束：Embedding / SFT experiment evidence、inference hardware benchmark evidence（KV cache / TOPS / provider skip reason）與 observability dashboard evidence（Grafana / Loki query examples / dashboard skeleton）。
- Validation 已通過：backend full test `260 passed, 1 warning`（pytest cache permission warning）、frontend build、baseline demo smoke（health `0.40.0`；本機 Qdrant unavailable 時 aggressive vector indexing 失敗但 fallback 符合預期；RAG answer source `ollama/qwen3.5:4b`，retrieval source `hybrid_rerank fallback: reranker_unavailable`）、Phase 40 evidence `rg`、release `rg` 與 `git diff --check`（只有 LF/CRLF 提示）。
- Release Impact：Version bump required: yes。Phase 40 已完成 `v0.40.0` JD evidence hardening release；不新增 production training、production inference autoscaling、production alerting / incident workflow 或 production guarantee。

40-02 Embedding SFT Experiment Evidence Status：
- 已完成 Phase 40 Embedding / SFT experiment evidence。新增 `fine-tuning/phase40-experiment-evidence.md` 與 `sample-data/fine-tuning/phase40-before-after-eval.csv`，並更新 fine-tuning dataset card / README。
- Report 串接既有 dataset card、SFT JSONL、embedding positive / negative pairs、reranker pairwise samples、invoice / contract / report synthetic data coverage、before / after eval table、Hit Rate@K / MRR@K / Recall@K / parser field accuracy、skip reason、privacy / label leakage / overfit risk notes 與 research-only runtime boundary。
- Validation 已通過：ticket `rg` 與 `git diff --check`。
- Release Impact：Version bump required: no。版本同步留到 `40-05`；本 ticket 不下載大型模型、不執行 training、不新增 dependency、不接 production runtime，也不改 OCR、parser、RAG、Agent、embedding 或 reranker behavior。

40-03 Inference Hardware Benchmark Evidence Status：
- 已完成 Phase 40 inference hardware benchmark evidence。新增 `docs/inference-hardware-benchmark-evidence.md`，整理 environment、provider matrix、request shape、metrics table、KV cache estimate、TOPS / NPU interpretation、vLLM command template、metrics endpoint note 與 honesty boundary。
- Metrics table 保留 p50 / p95 latency、time to first token、tokens/sec、prompt tokens、completion tokens、VRAM peak、KV cache estimated bytes、provider fallback 與 skip reason；沒有實測資料時明確標示 pending / skipped，不偽造 capacity 結論。
- Validation 已通過：ticket `rg` 與 `git diff --check`。
- Release Impact：Version bump required: no。版本同步留到 `40-05`；本 ticket 不啟動 vLLM、不新增 NPU profiler、不宣稱 production capacity guarantee，也不改 default provider、RAG prompt、Agent planner、VLM parser 或 OCR pipeline。

40-04 Observability Dashboard Evidence Status：
- 已完成 Phase 40 observability dashboard evidence。新增 `docs/observability-dashboard-evidence.md` 與 `infra/observability/grafana-dashboard-docurag-evidence.json`，並在 `infra/observability/README.md` 補上 dashboard skeleton 入口。
- Evidence 覆蓋 API log、worker log、RAG trace、retrieval latency、rerank latency、generation latency、eval metrics、API latency p95、API error rate、worker task failures、fallback count、Hit Rate、MRR 與 log schema mapping。
- Validation 已通過：ticket `rg`、Grafana dashboard JSON parse 與 `git diff --check`。
- Release Impact：Version bump required: no。版本同步留到 `40-05`；本 ticket 不新增 production alerting、SLO、incident workflow、distributed tracing 或 APM vendor integration，也不改 RAG ranking、Agent planner、OCR / parser behavior 或 worker runtime。

Phase 40 guardrails：

- Phase 40 只補面試證據 artifacts，不新增新的 production runtime 主線。
- `40-02` 可以補 SFT / embedding tuning / synthetic data report 或 notebook skeleton，但不得下載大型模型或執行長時間 training。
- `40-03` 可以補 inference benchmark report、KV cache / TOPS / NPU 評估方式與 script/template，但不得宣稱沒有實測的硬體結果。
- `40-04` 可以補 observability dashboard / query examples / demo-safe screenshots，但不得宣稱 production alerting 或 incident workflow 已完成。
- `42-05` 已完成 release sync，backend / frontend / health / Docker Compose version 已同步到 `v0.42.0`；Phase 43 仍需另依 ticket-first 流程執行。

## Phase 41-45 JD Completion Roadmap

Phase 41 `v0.41.0` - RAG quality regression / DatasetOps：
- [x] `tasks/phase-41-rag-quality-regression-datasetops/41-01-rag-quality-regression-contract.md`: 完成 Phase 41 RAG quality regression contract；固定 golden dataset、eval run、strategy snapshot、regression report、Hit Rate@K / MRR@K / Recall@K / latency / fallback count / failure count / trace metadata coverage 與 pass / warn / fail regression gate。文件 ticket，不 bump version。
- [x] `tasks/phase-41-rag-quality-regression-datasetops/41-02-golden-dataset-versioning.md`: 新增 golden dataset metadata manifest 與 dataset changelog，為既有 demo-safe eval cases 補上 case version、source document version、expected evidence mapping、expected answer outline 與 case tags；runtime eval JSON schema 不變，不 bump version。
- [x] `tasks/phase-41-rag-quality-regression-datasetops/41-03-retrieval-regression-ci-report.md`: 新增 CI-safe retrieval regression report script 與 baseline artifact，預設跑 keyword strategy，比較 baseline vs current Hit Rate@K / MRR@K / Recall@K / latency / fallback summary，並輸出 dataset version、provider availability、skip reason 與 threshold gate；不 bump version。
- [x] `tasks/phase-41-rag-quality-regression-datasetops/41-04-chunking-indexing-ablation-report.md`: 新增 chunking / indexing ablation report 與 sample artifact template，說明 fixed-size、semantic、parent-child、Qdrant payload filter / payload index、stale vector cleanup 與 reindex 的比較方式；欄位連回 Hit Rate@K / MRR@K / Recall@K / latency / fallback，並明確標示 keyword baseline 是實測，其餘策略為待測假設或 runtime 尚不支援。不 bump version。
- [x] `tasks/phase-41-rag-quality-regression-datasetops/41-05-phase-41-release-sync.md`: 完成 `v0.41.0` release sync，更新 backend / frontend / Docker Compose / `.env.example` / health test / demo smoke expected version，並同步 README / README_DEV / backend README / frontend README / TODO / ROADMAP；整理 golden dataset、regression report 與 ablation report validation，明確標示 Phase 41 是品質追蹤與回歸證據，不是 production eval platform。
- Validation 已通過：backend full test、frontend build、retrieval regression report smoke、Phase 41 keyword `rg` 與 `git diff --check`。Release Impact：Version bump required: yes，Phase 41 已完成 `v0.41.0` RAG quality regression / DatasetOps release；不新增 LLM-as-judge、production eval dashboard、DB eval history、排程任務或外部 monitoring。

Phase 42 `v0.42.0` - Inference gateway / capacity planning：
- [x] `tasks/phase-42-inference-gateway-capacity-planning/42-01-inference-gateway-contract.md`: 完成 Phase 42 inference gateway contract；文件固定 Ollama / vLLM / OpenAI-compatible / disabled provider domain、routing / fallback / timeout / token usage / latency metadata、provider health / circuit breaker 邊界與 capacity planning report 邊界。不 bump version。
- [x] `tasks/phase-42-inference-gateway-capacity-planning/42-02-provider-routing-and-fallback.md`: 補齊 demo-safe provider selected / fallback reason metadata；LLM、VLM parser、vector / embedding retrieval 與 rerank failure 會標示 provider status、fallback target 與既有 fallback reason，optional provider unavailable / timeout 時仍回到既有 fallback。不 bump version。
- [x] `tasks/phase-42-inference-gateway-capacity-planning/42-03-streaming-timeout-guardrails.md`: 補齊 RAG generation timeout、max tokens / num_predict、streaming mode、truncated reason 與 generation latency trace；provider timeout 仍 fallback 到 retrieved chunks。不 bump version。
- [x] `tasks/phase-42-inference-gateway-capacity-planning/42-04-capacity-planning-report.md`: 新增 inference capacity planning report，整理 workload profile、capacity table、latency p50 / p95、tokens/sec / throughput、VRAM、KV cache estimate、TOPS / NPU、fallback policy、skip reason 與模型 / 硬體選型。不 bump version。
- [x] `tasks/phase-42-inference-gateway-capacity-planning/42-05-phase-42-release-sync.md`: 完成 `v0.42.0` release sync，更新 backend / frontend / Docker Compose / `.env.example` / health test / demo smoke expected version，並同步 README / README_DEV / backend README / frontend README / TODO / ROADMAP；整理 provider routing、timeout guardrails 與 capacity planning report validation。
- Validation 已通過：backend full test、frontend build、inference benchmark smoke skipped report、Phase 42 keyword `rg` 與 `git diff --check`。Release Impact：Version bump required: yes，Phase 42 已完成 `v0.42.0` inference gateway / capacity planning release；不新增 production autoscaling、多 GPU serving、paid API key、production secret、SLA、production metrics service 或 autoscaling controller。
- `42-02` validation 已通過：focused backend tests `47 passed`；backend full test script；Phase 42 runtime keyword `rg`；`git diff --check`。本 ticket 不啟動 vLLM server、不新增大型模型下載、不新增 paid API key / production secret、不把 vLLM 或 OpenAI-compatible endpoint 設為唯一 runtime，也不新增 load balancing、多 tenant quota、production circuit breaker service 或 autoscaling。
- `42-03` validation 已通過：focused backend tests `41 passed`；backend full test script；Phase 42 guardrail keyword `rg`；`git diff --check`。本 ticket 不新增完整 SSE / WebSocket frontend streaming UI、不新增 queue-based inference scheduler、多使用者 quota、production rate limiter、不更換預設模型或新增外部 inference dependency。
- `42-04` validation 已通過：Phase 42 capacity docs `rg` 與 `git diff --check`。本 ticket 不要求真實 NPU 硬體或 TOPS profiler、不下載大型模型、不啟動長時間 benchmark、不承諾 production throughput，也不新增 production metrics service 或 autoscaling controller。

Phase 43 `v0.43.0` - AgentOps governance / secure tool runtime：
- [ ] `tasks/phase-43-agentops-governance-secure-runtime/43-01-agent-governance-contract.md`
- [ ] `tasks/phase-43-agentops-governance-secure-runtime/43-02-tool-permission-policy-runtime.md`
- [ ] `tasks/phase-43-agentops-governance-secure-runtime/43-03-human-approval-risk-tier.md`
- [ ] `tasks/phase-43-agentops-governance-secure-runtime/43-04-agent-run-replay-and-eval.md`
- [ ] `tasks/phase-43-agentops-governance-secure-runtime/43-05-phase-43-release-sync.md`

Phase 44 `v0.44.0` - Document Intelligence QA / human review loop：
- [ ] `tasks/phase-44-document-intelligence-qa-human-review/44-01-document-intelligence-qa-contract.md`
- [ ] `tasks/phase-44-document-intelligence-qa-human-review/44-02-field-confidence-and-evidence-view.md`
- [ ] `tasks/phase-44-document-intelligence-qa-human-review/44-03-human-correction-and-golden-labels.md`
- [ ] `tasks/phase-44-document-intelligence-qa-human-review/44-04-parser-field-accuracy-eval.md`
- [ ] `tasks/phase-44-document-intelligence-qa-human-review/44-05-phase-44-release-sync.md`

Phase 45 `v0.45.0` - Production readiness / interview portfolio pack：
- [ ] `tasks/phase-45-production-readiness-portfolio-pack/45-01-jd-evidence-matrix.md`
- [ ] `tasks/phase-45-production-readiness-portfolio-pack/45-02-system-design-walkthrough.md`
- [ ] `tasks/phase-45-production-readiness-portfolio-pack/45-03-demo-scenario-pack.md`
- [ ] `tasks/phase-45-production-readiness-portfolio-pack/45-04-risk-boundary-and-tradeoff-report.md`
- [ ] `tasks/phase-45-production-readiness-portfolio-pack/45-05-phase-45-final-release-sync.md`

Phase 41-45 guardrails：

- Phase 41-45 用來補強 JD 面試追問證據，不取代 Phase 35-40 的既有 backlog；仍必須一張 ticket 一張 ticket 執行。
- Phase 41 聚焦 RAG quality regression、golden dataset、CI-style report 與 chunking / indexing ablation，不新增 LLM-as-judge 或 production eval dashboard。
- Phase 42 聚焦 inference gateway、provider fallback、timeout guardrails 與 capacity planning，不要求 production autoscaling、多 GPU serving、paid API key 或外部 secret。
- Phase 43 聚焦 Agent tool permission、approval state、audit / replay evidence，不允許任意 SQL、shell、filesystem command 或 destructive tool。
- Phase 44 聚焦 OCR / VLM 欄位可信度、人工作業修正與 parser field accuracy eval，不新增 full annotation platform 或 model training。
- Phase 45 聚焦 JD evidence matrix、system design walkthrough、demo scenario pack 與 risk / tradeoff report，不新增新的 production runtime。
- 每個 Phase 完成 release sync ticket 前，不更新 backend / frontend / health / Docker Compose version。

## Phase 00 - Bootstrap Documents and Tickets

- [x] 建立 Phase 00 文件與任務票規範。
- [x] 更新 `README.md`，說明專案目標、MVP 範圍與開發方向。
- [x] 更新 `AGENTS.md`，說明 Codex 後續如何用小 ticket 開發。
- [x] 建立 `docs/PRD.md`。
- [x] 建立 `docs/ARCHITECTURE.md`。
- [x] 建立 `docs/ROADMAP.md`。
- [x] 建立 `tasks/_TEMPLATE.md`。
- [x] 建立 Phase 00 到 Phase 02 的初始 ticket。
- [x] 執行 `tasks/phase-00-bootstrap/00-01-repo-structure.md`。
- [x] 執行 `tasks/phase-00-bootstrap/00-02-project-docs.md`。

## Phase 01 - Backend Bootstrap

- [x] 執行 `tasks/phase-01-backend-bootstrap/01-01-backend-healthcheck.md`。
- [x] 執行 `tasks/phase-01-backend-bootstrap/01-02-backend-docker.md`。
- [x] 確認 backend healthcheck 可以用 ticket 指定方式驗證。
- [x] 確認 Docker 啟動邊界只涵蓋 Phase 01 所需範圍。

## Phase 02 - Document Foundation

- [x] 執行 `tasks/phase-02-document-foundation/02-01-document-upload-api.md`。
- [x] 執行 `tasks/phase-02-document-foundation/02-02-document-metadata-schema.md`。
- [x] 確認文件上傳 API 不觸發 OCR、RAG 或 async worker。
- [x] 確認 document metadata schema 可支援後續 OCR 與 RAG 狀態，但不提前實作資料庫遷移。

## MVP v0.1 Local Verification

- [x] 建立 `scripts/check-dev-env.ps1`。
- [x] 建立 `scripts/test-backend.ps1`。
- [x] 建立 `docs/LOCAL_DEV_SETUP.md`。
- [x] 診斷 Python：`py` launcher 不存在，`python` 目前無法執行。
- [x] 診斷 Docker：`docker` CLI 不在 PATH。
- [x] 修復本機 Python 後重跑 `scripts/test-backend.ps1`。
- [x] 修復 Docker 後重跑 `docker build` 與 `docker compose build`。

## MVP v0.2 Demo UI

- [x] 建立 GitHub Actions `Backend CI` workflow。
- [x] 建立最小 Vue 3 + Vite + TypeScript frontend。
- [x] frontend 可呼叫 `GET /health`。
- [x] frontend 可選擇檔案並呼叫 `POST /documents/upload` stub。
- [x] backend 加上 local frontend CORS 設定。
- [x] 建立 `frontend/README.md`。
- [x] 更新 demo 啟動與驗證文件。
- [x] 驗證 Docker CLI、Docker build 與 Docker Compose healthcheck。

## MVP v0.3 Document Local Storage

- [x] 將 `POST /documents/upload` 從 stub 升級為本機存檔。
- [x] 保存 document metadata 到 local JSON store。
- [x] 新增 `GET /documents` 文件列表 API。
- [x] 新增 `GET /documents/{document_id}` 文件詳情 API。
- [x] 新增安全下載端點 `GET /documents/{document_id}/download`。
- [x] 測試 unsafe filename 不會 path traversal。
- [x] frontend 顯示文件列表與 document metadata JSON。
- [x] Docker Compose 掛載 `data/` 並驗證 upload API。

## MVP v0.4 OCR Mock Pipeline

- [x] 建立 `tasks/phase-03-ocr-mock/03-01-ocr-mock-pipeline.md`。
- [x] 新增 `POST /documents/{document_id}/ocr/mock`。
- [x] 新增 `GET /documents/{document_id}/ocr`。
- [x] 保存 OCR mock result 到 local JSON metadata store。
- [x] 未執行 OCR 的文件回傳 `pending` OCR status。
- [x] OCR result 包含 status、text、extracted fields 與 updated timestamp。
- [x] frontend 可對文件執行 Run Mock OCR。
- [x] frontend 顯示 OCR status、OCR text 與 extracted fields。
- [x] 確認未接 PaddleOCR、Tesseract、VLM、RAG、Qdrant、Redis、NATS、vLLM、登入或 PostgreSQL。

## MVP v0.5 Local RAG Baseline

- [x] 建立 `tasks/phase-05-rag-baseline/05-01-local-rag-baseline.md`。
- [x] 從 OCR mock text 產生 chunks。
- [x] 每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。
- [x] chunks 保存到 local JSON metadata store，不新增 DB。
- [x] 新增 local keyword retrieval，依 query 回傳 `top_k` matched chunks。
- [x] retrieval result 包含 score、`document_id` 與 `chunk_id`。
- [x] 新增 `POST /rag/query`。
- [x] RAG response 包含 deterministic answer、citations 與 retrieved chunks。
- [x] citations 包含 `document_id`、`filename` 與 `chunk_id`。
- [x] frontend 新增 RAG chat，可顯示 answer、citations 與 retrieved chunks。
- [x] 保留既有 health、upload、document list 與 OCR mock UI。
- [x] backend version 更新為 `0.5.0`。
- [x] frontend package version 更新為 `0.5.0`。
- [x] 確認未接真正 LLM、OpenAI API、Ollama、vLLM、embedding、Qdrant、rerank、Redis、NATS、PostgreSQL、登入或 RBAC。

## MVP v0.5.1 Demo Hardening

- [x] 建立 `tasks/phase-05-rag-baseline/05-02-demo-hardening.md`。
- [x] 建立公開 sample documents，不包含真實個資或公司敏感資料。
- [x] 建立 `scripts/seed-demo-data.ps1`，可自動 upload、OCR mock、RAG query。
- [x] seed script 輸出 answer、citations 與 retrieved chunks。
- [x] 建立 `scripts/demo-smoke-test.ps1`，可驗證 `/health`、upload、OCR mock 與 `/rag/query`。
- [x] README 加入 5 分鐘 demo 指令、backend/frontend/Docker 啟動方式、範例問題與預期結果。
- [x] backend README 與 frontend README 加入 v0.5.1 demo flow。
- [x] OCR mock 對 text sample 納入公開 sample 文字，方便 local keyword RAG demo。
- [x] backend version 更新為 `0.5.1`。
- [x] frontend package version 更新為 `0.5.1`。
- [x] 確認仍未接 Qdrant、embedding、rerank、真正 LLM、OpenAI API、Ollama、vLLM、Redis、NATS、PostgreSQL、登入或 RBAC。

## MVP v0.6 Bridge Contracts

- [x] 建立 `tasks/phase-06-bridge/06-01-ocr-provider-interface.md`。
- [x] 建立 `tasks/phase-06-bridge/06-02-rag-provider-interface.md`。
- [x] 建立 `tasks/phase-06-bridge/06-03-processing-status-contract.md`。
- [x] 建立 `tasks/phase-06-bridge/06-04-chunk-citation-schema.md`。
- [x] 建立 `tasks/phase-06-bridge/06-05-processing-job-contract.md`。
- [x] 執行 OCR provider interface bridge，保留 mock provider 並維持 OCR API 相容。
- [x] 執行 RAG provider interface bridge，保留 local keyword provider 並維持 `/rag/query` 相容。
- [x] 執行 processing status contract，明確定義 upload、OCR、indexing、ready 與 failed 狀態。
- [x] 執行 chunk / citation schema bridge，補齊 page、bbox、confidence 與 trace metadata contract。
- [x] 執行 processing job contract，建立同步 job metadata，不引入真正 worker 或 queue。
- [x] 確認 v0.6 bridge 階段仍未接真正 OCR、embedding、Qdrant、rerank、LLM、Redis、NATS、PostgreSQL、登入或 RBAC。

## MVP v0.7 Real OCR Provider Spike

- [x] 建立 `tasks/phase-07-real-ocr-provider/07-01-ocr-provider-decision.md`。
- [x] 建立 `tasks/phase-07-real-ocr-provider/07-02-ocr-provider-adapter.md`。
- [x] 建立 `tasks/phase-07-real-ocr-provider/07-03-ocr-output-normalization.md`。
- [x] 建立 `tasks/phase-07-real-ocr-provider/07-04-real-ocr-demo-hardening.md`。
- [x] 執行 OCR provider decision spike，選定 PaddleOCR，並定義 real provider 不可用時明確失敗、mock path 保持可用。
- [x] 執行 local OCR provider adapter，新增 provider-selected `/documents/{document_id}/ocr`，預設仍保留 mock provider。
- [x] 執行 OCR output normalization，將 PaddleOCR lines 映射到 page、bbox、confidence 與 trace metadata。
- [x] 執行 real OCR demo hardening，讓缺少 real OCR dependency 時 mock demo 仍可重跑。
- [x] frontend UI 只顯示目前版本號，並提供 provider-selected OCR 操作。
- [x] backend 與 frontend 版本更新為 `0.7.0`。
- [x] 確認 Phase 07 仍未接 queue、Redis、NATS、Qdrant、embedding、rerank、LLM、PostgreSQL、登入或 RBAC。

## MVP v0.8.0 PaddleOCR Runtime Stabilization

- [x] 執行 `tasks/phase-08-paddleocr-runtime/08-01-paddleocr-environment-baseline.md`。
- [x] 執行 `tasks/phase-08-paddleocr-runtime/08-02-paddleocr-dependency-fix.md`。
- [x] 執行 `tasks/phase-08-paddleocr-runtime/08-03-paddleocr-default-flow-validation.md`。
- [x] 確認預設 PaddleOCR flow 可驗證，且 mock override 仍可重跑。
- [x] 確認 v0.8.0 不新增 PDF rendering、Qdrant、embedding、rerank、LLM、Redis、NATS、worker、資料庫 schema、登入或權限。
- [x] 以 Python 3.12、PaddleOCR 2.10.0 與 PaddlePaddle 3.0.0 驗證 real OCR sample，可完成 provider-selected OCR 與 chunks 產生。
- [x] backend 與 frontend 版本更新為 `0.8.0`。
- [x] Release 文件以 `v0.8.0` 記錄 Phase 08，不再用裸 `Phase 08` 當 release 條目。

## Parking Lot

- [ ] Production-grade OCR / VLM parser（v0.7 / v0.8 只先完成 provider spike 與 runtime stabilization）。
- [ ] Production-grade background embedding / Qdrant indexing pipeline（v0.27.0 只有 demo best-effort / manual indexing，不是正式 worker）。
- [ ] Production Redis session rotation / cross-service cache invalidation / worker lock runtime（33-02 只完成 demo-safe session cache、query cache 與 rate limit slice）。
- [ ] Production NATS worker pipeline / durable async execution（33-03 只完成 NATS helper、worker skeleton 與 task status slice）。
- [ ] Production-grade LLM / rerank / citation quality evaluation（local Ollama generation 與 FastEmbed adapter 已有 demo default，正式評測仍未做）。
- [ ] vLLM / OpenAI-compatible provider。

## MVP v0.9.x GPU Runtime Backlog

- [x] `tasks/phase-09-gpu-runtime/09-01-paddleocr-gpu-only-runtime.md`: PaddleOCR GPU-only runtime baseline；本機已以 Python 3.12.10、`paddlepaddle-gpu==3.3.0`、CUDA 12.9 runtime wheel 與 RTX 5070 Ti 通過 `paddle.utils.run_check()`、`check-dev-env.ps1 -CheckPaddleOcr` 與 provider-selected real OCR smoke。
- [x] `tasks/phase-09-gpu-runtime/09-02-paddleocr-v4-mobile-chinese-model.md`: PaddleOCR PP-OCRv4 mobile 中文 / 中英混合模型；已固定模型設定、記錄 det / rec / cls model directory、建立並驗證繁中 sample，mock OCR path 不受影響。
- [x] `tasks/phase-09-gpu-runtime/09-03-paddleocr-engine-lifecycle-preload.md`: 後端啟動時初始化 PaddleOCR engine，provider-selected OCR request 重用同一個 provider / engine，避免每次 request cold start。
- [x] `tasks/phase-09-gpu-runtime/09-04-paddleocr-performance-observability-tuning.md`: 加入 OCR timing log / baseline，評估 `cls=True`、warmup、圖片尺寸與推論參數對速度的影響，收斂 v0.9.1 performance hardening。

## MVP v0.10.0 LLM RAG Backlog

- [x] `tasks/phase-10-llm-rag/10-01-qwen3-ollama-provider-decision.md`: 依 `goal.md` 固定 Ollama `qwen3.5:4b` LLM / VLM provider 決策；已補齊 `DOCURAG_LLM_BASE_URL=http://127.0.0.1:11434` 與 `.env.example` provider env。
- [x] 10-01 validation：`nvidia-smi` 通過，GPU 為 RTX 5070 Ti；`ollama` CLI 目前不在 PATH，`http://127.0.0.1:11434/api/tags` 目前無服務回應，屬 10-02 前需補齊的本機前置條件。
- [x] `tasks/phase-10-llm-rag/10-02-ollama-qwen3-client.md`: 新增 Ollama `qwen3.5:4b` LLM client；預設 disabled，設定 `DOCURAG_LLM_PROVIDER=ollama` 後使用 native `POST /api/generate` 與 `stream=false`，並以 `GET /api/tags` 做 health helper。
- [x] 10-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`58 passed`；`curl.exe http://127.0.0.1:11434/api/tags` 仍因本機 Ollama service 未啟動而無法連線，mock HTTP / monkeypatch 測試已覆蓋 request / response。
- [x] `tasks/phase-10-llm-rag/10-03-qwen3-rag-generation.md`: 在既有 citations contract 上加入可選 `qwen3.5:4b` answer generation；prompt 只使用 query 與 retrieved chunks，LLM failure 會明確 fallback 到 retrieved OCR chunks。
- [x] 10-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`61 passed`；mock LLM client 測試已覆蓋 prompt assembly、成功生成、failure fallback、citation preservation 與 trace metadata。
- [x] `tasks/phase-10-llm-rag/10-04-qwen3-demo-smoke.md`: 補齊 Qwen3.5 demo smoke、UI answer source、`-RunLlm` optional smoke 與 `v0.10.0` release/version sync。
- [x] 10-04 validation：backend test script 通過，`61 passed`；`npm.cmd run build` 通過；`scripts/demo-smoke-test.ps1` 通過並確認 answer source 為 `deterministic baseline`；2026-05-22 follow-up 已安裝 Ollama 0.24.0、pull `qwen3.5:4b`，並以 LLM-enabled backend 跑通 `scripts/demo-smoke-test.ps1 -RunLlm`，確認 answer source 為 `ollama/qwen3.5:4b`。

## MVP v0.11.0 Vector RAG Backlog

- [x] `tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md`: 固定 Phase 11 第一版 embedding / vector store provider decision；選定 Ollama `qwen3-embedding:0.6b` 作為 local embedding 起點，Qdrant self-hosted Docker / Docker Compose 作為 vector store，並定義 `docurag_chunks_v1` collection 與 chunk payload metadata。
- [x] 11-01 validation：`rg -n "v0.11.0|phase-11|qwen3-embedding|Qdrant" TODO.md docs/ROADMAP.md tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-11-vector-rag/11-02-ollama-embedding-client.md`: 新增最小 Ollama embedding client building block；預設 disabled，設定 `DOCURAG_EMBEDDING_PROVIDER=ollama` 後使用 native `POST /api/embed` 與 `qwen3-embedding:0.6b`，不改 `/rag/query` 預設 keyword baseline。
- [x] 11-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`70 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`git diff --check` 通過。mock HTTP tests 已覆蓋 successful embed、connection error、HTTP error、timeout、missing model health 與 malformed response；2026-05-22 follow-up 已透過 Ollama API pull `qwen3-embedding:0.6b`，`scripts/ollama-embedding-smoke.ps1` 通過並確認實際 vector dimension 為 `1024`。
- [x] `tasks/phase-11-vector-rag/11-03-qdrant-local-runtime.md`: 新增 Qdrant local runtime / collection smoke；Docker Compose 包含 optional `qdrant` service，backend 不 `depends_on` Qdrant，`QdrantVectorStore` 可建立/檢查 `docurag_chunks_v1` collection，預設 vector size `1024`。
- [x] 11-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`76 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；mock Qdrant tests 覆蓋 collection exists、create collection、vector size mismatch、connection error、timeout 與 malformed response。2026-05-22 follow-up 已啟動 Docker Desktop、用 Docker Compose 啟動 Qdrant，並跑通 `scripts/qdrant-collection-smoke.ps1`，建立/確認 `docurag_chunks_v1` collection，vector size `1024`、distance `Cosine`。
- [x] `tasks/phase-11-vector-rag/11-04-vector-retrieval-demo-smoke.md`: 加入 optional vector retrieval path；預設仍是 keyword baseline，設定 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector` 後才嘗試 Ollama embedding + Qdrant search，任一 external runtime failure 會明確 fallback 到 keyword retrieval 並寫入 trace metadata。
- [x] 11-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`84 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`frontend` 的 `npm.cmd run build` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，answer source 為 `deterministic baseline`、retrieval source 為 `keyword baseline`；`git diff --check` 通過。2026-05-22 follow-up 已在本機準備 Ollama `qwen3-embedding:0.6b` 與 Qdrant，並用 vector-enabled backend 跑通 `scripts/demo-smoke-test.ps1 -RunVector`，answer source 為 `deterministic baseline`、retrieval source 為 `vector/qdrant`。Mock/unit tests 已覆蓋 default keyword path、vector success、embedding failure fallback、Qdrant failure fallback、collection missing fallback、route provider selection、Qdrant upsert/search。

## MVP v0.12.0 Vector Indexing Hardening Backlog

- [x] `tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md`: 固定 local vector indexing contract、Qdrant payload metadata、stable point id、failure / fallback 行為與 Phase 12 guardrails；文件 ticket，不 bump version。
- [x] 12-01 validation：`rg -n "v0.12.0|phase-12|Vector Indexing|docurag_chunks_v1" TODO.md docs/ROADMAP.md tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-12-vector-indexing/12-02-vector-indexing-service.md`: 新增最小同步 vector indexing service/helper，將 existing document chunks idempotently embed + upsert 到 Qdrant；不新增 API、worker、DB 或 default-on vector path。
- [x] 12-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`91 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`git diff --check` 通過。單元測試覆蓋 stable point id、payload metadata、empty chunks skipped、embedding failure、Qdrant failure、collection size mismatch 與 embedding dimension mismatch。
- [x] `tasks/phase-12-vector-indexing/12-03-vector-indexing-api.md`: 新增手動 vector indexing API，例如 `POST /documents/{document_id}/index/vector`，讓 demo 可明確執行 indexing；不新增 batch indexing、frontend 大改版或 async queue。
- [x] 12-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`97 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`git diff --check` 通過。Endpoint tests 覆蓋 success、document not found、OCR 未完成、empty chunks skipped、provider disabled 與 Qdrant failure。
- [x] `tasks/phase-12-vector-indexing/12-04-vector-indexing-demo-smoke.md`: 更新 optional vector demo smoke，先手動 vector indexing 再 vector retrieval query，並完成 `v0.12.0` release/version sync。
- [x] 12-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`97 passed`（本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12）；`frontend` 的 `npm.cmd run build` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，answer source 為 `deterministic baseline`、retrieval source 為 `keyword baseline`；optional vector indexing `scripts/demo-smoke-test.ps1 -RunVector` 通過，會先 manual vector indexing，retrieval source 為 `vector/qdrant`；`git diff --check` 通過。

Phase 12 guardrails：

- keyword RAG 仍為 baseline；vector indexing / retrieval 仍需明確 env 與手動 action。
- 保留 optional Ollama `qwen3.5:4b` generation path。
- 不實作 rerank、hybrid search、eval runner、Redis、NATS、worker、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- Qdrant 或 embedding 不可用時，baseline demo 不可被破壞。
- Stable vector point id 規則固定為 `uuid5(NAMESPACE_URL, f"docurag:{document_id}:{chunk_id}")`，重跑 manual indexing 只能 idempotently upsert 同一 chunk。
- Qdrant payload 必須保留 `document_id`、`filename`、`chunk_id`、`text`、`source`、`source_type`、`page_number`、`bbox`、`confidence`、`created_at` 與 chunk `metadata`。
- Empty chunks、embedding disabled / unavailable、Qdrant unavailable、collection missing 或 vector size mismatch 必須回傳清楚 skipped / failed result，不修改 local metadata，不影響 keyword RAG baseline。

## MVP v0.13.0 Retrieval Evaluation Baseline Backlog

- [x] `tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md`: 固定 retrieval evaluation dataset schema、metrics、result output contract 與 Phase 13 guardrails；文件 ticket，不 bump version。
- [x] 13-01 validation：`rg -n "v0.13.0|phase-13|Retrieval Evaluation|Hit Rate|MRR" TODO.md docs/ROADMAP.md tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-13-retrieval-eval/13-02-retrieval-eval-dataset.md`: 新增最小公開 retrieval eval dataset，使用既有虛構 sample documents，不新增 runner 或 runtime API。
- [x] 13-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`99 passed`（本機 PowerShell PATH 臨時補上 Codex bundled Python 3.12；pytest cache 權限警告不影響結果）；`git diff --check` 通過。
- [x] `tasks/phase-13-retrieval-eval/13-03-retrieval-eval-runner.md`: 新增本機 retrieval eval runner，計算 keyword baseline 與 optional vector retrieval 的 Hit Rate@K、MRR@K、Recall@K、latency 與 failure count。
- [x] 13-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`104 passed`（本機 PowerShell PATH 臨時補上 Codex bundled Python 3.12；pytest cache 權限警告不影響結果）；baseline `scripts/retrieval-eval-smoke.ps1` 通過，Hit Rate@K `0.8333`、MRR@K `0.6389`、Recall@K `0.75`、failure count `0`；optional vector `scripts/retrieval-eval-smoke.ps1 -RunVector` 通過，Hit Rate@K `0.6667`、MRR@K `0.6667`、Recall@K `0.5833`、failure count `0`；`git diff --check` 通過。
- [x] `tasks/phase-13-retrieval-eval/13-04-retrieval-eval-demo-smoke.md`: 補齊 retrieval eval demo smoke，完成 `v0.13.0` release/version sync。
- [x] 13-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`104 passed`（本機 PowerShell PATH 臨時補上 Codex bundled Python 3.12；pytest cache 權限警告不影響結果）；`frontend` 的 `npm.cmd run build` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，version `0.13.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；baseline `scripts/retrieval-eval-smoke.ps1` 通過，Hit Rate@K `0.8333`、MRR@K `0.6389`、Recall@K `0.75`、failure count `0`；optional vector `scripts/retrieval-eval-smoke.ps1 -RunVector` 通過，manual vector indexing API preflight indexed chunks `2`，Hit Rate@K `0.6667`、MRR@K `0.6667`、Recall@K `0.5833`、failure count `0`；`git diff --check` 通過。

Phase 13 guardrails：

- Phase 13 只建立 retrieval evaluation baseline，不實作 rerank、hybrid search、LLM-as-judge、answer faithfulness 或 citation quality scoring。
- Baseline eval 必須可在沒有 Ollama embedding 或 Qdrant 時執行 keyword retrieval 評估。
- Optional vector eval 必須明確 env、Qdrant collection 與 manual vector indexing；不可讓 eval、vector retrieval 或 vector indexing 成為 default-on path。
- Eval dataset 只使用公開虛構 sample data，不新增真實文件或敏感資料。
- 不新增 Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。

## MVP v0.14.0 Retrieval Quality Planning Backlog

- [x] `tasks/phase-14-retrieval-quality/14-01-rerank-provider-decision.md`: 固定 Phase 14 rerank provider decision 與 retrieval quality planning boundary，引用 Phase 13 metrics，記錄 local-first / disabled-by-default / fallback-safe decision criteria；只做文件決策，不新增 runtime。
- [x] 14-01 validation：`rg -n "v0.14.0|Phase 14|rerank|hybrid|retrieval quality" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-01-rerank-provider-decision.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-14-retrieval-quality/14-02-retrieval-quality-contract.md`: 定義 future strategy labels、rerank trace metadata、hybrid merge / dedupe trace metadata 與 fallback contract；只做 Markdown contract，不新增 implementation 或 version bump。
- [x] 14-02 validation：`rg -n "vector_rerank|hybrid_rerank|rerank score|fallback|default-on" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-02-retrieval-quality-contract.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md`: 規劃 retrieval eval dataset 擴充原則、lexical mismatch、multi-evidence、near-duplicate chunks、cross-document ambiguity、numeric / table lookup 等 future cases 與 quality gates；只做文件計畫，不修改 dataset JSON。
- [x] 14-03 validation：`rg -n "dataset expansion|lexical mismatch|multi-evidence|near-duplicate|cross-document" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md`: 規劃 future demo smoke preflight、validation checklist、release sync checklist 與 runtime implementation boundary；不執行 version bump、release sync、tag 或 runtime 實作。
- [x] 14-04 validation：`rg -n "v0.14.0|demo smoke|release sync|Version bump required: no|future implementation" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 14 guardrails：

- Phase 14 目前只做 retrieval quality planning 與 ticket 草案，不實作 rerank、hybrid search 或任何 runtime。
- 所有 Phase 14 ticket 都必須包含 `Release Impact`，且目前皆為 `Version bump required: no`。
- 不新增 backend / frontend 程式碼、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不修改 `sample-data/eval/retrieval-eval.json`，dataset 擴充只先做 Markdown planning。
- 不變更 keyword / vector retrieval 預設行為，不讓 future strategy 成為 default-on path。

## MVP v0.15.0 Rerank Runtime Spike Backlog

- [x] `tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md`: 決定 Phase 15 local-first rerank provider / model、dependency / model download 邊界與 `vector_rerank` 優先順序；文件票，不新增 runtime。
- [x] 15-01 validation：`rg -n "v0.15.0|Phase 15|rerank provider|vector_rerank|hybrid" TODO.md docs/ROADMAP.md tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-15-rerank-runtime/15-02-rerank-provider-adapter.md`: 實作 disabled-by-default rerank provider adapter，保留 keyword baseline 與 vector retrieval fallback。
- [x] 15-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-15-rerank-runtime/15-03-vector-rerank-eval-integration.md`: 將 optional `vector_rerank` 接入 retrieval eval runner，輸出 Phase 13 metrics 與 rerank trace metadata。
- [x] 15-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1` 通過；optional rerank eval smoke command documented as `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVectorRerank`；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-15-rerank-runtime/15-04-rerank-demo-release-sync.md`: 補齊 optional rerank demo / eval smoke 並執行 `v0.15.0` release/version sync。
- [x] 15-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過；`frontend` 的 `npm.cmd run build` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，version `0.15.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；baseline `scripts/retrieval-eval-smoke.ps1` 通過，Hit Rate@K `0.8333`、MRR@K `0.6389`、Recall@K `0.75`、failure count `0`；optional `vector_rerank` eval smoke command 已文件化為 `scripts/retrieval-eval-smoke.ps1 -RunVectorRerank`，本機未執行 optional rerank smoke，因為 `.venv` 未安裝 optional FastEmbed runtime（Ollama embedding 與 Qdrant collection 可連線）；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] Phase 15 planning validation：`rg -n "v0.15.0|Phase 15|15-01|15-04|rerank runtime" TODO.md docs/ROADMAP.md tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md tasks/phase-15-rerank-runtime/15-02-rerank-provider-adapter.md tasks/phase-15-rerank-runtime/15-03-vector-rerank-eval-integration.md tasks/phase-15-rerank-runtime/15-04-rerank-demo-release-sync.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 15 goal：

- 以 Phase 14 planning 為基礎，優先做 disabled-by-default `vector_rerank` runtime spike。
- 15-01 已選定第一版 rerank runtime 路線為 FastEmbed `TextCrossEncoder` + `BAAI/bge-reranker-base`；實作仍必須 disabled-by-default。
- 保留 keyword baseline 可在無 external runtime 時執行。
- 使用 Phase 13 eval metrics 比較 `vector` 與 `vector_rerank`，先不實作 hybrid search。

Phase 15 guardrails：

- 先執行 `15-01` provider decision，再開始任何 code implementation。
- 不讓 rerank、vector retrieval 或 eval strategy default-on。
- 不實作 hybrid search、BM25、score fusion、merge / dedupe policy 或 frontend trace UI，除非後續 ticket 明確要求。
- 不新增 Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 若需要外部依賴、模型下載或 Docker runtime，必須由 ticket 明確列出，並依工具要求取得 approval。
- Phase 15 完成後，hybrid search、dataset JSON expansion、frontend trace UI 與真正 dependency packaging 留到 Phase 16 或後續 ticket 規劃。

## MVP v0.16.0 Hybrid Retrieval Planning Backlog

- [x] `tasks/phase-16-hybrid-retrieval/16-01-hybrid-retrieval-contract.md`: 固定 optional `hybrid` strategy、candidate source、merge policy、dedupe key 與 trace metadata contract；文件 ticket，不 bump version。
- [x] `tasks/phase-16-hybrid-retrieval/16-02-eval-dataset-expansion-json.md`: 依 Phase 14 plan 擴充公開 retrieval eval dataset JSON，至少讓總 cases 達到 `12`，並保留 baseline keyword eval 可重跑。
- [x] `tasks/phase-16-hybrid-retrieval/16-03-hybrid-eval-strategy-integration.md`: 將 optional `hybrid` strategy 接入 retrieval eval runner，沿用 Phase 13 metrics 並保留 fallback trace metadata。
- [x] `tasks/phase-16-hybrid-retrieval/16-04-hybrid-demo-release-sync.md`: 補齊 optional hybrid demo / eval smoke，並在 implementation 完成時執行 `v0.16.0` release/version sync。
- [x] Phase 16 planning validation：`rg -n "v0.16.0|Phase 16|16-01|16-04|hybrid retrieval" TODO.md docs/ROADMAP.md tasks/phase-16-hybrid-retrieval/*.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 16 goal：

- 在 Phase 15 disabled-by-default `vector_rerank` runtime spike 後，規劃下一個 retrieval quality slice：公開 dataset expansion 與 optional `hybrid` eval strategy。
- `hybrid` 第一版只用既有 keyword branch 與 optional vector branch，不新增 BM25 dependency。
- 使用 Phase 13 eval metrics 比較 `keyword`、`vector`、`vector_rerank` 與 `hybrid`。
- 16-04 才允許 `v0.16.0` version bump 與 release docs sync。

Phase 16 guardrails：

- 先執行 `16-01` contract，再開始 dataset 或 runtime implementation。
- 不讓 hybrid、vector retrieval、rerank 或 eval strategy default-on。
- 不實作 `hybrid_rerank`、frontend trace UI、LLM-as-judge、answer faithfulness、citation quality scoring 或 eval dashboard，除非後續 ticket 明確要求。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 deployment 設定。
- Dataset expansion 只能使用公開虛構資料；若既有 sample documents 不足，必須停止並回報，不可自行加入真實或敏感資料。

16-01 contract status：

- Strategy label 固定為 `hybrid`，只作為 retrieval eval runner 的 optional strategy，不接 `/rag/query` 或 frontend UI。
- Candidate sources 固定為 existing keyword branch + optional vector branch；`vector_rerank` / `hybrid_rerank` 不屬於第一版 hybrid source。
- Dedupe key 優先使用 `(document_id, chunk_id)`；欄位不足時必須記錄 dedupe fallback metadata。
- Merge policy 固定為 deterministic `rank_based_fusion`，保留 branch rank / score，不直接相加 keyword score 與 vector similarity。
- Vector branch unavailable 時 fallback 到 keyword-only candidates，並記錄 branch failure / fallback reason，keyword baseline 不受影響。
- 16-01 validation：`rg -n "v0.16.0|Phase 16|hybrid retrieval|merge policy|dedupe" TODO.md docs/ROADMAP.md tasks/phase-16-hybrid-retrieval/16-01-hybrid-retrieval-contract.md` 通過；`git diff --check` 通過。

16-02 dataset status：

- `sample-data/eval/retrieval-eval.json` 已由 6 筆擴充到 12 筆。
- 新增 cases 只引用既有公開虛構 sample documents：`mock-invoice-aurora.txt` 與 `mock-contract-support.txt`。
- Tags 已覆蓋 `lexical_mismatch`、`multi_evidence`、`near_duplicate`、`cross_document_ambiguity` 與 `numeric_table_lookup`。
- Baseline keyword eval smoke 仍可在無 Ollama embedding、Qdrant 或 FastEmbed runtime 時執行。
- 16-02 validation：`scripts/test-backend.ps1` 通過；`scripts/retrieval-eval-smoke.ps1` 通過；`git diff --check` 通過。

16-03 hybrid eval status：

- Eval runner 已支援 explicit `hybrid` strategy，預設仍為 keyword baseline。
- `hybrid` 使用 existing keyword branch + optional vector branch，依 deterministic `rank_based_fusion` merge / dedupe candidates。
- Hybrid trace metadata 保留 branch ranks、branch scores、merged score、candidate counts、dedupe count、branch failures 與 fallback reason。
- Vector branch unavailable 時 fallback 到 keyword-only candidates，不讓 baseline eval 失敗，也不把 optional hybrid fallback 算成 eval failure。
- `scripts/retrieval-eval-smoke.ps1 -RunHybrid` 已可執行 optional hybrid eval smoke；本機 vector preflight 可用時已跑通，Hit Rate@K `0.5833`、MRR@K `0.5`、Recall@K `0.5833`、failure count `0`。
- 16-03 validation：`scripts/test-backend.ps1` 通過，`120 passed`；baseline `scripts/retrieval-eval-smoke.ps1` 通過，keyword Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`；optional `scripts/retrieval-eval-smoke.ps1 -RunHybrid` 通過；`git diff --check` 通過。

16-04 release sync status：

- Backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 已同步到 `0.16.0`。
- README、backend README、frontend README、TODO 與 ROADMAP 已補齊 `v0.16.0` release status。
- Baseline demo smoke 通過，version `0.16.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`。
- Baseline retrieval eval smoke 通過，Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`。
- Optional vector eval smoke 在本機 vector preflight 可用時通過，Hit Rate@K `0.5`、MRR@K `0.4167`、Recall@K `0.4583`、failure count `0`。
- Optional `vector_rerank` eval smoke 在本機 vector preflight 可用時通過，Hit Rate@K `0.5`、MRR@K `0.4167`、Recall@K `0.4583`、failure count `0`。
- Optional hybrid eval smoke 在本機 vector preflight 可用時通過，Hit Rate@K `0.5833`、MRR@K `0.5`、Recall@K `0.5833`、failure count `0`。
- `hybrid_rerank`、frontend trace UI、worker、DB、auth 與 deployment 仍留到後續 Phase。

## MVP v0.17.0 Retrieval Trace UI / Eval Visibility Backlog

- [x] `tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md`: 固定 frontend trace UI / eval visibility contract，涵蓋 keyword、vector、`vector_rerank`、`hybrid`、fallback 與 missing metadata display；文件 ticket，不 bump version。
- [x] 17-01 validation：`rg -n "v0.17.0|Phase 17|trace UI|hybrid|vector_rerank" TODO.md docs/ROADMAP.md tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-17-retrieval-trace-ui/17-02-frontend-retrieval-trace-panel.md`: 在既有 RAG result UI 顯示 retrieval trace panel，只讀既有 response，不新增 backend API。
- [x] 17-02 validation：`npm.cmd run build` 通過；Browser 檢查 `http://localhost:5173` RAG result trace panel 可顯示 baseline answer / retrieval source、candidate table、fallback state，且無水平溢出；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。
- [x] `tasks/phase-17-retrieval-trace-ui/17-03-eval-result-report-summary.md`: 改善 retrieval eval runner / smoke summary，讓 strategy metrics、fallback count 與 trace metadata 更適合 demo / README 摘錄。
- [x] 17-03 validation：`PATH="/c/Users/USER/AppData/Local/Programs/Python/Python312:/c/Users/USER/AppData/Local/Programs/Python/Python312/Scripts:$PATH" powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`121 passed`（僅 pytest cache 權限警告）；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional vector-backed smoke 未完成，因 backend upload preflight 在本機 data dir 建立 `uploads` 時遇到 Windows `PermissionError`，因此 local preflight 不完整。
- [x] `tasks/phase-17-retrieval-trace-ui/17-04-trace-ui-demo-release-sync.md`: 補齊 trace UI / eval visibility demo validation，並完成 `v0.17.0` release/version sync。
- [x] 17-04 validation：`PATH="/c/Users/USER/AppData/Local/Programs/Python/Python312:/c/Users/USER/AppData/Local/Programs/Python/Python312/Scripts:$PATH" powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`121 passed`（僅 pytest cache 權限警告）；`npm.cmd run build` 通過；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/demo-smoke-test.ps1` 通過，version `0.17.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional `-RunVector`、`-RunVectorRerank` 與 `-RunHybrid` 均通過，`vector_rerank` 在未安裝 FastEmbed 時記錄 fallback count `12` 與 fallback reason；Browser 檢查 `http://localhost:5173` trace panel 可顯示 `v0.17.0` health、candidate table 與 fallback state，且無水平溢出。
- [x] Phase 17 planning validation：`rg -n "v0.17.0|Phase 17|17-01|17-04|trace UI|eval visibility" TODO.md docs/ROADMAP.md tasks/phase-17-retrieval-trace-ui/*.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 17 goal：

- 把 Phase 13-16 已產生的 retrieval eval output、rerank metadata 與 hybrid trace metadata，轉成可展示、可閱讀、可驗證的 frontend / report visibility。
- 17-01 已固定 trace UI contract；17-02 已加入 frontend trace panel；17-03 已改善 eval reporting；17-04 已完成 `v0.17.0` version bump、release docs sync 與 demo / eval smoke validation。
- 保留 baseline keyword demo 與 optional vector / `vector_rerank` / `hybrid` eval smoke 可重跑。

Phase 17 guardrails：

- 先執行 `17-01` contract，再開始 frontend 或 reporting implementation。
- Frontend trace panel 只能讀既有 response，不得為 UI 新增 backend endpoint 或改 API contract。
- Missing metadata 必須 graceful hidden 或顯示清楚 fallback state，不得讓 keyword baseline demo 因缺少 optional metadata 失效。
- 不讓 hybrid、vector retrieval、rerank 或 eval strategy default-on。
- 不實作 `hybrid_rerank`、production eval dashboard、LLM-as-judge、answer faithfulness、citation quality scoring、query rewriting 或 BM25 dependency，除非後續 ticket 明確要求。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 deployment 設定。

## MVP v0.18.0 Hybrid Rerank Planning Backlog

- [x] `tasks/phase-18-hybrid-rerank-planning/18-01-hybrid-rerank-boundary-contract.md`: 規劃 `hybrid_rerank` candidate flow、disabled-by-default 邊界、trace metadata 與 fallback states；文件 ticket，不 bump version。
- [x] `tasks/phase-18-hybrid-rerank-planning/18-02-hybrid-rerank-eval-dataset-plan.md`: 規劃 future `hybrid_rerank` eval dataset case 類型與 metrics 摘要使用方式；文件 ticket，不 bump version。
- [x] `tasks/phase-18-hybrid-rerank-planning/18-03-hybrid-rerank-trace-report-plan.md`: 規劃 future `hybrid_rerank` trace / report visibility 與 missing metadata behavior；文件 ticket，不 bump version。
- [x] `tasks/phase-18-hybrid-rerank-planning/18-04-phase-18-demo-release-plan.md`: 規劃 future `hybrid_rerank` demo validation 與 release sync checklist；文件 ticket，不 bump version。
- [x] Phase 18 planning validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no|release sync" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過（僅顯示既有 Windows LF/CRLF 提示）。

Phase 18 goal：

- 只做 `hybrid_rerank` planning backlog，讓後續 implementation 能清楚區分 hybrid merge、rerank reordering、fallback metadata 與 demo / release validation。
- 本次規劃不修改 backend、frontend、sample data、eval runner、smoke script、版本號或 Docker Compose。
- 後續 implementation 已排入 Phase 19，目標版本號使用 `v0.19.0`。

Phase 18 guardrails：

- 18-01 到 18-04 都是 Markdown-only planning ticket，`Release Impact` 必須寫 `Version bump required: no`。
- 不實作 `hybrid_rerank` runtime、BM25 dependency、score fusion code、rerank invocation、backend API、frontend UI 或 production eval dashboard。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 deployment 設定。

18-01 boundary contract status：

- `hybrid_rerank` candidate flow 固定為 keyword branch + vector branch -> hybrid merge / dedupe -> optional rerank reordering。
- Strategy label 固定為 `hybrid_rerank`，後續 implementation 必須 explicit opt-in 且 disabled-by-default，不得改變 keyword baseline demo。
- Trace metadata 已規劃 run-level candidate counts、merge policy、dedupe key、rerank provider / model / status / latency、branch failures 與 fallback reason。
- Fallback states 已規劃 `vector_unavailable`、`vector_empty`、`merge_dedupe_partial`、`reranker_disabled` 與 `reranker_unavailable`。
- 18-01 validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過。

18-02 dataset plan status：

- Future dataset case types 已規劃 `lexical_heavy`、`semantic_heavy`、`branch_disagreement`、`rerank_improves_ordering`、`rerank_filters_distractor` 與 `rerank_fallback`。
- 後續 dataset update ticket 必須只使用公開虛構 sample documents；若既有 sample 不足，需停止並拆新 sample ticket。
- Metrics summary 邊界沿用 `fallback_count`、`trace_metadata_count`、`result_strategy_counts`、`fallback_reasons` 與既有 Hit Rate@K / MRR@K / Recall@K / latency / failure count。
- 18-02 validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|dataset|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過。

18-03 trace report plan status：

- Future visibility surfaces 已規劃 CLI summary、JSON output 與既有 frontend trace panel 的只讀顯示邊界。
- Report fields 已拆成 run-level、case-level 與 candidate-level，涵蓋 branch counts、merge policy、dedupe、rerank provider / status / score、fallback reason 與 candidate ordering。
- Missing metadata behavior 沿用 Phase 17：graceful hidden、`metadata unavailable` 或清楚 fallback state；不得把 branch score、merged score 與 rerank score 混成單一分數。
- 18-03 validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|trace|report|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過。

18-04 demo release plan status：

- Future validation checklist 已規劃 backend tests、frontend build、baseline demo smoke、baseline eval smoke、optional vector / `vector_rerank` / `hybrid` / future `hybrid_rerank` eval smoke 與 `git diff --check`。
- Future release sync files 已規劃 backend version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP；實作已順延到 Phase 19。
- Deferred items 已明確保留 production eval dashboard、Redis、NATS、worker、DB schema、auth、RBAC、deployment、LLM-as-judge、answer faithfulness、citation quality scoring、query rewriting 與 BM25 到後續 Phase。
- 18-04 validation：`rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no|release sync" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md` 通過；`git diff --check` 通過。

## MVP v0.19.0 Hybrid Rerank Runtime Backlog

- [x] `tasks/phase-19-hybrid-rerank-runtime/19-01-hybrid-rerank-eval-provider.md`: 實作 disabled-by-default `hybrid_rerank` eval provider，流程為 keyword branch + vector branch -> hybrid merge / dedupe -> rerank reordering。
- [x] 19-01 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Set-Location 'C:/Users/USER/Desktop/DocuRAG'; ./scripts/test-backend.ps1"` 通過，`125 passed`（僅 pytest cache 權限警告）；`rg -n "hybrid_rerank|HybridRerank|rerank_fallback_reason|strategy_label" backend/app/services/evaluation.py backend/tests/test_evaluation.py TODO.md docs/ROADMAP.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-19-hybrid-rerank-runtime/19-02-hybrid-rerank-smoke-flag.md`: 將 `hybrid_rerank` 接入 eval runner CLI 與 `scripts/retrieval-eval-smoke.ps1 -RunHybridRerank`。
- [x] 19-02 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Set-Location 'C:/Users/USER/Desktop/DocuRAG'; ./scripts/test-backend.ps1"` 通過，`125 passed`（僅 pytest cache 權限警告）；baseline `scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional `scripts/retrieval-eval-smoke.ps1 -RunHybridRerank` 已進入 vector preflight，但本機 Qdrant collection `docurag_chunks_v1` / Docker daemon 未啟動而停止，需先啟動 Qdrant 並重跑 `scripts/qdrant-collection-smoke.ps1`；`rg -n "RunHybridRerank|hybrid_rerank|retrieval-eval-result-hybrid-rerank" scripts backend README.md sample-data/eval/README.md TODO.md docs/ROADMAP.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-19-hybrid-rerank-runtime/19-03-hybrid-rerank-trace-report-sync.md`: 補齊 `hybrid_rerank` trace / report visibility，確保 branch score、merged score 與 rerank score 可區分。
- [x] 19-03 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Set-Location 'C:/Users/USER/Desktop/DocuRAG'; ./scripts/test-backend.ps1"` 通過，`126 passed`（僅 pytest cache 權限警告）；baseline `scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional `scripts/retrieval-eval-smoke.ps1 -RunHybridRerank` 仍因本機 Qdrant collection / Docker daemon 未啟動停在 vector preflight；`rg -n "hybrid_rerank|merged_score|rerank_score|fallback_count|trace_metadata_count" README.md backend/README.md frontend/README.md sample-data/eval/README.md backend/app/services/evaluation.py backend/tests/test_evaluation.py TODO.md docs/ROADMAP.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-19-hybrid-rerank-runtime/19-04-hybrid-rerank-demo-release-sync.md`: 重跑 final validation，確認 baseline / optional smoke 狀態，並完成 `v0.19.0` release/version sync。
- [x] 19-04 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`126 passed`（僅 pytest cache 權限警告），backend editable package 已同步為 `docurag-agentops-backend==0.19.0`；`npm.cmd run build` 於 `frontend/` 通過；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/demo-smoke-test.ps1` 通過，health version `0.19.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；baseline `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=12`、Hit Rate@K `0.6667`、MRR@K `0.4861`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `34`；optional `-RunVector`、`-RunVectorRerank`、`-RunHybrid` 與 `-RunHybridRerank` 均已執行 preflight，但本機 Qdrant collection `docurag_chunks_v1` 不可用而停止，需先啟動 Qdrant 並重跑 `scripts/qdrant-collection-smoke.ps1`；backend version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `0.19.0`。

Phase 19 goal：

- 將 Phase 18 planning 中的 `hybrid_rerank` 從規格落地成 optional eval runner strategy。
- 保留 keyword baseline、`vector`、`vector_rerank` 與 `hybrid` 既有行為，不讓 `hybrid_rerank` default-on。
- 只把 `hybrid_rerank` 接入 evaluation / smoke / trace reporting，不接 production dashboard 或 default chat path。

Phase 19 guardrails：

- 先執行 `19-01` provider flow，再接 smoke flag、trace report sync 與 final release sync。
- 不接 `/rag/query`、frontend live chat、production eval dashboard、backend API endpoint 或 default retrieval path。
- 不新增 BM25 dependency、query rewriting、LLM-as-judge、answer faithfulness scoring、citation quality scoring、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、Agent runtime、VLM parser、PDF rendering、production OCR pipeline、K8s 或 deployment 設定。
- `19-04` 才允許 `v0.19.0` version bump；`19-01` 到 `19-03` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

## MVP v0.20.0 Interview MVP Packaging Backlog

- [x] `tasks/phase-20-interview-mvp-packaging/20-01-interview-demo-doc-refresh.md`: 更新 README / demo script / PRD / architecture 的面試 demo 敘事，對齊 `v0.17.0` runtime、`v0.18.0` planning-only 與 `v0.19.0` `hybrid_rerank` implementation 狀態；文件 ticket，不 bump version。
- [x] 20-01 validation：`rg -n "v0.17.0|v0.18.0|v0.19.0|Phase 20|interview MVP|面試" README.md docs/demo-script.md docs/PRD.md docs/architecture.md TODO.md docs/ROADMAP.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-20-interview-mvp-packaging/20-02-sample-eval-coverage-expansion.md`: 補齊公開虛構 sample documents 與 retrieval eval cases，目標至少 5 份 sample documents、20 筆 eval cases；不改 retrieval algorithm。
- [x] 20-02 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`127 passed`（僅 pytest cache 權限警告）；baseline `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=20`、Hit Rate@K `0.7`、MRR@K `0.475`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `62`；`rg -n "case_count|20|sample documents|demo-safe|synthetic" sample-data docs/ROADMAP.md TODO.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-20-interview-mvp-packaging/20-03-demo-media-and-readme-polish.md`: 補齊 README 5 到 10 分鐘面試導覽、截圖或 GIF 等 demo media；不新增 production UI 或 API。
- [x] 20-03 validation：`npm.cmd run build` 於 `frontend/` 通過；Browser 檢查 `http://localhost:5173` local frontend demo view 通過，並產出 `docs/demo-media/frontend-overview.png`、`docs/demo-media/frontend-trace.png` 與 `docs/demo-media/eval-summary.png`；`rg -n "screenshot|GIF|demo media|interview demo|面試" README.md docs/demo-script.md docs/ROADMAP.md TODO.md` 通過；`git diff --check` 通過。
- [x] `tasks/phase-20-interview-mvp-packaging/20-04-final-interview-mvp-validation.md`: 重跑 final validation，確認 baseline / optional smoke 狀態，並完成 `v0.20.0` release/version sync。
- [x] 20-04 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`127 passed`（僅 pytest cache 權限警告），backend editable package 已同步為 `docurag-agentops-backend==0.20.0`；`npm.cmd run build` 於 `frontend/` 通過；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/demo-smoke-test.ps1` 通過，health version `0.20.0`、answer source `deterministic baseline`、retrieval source `keyword baseline`；baseline `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=20`、Hit Rate@K `0.7`、MRR@K `0.475`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `62`；optional `-RunVector`、`-RunVectorRerank` 與 `-RunHybrid` 均已執行 preflight，但本機 Qdrant collection `docurag_chunks_v1` 不可用而停止，需先啟動 Qdrant 並重跑 `scripts/qdrant-collection-smoke.ps1`；backend version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `0.20.0`；`rg` 與 `git diff --check` 通過。

Phase 20 goal：

- 把已完成的受控 MVP 包裝成面試可展示版本，讓面試官能快速看懂 upload -> OCR -> RAG -> citation -> trace -> eval 的價值。
- 補齊 `goal.md` 成功標準中與面試展示直接相關的 sample coverage、eval coverage、demo script 與截圖 / GIF。
- 只做 demo readiness / packaging / validation，不把企業級 runtime scope 偷渡進來。

Phase 20 guardrails：

- 先執行 `20-01` 文件刷新，再做 sample/eval 擴充、demo media 與 final release sync。
- 不實作 production eval dashboard、BM25 dependency、query rewriting、LLM-as-judge、answer faithfulness scoring 或 citation quality scoring。
- 不新增 backend API、frontend route、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、Agent runtime、VLM parser、PDF rendering、production OCR pipeline、K8s 或 deployment 設定。
- `20-04` 才允許 `v0.20.0` version bump；`20-01` 到 `20-03` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

## MVP v0.20.1 Frontend Demo UI Polish

- [x] `tasks/phase-20-interview-mvp-packaging/20-05-frontend-demo-ui-polish.md`: 改善既有 Vue demo UI 的第一屏資訊層次、workflow 狀態、卡片 / 表格 / trace 視覺質感；不新增 route、API、外部依賴或 backend runtime。
- [x] 20-05 validation：`npm.cmd run build` 於 `frontend/` 通過；Browser 檢查 `http://localhost:5173/` local frontend demo view，desktop viewport 無 horizontal overflow；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] 20-05 follow-up：移除後台知識庫管理的長段階段說明，將資料匯入狀態改為預設收合，並將 Agent 執行紀錄主要文案、狀態、工具名、觀察結果與常見回答格式中文化；不新增 route、API、外部依賴或 backend runtime。
- [x] `tasks/phase-20-interview-mvp-packaging/20-06-readme-demo-media-refresh.md`: 用 20-05 polish 後的 local frontend demo 與 baseline eval summary 重新覆蓋 README 引用的三張 demo 圖；不新增 route、API、外部依賴或 backend runtime。
- [x] 20-06 validation：`npm.cmd run build` 於 `frontend/` 通過；Browser 重新截取 `docs/demo-media/frontend-overview.png` 與 `docs/demo-media/frontend-trace.png`；baseline `scripts/retrieval-eval-smoke.ps1` 通過，keyword summary `case_count=20`、Hit Rate@K `0.7`、MRR@K `0.475`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `62`；重新產生 `docs/demo-media/eval-summary.png`；`rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-07-frontend-zh-tw-copy-polish.md`: 將 frontend demo 的 hero、summary cards、workflow、panel、按鈕、表格、empty states、常見狀態與瀏覽器標題中文化；保留 API endpoint、JSON key、provider / model 名稱與技術 token 原文，不新增 route、API、外部依賴或 backend runtime。
- [x] 20-07 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend demo view 檢查標題、主要中文 panel、舊英文可見標籤與 desktop horizontal overflow 通過；ticket 指定 `rg` 已執行，剩餘命中僅 `listDocuments` / `refreshDocuments` 程式識別符；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-08-readme-zh-tw-demo-media-refresh.md`: 用 20-07 中文化後的 local frontend demo 重新覆蓋 README 引用的 `frontend-overview.png` 與 `frontend-trace.png`；不新增 README 圖片路徑、route、API、外部依賴或 backend runtime。
- [x] 20-08 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend demo view 重新截取 `docs/demo-media/frontend-overview.png` 與 `docs/demo-media/frontend-trace.png`，檢查中文標題 / panel / trace、舊英文可見標籤與 desktop horizontal overflow 通過；`rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-09-frontend-chat-first-demo.md`: 將 frontend demo 第一屏調整為客服式 RAG chat，upload / OCR / metadata 保留在同頁後台知識庫管理區；不新增 route、API、外部依賴或 backend runtime。
- [x] 20-09 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend demo view 檢查第一屏 chat-first、後台區塊仍可用、RAG query 後 answer / citations / trace / retrieved chunks 可見、desktop horizontal overflow 為 `0`；ticket 指定 `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-10-readme-chat-first-demo-refresh.md`: 更新 root README 的 chat-first recommended demo flow、前台 / 後台分工與 baseline / optional path 說明；不修改 frontend、backend、sample data 或 demo media。
- [x] 20-10 validation：ticket 指定 `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-11-frontend-minimal-chat-upload.md`: 將 frontend demo 收斂成兩個使用者可見入口：客服問答與文件上傳；OCR、indexing、document list、raw JSON、retrieval trace table 與 eval metrics 留在 backend API / CLI / smoke scripts。
- [x] 20-11 validation：`npm.cmd run build` 於 `frontend/` 通過；Browser 檢查 `http://localhost:5174/` local frontend demo view 只有客服問答與文件上傳，沒有 OCR panel、document list、metadata JSON、API response JSON、trace table，desktop horizontal overflow 為 `0`；ticket 指定 `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/phase-20-interview-mvp-packaging/20-12-default-llm-answer.md`: 將 local demo `/rag/query` 預設改為嘗試 Ollama `qwen3.5:4b` answer generation，Ollama 不可用時保留 retrieved OCR chunks fallback，並保留 `DOCURAG_LLM_PROVIDER=` 關閉 path。
- [x] 20-12 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`129 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 通過，answer source 為 `LLM unavailable fallback`、retrieval source 為 `keyword baseline`；ticket 相關 `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。

Phase 20.1 goal：

- 讓面試 demo 的 frontend 第一眼就是產品入口：使用者只看到客服式 RAG chat 與文件上傳，OCR、chunking、indexing、trace、raw JSON 與 eval metrics 都回到 backend API / CLI / smoke scripts。
- 只做展示質感與 README demo media 加分，不改 API contract、不新增功能範圍、不 bump version。

Phase 20.1 guardrails：

- 不新增 production eval dashboard、strategy comparison page、live eval runner、backend API、frontend route、外部依賴、DB、auth、Redis、NATS、worker、Agent runtime 或 deployment。
- 不改 retrieval algorithm、eval runner、smoke script、sample data 或 backend service。

## MVP v0.21.0 Real GPU OCR Interview Demo Path

- [x] `tasks/phase-21-real-gpu-ocr-demo/21-01-real-gpu-ocr-frontend-flow.md`: 將 frontend upload 預設改為 provider-selected `POST /documents/{document_id}/ocr` real GPU OCR-first，real OCR 失敗時保留已上傳文件並提供手動 mock OCR fallback。
- [x] 21-01 validation：`npm.cmd run build` 於 `frontend/` 通過；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`129 passed`（僅 pytest cache 權限警告）；baseline `scripts/demo-smoke-test.ps1` 通過，health version `0.21.0`、answer source `ollama/qwen3.5:4b`、retrieval source `keyword baseline`；以臨時 `DOCURAG_OCR_PROVIDER=paddleocr` backend 跑 `scripts/demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8012 -RunRealOcr` 通過，provider-selected OCR completed 且 metadata OK；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

Phase 21 goal：

- 讓面試主線不再看起來像 mock OCR demo；frontend upload 預設展示你已經有的 provider-selected PaddleOCR GPU flow。
- 保留 mock OCR 作為無 GPU / runtime 失敗時的明確手動 fallback，而不是靜默替代。
- 同步 `v0.21.0` 版本、README、backend README、frontend README、TODO、ROADMAP 與 demo script。

Phase 21 guardrails：

- 不修改 PaddleOCR provider、engine lifecycle、模型設定、OCR normalization 或 backend OCR API contract。
- 不新增 PDF rendering、image preprocessing、VLM parser、多頁 production OCR pipeline、DB、Auth、RBAC、Redis、NATS、worker、Agent runtime 或 deployment。

## MVP v0.22.0 RAG Query Hardening

- [x] `tasks/phase-22-rag-query-hardening/22-01-keyword-query-normalization.md`: 強化 `KeywordRagProvider` 的中文 tokenization 與 demo-safe alias，讓 `付款期限是什麼？` 可在 keyword baseline 命中 `Payment terms: Net 15`；同步修正 frontend / README 文案，不宣稱 backend 已有正式知識庫 ingestion / indexing pipeline。
- [x] 22-01 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`131 passed`（僅 pytest cache 權限警告）；`npm.cmd run build` 於 `frontend/` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，health version `0.22.0`、answer source `LLM unavailable fallback`、retrieval source `keyword baseline`；ticket `rg` 與 knowledge-base copy guard `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。

Phase 22 goal：

- 修正中文或近似問法無法觸發 RAG retrieval 的 demo 體感問題。
- 保留 default `/rag/query` 為 keyword baseline，不把 vector、hybrid、rerank 或 query rewrite 提前變成預設路徑。
- 同步 `v0.22.0` 版本、README、backend README、frontend README、TODO 與 ROADMAP。

Phase 22 guardrails：

- 不新增 embedding、Qdrant、BM25、rerank、hybrid retrieval、`hybrid_rerank` default chat path 或新外部依賴。
- 不新增 LLM-as-judge、answer faithfulness scoring、citation quality scoring、DB、Auth、RBAC、Redis、NATS、worker、PDF rendering、image preprocessing 或 production OCR pipeline。

## MVP v0.23.0 Viewer Chat / Admin Ingestion Role Split

- [x] `tasks/phase-23-role-split-demo/23-01-role-boundary-contract.md`: 固定 Phase 23 產品邊界，明確區分前台 Viewer Chat 與後台 Admin / Analyst Ingestion；文件 ticket，不 bump version。
- [x] `tasks/phase-23-role-split-demo/23-02-viewer-chat-only-surface.md`: 將 frontend 預設入口收斂為 Viewer Chat-only，不在前台主畫面顯示 upload / OCR / mock fallback。
- [x] `tasks/phase-23-role-split-demo/23-03-admin-ingestion-surface.md`: 建立明確的 Admin / Analyst 知識庫管理 surface，放置文件上傳、provider-selected OCR、狀態與手動 fallback。
- [x] `tasks/phase-23-role-split-demo/23-04-role-split-demo-release-sync.md`: 重跑 final validation，並在 Phase 23 完成時執行 `v0.23.0` release/version sync。
- [x] 23-01 validation：README、frontend README、demo script、architecture、ROADMAP 與 TODO 已固定 Viewer Chat / Admin Ingestion 產品邊界；文件明確說明 OCR 是 backend ingestion layer，不是前端直接對圖片聊天；保留 local JSON、local chunks、manual / explicit vector path、無正式 parser / worker / DB / auth 的限制；ticket `rg` 與 `git diff --check` 通過。
- [x] 23-02 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend 檢查首頁無文件上傳 / OCR / mock fallback controls，Viewer Chat query 後仍顯示 answer、answer source、retrieval source 與 citation summary；ticket `rg` 與 `git diff --check` 通過。
- [x] 23-03 validation：`npm.cmd run build` 於 `frontend/` 通過；local frontend 檢查 Viewer Chat 首屏無 upload / OCR controls，後台 Admin / Analyst ingestion surface 可看到文件上傳、provider-selected OCR flow、mock fallback 與 document / OCR / local chunks 狀態；baseline `scripts/demo-smoke-test.ps1` 通過；ticket `rg` 與 `git diff --check` 通過。
- [x] 23-04 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`131 passed`（僅 pytest cache 權限警告）；`npm.cmd run build` 於 `frontend/` 通過；baseline `scripts/demo-smoke-test.ps1` 通過，health version `0.23.0`、answer source `LLM unavailable fallback`、retrieval source `keyword baseline`；Browser 檢查 Viewer Chat first、Admin / Analyst ingestion surface 分離，桌面與手機寬度無 horizontal overflow；ticket `rg` 與 `git diff --check` 通過。

Phase 23 goal：

- 將產品入口拆成兩條清楚路徑：Viewer 只進入 Chat 查詢已建立的知識庫；Admin / Analyst 才進入後台知識庫管理流程執行上傳、OCR 與 ingestion 狀態檢查。
- 修正目前 demo UI 把「查詢使用者」與「知識庫管理者」混在同一畫面的語意問題。
- 保留目前 local MVP 能力：backend upload、provider-selected OCR、local chunks、keyword baseline、citation 與 optional demo / eval paths。

Phase 23 guardrails：

- 不新增真實登入、RBAC、role guard、multi-user permission、PostgreSQL、Redis、NATS、worker、async queue 或 database schema。
- 不實作 VLM parser、PDF rendering、多頁 production OCR pipeline、automatic Qdrant indexing、default-on vector / hybrid / rerank chat path、Agent runtime 或 deployment。
- 不把 Admin / Analyst 後台入口說成正式權限系統；本階段只拆產品表面與 demo 工作流。
- `23-04` 才允許 `v0.23.0` version bump；`23-01` 到 `23-03` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

## MVP v0.24.0 VLM / Parser Minimal MVP

- [x] `tasks/phase-24-vlm-parser-mvp/24-01-parser-contract.md`: 固定 VLM-compatible parser contract，定義 OCR text -> invoice structured fields、parser status、source trace 與 fallback metadata；文件 ticket，不 bump version。
- [x] `tasks/phase-24-vlm-parser-mvp/24-02-invoice-parser-service.md`: 實作 deterministic invoice parser service，從既有 OCR text 抽取 invoice number、date、total amount、currency 等 MVP 欄位。
- [x] `tasks/phase-24-vlm-parser-mvp/24-03-document-fields-api.md`: 新增 `POST /documents/{document_id}/parse` 與 `GET /documents/{document_id}/fields`，並保存 parser result 到 local JSON metadata store。
- [x] `tasks/phase-24-vlm-parser-mvp/24-04-frontend-fields-surface.md`: 在 Admin / Analyst ingestion surface 顯示 parser status 與 structured fields 摘要，Viewer Chat 預設入口不顯示 parse / upload / OCR 操作。
- [x] `tasks/phase-24-vlm-parser-mvp/24-05-parser-demo-release-sync.md`: 重跑 final validation，補齊 parser demo 文件與 smoke，並在 Phase 24 完成時執行 `v0.24.0` release/version sync。

Phase 24 goal：

- 補上 JD 中「OCR / VLM 流程、複雜單據解析與結構化資料提取」的可展示切片。
- 先完成 VLM-compatible contract 與 deterministic invoice parser fallback，讓 demo 可穩定展示 OCR -> structured fields。
- 保留 future VLM / LLM parser 替換位置，但不把真正 vision model runtime 塞進第一個 parser MVP。

Phase 24 guardrails：

- 不新增真正 VLM、Ollama vision call、OpenAI-compatible VLM、LLM parser 或新外部依賴。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、Agent runtime、K8s 或 deployment 設定。
- 不修改 PaddleOCR provider、OCR model、OCR preprocessing、RAG retrieval、eval runner、Qdrant indexing 或 default chat path。
- 不實作人工修正欄位、欄位版本紀錄、audit log、表格完整重建、PDF rendering、多頁 production OCR pipeline 或 production parser dashboard。
- 不把 structured fields 接成 SQL query tool、Agent tool 或 default vector metadata filtering。
- `24-05` 才允許 `v0.24.0` version bump；`24-01` 到 `24-04` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

24-01 contract status：

- 已在 `docs/api.md` 與 `docs/architecture.md` 固定 `DocumentFields`、`ExtractedField`、`ParserResult`、parser status、source trace、fallback metadata、`POST /documents/{document_id}/parse` 與 `GET /documents/{document_id}/fields` 草案。
- Parser source 明確區分 Phase 24 MVP 的 deterministic invoice parser fallback、future text-only LLM parser 與 future VLM parser；目前不宣稱 production VLM parser，也不 bump version。
- [x] 24-01 validation：`rg -n "v0.24.0|Phase 24|Parser|VLM-compatible|DocumentFields|ExtractedField|fallback_reason" README.md TODO.md docs/ROADMAP.md docs/api.md docs/architecture.md tasks/phase-24-vlm-parser-mvp/24-01-parser-contract.md` 通過；`git diff --check` 通過（僅顯示 Windows `LF will be replaced by CRLF` 提示）。

24-02 parser service status：

- 已新增 `DocumentFields`、`ExtractedField`、`ParserResult` 與 `ParserStatus` schema，並建立 `DeterministicInvoiceParser` 作為 future VLM / LLM parser 的 fallback。
- Parser 只使用既有 OCR text / OCR lines，保留 `source_text`、`source_page`、`source_bbox`、`confidence`、`parser_source` 與 `fallback_reason`；缺欄位會回傳 missing metadata，不硬填假值。
- Unit tests 已覆蓋 sample invoice OCR text、missing field、中文標籤、TWD / 千分位金額與 OCR 未完成失敗案例；本 ticket 不新增 parse API、frontend UI、外部依賴或 version bump。
- [x] 24-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`135 passed`（僅 pytest cache 權限警告）；`rg -n "DocumentFields|ExtractedField|ParserResult|document_parser|fallback_reason" backend/app backend/tests TODO.md docs/ROADMAP.md tasks/phase-24-vlm-parser-mvp/24-02-invoice-parser-service.md` 通過；`git diff --check` 通過。

24-03 fields API status：

- 已新增 `POST /documents/{document_id}/parse` 與 `GET /documents/{document_id}/fields`，並將 parser result 保存到既有 local JSON metadata store 的 `parser_result`。
- `ProcessingStatus` 已加入 parser step，`ProcessingJobType.PARSER` 記錄明確 parse request；parser failure 不覆蓋 OCR / indexing 狀態，也不觸發 vector indexing、RAG ingestion、Qdrant upsert 或 eval run。
- API tests 已覆蓋 pending fields lookup、未 OCR parse failure、OCR 後 parse、保存後 fields lookup、storage reload 後 lookup、document not found 與 missing fields metadata。
- [x] 24-03 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`143 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 通過，health version `0.23.0`、answer source `ollama/qwen3.5:4b`、retrieval source `keyword baseline`；`rg -n "/parse|/fields|ParserResult|DocumentFields|fallback_reason" backend/app backend/tests docs/api.md TODO.md docs/ROADMAP.md tasks/phase-24-vlm-parser-mvp/24-03-document-fields-api.md` 通過；`git diff --check` 通過。

24-04 frontend fields surface status：

- 已在 Admin / Analyst ingestion surface 顯示 parser status、欄位解析操作、structured fields 摘要、confidence、source text、missing fields 與 failed parser state。
- Viewer Chat 預設入口仍只提供 RAG query，不顯示 upload、OCR、parse 或 ingestion 操作；UI 不宣稱 production VLM parser 或正式 RBAC。
- `frontend/README.md` 已補充 Phase 24 deterministic parser frontend slice 與 structured fields / `GET /fields` 檢查方式，並保留 production VLM parser / worker / DB 非目標說明。
- [x] 24-04 validation：`npm.cmd run build` 通過；Browser 檢查 `http://localhost:5173` desktop 與 390px mobile 通過，Viewer Chat first 不顯示 parse / upload / OCR 操作，Admin / Analyst ingestion surface 可觸發欄位解析並顯示 `AUR-2026-051`、vendor、total、confidence 與 source text，且無 horizontal overflow；`rg -n "structured fields|欄位解析|Parser|parse|fields|Viewer Chat|Admin / Analyst" frontend/src frontend/README.md TODO.md docs/ROADMAP.md tasks/phase-24-vlm-parser-mvp/24-04-frontend-fields-surface.md` 通過；`git diff --check` 通過。

24-05 parser demo release sync status：

- 已完成 `v0.24.0` version sync：backend package / app version、frontend package / lock / fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 已同步。
- `README.md`、`backend/README.md`、`frontend/README.md`、`docs/demo-script.md`、`TODO.md` 與 `docs/ROADMAP.md` 已補齊 parser demo wording；文件明確說明 Phase 24 是 deterministic parser MVP / VLM-compatible contract，不是 production VLM parser、LLM parser、worker、DB、Auth/RBAC、Agent runtime 或 deployment。
- `scripts/demo-smoke-test.ps1` 已加入 upload -> OCR mock -> parser -> fields lookup -> baseline RAG query 驗證，並檢查 `/health` version `0.24.0`、parser source、invoice number、vendor、total、currency 與 source text。
- [x] 24-05 validation：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`143 passed`（僅 pytest cache 權限警告）；`npm.cmd run build` 通過；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/demo-smoke-test.ps1` 通過，health version `0.24.0`、parser fields `AUR-2026-051` / `1248.5 USD`、answer source `LLM unavailable fallback`、retrieval source `keyword baseline`；Browser 檢查 `http://localhost:5173` desktop 與 390px mobile 通過，Viewer Chat first 不顯示 parse / upload / OCR，Admin / Analyst ingestion surface 顯示 parser status、欄位解析操作、`AUR-2026-051` 與 structured fields 摘要，且無 horizontal overflow；`rg -n "v0.24.0|Phase 24|Parser|structured fields|欄位解析|VLM-compatible|DocumentFields|ExtractedField" README.md backend/README.md frontend/README.md docs/demo-script.md docs/ROADMAP.md TODO.md backend/app frontend/src tasks/phase-24-vlm-parser-mvp` 通過；`git diff --check` 通過。

## MVP v0.25.0 Agent Tool-use Minimal MVP

- [x] `tasks/phase-25-agent-tool-use-mvp/25-01-agent-boundary-contract.md`: 固定 Agent MVP boundary、allowlisted tools、deterministic planner、run / step / tool call / observation / final answer trace schema；文件 ticket，不 bump version。
- [x] `tasks/phase-25-agent-tool-use-mvp/25-02-agent-tool-adapters.md`: 實作 demo-safe allowlisted tool adapters：`get_document_fields`、`search_documents`、`summarize_invoice_fields`，只封裝既有 structured fields 與 retrieval 能力。
- [x] `tasks/phase-25-agent-tool-use-mvp/25-03-agent-run-api.md`: 新增 deterministic Agent run API，支援 `POST /agent/run` 與 `GET /agent/runs/{run_id}`，並輸出 plan、tool calls、observations、final answer 與 citations。
- [x] `tasks/phase-25-agent-tool-use-mvp/25-04-frontend-agent-trace-surface.md`: 在 demo UI 新增 Agent trace surface，展示 plan -> tool calls -> observations -> final answer + citations；Viewer Chat 預設入口保持不變。
- [x] `tasks/phase-25-agent-tool-use-mvp/25-05-agent-demo-release-sync.md`: 補齊 Agent demo validation、文件同步與 `v0.25.0` release/version bump。

Phase 25 goal：
- 補上 JD 中「AI Agent 架構、Skill / Tool-use 與 Task Planning」的 demo 證據。
- 把 Phase 24 structured fields、既有 RAG retrieval 與 citation 串成 deterministic tool-use flow。
- 讓 demo 展示 plan -> tool calls -> observations -> final answer + citations，並維持 production guardrails。

Phase 25 guardrails：
- 不新增 LLM autonomous planner、OpenAI function calling、Ollama planning call、streaming agent 或新外部依賴。
- 不新增任意 SQL、PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、role guard、project permission 或 multi-user isolation。
- 不允許 Agent 執行 delete、reindex、file system command、shell command、任意 tool execution 或 destructive operation。
- 不修改 parser extraction、OCR provider、RAG ranking、eval runner、Qdrant indexing 或 default Viewer Chat path。
- 不把 Agent trace surface 說成 production Agent dashboard 或正式權限系統。
- `25-05` 才允許 `v0.25.0` version bump；`25-01` 到 `25-04` 若未形成完整 release artifact，必須寫 `Version bump required: no`。

25-01 agent boundary contract status：

- 已在 `docs/api.md` 定義 Phase 25 Agent Tool-use contract：`AgentRun`、`AgentStep`、`AgentToolCall`、observation、final answer、citations、trace metadata 與 future `POST /agent/run` / `GET /agent/runs/{run_id}` endpoint boundary。
- 已在 `docs/architecture.md` 固定 Agent MVP 只能使用 deterministic planner 與 allowlisted read-only tools：`get_document_fields`、`search_documents`、`summarize_invoice_fields`。
- 文件明確禁止任意 SQL、任意工具執行、delete、reindex、shell / file system command、DB、RBAC、worker、Redis / NATS 與 production autonomous Agent 宣稱。
- 本 ticket 只改 Markdown，不 bump version；完整 runtime 與 `v0.25.0` release sync 留給 `25-02` 到 `25-05`。
- [x] 25-01 validation：`rg -n "v0.25.0|Phase 25|Agent|tool-use|get_document_fields|search_documents|summarize_invoice_fields|deterministic planner|allowlisted" README.md TODO.md docs/ROADMAP.md docs/api.md docs/architecture.md tasks/phase-25-agent-tool-use-mvp/25-01-agent-boundary-contract.md` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。

25-02 agent tool adapters status：

- 已新增 `backend/app/schemas/agent.py` 與 `backend/app/services/agent_tools.py`，固定 `AgentToolCall`、tool observation、tool status 與 allowlisted tool output shape。
- 已實作 read-only `get_document_fields`、`search_documents` 與 `summarize_invoice_fields` adapters，只讀既有 local JSON parser result 與既有 RAG / keyword retrieval path，不執行任意 SQL、delete、reindex、shell / file system command 或 destructive operation。
- Backend tests 已覆蓋有 fields、缺 parser result、search hit、search miss、tool error 與 deterministic invoice summary。
- 本 ticket 不新增 Agent run API、frontend UI、LLM planner、DB、RBAC、worker、Redis / NATS 或新外部依賴；完整 release sync 留給 `25-05`。
- [x] 25-02 validation：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`149 passed`（僅 pytest cache 權限警告）；ticket 指定 `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

25-03 agent run API status：

- 已新增 `POST /agent/run` 與 `GET /agent/runs/{run_id}`，用 deterministic planner 串接 allowlisted `get_document_fields`、`search_documents` 與 `summarize_invoice_fields`。
- Agent run result 會保存到 local JSON metadata store `agent_runs.json`，lookup endpoint 只讀保存結果，不重跑 planner 或 tools。
- Backend tests 已覆蓋 successful run、missing parser fields、search fallback、run lookup、invalid document 與 missing run lookup。
- 本 ticket 不新增 frontend UI、LLM autonomous planner、OpenAI function calling、Ollama planning call、streaming、DB、RBAC、worker、Redis / NATS、destructive tools 或新外部依賴；完整 release sync 留給 `25-05`。
- [x] 25-03 validation：`python -m pytest backend/tests/test_agent.py -q` 通過，`6 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` 通過，`155 passed`（僅 pytest cache 權限警告）；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 通過，health version `0.24.0`、parser fields `AUR-2026-051` / `1248.5 USD`、RAG query OK；ticket 指定 `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

25-04 frontend agent trace surface status：

- 已在 Admin / Analyst ingestion surface 新增 Agent trace panel，可用 demo-safe task、document 與 query 呼叫 `POST /agent/run`。
- Agent trace surface 會顯示 plan、tool calls、observation、final answer、citations、trace metadata 與 fallback state；Viewer Chat 預設入口仍不顯示 upload、OCR、parse 或 Agent operations。
- 本 ticket 不新增 frontend route、auth / RBAC、role guard、project permission、LLM autonomous planner、streaming UI、worker、DB、tool console 或 production Agent dashboard。
- [x] 25-04 validation：`npm.cmd run build` 通過；Browser 檢查 `http://localhost:5176`（臨時 backend `http://127.0.0.1:8003`）通過，Viewer Chat first 不顯示 Agent trace / Run Agent / upload 操作，Admin / Analyst Agent trace surface 可執行成功 run 並顯示 final answer / citations / tool trace，fallback run 顯示 `no_retrieved_chunks`，desktop 1280px 與 mobile 390px 均無 horizontal overflow；ticket 指定 `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

25-05 agent demo release sync status：

- 已完成 `v0.25.0` version sync 實作：backend package / app version、frontend package / lock / fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 已同步。
- `scripts/demo-smoke-test.ps1` 已加入 upload -> OCR mock -> parser -> fields lookup -> Agent run -> Agent lookup -> baseline RAG query 驗證，並檢查 deterministic planner、`allowlisted_read_only` tool policy、三個 allowlisted tools、final answer 與 citations。
- `README.md`、`backend/README.md`、`frontend/README.md`、`docs/demo-script.md`、`TODO.md` 與 `docs/ROADMAP.md` 已補齊 Agent tool-use demo wording；文件明確說明 Phase 25 是 deterministic planner + allowlisted tools，不是 production autonomous Agent、LLM planner、任意 SQL、正式 RBAC、worker、DB 或 deployment。
- [x] 25-05 validation：backend tests 通過，`155 passed`（僅 pytest cache 權限警告）；frontend build 通過；baseline demo smoke 通過，health version `0.25.0`，Agent run / lookup OK，RAG query OK；Browser 桌面檢查通過，Viewer Chat first、Admin / Analyst ingestion Agent trace surface、`Run Agent` success 與無 horizontal overflow 已確認；本批 final `rg` 與 `git diff --check` 已重跑通過。

## MVP v0.26.0 Real VLM Parser Provider Spike

- [x] `tasks/phase-26-vlm-parser-provider-spike/26-01-vlm-provider-decision.md`: 固定 VLM provider env、input / output contract、fallback policy 與 Agent 承接方式；文件 ticket，不 bump version。
- [x] `tasks/phase-26-vlm-parser-provider-spike/26-02-vlm-input-resolver.md`: 新增 demo-safe image input resolver，只解析既有上傳檔案，不做 PDF rendering 或 VLM call。
- [x] `tasks/phase-26-vlm-parser-provider-spike/26-03-vlm-parser-adapter.md`: 新增 VLM-first `vlm_invoice` parser adapter，輸出沿用 Phase 24 `DocumentFields` schema。
- [x] `tasks/phase-26-vlm-parser-provider-spike/26-04-parser-source-comparison.md`: 在 API / trace 顯示 `deterministic_invoice` vs `vlm_invoice` 的 parser source、fallback reason、confidence 與 source input。
- [x] `tasks/phase-26-vlm-parser-provider-spike/26-05-vlm-parser-demo-release-sync.md`: 補齊 VLM parser demo validation、文件同步與 `v0.26.0` release/version bump。

Phase 26 goal：
- 補上 JD 中「多模態與 OCR：熟悉 VLM 與 OCR 流程，能處理複雜單據解析與結構化資料提取」的可展示切片。
- 承接 Phase 24 parser schema 與 Phase 25 Agent tool-use：VLM parser 產生 structured fields，Agent `get_document_fields` 讀取保存結果。
- 以 VLM-first provider spike 展示 provider boundary、fallback、trace 與 demo-safe validation；`deterministic_invoice` 只作 fallback / debug override，不再是 Phase 26 後的預設路徑。

Phase 26 guardrails：
- 不新增 production VLM parser、OpenAI SDK、streaming、function calling 或新外部依賴；Phase 26 的 default-on 只代表 demo parser path 預設 VLM-first。
- 不新增 PDF rendering、image preprocessing、layout analysis、多頁 production parser pipeline、table reconstruction、人工修正 workflow 或 parser dashboard。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、Agent permission model、K8s 或 deployment 設定。
- 不修改 Phase 25 Agent planner / tool allowlist；Agent 不直接呼叫 VLM，只透過 `get_document_fields` 消費 parser result。
- 不修改 RAG ranking、eval runner、Qdrant indexing 或 default Viewer Chat path。
- `26-05` 才允許 `v0.26.0` version bump；`26-01` 到 `26-04` 若未形成完整 release artifact，必須寫 `Version bump required: no`。
- 後續執行 Phase 26 runtime ticket 時，不得為了維持舊 demo 相容而讓 deterministic parser 繼續當預設；VLM provider unavailable / timeout / invalid response 時才 fallback。

26-01 VLM provider decision status：

- 已在 `docs/api.md` 定義 `DOCURAG_VLM_PROVIDER`、`DOCURAG_VLM_BASE_URL`、`DOCURAG_VLM_MODEL`、`DOCURAG_VLM_TIMEOUT_SECONDS`、`DOCURAG_VLM_MIN_CONFIDENCE` 與 `DOCURAG_PARSER_SOURCE`。
- 已在 `docs/api.md` / `docs/architecture.md` 固定 VLM-first parser input / output contract、fallback chain、confidence metadata 與 Agent `get_document_fields` 承接方式。
- 本 ticket 只改 Markdown，不 bump version；完整 runtime 與 `v0.26.0` release sync 留給 `26-02` 到 `26-05`。

26-02 VLM input resolver status：

- 已新增 `VlmInputResolver` / `VlmInputDescriptor` building block，從既有 document upload metadata 解析 `data/uploads/` 內的 demo-safe `.png` / `.jpg` / `.jpeg`。
- Resolver 對 `unsupported_file`、`missing_file`、`unsafe_path` 與 `file_not_readable` 回傳明確 fallback reason，不呼叫 VLM、不改 `POST /documents/{document_id}/parse` 行為。
- Focused tests 已覆蓋 supported image、missing file、unsupported extension 與 unsafe path。

26-03 VLM parser adapter status：

- 已新增 VLM-first `VlmInvoiceParser`、Ollama-style local HTTP provider、disabled provider 與 parser dependency routing；`DOCURAG_PARSER_SOURCE=deterministic_invoice` 只作 explicit debug / validation override。
- VLM success 會輸出既有 `DocumentFields` / `ParserResult` schema，並標記 `parser_source=vlm_invoice`；provider unavailable、timeout、invalid response、missing fields 或低 confidence 時 fallback 到 `deterministic_invoice`。
- Focused tests 已覆蓋 VLM success、provider unavailable fallback、timeout / provider failure、invalid response、missing fields 與 explicit deterministic override。

26-04 parser source comparison status：

- Parser response trace 已可透過 `parser_route`、`fallback_chain`、`fallback_reason`、`deterministic_fallback_reason`、`confidence_summary` 與 source input metadata 區分 `vlm_invoice` vs `deterministic_invoice`。
- VLM fallback 時 top-level `ParserResult.fallback_reason` 顯示 VLM / resolver failure reason；deterministic fallback 自身 missing metadata 保留於 trace，不新增平行 schema。
- Backend tests 已覆蓋 VLM success trace、VLM fallback trace 與 explicit deterministic override trace；`frontend/README.md` 已補充這是 demo visibility，不是 production parser comparison dashboard。

26-05 VLM parser demo release sync status：

- 已同步 backend package / app version、frontend package / lock / fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `0.26.0`。
- `scripts/demo-smoke-test.ps1` 現在驗證 text input 的 VLM-first fallback path：`fallback_reason=unsupported_file`、`fallback_chain=vlm_invoice -> deterministic_invoice`，並確認 Agent `get_document_fields` observation 可讀到 parser source / fallback reason。
- 新增 `DOCURAG_VLM_PROVIDER=fake` demo / smoke stub，用於 image input 的 `vlm_invoice` success path；Agent tool contract 不變，仍只讀保存後的 parser result。
- README、backend README、frontend README、docs/demo-script.md、docs/api.md、docs/architecture.md、TODO 與 ROADMAP 已同步 Phase 26 demo 說法：這是 VLM-first provider spike，不是 production VLM parser。

## MVP v0.27.0 Aggressive Demo Defaults

- [x] `tasks/phase-27-aggressive-defaults/27-01-aggressive-demo-defaults.md`: 啟用 default `hybrid_rerank` RAG / Agent search、Ollama embedding、FastEmbed rerank adapter、frontend parser + vector indexing best-effort flow 與 `v0.27.0` release/version bump。
- [x] `tasks/phase-27-aggressive-defaults/27-02-ocr-vlm-evidence-alignment.md`: 讓 VLM parser 同時使用圖片與 OCR context，並把 VLM 欄位結果對回 OCR line / bbox；target `v0.27.1`。
- [x] `tasks/phase-27-aggressive-defaults/27-03-vector-source-expansion-contract.md`: 固定 vector DB source contract，明確規劃 `.txt` direct chunks、text-native PDF 與 scanned PDF 的不同路徑；planning ticket，不 bump version。

Phase 27 goal：
- 把已實作、已有 fallback、可驗證的進階 demo 能力改成預設路徑：`hybrid_rerank` RAG / Agent search、Ollama embedding、FastEmbed rerank adapter，以及 Admin ingestion 後的 parser + vector indexing best-effort flow。
- 讓 demo 開場就走最完整的先進路徑；本機模型、Qdrant 或 reranker 不可用時，回到 keyword evidence，並在 trace / UI 顯示原因。
- Phase 27 patch backlog 需補齊 OCR / VLM evidence alignment：OCR 產生文字層，VLM 同時看圖片與 OCR context，欄位結果可對回 OCR line / bbox，RAG 與 Agent 仍使用 OCR chunks 作為 retrieval evidence。
- Vector DB 長期不應只依賴 OCR chunks；`.txt` 應走 direct text chunking，PDF 需拆成 text-native PDF extraction 與 scanned PDF rendering / OCR pipeline。

Phase 27 guardrails：
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth / RBAC、OpenAI SDK、vLLM、production VLM parser、PDF rendering、K8s 或 deployment 設定。
- 不把 best-effort vector indexing 說成正式背景任務或 production ingestion pipeline。
- 不移除 keyword、deterministic parser 或 mock OCR；它們只作 fallback、manual override、debug path 或 validation path。
- 不把 text-native PDF 與 scanned PDF 混成同一個已完成能力；未實作 PDF rendering 前，不宣稱支援 scanned PDF ingestion。

27-01 aggressive defaults status：

- Backend 預設已改為 `hybrid_rerank`，embedding 預設 Ollama，rerank 預設 FastEmbed adapter；`/rag/query` 與 Agent `search_documents` 使用同一個 RAG provider selection。
- `/rag/query` 已接上 `vector`、`vector_rerank`、`hybrid` 與 `hybrid_rerank` runtime provider；embedding、Qdrant 或 reranker 不可用時，會回到 keyword evidence 並保留 fallback metadata。
- Frontend 預設進入 Admin / Analyst ingestion surface；OCR 成功後會 best-effort 執行 parser 與 vector indexing，失敗時保留明確訊息，不阻斷主要 demo。
- README、backend README、frontend README、docs/demo-script.md、docs/api.md、docs/architecture.md、PRD、TODO、ROADMAP、Docker Compose、`.env.example` 與 demo smoke script 已同步 `v0.27.0` aggressive default 說法。
- [x] 27-01 validation：backend tests 通過，`166 passed`（僅 pytest cache 權限警告）；frontend build 通過；baseline demo smoke 通過，health version `0.27.0`、retrieval source `hybrid_rerank fallback: reranker_unavailable`；Browser 檢查 desktop 1280px 與 mobile 390px 預設皆為 Admin / Analyst ingestion surface，且無 horizontal overflow；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。

27-02 / 27-03 patch backlog status：

- 已完成。`27-02` 讓 VLM request 同時帶圖片與 compact OCR context，並在 `vlm_invoice` 欄位結果中保存 matched OCR `source_text` / `source_page` / `source_bbox`；未命中時以 `evidence_unmatched` / `evidence_unavailable` 標示。RAG / vector indexing 仍使用 OCR chunks，Agent allowlist 不變。
- [x] 27-02 validation：backend tests 通過，`168 passed`（僅 pytest cache 權限警告）；frontend build 通過；demo smoke with fake VLM 通過，health version `0.27.1`、RAG answer source `LLM unavailable fallback`、retrieval source `hybrid_rerank fallback: reranker_unavailable`；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- 已完成。`27-03` 是 source contract / planning ticket，用來拆清楚 `ocr_image`、`text_upload`、`pdf_text` 與 `pdf_scanned_pending_ocr` 的 vector ingestion 邊界；目前 runtime 仍主要索引 OCR chunks，`.txt` direct chunks、PDF text extraction 與 scanned PDF rendering / OCR pipeline 留給 Phase 28 後續小票。
- [x] 27-03 validation：ticket `rg` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。本 ticket 不 bump version，且未修改 runtime。

## MVP v0.28.0 Document Sources / Demo Auth Mode

- [x] `tasks/phase-28-document-sources-auth-mode/28-01-document-source-router.md`: 固定 image OCR、`.txt` direct text、text-native PDF 與 scanned PDF pending OCR 的 source router contract；planning ticket，不 bump version。
- [x] `tasks/phase-28-document-sources-auth-mode/28-02-direct-text-upload-ingestion.md`: 讓 `.txt` 直接建立 `text_upload` chunks，接到 RAG、Qdrant vector indexing 與 Agent search。
- [x] `tasks/phase-28-document-sources-auth-mode/28-03-text-native-pdf-ingestion.md`: 支援 text-native PDF 文字抽取並建立 `pdf_text` chunks；scanned PDF 清楚標示 pending / unsupported。
- [x] `tasks/phase-28-document-sources-auth-mode/28-04-demo-login-mode-and-role-gates.md`: 新增 demo login mode、`/auth/login` / `/auth/me` / `/auth/logout`、frontend login screen 與基本 role gates。
- [x] `tasks/phase-28-document-sources-auth-mode/28-05-phase-28-demo-release-sync.md`: 重跑 final validation，並同步 `v0.28.0` 版本與文件。

Phase 28 goal：

- 把文件上傳從「圖片 OCR 主線」擴充成更合理的文件來源主線：圖片走 OCR、`.txt` 直接進 chunks、text-native PDF 抽文字、scanned PDF 等待 PDF rendering / OCR pipeline。
- 讓 vector DB 的來源不只依賴 OCR chunks；`.txt` 與 text-native PDF 都要能成為 first-class retrieval evidence。
- 新增 demo-safe 使用者登入模式，讓 Admin / Analyst / Viewer 不再只是前端文字區分，而是能透過登入狀態與基本 API guard 呈現。

Phase 28 guardrails：

- 不把 `.txt` direct ingestion 說成 OCR；source 必須是 `text_upload` 或等價命名。
- 不把 text-native PDF 和 scanned PDF 混成同一個已完成能力；未實作 PDF rendering 前，不宣稱 scanned PDF OCR 已支援。
- Demo login mode 不等於正式 RBAC、tenant isolation、organization / project permission 或 production auth。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、SSO、OAuth、MFA、K8s 或 deployment 設定。
- `28-05` 才允許 `v0.28.0` version bump；`28-01` 若只做 planning 必須寫 `Version bump required: no`。

28-01 to 28-05 backlog status：

- 已完成。`28-01` 已固定 source router contract，避免後續把 text、PDF、OCR 混成同一路徑；validation `rg` 與 `git diff --check` 通過。
- 已完成。`28-02` 讓 `.txt` 正式直接進 chunks / RAG / vector / Agent，不再透過 mock OCR；backend tests、frontend build、demo smoke、ticket `rg` 與 `git diff --check` 已通過。
- 已完成。`28-03` 使用 `pypdf` 抽 text-native PDF 文字層並建立 `pdf_text` chunks；scanned / empty PDF 只標示 `pdf_scanned_pending_ocr`，invalid PDF 顯示 `pdf_text_extraction_failed`。backend tests `178 passed`（僅 pytest cache 權限警告）；frontend build、demo smoke、ticket `rg` 與 `git diff --check` 已通過。
- 已完成。`28-04` 做 demo login mode 與基本 role gates，但不做正式多租戶 RBAC；backend tests `185 passed`（僅 pytest cache 權限警告）、frontend build、`DOCURAG_AUTH_MODE=demo` demo smoke、Browser login / role gate 檢查、ticket `rg` 與 `git diff --check` 已通過。
- 已完成。`28-05` 完成 `v0.28.0` release sync 與 validation；backend tests `185 passed`（僅 pytest cache 權限警告）、frontend build、`DOCURAG_AUTH_MODE=demo` demo smoke、Browser `v0.28.0` login / role gate / overflow 檢查、final `rg` 與 `git diff --check` 已通過。

## MVP v0.29.0 Built-in RAG Eval Admin Surface

- [x] `tasks/phase-29-rag-eval-admin-surface/29-01-built-in-rag-eval-admin-surface.md`: 在後台知識庫管理新增「測試RAG」內建基準測試，固定 `hybrid_rerank`，只顯示 Hit Rate@K、MRR@K、平均延遲與 Failure / Fallback，並把 Agent 執行紀錄改成可摺疊。

Phase 29 goal：

- 讓 Admin / Analyst 可以在後台直接跑內建 retrieval benchmark，不需要切到 CLI 才能展示 RAG 評估能力。
- 第一版策略固定 `hybrid_rerank`，避免策略比較 UI 擴張；重點是把現有 eval runner 變成面試可展示的後台操作。
- 內建 benchmark 使用 10 張 demo-safe synthetic 中文發票 fixture：`NVDLA` 1 張、`GOOGLE` 1 張、`OpenAI` 1 張、`Intel` 3 張、`DocuRAG` 4 張；每張日期 / 金額不同且幣別皆為台幣。
- 後台 trace 區塊維持可讀性：Agent 執行紀錄預設可收合，使用者需要時再展開。

Phase 29 guardrails：

- 不新增策略選擇；第一版只跑 `hybrid_rerank`。
- 不新增 production eval dashboard、歷史趨勢、圖表分析、自訂 eval dataset 上傳、case builder 或 DB-backed eval runs。
- 不新增 Recall@K、LLM-as-judge、answer faithfulness、citation quality scoring 或人工標註流程。
- 不把中文發票 fixture 說成 OCR 準確率測試；本 phase 測 retrieval evidence 是否被找回，不測 OCR、PDF rendering、layout analysis 或 VLM parser。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、正式 RBAC、tenant isolation、OpenAI API、vLLM、K8s 或 deployment 設定。

Phase 29 validation：

- Backend targeted eval tests：`python -m pytest backend/tests/test_evaluation.py backend/tests/test_eval_dataset.py backend/tests/test_evaluation_api.py -q` 通過，`27 passed, 1 warning`。
- Backend full suite：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/test-backend.ps1` 通過，`191 passed, 1 warning`（pytest cache 權限警告）。
- Frontend build：`npm.cmd run build` 通過，frontend package version 顯示 `0.29.0`。
- Retrieval eval smoke：既有 `127.0.0.1:8000` 因 demo auth 回 `401`，改用 temporary auth-disabled backend（port `8019`、Temp data dir）執行 `retrieval-eval-smoke.ps1 -RunHybridRerank` 通過；`case_count=20`、`hit_rate_at_k=0.65`、`mrr_at_k=0.575`、`failure_count=0`、`fallback_count=0`。
- Browser validation：Admin 可登入後台執行「測試RAG」，顯示 `10 cases`、Hit Rate@K `100%`、MRR@K `1.00`、Failure / Fallback `0 / 10`；Agent 執行紀錄預設收合且可展開；desktop `1280px` 與 mobile `390px` 無 horizontal overflow。
- Demo auth role validation：Viewer 只看到前台查詢，不顯示或不可操作後台「測試RAG」與 Agent 操作。
- Ticket search / whitespace：`rg -n "測試RAG|hybrid_rerank|Hit Rate@K|MRR@K|fallback_count|Agent 執行紀錄" frontend/src backend/app sample-data docs TODO.md tasks/phase-29-rag-eval-admin-surface` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。

## Documentation Maintenance

- [x] `tasks/docs-readme-image-refresh.md`: 使用使用者提供的兩張 demo 截圖，將 root README 改成精簡繁中展示入口；不 bump version、不改 runtime。
- [x] README image refresh validation：`rg -n "readme-viewer-query.jpg|readme-admin-ingestion.jpg|文件知識庫問答|README_DEV.md" README.md TODO.md tasks/docs-readme-image-refresh.md` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/docs-readme-interview-dev-split.md`: 將 root README 切分為面試官入口 `README.md` 與開發紀錄 `README_DEV.md`；不 bump version、不改 runtime。
- [x] README split validation：`rg -n "README_DEV.md|開發紀錄|面試官|技術亮點|Release Status" README.md README_DEV.md TODO.md tasks/docs-readme-interview-dev-split.md` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/docs-agents-readme-split-guidelines.md`: 更新 `AGENTS.md` 雙 README 分工規範，讓後續 ticket 區分面試官入口與開發紀錄；不 bump version、不改 runtime。
- [x] AGENTS README split validation：`rg -n "README_DEV.md|README 分工|面試官|Release Status|開發紀錄" AGENTS.md TODO.md tasks/docs-agents-readme-split-guidelines.md` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `tasks/docs-agents-auto-push-authorization.md`: 更新 `AGENTS.md` Git 自動上傳規範，記錄使用者授權完成 ticket 後自動 push 目前分支 upstream；不 bump version、不改 runtime。
- [x] AGENTS auto push authorization validation：`rg -n "自動 push|自動上傳|授權|force push|安全審核|upstream" AGENTS.md TODO.md tasks/docs-agents-auto-push-authorization.md` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。
- [x] `AGENTS.md`：註記回覆語氣偏好，預設少用工程黑話、先用白話講重點；使用者追問相關細節時補上必要名詞、背景與實際影響。
- [x] AGENTS tone preference validation：`rg -n "工程黑話|白話|語氣|相關細節" AGENTS.md TODO.md` 通過；`git diff --check` 通過（僅 Windows LF/CRLF 提示）。

## Release Verification Status

- [x] v0.0: repo structure、docs、tasks 已完成。
- [x] v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- [x] Python fallback: `scripts/check-dev-env.ps1` 與 `scripts/test-backend.ps1` 可透過 `pip.exe` 反推實際 `python.exe`。
- [x] Upload stub: pytest 與本機 HTTP 驗證皆通過。
- [x] Docker: `docker` CLI、Docker build 與 Docker Compose healthcheck 已驗證。
- [x] v0.2.0: Demo UI、backend CORS、Backend CI 與 Docker 驗證已完成。
- [x] v0.3.0: Document Local Storage、文件列表、文件詳情、frontend list UI 與 Docker Compose upload 驗證已完成。
- [x] v0.4.0: OCR Mock Pipeline、frontend OCR UI 與 Docker Compose OCR mock API 驗證已完成。
- [x] v0.5.0: Local RAG Baseline、frontend Chat UI 與 Docker Compose RAG API 驗證已完成。
- [x] v0.5.1: Demo Hardening、公開 sample data、demo seed script、API smoke test 與 Docker Compose demo 驗證已完成。
- [x] v0.6.0: Bridge Contracts、OCR provider interface、RAG provider interface、processing status、chunk citation schema 與 processing job contract。
- [x] v0.7.0: Real OCR Provider Spike 已完成；07-01 到 07-04 已執行，Docker validation 需待 Docker Desktop daemon 可用後重跑。
- [x] v0.8.0: PaddleOCR Runtime Stabilization 已完成；Python 3.12、PaddleOCR 2.10.0、PaddlePaddle 3.0.0 sample real OCR flow 已驗證。
- [x] v0.9.0: GPU Runtime 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.9.0`，本機 Python 3.12 + CUDA PaddlePaddle GPU runtime 與繁中 provider-selected OCR smoke 已通過。
- [x] v0.9.1: OCR Performance Hardening 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.9.1`，PaddleOCR startup preload、provider reuse、timing metadata、`cls=False` baseline 與 provider-selected real OCR smoke 已通過。
- [x] v0.10.0: LLM RAG Backlog 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.10.0`，Ollama `qwen3.5:4b` provider decision、最小 client、optional generation path、demo smoke `-RunLlm` 與 frontend answer source 已補齊。
- [x] v0.11.0: Vector RAG Backlog 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.11.0`，Ollama `qwen3-embedding:0.6b` embedding client、Qdrant local runtime / collection smoke、optional vector retrieval path、fallback trace metadata、demo smoke `-RunVector` 與 frontend retrieval source 已補齊。
- [x] v0.12.0: Vector Indexing Hardening 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.12.0`，manual vector indexing contract、同步 indexing service、`POST /documents/{document_id}/index/vector`、optional vector indexing smoke 與 fallback-safe vector retrieval 已補齊。
- [x] v0.13.0: Retrieval Evaluation Baseline 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.13.0`，公開 eval dataset、retrieval eval runner、baseline eval smoke、optional vector eval smoke 與 metrics output 已補齊。
- [x] v0.15.0: Rerank Runtime Spike 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.15.0`，FastEmbed provider decision、disabled-by-default rerank adapter、optional `vector_rerank` eval strategy、rerank trace metadata 與 baseline smoke 已補齊。
- [x] v0.16.0: Hybrid Retrieval Slice 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.16.0`，公開 eval dataset 擴充到 12 筆、optional `hybrid` eval strategy、hybrid trace metadata、baseline smoke 與 optional `-RunHybrid` smoke 已補齊。
- [x] v0.17.0: Retrieval Trace UI / Eval Visibility 已完成；backend / frontend / health test / Docker Compose / README / backend README / frontend README / TODO / ROADMAP 已同步到 `v0.17.0`，frontend trace panel、eval summary fallback / trace metadata reporting、baseline demo smoke、baseline eval smoke、optional `-RunVector` / `-RunVectorRerank` / `-RunHybrid` smoke 與 Browser trace UI 檢查已補齊。
- [x] v0.18.0: Hybrid Rerank Planning 已完成；本次只新增 Markdown planning tickets / TODO / ROADMAP，不 bump backend、frontend、health test 或 Docker Compose version。
- [x] v0.19.0: Hybrid Rerank Runtime 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `v0.19.0`，optional `hybrid_rerank` eval provider、`-RunHybridRerank` smoke flag、trace / report metadata、baseline demo smoke 與 baseline eval smoke 已補齊；optional vector-backed smoke 需待本機 Qdrant collection `docurag_chunks_v1` 可用後重跑。
- [x] v0.20.0: Interview MVP Packaging 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `v0.20.0`，demo script、sample / eval coverage、demo media、baseline demo smoke、baseline retrieval eval smoke 與 final validation 已補齊；optional vector-backed smoke 需待本機 Qdrant collection `docurag_chunks_v1` 可用後重跑。
- [x] v0.21.0: Real GPU OCR Interview Demo Path 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO、ROADMAP 與 demo script 已同步到 `v0.21.0`；frontend upload 已改為 provider-selected real OCR-first flow，mock OCR 只作手動 fallback；frontend build、backend tests、baseline demo smoke、real OCR smoke、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.22.0: RAG Query Hardening 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP 已同步到 `v0.22.0`；keyword query normalization、CJK tokenization、demo-safe 中文 alias、backend tests、frontend build、baseline demo smoke、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.23.0: Viewer Chat / Admin Ingestion Role Split 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、frontend fallback version、demo script、architecture、TODO 與 ROADMAP 已同步到 `v0.23.0`；Viewer Chat-only 預設入口、Admin / Analyst ingestion surface、backend tests、frontend build、baseline demo smoke、Browser role split / overflow 檢查、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.24.0: VLM / Parser Minimal MVP 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、demo script、TODO 與 ROADMAP 已同步到 `v0.24.0`；deterministic invoice parser fallback、parse / fields API、local JSON parser result persistence、frontend structured fields surface、parser demo smoke、Browser structured fields / overflow 檢查、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.25.0: Agent Tool-use Minimal MVP 版本 / 文件 / smoke 實作已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、demo script、TODO 與 ROADMAP 已同步到 `v0.25.0`；deterministic planner、allowlisted tool adapters、Agent run / lookup API、frontend trace surface、Agent demo smoke、Browser desktop Agent trace / overflow 檢查、ticket `rg` 與 `git diff --check` 已通過。
- [x] v0.26.0: Real VLM Parser Provider Spike 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、demo script、TODO、ROADMAP、API 與 architecture 文件已同步到 `v0.26.0`；VLM-first parser provider boundary、demo-safe image input resolver、`vlm_invoice` adapter、parser source comparison、fake / stub success smoke、provider unavailable fallback 與 Agent `get_document_fields` consumption validation 已補齊。
- [x] v0.27.0: Aggressive Demo Defaults 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、demo script、TODO、ROADMAP、API、architecture、PRD 與 `.env.example` 已同步到 `v0.27.0`；default `hybrid_rerank` RAG / Agent search、Ollama embedding、FastEmbed rerank adapter、frontend parser + vector indexing best-effort flow、fallback-safe demo smoke 與 Browser default surface validation 已補齊。
- [x] v0.27.1: OCR / VLM Evidence Alignment 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、README_DEV、backend README、frontend README、demo script、TODO、ROADMAP、API 與 architecture 文件已同步到 `v0.27.1`；VLM request 帶 image + OCR context，欄位 evidence mapping、unmatched trace、deterministic fallback 與 Agent structured fields + OCR chunk validation 已補齊。
- [x] v0.28.0: Document Sources / Demo Auth Mode 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、demo script、TODO、ROADMAP、API 與 architecture 文件已同步到 `v0.28.0`；`.txt` direct ingestion、text-native PDF extraction、scanned PDF pending state、demo login / role guard、demo auth smoke 與 Browser login / role gate validation 已補齊。
- [x] v0.29.0: Built-in RAG Eval Admin Surface 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、demo script、TODO、ROADMAP、API、architecture 與 PRD 已同步到 `v0.29.0`；後台「測試RAG」內建 `hybrid_rerank` benchmark、10 張 synthetic 中文發票 fixture、built-in eval API、fallback-aware metrics、Agent 執行紀錄摺疊、Viewer role guard、backend tests、frontend build、hybrid rerank smoke、Browser desktop / mobile validation 與 `git diff --check` 已補齊。
- [x] v0.31.0: PostgreSQL / Schema / Repository Foundation 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 Phase 31 ticket 已同步到 `v0.31.0`；local JSON fallback、opt-in PostgreSQL repository adapter、local JSON migration command、backend tests、frontend build、demo smoke、repository keyword validation 與 `git diff --check` 已補齊。
- [x] v0.32.0: Formal Auth / RBAC / Tenant Boundary 已完成；backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、TODO、ROADMAP 與 Phase 32 ticket 已同步到 `v0.32.0`；formal signed bearer guard、project access filtering、Admin / Analyst / Viewer role surface、Viewer forbidden validation、backend tests、frontend build、demo smoke、Browser desktop / mobile validation 與 `git diff --check` 已補齊。
