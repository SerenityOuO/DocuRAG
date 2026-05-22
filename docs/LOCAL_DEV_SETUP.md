# Local Development Setup

本文件說明 DocuRAG AgentOps MVP v0.3 的本機驗證需求，以及目前環境缺 Python、Node 或 Docker 時的修復方式。

## Required Tools

- Python 3.12。
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
- `py -3.12 --version`
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

1. 安裝 Python 3.12。
2. 安裝時勾選 `Add python.exe to PATH`。
3. 安裝時保留 `py launcher`。
4. 重新開啟終端機。
5. 執行：

```powershell
where python
where py
py -0p
py --version
py -3.12 --version
py -3.12 -m pip --version
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

## v0.7 / v0.9.1 Real OCR Flow

mock demo 不需要 PaddleOCR dependency，明確設定 `DOCURAG_OCR_PROVIDER=mock` 或直接呼叫 `/ocr/mock`：

```powershell
cd backend
py -3.12 -m pip install -e ".[dev]"
$env:DOCURAG_OCR_PROVIDER="mock"
py -3.12 -m uvicorn app.main:app --reload
```

v0.8 起 provider-selected `/ocr` 預設走 PaddleOCR。Phase 09 起 real OCR 只支援 PaddlePaddle GPU / CUDA runtime；若要手動嘗試 provider-selected real OCR，先用 Python 3.12 安裝 CUDA wheel 與 optional extra，再啟動 backend：

```powershell
cd backend
py -3.12 -m pip install "paddlepaddle-gpu==3.3.0" -i https://www.paddlepaddle.org.cn/packages/stable/cu129/
py -3.12 -m pip install -e ".[dev,real-ocr]"
$env:DOCURAG_OCR_PROVIDER="paddleocr"
py -3.12 -m uvicorn app.main:app --reload
```

PP-OCRv4 mobile 中文 / 中英混合模型預設：

| 設定 | 預設值 | 預期 cache / model directory |
|---|---|---|
| `DOCURAG_OCR_LANGUAGE` | `ch` | - |
| `DOCURAG_OCR_VERSION` | `PP-OCRv4` | - |
| `DOCURAG_OCR_DET_MODEL_NAME` | `PP-OCRv4_mobile_det` | `%USERPROFILE%\.paddleocr\whl\det\ch\ch_PP-OCRv4_det_infer` |
| `DOCURAG_OCR_REC_MODEL_NAME` | `PP-OCRv4_mobile_rec` | `%USERPROFILE%\.paddleocr\whl\rec\ch\ch_PP-OCRv4_rec_infer` |
| `DOCURAG_OCR_CLS_MODEL_NAME` | `ch_ppocr_mobile_v2.0_cls` | `%USERPROFILE%\.paddleocr\whl\cls\ch\ch_ppocr_mobile_v2.0_cls_infer` |
| `DOCURAG_OCR_USE_ANGLE_CLS` | `false` | 直立 demo sample 不啟用 angle classifier |
| `DOCURAG_OCR_DET_LIMIT_SIDE_LEN` | `960` | 保留 PaddleOCR mobile detection 預設尺寸上限 |
| `DOCURAG_OCR_REC_BATCH_NUM` | `6` | 保留 PaddleOCR recognition 預設 batch |

可用 `DOCURAG_OCR_DET_MODEL_DIR`、`DOCURAG_OCR_REC_MODEL_DIR`、`DOCURAG_OCR_CLS_MODEL_DIR` 指到已下載的 inference model directory。PP-OCRv4 mobile 中文 recognition 主要驗證簡中 / 中英數字；繁中 sample 只記錄結果與限制，不在本 ticket 自動切到 `chinese_cht_PP-OCRv3_rec`。

real OCR smoke check：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr
```

若 PaddleOCR GPU dependency、CUDA build、模型下載或 Docker 環境不可用，`-RunRealOcr` 會明確失敗；mock flow 仍應可透過 `/ocr/mock` 或 `DOCURAG_OCR_PROVIDER=mock` 重跑。這仍不是 production OCR pipeline。

## v0.9 PaddleOCR GPU Environment Baseline

v0.8 起本專案 backend runtime 固定使用 Python 3.12。Python 3.13+ 或 3.11 會被 `PaddleOcrProvider` 明確拒絕，並回傳 `paddleocr_python_unsupported`，不會靜默 fallback 到 mock。Phase 09 起 PaddleOCR real provider 還會要求 `paddle.device.is_compiled_with_cuda()` 為 `True` 且 `paddle.utils.run_check()` 通過；CPU PaddlePaddle 會回傳 `paddleocr_gpu_required`。

Windows GPU 安裝建議：

```powershell
cd backend
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install "paddlepaddle-gpu==3.3.0" -i https://www.paddlepaddle.org.cn/packages/stable/cu129/
py -3.12 -m pip install -e ".[dev,real-ocr]"
py -3.12 -c "import paddle, paddleocr; print(paddle.__version__, paddleocr.__version__); print(paddle.device.is_compiled_with_cuda()); print(paddle.device.get_device()); paddle.utils.run_check()"
```

Docker real OCR build 使用 `python:3.12-slim` 並在 build arg 開啟時安裝 CUDA 12.9 `paddlepaddle-gpu` wheel；需要 Docker Desktop 可正常讀取 `C:\Users\USER\.docker\config.json` 且容器環境可使用 GPU 後再執行：

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr -PaddleOcrSamplePath .\sample-data\documents\sample-ocr-zh-tw.png
```

此檢查會分段輸出：

- Python runner 與 Python 版本。
- `nvidia-smi` 與 `nvcc --version`。
- `paddle` / `paddleocr` dependency import 與版本。
- `paddle.device.is_compiled_with_cuda()`、`paddle.device.get_device()` 與 `paddle.utils.run_check()`。
- PaddleOCR model cache 狀態；若 `~/.paddleocr` 不存在，初始化可能需要下載模型。
- PP-OCRv4 mobile det / rec / cls model selection 與預期 model directory。
- PaddleOCR engine initialization 與 `engine_init_ms`；若失敗，會標示 initialization 或 model download 相關錯誤。
- `sample-data/documents/sample-ocr-invoice.png` 或 `sample-data/documents/sample-ocr-zh-tw.png` 的 sample image OCR runtime 結果，包含 image size、`use_angle_cls`、`det_limit_side_len`、`rec_batch_num`、`inference_ms` 與 `normalization_ms`。

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
    "error": "PaddleOCR local runtime is supported only on Python 3.12 in this project. Current Python is 3.14.5. Install Python 3.12, then run py -3.12 -m pip install -e \".[dev,real-ocr]\" from the backend directory."
  }
}
```

2026-05-21 08-02 validation notes：

- 舊版 Python launcher 預設命令曾因本機 `py.exe` 無法執行而失敗：`指定的登入工作階段不存在。可能已被終止。`
- 使用 08-01 偵測到的 Python fallback 執行 `C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest`，結果 `47 passed`；此驗證只確認 mock flow 與 unsupported-Python failure path，不代表 real OCR dependency 已安裝。
- 直接執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 仍會打到目前既有 `http://127.0.0.1:8000` 服務，該服務 upload 回傳 `HTTP 500` 與 `Internal Server Error`。
- 以隔離資料目錄啟動 mock backend 後，`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8019` 通過。
- 在已安裝 real OCR dependency 的環境需改用 Python 3.12 重跑 `demo-smoke-test.ps1 -RunRealOcr`；目前本機 Python 3.14.5 會得到預期的 `paddleocr_python_unsupported` actionable error。

2026-05-21 08-03 validation notes：

- v0.8 決策：不設定 `DOCURAG_OCR_PROVIDER` 時，provider-selected `/ocr` 預設走 `paddleocr`；需要 mock override 時，設定 `DOCURAG_OCR_PROVIDER=mock` 或直接呼叫 `/documents/{document_id}/ocr/mock`。
- 舊版 Python launcher 預設命令仍因本機 `py.exe` 無法執行而失敗：`指定的登入工作階段不存在。可能已被終止。`
- 使用 fallback Python 執行 `C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest`，結果 `48 passed`；新增測試覆蓋預設 provider 與 `DOCURAG_OCR_PROVIDER=mock` override。
- `npm.cmd run build` 在一般 sandbox 內因 esbuild 讀取上層目錄被拒失敗；以同一命令取得許可後重跑通過。
- 直接執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` 仍會打到目前既有 `http://127.0.0.1:8000` 服務，該服務 upload 回傳 `HTTP 500` 與 `Internal Server Error`。
- 以隔離資料目錄與 `DOCURAG_OCR_PROVIDER=mock` 啟動 backend 後，`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8021` 通過，確認 mock override flow 可完整重跑。
- 以隔離資料目錄、不設定 `DOCURAG_OCR_PROVIDER` 啟動 backend 後，`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8022 -RunRealOcr` 會進入預設 PaddleOCR provider，但目前 Python 3.14.5 不支援 real OCR，因此回傳 `503` 與 `paddleocr_python_unsupported`。這確認沒有 fallback 到 mock；真正 `status=completed` 的 sample image OCR 需在 Python 3.12 且已安裝 `backend[real-ocr]` 的環境重跑。
- 手動上傳 `sample-data/documents/sample-ocr-invoice.png` 後呼叫 `POST /documents/{document_id}/ocr`，目前同樣回傳 `503` / `paddleocr_python_unsupported`；document id 範例為 `614223c1-9389-40be-9bac-9c3618dfbed5`。

2026-05-21 Python 3.12 follow-up validation：

- 安裝 Python 3.12.10 後，`py -3.12 -m pip install -e ".[dev,real-ocr]"` 會因既有 `.egg-info` Windows 檔案鎖失敗；改以逐項安裝 runtime/test dependency 完成驗證環境。
- v0.8 曾以 Windows CPU PaddlePaddle 3.0.0 完成 sample OCR baseline；Phase 09 已移除 CPU PaddleOCR baseline，`backend[real-ocr]` 改為 `paddlepaddle-gpu==3.3.0`，需使用 CUDA 12.9 stable index 安裝。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr` 現在會在非 CUDA Paddle build 明確失敗；需看到 `is_compiled_with_cuda=True` 與 `paddle.utils.run_check()` 通過後才算 real OCR baseline 通過。
- 以隔離資料目錄與 Python 3.12 backend 啟動 `http://127.0.0.1:8023` 後，`demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8023` 通過。
- 同一 backend 執行 `demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8023 -RunRealOcr` 通過；provider-selected OCR 回傳 `status=completed`，並通過 saved OCR、processing、latest job 與 chunks 檢查。

2026-05-22 Phase 09 validation notes：

- `nvidia-smi` 通過，GPU 為 NVIDIA GeForce RTX 5070 Ti，driver 596.49。
- `nvcc --version` 通過，CUDA compiler 為 12.8；PaddlePaddle GPU install 指令仍依官方 stable CUDA 12.9 wheel 記錄。
- 已安裝官方 Python 3.12.10，並讓 `python` 與 `py -3.12` 優先指向 `C:\Users\USER\AppData\Local\Programs\Python\Python312\python.exe`，避開 WindowsApps Python Manager / Store alias。
- 已安裝 `paddlepaddle-gpu==3.3.0`、PaddleOCR 2.10.0 與 CUDA 12.9 runtime wheels；全域 Python 與 `backend/.venv` 皆通過 `paddle.device.is_compiled_with_cuda() == True`、`paddle.device.get_device() == gpu:0` 與 `paddle.utils.run_check()`。
- `check-dev-env.ps1 -CheckPaddleOcr` 通過；sample invoice OCR `recognized_lines=4`，preview 包含 `DocuRAG OcR Demo Invoice`、`Invoice: OCR-2026-001` 與 `Total: USD 42.00`。
- `check-dev-env.ps1 -CheckPaddleOcr -PaddleOcrSamplePath .\sample-data\documents\sample-ocr-zh-tw.png` 通過；繁中 sample OCR `recognized_lines=4`，preview 包含 `DocuRAG 繁中 OCR 測試`、`發票號碼：OCR-2026-009` 與 `客户：星河科技股份有限公司`。
- 以隔離資料目錄與 `backend/.venv` 啟動 `http://127.0.0.1:8024` 後，`demo-smoke-test.ps1 -ApiBaseUrl http://127.0.0.1:8024 -RunRealOcr` 通過；同一 backend 針對 `sample-ocr-zh-tw.png` 的 provider-selected OCR 也回傳 `status=completed`。
- 繁中 sample 實際 provider-selected OCR 結果為 `DocuRAG 繁中 OCR 測試`、`發票號碼：OCR-2026-009`、`客户：星河科技股份有限公司`、`總計 : NT$ 12,345`，平均 confidence `0.9525`。其中 `客戶` 被辨識為簡中 `客户`，此為 PP-OCRv4 mobile 對繁中支援的已知限制；後續候選仍是 `chinese_cht_PP-OCRv3_rec`，本 ticket 不自動切換。

2026-05-22 Phase 09 performance hardening validation notes：

- `09-03` 已將 backend lifespan startup 接到 `PaddleOcrProvider.preload()`；selected provider 為 PaddleOCR 時會 preload engine，後續 provider-selected OCR request 重用同一個 provider / engine。
- `POST /documents/{document_id}/ocr/mock` 仍使用 mock override，不觸發 PaddleOCR preload。
- `09-04` 已在 OCR result `extracted_fields` 加入 `timing_engine_preload_ms`、`timing_engine_load_ms`、`timing_inference_ms`、`timing_normalization_ms`、`timing_total_ms` 與 `engine_preloaded_before_request`。
- backend log 會輸出 PaddleOCR startup preload 與每次 OCR completed timing summary。
- 以 TestClient lifespan 手動觸發 startup preload 後，連續對 `sample-ocr-invoice.png` 執行兩次 provider-selected OCR，兩次皆回傳 `status=completed`、`line_count=4`，startup log 顯示 `PaddleOCR provider preloaded during backend startup`。

v0.9.1 local tuning baseline：

| Config | Sample | Image size | Engine init | First OCR | Second OCR | Lines |
|---|---|---:|---:|---:|---:|---:|
| `cls=True`, `det_limit_side_len=960` | `sample-ocr-invoice.png` | 760x260 | 4895.57 ms | 567.09 ms | 52.96 ms | 4 |
| `cls=True`, `det_limit_side_len=960` | `sample-ocr-zh-tw.png` | 1000x420 | 4895.57 ms | 90.27 ms | 65.28 ms | 4 |
| `cls=False`, `det_limit_side_len=960` | `sample-ocr-invoice.png` | 760x260 | 3749.86 ms | 84.18 ms | 39.81 ms | 4 |
| `cls=False`, `det_limit_side_len=960` | `sample-ocr-zh-tw.png` | 1000x420 | 3749.86 ms | 53.75 ms | 51.39 ms | 4 |
| `cls=False`, `det_limit_side_len=736` | `sample-ocr-invoice.png` | 760x260 | 3712.03 ms | 89.88 ms | 40.21 ms | 4 |
| `cls=False`, `det_limit_side_len=736` | `sample-ocr-zh-tw.png` | 1000x420 | 3712.03 ms | 71.28 ms | 51.14 ms | 4 |

決策：

- `cls=False` 在兩張直立 sample 上保留相同行數與文字預覽，且首張推論明顯較快，因此 v0.9.1 預設 `DOCURAG_OCR_USE_ANGLE_CLS=false`。
- `det_limit_side_len=736` 沒有穩定收益，保留 `DOCURAG_OCR_DET_LIMIT_SIDE_LEN=960`。
- startup warmup 可把第一張圖的推論成本移到啟動階段，但需要啟動時跑 sample image inference；本 patch 不採用預設 warmup，避免 backend startup 依賴 runtime sample。

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
