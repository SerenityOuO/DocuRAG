# 08-02 PaddleOCR Dependency Fix

## Goal

依 08-01 的 baseline 修復 PaddleOCR dependency 與 runtime 相容性，讓 backend 能在受控環境中成功初始化 PaddleOCR。

## Scope

- 根據 08-01 的錯誤結果調整 `backend[real-ocr]` optional dependency 版本或安裝說明。
- 若 Windows 與 Docker 需要不同處理，明確拆出本機與容器的安裝指令。
- 保持 `PaddleOcrProvider` lazy import，避免未安裝 real OCR dependency 時破壞 mock flow。
- 補上最小測試或 smoke check，確認 dependency 缺失時錯誤訊息仍清楚。

## Out of Scope

- 不新增 OCR worker、queue、Redis、NATS 或 background job。
- 不新增 Qdrant、embedding、rerank、LLM、OpenAI API、Ollama 或 vLLM。
- 不新增資料庫 schema、migration、登入或權限。
- 不處理 PDF rendering、image preprocessing 或多語言 OCR 調校。

## Files likely to change

- `backend/pyproject.toml`
- `backend/app/services/ocr.py`
- `backend/tests/test_documents.py`
- `backend/README.md`
- `docs/LOCAL_DEV_SETUP.md`
- `infra/docker-compose.yml`

## Acceptance Criteria

- [ ] `py -3 -m pip install -e ".[dev,real-ocr]"` 後可以 import `paddleocr` 與 `paddlepaddle`。
- [ ] `PaddleOcrProvider` 可以初始化 engine，或在環境不支援時回傳明確 actionable error。
- [ ] 缺少 real OCR dependency 時，mock API 與預設 mock validation 仍可通過。
- [ ] Docker real OCR build 條件與限制被清楚記錄。

## Validation

- `py -3 -m pytest`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- 在已安裝 real OCR dependency 的環境執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr`
