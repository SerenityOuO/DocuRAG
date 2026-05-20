# MVP Architecture

本文件只描述 DocuRAG AgentOps 的 MVP 架構。長期目標中的 OCR、RAG、Qdrant、Redis、NATS、vLLM 與 Agent worker 都先保留擴充位置，不在 Phase 00 文件交付中實作。

## MVP Shape

```text
Documentation
    |
    |-- README / PRD / Architecture / Roadmap
    |-- TODO / task tickets
    |
Future Backend
    |
    |-- healthcheck
    |-- document upload API
    |-- document metadata schema
```

Phase 00 的交付是文件與任務票，不建立 runtime app。Phase 01 才會建立最小 backend healthcheck。Phase 02 才會建立文件上傳與 metadata 基礎。

## Near-Term Runtime Boundary

Phase 01 到 Phase 02 的最小 runtime 邊界如下：

```text
Client or API tester
    |
FastAPI Backend
    |
Document metadata model
```

這個階段只需要確認服務可啟動、`/health` 可驗證、文件上傳 API 與 metadata contract 清楚。是否接資料庫、storage、worker 或向量資料庫，要由後續 ticket 決定。

## Deferred Components

以下元件是目標架構的一部分，但不屬於目前 MVP bootstrap：

- Vue frontend。
- OCR worker。
- VLM / parser pipeline。
- Embedding 與 chunking pipeline。
- Qdrant vector database。
- Redis session、cache、rate limit。
- NATS event bus。
- Rerank 與 RAG generation。
- Eval runner。
- Agent tool-use runtime。
- vLLM / Ollama / OpenAI-compatible serving。
- K8s manifests。

## Design Rules

- 先完成可驗收的最小切片，再擴充 AI pipeline。
- API contract 先保持清楚，不提前建立複雜抽象。
- metadata 欄位要能支援後續 OCR / RAG 狀態，但不在當前階段實作資料庫 schema。
- 每次只依 ticket 修改必要檔案。
- 文件與 TODO 要跟 ticket 狀態同步。
