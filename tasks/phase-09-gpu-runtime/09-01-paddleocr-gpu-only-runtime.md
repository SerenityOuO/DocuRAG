# 09-01 PaddleOCR GPU-Only Runtime Baseline

## Goal

讓 provider-selected PaddleOCR 在 RTX 5070 Ti 上以 GPU 模式跑起來，並把 real OCR runtime 收斂為 GPU-only；不再維護 CPU PaddleOCR baseline。

## Scope

- 將 real OCR 安裝與驗證路徑改成 GPU-only。
- 移除或取代目前 `backend[real-ocr]` 內的 CPU `paddlepaddle` dependency。
- 選定 PaddlePaddle GPU wheel 與 CUDA index，優先評估 `paddlepaddle-gpu` + `cu129`，因目前 Windows GPU 官方 stable index 已提供 CUDA 12.9 wheel。
- 更新 dev env check，若 Paddle 不是 CUDA build，`-CheckPaddleOcr` 必須明確失敗，不 fallback CPU。
- 更新 README / backend README / local dev docs，明確標示本專案 real OCR 需要 GPU runtime。
- 以 sample image 驗證 provider-selected OCR 可以在 GPU runtime 完成。

## Out of Scope

- 不處理中文模型選擇；由 `09-02` 負責。
- 不接 LLM serving、vLLM、Ollama、embedding、Qdrant 或 rerank。
- 不新增 worker queue、Redis、NATS、資料庫 schema、登入或權限。
- 不調整 OCR quality tuning、PDF rendering、image preprocessing 或版面分析。

## Release Impact

- Target version: `v0.9.0`。
- Version bump required: no，本 ticket 是 Phase 09 的第一個 runtime baseline，最終版本更新由 `09-02` 收斂。
- 完成後仍需更新 TODO 與相關文件，標示 Phase 09 尚未 release complete。

## Files likely to change

- `backend/pyproject.toml`
- `scripts/check-dev-env.ps1`
- `scripts/test-backend.ps1`
- `scripts/demo-smoke-test.ps1`
- `docs/LOCAL_DEV_SETUP.md`
- `backend/README.md`
- `README.md`

## Acceptance Criteria

- [ ] `backend[real-ocr]` 不再安裝 CPU `paddlepaddle`。
- [ ] PaddleOCR baseline 在非 CUDA Paddle build 時明確失敗，錯誤訊息要求安裝 GPU runtime。
- [ ] `paddle.device.is_compiled_with_cuda()` 為 `True`，且 `paddle.utils.run_check()` 通過。
- [ ] provider-selected OCR 用 sample image 跑完並產生 `status=completed`。
- [ ] mock OCR path 仍可用，但不作為 real OCR fallback。

## Validation

- `nvidia-smi`
- `nvcc --version`
- `python -c "import paddle; print(paddle.__version__); print(paddle.device.is_compiled_with_cuda()); print(paddle.device.get_device()); paddle.utils.run_check()"`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1 -CheckPaddleOcr`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunRealOcr`
