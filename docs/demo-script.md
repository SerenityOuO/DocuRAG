# Demo Script

此 demo script 用於面試展示，目標是在 5 到 10 分鐘內說清楚產品價值與工程取捨。

## 1. Project Intro

DocuRAG AgentOps 是一個 AI 文件平台，展示文件解析、RAG citation、RAG evaluation 與 AgentOps 的端到端產品能力。

## 2. Architecture

說明 MVP 先用 fixture-driven flow 跑通產品與 API 邊界，後續再逐步接 OCR、Qdrant、Redis、NATS 與 LLM provider。

## 3. Demo Flow

```text
Login
Create Project
View Documents
Open Document Detail
Show OCR Text / Extracted Fields / Chunks
Ask Question
Show Answer + Citation
Show RAG Trace
Compare Eval Metrics
```

## 4. Interview Talking Points

- 不只做 Chatbot，而是設計可觀測、可評估的 RAG 平台。
- Citation 與 trace 是文件型 AI 系統可信度的核心。
- MVP 刻意控制 scope，先完成可展示 thin slice。
- 架構預留 Redis、NATS、Qdrant、workers 與推論後端，但不在第一階段過度實作。

## 5. Deferred Demo Items

- 真 OCR
- 真 embeddings
- 真 Qdrant retrieval
- 真 rerank
- Agent tool-use
- Docker Compose full stack
