# API Draft

此文件先定義 MVP API 邊界，實作時可依 ticket 逐步補齊。

## System

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |

## Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login` | Demo login |
| POST | `/auth/logout` | Logout |
| GET | `/auth/me` | Current user |

## Projects

| Method | Endpoint | Description |
|---|---|---|
| GET | `/projects` | List visible projects |
| POST | `/projects` | Create project |
| GET | `/projects/{project_id}` | Project detail |

## Documents

| Method | Endpoint | Description |
|---|---|---|
| GET | `/projects/{project_id}/documents` | List documents |
| POST | `/projects/{project_id}/documents` | Create document metadata |
| GET | `/documents/{document_id}` | Document detail |
| GET | `/documents/{document_id}/pages` | OCR page text |
| GET | `/documents/{document_id}/fields` | Extracted fields |
| GET | `/documents/{document_id}/chunks` | Document chunks |
| POST | `/documents/{document_id}/index/vector` | Manually index document chunks into Qdrant when embedding / Qdrant runtime is explicitly enabled |

## Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/projects/{project_id}/chat` | Ask a demo RAG question |

## Eval

| Method | Endpoint | Description |
|---|---|---|
| GET | `/projects/{project_id}/eval-runs` | List sample eval metrics |
