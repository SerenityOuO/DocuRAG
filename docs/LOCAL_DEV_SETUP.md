# Local Development Setup

本文件說明 DocuRAG AgentOps MVP v0.3 的本機驗證需求，以及目前環境缺 Python、Node 或 Docker 時的修復方式。

## Required Tools

- Python 3.11 或更新版本。
- Python launcher for Windows，也就是 `py` 指令。
- `pip`。
- Node.js 與 `npm.cmd`。
- Docker Desktop，需包含 `docker` 與 `docker compose` CLI。

## Quick Check

在 repo root 執行：

```powershell
.\scripts\check-dev-env.ps1
```

若 PowerShell execution policy 阻擋 `.ps1`，使用單次 bypass，不需要修改全域設定：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1
```

此腳本會檢查：

- `where python`
- `where py`
- `py -0p`
- `python --version`
- `py --version`
- `pip`
- `node --version`
- `npm.cmd --version`
- `where docker`
- `docker --version`
- `docker compose version`

## Current Observed Issue

先前本機環境曾觀察到：

- `where python` 找不到可執行 Python。
- `py` launcher 不存在。
- `python --version` 命中 WindowsApps Python alias，但無法啟動。
- `docker` 不在 PATH。

目前 v0.3.0 驗證要求 backend pytest、local document API、frontend build、Docker build、Docker Compose healthcheck 與 Compose upload API 皆通過後，才可以建立 release tag。

## Fix Python on Windows

建議使用 Python 官方 Windows installer：

1. 安裝 Python 3.11 或更新版本。
2. 安裝時勾選 `Add python.exe to PATH`。
3. 安裝時保留 `py launcher`。
4. 重新開啟終端機。
5. 執行：

```powershell
where python
where py
py -0p
py --version
py -m pip --version
```

如果 `python` 仍指向 Microsoft Store alias，請到 Windows：

```text
Settings -> Apps -> Advanced app settings -> App execution aliases
```

關閉 `python.exe` 與 `python3.exe` 的 App Installer alias，然後重新開啟終端機。

## Fix Docker on Windows

建議安裝 Docker Desktop：

1. 安裝 Docker Desktop for Windows。
2. 啟動 Docker Desktop，等待 Docker Engine running。
3. 確認 Docker CLI 已加入 PATH。
4. 重新開啟終端機。
5. 執行：

```powershell
where docker
docker --version
docker compose version
```

## Run Backend Tests

環境修復後，在 repo root 執行：

```powershell
.\scripts\test-backend.ps1
```

若 PowerShell execution policy 阻擋 `.ps1`：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1
```

腳本會：

1. 優先使用 `py -3`，其次使用 `python`。
2. 建立 `backend/.venv`。
3. 安裝 backend 開發依賴。
4. 執行 `pytest`。

## Run Frontend

安裝 dependencies：

```powershell
cd frontend
npm.cmd install
```

啟動 dev server：

```powershell
cd frontend
npm.cmd run dev
```

frontend 預設在：

```text
http://localhost:5173
```

frontend 預設 API base URL：

```text
http://127.0.0.1:8000
```

如需覆寫，建立 `frontend/.env.local`：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Build：

```powershell
cd frontend
npm.cmd run build
```

## Manual Backend Run

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

另一個終端機驗證：

```powershell
curl http://127.0.0.1:8000/health
```

驗證 local storage API：

```powershell
curl -X POST http://127.0.0.1:8000/documents/upload -F "file=@sample.pdf"
curl http://127.0.0.1:8000/documents
curl http://127.0.0.1:8000/documents/{document_id}
```

預設資料位置：

```text
data/uploads/
data/documents.json
```

也可用 `DOCURAG_DATA_DIR` 覆寫資料根目錄。

## Phase 07 / Phase 08 Real OCR Flow

mock demo 不需要 PaddleOCR dependency，明確設定 `DOCURAG_OCR_PROVIDER=mock` 或直接呼叫 `/ocr/mock`：

```powershell
cd backend
py -3 -m pip install -e ".[dev]"
$env:DOCURAG_OCR_PROVIDER="mock"
py -3 -m uvicorn app.main:app --reload
```

Phase 08 起 provider-selected `/ocr` 預設走 PaddleOCR。若要手動嘗試 provider-selected real OCR，先用 Python 3.12 安裝 optional extra，再啟動 backend：

```powershell
cd backend
py -3.12 -m pip install -e ".[dev,real-ocr]"
$env:DOCURAG_OCR_PROVIDER="paddleocr"
py -3.12 -m uvicorn app.main:app --reload
```

real OCR smoke check：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr
```

若 PaddleOCR dependency、模型下載或 Docker 環境不可用，`-RunRealOcr` 會明確失敗；mock flow 仍應可透過 `/ocr/mock` 或 `DOCURAG_OCR_PROVIDER=mock` 重跑。這仍不是 production OCR pipeline。

## Phase 08 PaddleOCR Environment Baseline

Phase 08 real OCR dependency 目前只支援 Python 3.11 或 3.12。PaddlePaddle Windows 安裝文件列出的支援範圍到 Python 3.12，本專案 backend 則要求 Python 3.11+；因此 Windows 本機 real OCR 建議固定使用 Python 3.12。Python 3.13+ 會被 `PaddleOcrProvider` 明確拒絕，並回傳 `paddleocr_python_unsupported`，不會靜默 fallback 到 mock。

Windows CPU 安裝建議：

```powershell
cd backend
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install "paddlepaddle>=3.0,<3.1" -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
py -3.12 -m pip install -e ".[dev,real-ocr]"
py -3.12 -c "import paddle, paddleocr; paddle.utils.run_check(); print(paddle.__version__, paddleocr.__version__)"
```

Docker real OCR build 使用 `python:3.12-slim`，因此與 Windows 本機 Python 3.14 問題分開處理。需要 Docker Desktop 可正常讀取 `C:\Users\USER\.docker\config.json` 後再執行：

```powershell
$env:DOCURAG_INSTALL_REAL_OCR="true"
$env:DOCURAG_OCR_PROVIDER="paddleocr"
docker compose -f infra/docker-compose.yml up -d --build
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr
docker compose -f infra/docker-compose.yml down
```

從 repo root 執行 PaddleOCR baseline：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr
```

可選擇指定 sample image：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr -PaddleOcrSamplePath .\sample-data\documents\sample-ocr-invoice.png
```

此檢查會分段輸出：

- Python runner 與 Python 版本。
- `paddle` / `paddleocr` dependency import 與版本。
- PaddleOCR model cache 狀態；若 `~/.paddleocr` 不存在，初始化可能需要下載模型。
- PaddleOCR engine initialization；若失敗，會標示 initialization 或 model download 相關錯誤。
- `sample-data/documents/sample-ocr-invoice.png` 的 sample image OCR runtime 結果。

2026-05-21 Windows 本機 baseline：

- `py` 與 `python` 不在可用 PATH；腳本透過 `pip.exe --version` 反推到 `C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\python.exe`，版本為 Python 3.14.5。
- Python 3.14.5 超出本專案 real OCR 支援範圍；需改用 Python 3.12 重建 backend real OCR 環境。
- `paddle` import 失敗：`ModuleNotFoundError: No module named 'paddle'`。
- `C:\Users\USER\.paddleocr` 不存在，因此尚無本機 PaddleOCR model cache。
- 因 dependency import 失敗，engine initialization 與 sample image OCR runtime 皆被跳過。
- Docker CLI 可找到，但 `docker compose version` 失敗：`open C:\Users\USER\.docker\config.json: Access is denied.`；Docker real OCR baseline 需先修正 Docker config 權限後再分開驗證。

backend 以預設 PaddleOCR provider 或 `DOCURAG_OCR_PROVIDER=paddleocr` 啟動時，缺少 real OCR dependency 會回傳明確 503，不會靜默 fallback 到 mock。可重現指令：

```powershell
$env:DOCURAG_OCR_PROVIDER="paddleocr"
cd backend
py -3.12 -m uvicorn app.main:app --reload
```

另一個終端機：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr
```

2026-05-21 直接執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr` 時，當前 `http://127.0.0.1:8000` 既有 backend 的 `/health` 回傳 `0.7.0`，但 upload 回傳 `HTTP 500` 與 `Internal Server Error`；此為既有本機服務狀態，與 PaddleOCR dependency baseline 分開處理。

同日完成 08-02 後，以目前 Python 3.14.5、隔離資料目錄與 `DOCURAG_OCR_PROVIDER=paddleocr` 啟動 backend，`demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8020 -RunRealOcr` 的 mock upload -> OCR mock -> RAG flow 通過；real OCR sample 回傳：

```json
{
  "detail": {
    "provider": "paddleocr",
    "error_code": "paddleocr_python_unsupported",
    "error": "PaddleOCR local runtime is supported only on Python 3.11 or 3.12 in this project. Current Python is 3.14.5. Install Python 3.12, then run py -3.12 -m pip install -e \".[dev,real-ocr]\" from the backend directory."
  }
}
```

2026-05-21 08-02 validation notes：

- `py -3 -m pip install -e ".[dev,real-ocr]"` 與 `py -3 -m pytest` 皆因本機 `py.exe` 無法執行而失敗：`指定的登入工作階段不存在。可能已被終止。`
- 使用 08-01 偵測到的 Python fallback 執行 `C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest`，結果 `47 passed`；此驗證只確認 mock flow 與 unsupported-Python failure path，不代表 real OCR dependency 已安裝。
- 直接執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 仍會打到目前既有 `http://127.0.0.1:8000` 服務，該服務 upload 回傳 `HTTP 500` 與 `Internal Server Error`。
- 以隔離資料目錄啟動 mock backend 後，`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8019` 通過。
- 在已安裝 real OCR dependency 的環境需改用 Python 3.12 重跑 `demo-smoke-test.ps1 -RunRealOcr`；目前本機 Python 3.14.5 會得到預期的 `paddleocr_python_unsupported` actionable error。

2026-05-21 08-03 validation notes：

- Phase 08 決策：不設定 `DOCURAG_OCR_PROVIDER` 時，provider-selected `/ocr` 預設走 `paddleocr`；需要 mock override 時，設定 `DOCURAG_OCR_PROVIDER=mock` 或直接呼叫 `/documents/{document_id}/ocr/mock`。
- `py -3 -m pytest` 仍因本機 `py.exe` 無法執行而失敗：`指定的登入工作階段不存在。可能已被終止。`
- 使用 fallback Python 執行 `C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest`，結果 `48 passed`；新增測試覆蓋預設 provider 與 `DOCURAG_OCR_PROVIDER=mock` override。
- `npm.cmd run build` 在一般 sandbox 內因 esbuild 讀取上層目錄被拒失敗；以同一命令取得許可後重跑通過。
- 直接執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 仍會打到目前既有 `http://127.0.0.1:8000` 服務，該服務 upload 回傳 `HTTP 500` 與 `Internal Server Error`。
- 以隔離資料目錄與 `DOCURAG_OCR_PROVIDER=mock` 啟動 backend 後，`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8021` 通過，確認 mock override flow 可完整重跑。
- 以隔離資料目錄、不設定 `DOCURAG_OCR_PROVIDER` 啟動 backend 後，`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8022 -RunRealOcr` 會進入預設 PaddleOCR provider，但目前 Python 3.14.5 不支援 real OCR，因此回傳 `503` 與 `paddleocr_python_unsupported`。這確認沒有 fallback 到 mock；真正 `status=completed` 的 sample image OCR 需在 Python 3.12 且已安裝 `backend[real-ocr]` 的環境重跑。
- 手動上傳 `sample-data/documents/sample-ocr-invoice.png` 後呼叫 `POST /documents/{document_id}/ocr`，目前同樣回傳 `503` / `paddleocr_python_unsupported`；document id 範例為 `614223c1-9389-40be-9bac-9c3618dfbed5`。

2026-05-21 Python 3.12 follow-up validation：

- 安裝 Python 3.12.10 後，`py -3.12 -m pip install -e ".[dev,real-ocr]"` 會因既有 `.egg-info` Windows 檔案鎖失敗；改以逐項安裝 runtime/test dependency 完成驗證環境。
- `paddlepaddle>=3.0,<3.4` 會安裝 PaddlePaddle 3.3.1，sample OCR 在 Windows CPU 上失敗：`OneDnnContext does not have the input Filter`。因此 `backend[real-ocr]` 收斂為 `paddlepaddle>=3.0,<3.1`，實測使用 PaddlePaddle 3.0.0。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr` 通過；`paddle=3.0.0`、`paddleocr=2.10.0`，sample image OCR `recognized_lines=4`。
- 以隔離資料目錄與 Python 3.12 backend 啟動 `http://127.0.0.1:8023` 後，`demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8023` 通過。
- 同一 backend 執行 `demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8023 -RunRealOcr` 通過；provider-selected OCR 回傳 `status=completed`，並通過 saved OCR、processing、latest job 與 chunks 檢查。

## Docker Validation

```powershell
docker build -t docurag-backend ./backend
docker compose -f infra/docker-compose.yml build
docker compose -f infra/docker-compose.yml up -d
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/documents/upload -F "file=@sample.pdf"
curl http://127.0.0.1:8000/documents
docker compose -f infra/docker-compose.yml down
```

Real OCR Docker dependency 可用 build arg 開啟，預設關閉：

```powershell
$env:DOCURAG_INSTALL_REAL_OCR="true"
$env:DOCURAG_OCR_PROVIDER="paddleocr"
docker compose -f infra/docker-compose.yml up -d --build
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr
docker compose -f infra/docker-compose.yml down
```

## Current Verification Notes

- Python: `python` / `py` 可能指向不可執行的 WindowsApps alias；`scripts/check-dev-env.ps1` 與 `scripts/test-backend.ps1` 會在必要時透過可執行的 `pip.exe --version` 反推實際 `python.exe`。
- Backend tests: `scripts/test-backend.ps1` 會建立或使用 `backend/.venv`，安裝 backend dev dependencies，並執行 `pytest`。
- v0.1.0: pytest 與本機 `GET /health` HTTP 驗證已完成。
- v0.2.0: frontend build、Docker build 與 Docker Compose healthcheck 已納入 release 驗證。
- v0.3.0: local storage upload、document list/detail、frontend list UI、Docker Compose upload API 已納入 release 驗證。
