# Scanned PDF Demo and Phase 34 Release Sync

## Goal

完成 Phase 34 `v0.34.0` release sync，讓 scanned PDF / multi-page OCR pipeline 成為可展示的文件處理能力。

## Scope

- 建立 scanned PDF demo smoke，驗證 PDF rendering、page image、OCR、chunks、parser / RAG handoff。
- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.34.0`。
- 更新 README、README_DEV、backend / frontend README、TODO 與 ROADMAP。
- 記錄 limitation：不是完整 table reconstruction 或 production OCR accuracy tuning。

## Out of Scope

- 不新增 layout analysis、table reconstruction、human correction workflow 或 full production OCR benchmark。
- 不修改 RAG ranking、VLM parser strategy、Agent planner 或 eval dashboard。
- 不新增 K8s、GPU scheduler 或 autoscaling。

## Release Impact

- Target version: `v0.34.0`
- Version bump required: yes
- 原因：Phase 34 完成 scanned PDF / multi-page OCR user-facing release。

## Files likely to change

- `backend/`
- `frontend/`
- `scripts/`
- `infra/docker-compose.yml`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `tasks/phase-34-production-ocr-scanned-pdf/34-04-scanned-pdf-demo-release-sync.md`

## Acceptance Criteria

- [ ] `/health` 回傳 `0.34.0`。
- [ ] Scanned PDF demo smoke 通過，並產生 page-aware OCR chunks。
- [ ] README / README_DEV 清楚說明支援 scanned PDF OCR baseline，但不宣稱完整 layout understanding。
- [ ] ROADMAP / TODO 記錄 Phase 34 validation 結果。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Scanned PDF demo smoke script。
- Browser 檢查 PDF upload / OCR status surface，桌面與手機寬度無 horizontal overflow。
- `rg -n "v0.34.0|Phase 34|scanned PDF|PDF rendering|page image|multi-page OCR" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend scripts tasks/phase-34-production-ocr-scanned-pdf`
- `git diff --check`
