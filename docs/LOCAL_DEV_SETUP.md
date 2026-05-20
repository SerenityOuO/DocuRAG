# Local Development Setup

本文件說明 DocuRAG AgentOps MVP v0.1 的本機驗證需求，以及目前環境缺 Python 或 Docker 時的修復方式。

## Required Tools

- Python 3.11 或更新版本。
- Python launcher for Windows，也就是 `py` 指令。
- `pip`。
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
- `where docker`
- `docker --version`
- `docker compose version`

## Current Observed Issue

目前本機環境觀察到：

- `where python` 找不到可執行 Python。
- `py` launcher 不存在。
- `python --version` 命中 WindowsApps Python alias，但無法啟動。
- `docker` 不在 PATH。

這代表 backend 程式碼已存在；目前 `python` / `py` alias 不可用，但腳本可透過 `pip.exe` 反推實際 Python 並執行 `pytest`、`uvicorn`。Docker CLI 仍不在 PATH，因此 Docker build 尚未驗證。

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

## Manual Backend Run

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

另一個終端機驗證：

```powershell
curl http://127.0.0.1:8000/health
```

## Docker Validation

```powershell
docker build -t docurag-backend ./backend
docker compose -f infra/docker-compose.yml build
docker compose -f infra/docker-compose.yml up
```

## Current Verification Notes

- Python: `python` / `py` 可能指向不可執行的 WindowsApps alias；`scripts/check-dev-env.ps1` 與 `scripts/test-backend.ps1` 會在必要時透過可執行的 `pip.exe --version` 反推實際 `python.exe`。
- Backend tests: `scripts/test-backend.ps1` 會建立或使用 `backend/.venv`，安裝 backend dev dependencies，並執行 `pytest`。
- v0.1.0: pytest 與本機 `GET /health` HTTP 驗證已完成。
- Docker: `docker` CLI 目前不在 PATH，Docker build / Compose 尚未驗證。
