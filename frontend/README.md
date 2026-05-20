# DocuRAG AgentOps Frontend

最小 Vue 3 + Vite demo UI，用來檢查 backend health、上傳文件、顯示文件列表，並查看單一文件 metadata JSON。

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

## Document List UI

v0.3.0 UI 支援：

- `GET /health` 顯示 backend 狀態。
- `POST /documents/upload` 上傳本機文件。
- 上傳成功後自動刷新 `GET /documents` 文件列表。
- 文件列表顯示 filename、status、size、created_at 與 content_type。
- 點選 filename 後呼叫 `GET /documents/{document_id}`，並顯示 metadata JSON。
