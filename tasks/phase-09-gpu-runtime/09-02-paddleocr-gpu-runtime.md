# 09-02 PaddleOCR GPU Runtime Baseline

## Goal

在不破壞目前 Python 3.12 CPU baseline 的前提下，建立 PaddleOCR GPU runtime 安裝與驗證路徑，讓 RTX 5070 Ti 可用 GPU 跑 provider-selected OCR。

## Scope

- 評估並選定 PaddlePaddle GPU wheel 來源與 CUDA runtime，例如 `paddlepaddle-gpu` 的 `cu129` index。
- 將 CPU 與 GPU real OCR dependency 拆清楚，避免 `backend[real-ocr]` 同時拉到 CPU 與 GPU PaddlePaddle。
- 更新 dev env check，輸出 `paddle.device.is_compiled_with_cuda()`、`paddle.device.get_device()` 與 sample OCR runtime。
- 補齊 Windows 本機啟動與驗證文件。
- 以 sample image 驗證 PaddleOCR GPU path 能完成 provider-selected OCR。

## Out of Scope

- 不處理 OCR 中文 language；由 `09-01` 負責。
- 不接 LLM serving、vLLM、Ollama、embedding、Qdrant 或 rerank。
- 不新增 worker queue、Redis、NATS、資料庫 schema、登入或權限。
- 不保證所有 CUDA / driver / wheel 組合；本 ticket 只建立本機 RTX 5070 Ti 的可重現 baseline。

## Files likely to change

- `backend/pyproject.toml`
- `scripts/check-dev-env.ps1`
- `scripts/test-backend.ps1`
- `scripts/demo-smoke-test.ps1`
- `docs/LOCAL_DEV_SETUP.md`
- `backend/README.md`
- `README.md`

## Acceptance Criteria

- [ ] 文件明確區分 CPU OCR baseline 與 GPU OCR baseline。
- [ ] GPU OCR 安裝指令不會覆蓋或破壞既有 mock path。
- [ ] `check-dev-env.ps1 -CheckPaddleOcr` 能顯示 Paddle 是否為 CUDA build。
- [ ] 在 RTX 5070 Ti 上，provider-selected OCR 可以用 GPU path 完成 sample image OCR，或回傳清楚 actionable error。

## Validation

- `nvidia-smi`
- `nvcc --version`
- `python -c "import paddle; print(paddle.__version__); print(paddle.device.is_compiled_with_cuda()); print(paddle.device.get_device()); paddle.utils.run_check()"`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr`
