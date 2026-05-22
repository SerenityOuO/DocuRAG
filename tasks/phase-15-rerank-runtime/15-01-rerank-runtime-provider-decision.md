# 15-01 Rerank Runtime Provider Decision

## Goal

根據 Phase 14 的 rerank decision criteria，選定 Phase 15 / `v0.15.0` 的 rerank runtime provider 與模型候選，並明確記錄 dependency、model download、fallback 與 validation 風險。此 ticket 是文件與決策票，不新增 runtime。

## Scope

- 回顧 Phase 14 的 local-first、disabled-by-default、fallback-safe decision criteria。
- 比較 local reranker provider 候選，記錄模型大小、安裝方式、CPU/GPU 需求、授權與離線可用性。
- 決定 Phase 15 是否先做 `vector_rerank`，並確認 hybrid search 延後。
- 明確列出後續 implementation ticket 是否需要新增外部依賴、模型下載或 env setting。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 15 backlog。

## Out of Scope

- 不新增或修改 backend / frontend 程式碼。
- 不新增外部依賴、模型下載、Docker service 或 runtime provider。
- 不實作 rerank、hybrid search、BM25、score fusion 或 ranking pipeline。
- 不新增 eval dataset JSON、API endpoint、frontend UI、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。

## Release Impact

- Target version: `v0.15.0`。
- Version bump required: no。
- 原因：本 ticket 只決定 rerank runtime provider 與後續 implementation 邊界，不完成 runtime release，也不改變產品行為。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md`

## Decision Notes

### Phase 14 criteria recap

Phase 14 已固定 rerank 只能作為 local-first、disabled-by-default、fallback-safe 的品質層。Phase 15 因此先做 `vector_rerank`，讓既有 Qdrant vector candidates 經 reranker 重排，再用 Phase 13 eval runner 比較 `vector` 與 `vector_rerank` 的 Hit Rate@K、MRR@K、Recall@K、latency 與 failure count。

Hybrid search 會延後，因為它還需要 BM25 / sparse retrieval、merge policy、dedupe rule 與 branch trace contract；若和 rerank 放在同一階段，會同時引入兩個 retrieval 變因。

### Provider candidates

| Candidate | Runtime path | Model / size | License | Fit | Risk |
|---|---|---:|---|---|---|
| FastEmbed `TextCrossEncoder` + `BAAI/bge-reranker-base` | Local ONNX cross-encoder via FastEmbed | 1.04 GB | MIT | Qdrant / FastEmbed 官方支援；中英 rerank；適合本 repo 的 Qdrant-first vector path | 需要新增 optional Python dependency 與首次 model download |
| FastEmbed `TextCrossEncoder` + `jinaai/jina-reranker-v2-base-multilingual` | Local ONNX cross-encoder via FastEmbed | 1.11 GB | CC-BY-NC-4.0 | Multilingual，FastEmbed 官方支援 | 非商用授權對公開作品與後續 reuse 較不乾淨 |
| FastEmbed `TextCrossEncoder` + `Xenova/ms-marco-MiniLM-L-6-v2` | Local ONNX cross-encoder via FastEmbed | 0.08 GB | Apache-2.0 | 很小、容易 smoke test | 英文 MS MARCO 導向，對繁中 OCR / 中英混合文件不理想 |
| `BAAI/bge-reranker-v2-m3` via FlagEmbedding / Transformers | Local PyTorch / HF model | 568M params | Likely open model card license; must verify before dependency ticket | BGE 文件推薦多語與中英 rerank，和長期 PRD 設定接近 | FastEmbed supported list 目前未列此 model；需要較重 dependency、GPU / torch runtime 與模型下載 |
| `Qwen/Qwen3-Reranker-0.6B` via Sentence Transformers / Transformers / vLLM | Local PyTorch / vLLM model | 0.6B params | Apache-2.0 | Qwen family、一致於既有 Qwen embedding / LLM 方向，100+ languages | 需要 `sentence-transformers` / `transformers` 或 vLLM；現有 Ollama path 沒有 native rerank API，整合成本高於 Phase 15 spike |

### Decision

Phase 15 第一版選定：

- Rerank provider：`fastembed`。
- Rerank model：`BAAI/bge-reranker-base`。
- Strategy label：`vector_rerank`。
- Enable flag：`DOCURAG_RERANK_PROVIDER=fastembed`；未設定或設為 `disabled` 時保持 no-op provider。
- Default model env：`DOCURAG_RERANK_MODEL=BAAI/bge-reranker-base`。
- Default rerank top K env：`DOCURAG_RERANK_TOP_K=5`。
- Default candidate limit：沿用 vector retrieval candidates，不在 15-02 新增 hybrid / BM25 candidate source。

選擇理由：

- FastEmbed 已是 Qdrant 官方文件示範的 reranker runtime path，並提供 supported model list；這與本專案 Phase 11 / 12 已選 Qdrant local runtime 的方向一致。
- `BAAI/bge-reranker-base` 是 FastEmbed 目前支援清單中的 BGE reranker，授權為 MIT，且描述為 cross-encoder reranking model；比 CC-BY-NC multilingual Jina model更適合作為可公開展示的 local-first default candidate。
- `BAAI/bge-reranker-v2-m3` 與 `Qwen/Qwen3-Reranker-0.6B` 都是合理的 future candidate，但需要更重的 dependency / serving decision。Phase 15 先以 FastEmbed ONNX path 降低 adapter 與 smoke test 風險。
- Provider 必須 disabled-by-default；任何 model download 或 external runtime failure 都只能 fallback 到原 vector candidates，不可影響 keyword baseline。

### Dependency and model download boundary

15-01 不新增 runtime、dependency 或 model cache。後續 ticket 的邊界如下：

- `15-02` 若新增 runtime，必須使用 optional dependency，例如 backend optional extra `rerank`，不得讓 base install 自動下載 reranker dependency。
- `15-02` provider implementation 必須 lazy import FastEmbed；dependency 不存在時回傳 provider unavailable，並 fallback 到原 candidates。
- `15-02` 不可在 backend startup 自動 preload 或下載 reranker model。
- `15-04` 才能補 optional rerank eval smoke preflight；若本機未安裝 optional dependency 或 model cache 不可用，必須清楚標示 skipped / unavailable，不可讓 baseline smoke fail。
- 若工具因安裝 optional dependency 或下載 model 需要 approval，必須依工具要求取得 approval 後才可執行。

### References checked on 2026-05-22

- FastEmbed supported rerank cross encoder models：`https://qdrant.github.io/fastembed/examples/Supported_Models/`
- Qdrant FastEmbed reranking guide：`https://qdrant.tech/documentation/fastembed/fastembed-rerankers/`
- BGE reranker model docs：`https://bge-model.com/tutorial/5_Reranking/5.2.html`
- `BAAI/bge-reranker-v2-m3` model card：`https://huggingface.co/BAAI/bge-reranker-v2-m3`
- `Qwen/Qwen3-Reranker-0.6B` model card：`https://huggingface.co/Qwen/Qwen3-Reranker-0.6B`

## Acceptance Criteria

- [x] Rerank provider candidates 已比較。
- [x] Provider / model 選擇理由已記錄。
- [x] 依賴、模型下載與 env setting 風險已記錄。
- [x] 明確標示 Phase 15 先做 `vector_rerank`，hybrid search 延後。
- [x] 明確標示此 ticket 不新增 runtime 或 version bump。

## Validation

- `rg -n "v0.15.0|Phase 15|rerank provider|vector_rerank|hybrid" TODO.md docs/ROADMAP.md tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md`
- `git diff --check`
