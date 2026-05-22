# MVP Architecture

本文件描述 DocuRAG AgentOps 目前的受控 MVP 架構。到 v0.19.0 為止，專案已完成 backend / frontend demo、provider-selected OCR、local RAG、citation trace、retrieval eval runner、optional vector / rerank / hybrid / `hybrid_rerank` eval strategy。Phase 20 只做 interview MVP packaging，不新增 production runtime。

## MVP Shape

```text
Vue Demo UI
    |
    |-- upload / document detail / OCR result
    |-- RAG answer / citations / retrieved chunks / trace panel
    |
FastAPI Backend
    |
    |-- health / document API / OCR API / RAG API
    |-- manual vector indexing API
    |-- retrieval eval runner CLI
    |
Local Data Store
    |
    |-- uploads / metadata JSON / OCR results / chunks
    |
Optional Local AI Runtime
    |
    |-- PaddleOCR GPU provider
    |-- Ollama generation / embedding
    |-- Qdrant vector collection
    |-- FastEmbed rerank adapter
```

MVP 的預設路徑保持 local keyword RAG baseline，確保沒有 optional runtime 時也能重跑 demo。vector retrieval、rerank、hybrid 與 `hybrid_rerank` 都必須 explicit opt-in；`hybrid_rerank` 目前只在 retrieval eval runner 裡使用，不接 default `/rag/query` 或 frontend chat route。

## Near-Term Runtime Boundary

Phase 20 的 runtime 邊界如下：

```text
Browser / PowerShell smoke scripts
    |
FastAPI Backend
    |
Local JSON store and optional local model services
```

這個階段只整理 demo readiness、sample / eval coverage、README media 與 final validation。不得新增 backend API、frontend route、database schema、worker、auth、queue 或 deployment 設定。

## Deferred Or Explicitly Optional Components

以下能力是長期目標或 optional local runtime，不屬於目前 production-ready MVP：

- VLM / parser pipeline、PDF rendering、image preprocessing、多頁 production OCR pipeline。
- Default-on vector retrieval、default-on rerank、default-on hybrid / `hybrid_rerank` chat path。
- Production eval dashboard、strategy comparison UI、LLM-as-judge、answer faithfulness scoring、citation quality scoring。
- PostgreSQL schema、multi-user tenancy、login、RBAC。
- Redis session、cache、rate limit。
- NATS event bus。
- Agent tool-use runtime。
- vLLM / OpenAI-compatible serving。
- K8s manifests and deployment hardening。

## Design Rules

- 先完成可驗收的最小切片，再擴充 AI pipeline。
- API contract 先保持清楚，不提前建立複雜抽象。
- metadata 欄位要能支援 OCR / RAG / eval trace 狀態，但不在目前 MVP 實作資料庫 schema。
- 每次只依 ticket 修改必要檔案。
- 文件與 TODO 要跟 ticket 狀態同步。
