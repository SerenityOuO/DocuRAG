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
| POST | `/documents/{document_id}/parse` | Run the MVP parser for an OCR-completed document |
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

## Phase 24 Parser Contract Draft

Phase 24 的 parser contract 先支援 invoice MVP。`24-01` 只固定文件與 API 草案；runtime、metadata persistence 與 frontend surface 由後續 tickets 實作。此 contract 是 VLM-compatible，不代表目前已接真正 VLM、LLM parser、DB、worker 或 production parser pipeline。

### Parser Sources

| Source | Scope |
|---|---|
| `deterministic_invoice` | Phase 24 MVP fallback。只從既有 OCR text / OCR lines 做 demo-safe 規則抽取，不新增外部依賴。 |
| `llm_invoice` | Future text-only parser。只使用 OCR text / lines，不直接讀圖片。 |
| `vlm_invoice` | Future VLM parser。可使用原始圖片 / layout trace，但不屬於 `24-01` 或 deterministic MVP runtime。 |

### Status Contract

Parser 狀態存在於 `ParserResult.status`，後續若接入 document processing metadata，才新增可選 `processing.parser` step。Parser failure 不應清空 OCR result、chunks 或影響 Viewer Chat 的 default RAG path。

| Status | Meaning |
|---|---|
| `pending` | 尚未執行 parser，或沒有已保存的 structured fields。 |
| `parsing` | Parser request 已開始；同步 MVP 通常只在 request lifecycle 內短暫出現。 |
| `parsed` | Parser 完成，`fields` 包含 structured fields 與 source trace。 |
| `failed` | Parser 失敗；`fallback_reason` 或 `error_message` 必須說明原因。 |

Document-level processing 後續以 `processing.parser=pending/running/completed/failed` 對應上述狀態；OCR 已完成但 parser 失敗時，`processing.ocr` 與 `processing.indexing` 保持原本狀態，`processing.failed_reason` 不應被 parser error 覆蓋，除非該 request 本身只回傳 parser failure。

### Schema Draft

`ExtractedField` 是欄位層級的最小 source trace 單位：

```json
{
  "value": "INV-2026-001",
  "confidence": 0.86,
  "source_text": "Invoice No: INV-2026-001",
  "source_page": 1,
  "source_bbox": {
    "x_min": 10,
    "y_min": 20,
    "x_max": 260,
    "y_max": 44
  },
  "parser_source": "deterministic_invoice",
  "fallback_reason": null
}
```

欄位規則：

- `confidence` 是 `0` 到 `1` 的 parser confidence；未知時可為 `null`，不可硬填假高分。
- `source_text` 必須來自 OCR text / OCR line / future VLM trace；無來源時可為 `null`，並用 `fallback_reason` 說明。
- `source_page` 與 `source_bbox` 延用 OCR line trace；OCR 沒提供時可為 `null`。
- `parser_source` 必須標明欄位來自 `deterministic_invoice`、`llm_invoice` 或 `vlm_invoice`。
- `fallback_reason` 只在欄位缺失、格式無法 normalization 或 parser fallback 時填入，例如 `field_not_found`、`ambiguous_currency`、`ocr_not_completed`。

`DocumentFields` 的 invoice MVP 欄位：

```json
{
  "document_type": { "value": "invoice" },
  "vendor_name": { "value": "Orion Office Supplies" },
  "invoice_number": { "value": "INV-2026-001" },
  "issue_date": { "value": "2026-05-24" },
  "total_amount": { "value": 1250.0 },
  "tax_amount": { "value": 62.5 },
  "currency": { "value": "USD" },
  "line_items": [
    {
      "description": { "value": "Notebook pack" },
      "quantity": { "value": 10 },
      "unit_price": { "value": 12.5 },
      "amount": { "value": 125.0 }
    }
  ]
}
```

完整 `ParserResult`：

```json
{
  "document_id": "doc_123",
  "status": "parsed",
  "parser_source": "deterministic_invoice",
  "schema_version": "invoice_fields_v1",
  "fields": {},
  "fallback_reason": null,
  "error_message": null,
  "source_ocr_status": "completed",
  "source_ocr_updated_at": "2026-05-24T10:00:00Z",
  "updated_at": "2026-05-24T10:00:01Z",
  "trace_metadata": {
    "input": "ocr_text",
    "parser_mode": "deterministic"
  }
}
```

### Endpoint Drafts

`POST /documents/{document_id}/parse`

- Requires an existing document and completed OCR text.
- Request body is optional for MVP. If provided, `document_type` may be `invoice`; `parser_source` defaults to `deterministic_invoice`.
- Returns `ParserResult`.
- `404` when document does not exist.
- `409` when OCR is not completed or OCR text is empty; response body should include `status=failed` and `fallback_reason=ocr_not_completed` or `empty_ocr_text`.

`GET /documents/{document_id}/fields`

- Returns saved `ParserResult` when parser has completed or failed.
- Returns `status=pending` when the document exists but no parser result has been saved yet.
- Does not trigger OCR, parser, vector indexing, RAG retrieval or any async worker.
