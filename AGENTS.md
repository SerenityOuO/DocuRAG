# 全局開發配置

## DocuRAG AgentOps 小 Ticket 開發規範

本專案後續開發必須採用 ticket-first 工作流。Codex 每次只處理一張 `tasks/` 底下的任務票，並且在開始前先閱讀該 ticket 的 `Goal`、`Scope`、`Out of Scope`、`Files likely to change`、`Acceptance Criteria` 與 `Validation`。

執行原則：

- 一張 ticket 應小到 Codex 一次可以完成，完成後應可單獨 commit。
- 若任務超出 ticket 的 `Scope`，先停止並回報，不要順手擴張。
- 嚴格遵守 `Out of Scope`，尤其不要提前實作 OCR、RAG、Qdrant、Redis、NATS、vLLM、登入、權限或資料庫 schema。
- 實作前先檢查 `README.md`、`TODO.md`、`docs/PRD.md`、`docs/ARCHITECTURE.md`、`docs/ROADMAP.md` 與當前 ticket。
- 每次完成後更新 `TODO.md` 中對應 checklist，並執行 ticket 指定的 validation。
- 文件 ticket 只改 Markdown；程式 ticket 才能新增或修改程式碼。
- 優先最小改動、貼合既有風格，不為未來擴充提前抽象化。

建議執行順序：

1. `tasks/phase-00-bootstrap/00-01-repo-structure.md`
2. `tasks/phase-00-bootstrap/00-02-project-docs.md`
3. `tasks/phase-01-backend-bootstrap/01-01-backend-healthcheck.md`
4. `tasks/phase-01-backend-bootstrap/01-02-backend-docker.md`
5. `tasks/phase-02-document-foundation/02-01-document-upload-api.md`
6. `tasks/phase-02-document-foundation/02-02-document-metadata-schema.md`

## 最重要
- Always reply in Traditional Chinese. 
- 除非用戶明確要求英文，否則所有回覆使用繁體中文。
- 代碼標識符、命令、日志、報錯信息保持原始語言；其餘解釋用繁體中文。
- 如果不小心用英文作答，立即用中文重寫同一答案（不要只追加一句中文）
- 請不要過度封裝函數。除非邏輯會被覆用、能顯著提升可讀性，或有明確業務邊界，否則保持內聯實現。不要創建只調用另一個函數的 wrapper，也不要為了未來擴展創建抽象層。優先最小改動、貼合現有代碼風格。

## 核心原則
- **維持質量與一致性** — 徹底執行自動檢查
- **事實確認** — 自行確認信息來源，不將猜測作為事實陳述
- **優先現有文件** — 優先編輯現有文件而非創建新文件
- **任務性質確認** — 確認任務是否需要改動代碼，如果是計劃或技術文檔不要動源代碼

---

## 通用交互規範

- 用中文回答，優先解決核心問題
- 直接進入 ultrathink 模式，如果分析代碼問題和修覆bug，啟用sequential-thinking
- 如果有思考，請詳細說明你的思考過程，再給出答案
- **先驗證再判斷** — 遇到可疑信息（新聞、聲明、技術更新等），必須先用工具（WebFetch/WebSearch）查證事實，再給出結論。禁止"光質疑不驗證"或"光分析邏輯不看證據"
- 解決覆雜問題前先在聯網搜索是否有相似方案參考
- 當需求不明確時先提出 1-2 個關鍵問題確認細節
- 分析問題背後的問題，預測代碼可能導致的隱患
- 當創建或更新 TODO 時向用戶展示
- 修覆完成要自己做驗證測試，遞歸修覆最少 3 輪
- 所有需要用戶確定的選項提供交互式選擇菜單


---

## ⚠️ 執行環境：Windows（強制規範）

### 核心原則
**文件操作用專用工具，系統命令用 Bash**

### 工具映射表

| 操作 | 使用工具 | 禁止 | 原因 |
|------|---------|------|------|
| 讀文件 | Read | cat/head/tail/Get-Content | 專用工具支持分塊、編碼檢測 |
| 搜文件 | Glob | find/ls/Get-ChildItem | 跨平台一致性 |
| 搜內容 | Grep | grep/rg/Select-String | 自動處理權限和編碼 |
| 編輯 | Edit | sed/awk | 觸發 VSCode diff view |
| 創建 | Write | echo >/cat <<EOF | 保證原子性寫入 |
| 系統命令 | Bash | PowerShell/CMD 命令 | Git、npm、docker 等 |

**Bash 僅用於**：git、pnpm、npm、vite、tsc、docker、node 等系統命令

**環境說明**：
- Bash 運行在 `/usr/bin/bash`（Git Bash）
- 不支持 PowerShell 命令（Get-ChildItem、Select-String 等）
- 環境變量使用 Linux 語法（`$PATH` 而非 `%PATH%`）

---

### Windows 特有規則（強制執行）

#### 1. 路徑處理規範（必須遵守）

**強制要求**：
- **所有包含空格的路徑必須用雙引號包裹**
- **所有中文路徑必須用雙引號包裹**
- **統一使用正斜杠 `/` 作為路徑分隔符**（推薦）
- **禁止混用正斜杠和反斜杠**

**正確示例**：
bash
# ✅ 空格路徑
cd "C:/Program Files/nodejs"
git add "src/my file.ts"

# ✅ 中文路徑
cd "C:/Users/張三/Documents"
pnpm install --prefix "D:/項目/前端代碼"

# ✅ 統一正斜杠
cd C:/Users/X1/Projects/myapp

**錯誤示例**：
bash
# ❌ 空格路徑未加引號
cd C:/Program Files/nodejs

# ❌ 混用路徑分隔符
cd C:\Users/張三\Documents

# ❌ 中文路徑未加引號
git add src/文件名.ts

**特殊字符處理**：
bash
# 文件名包含特殊字符時必須加引號
git add "src/config&settings.ts"
git commit -m "fix: 更新配置文件"

---

#### 2. Git Bash 特性說明

**盤符訪問規則**：
- Windows 格式：`C:\Users\X1`
- Git Bash 格式：`/c/Users/X1` 或 C:/Users/X1
- pwd 命令返回：`/d/Projects/myapp`（自動轉換）

**環境變量語法**：
bash
# ✅ Git Bash 使用 Linux 語法
echo $PATH
export NODE_ENV=production

# ❌ 不要使用 PowerShell 語法
echo $env:PATH  # 無效

**工作目錄切換**：
bash
# ✅ 推薦：使用絕對路徑 + 正斜杠
cd C:/Users/X1/Projects

# ✅ 可選：Git Bash 盤符格式
cd /c/Users/X1/Projects

# ⚠️ 避免：頻繁 cd 會導致工作目錄混亂
# 推薦：直接在命令中使用絕對路徑
pnpm test C:/Users/X1/Projects/myapp/tests

---

#### 3. 命令字符串規範（強制執行）

⚠️ **嚴禁 HTML 實體編碼污染 Bash 命令**

**核心要求**：
- **Bash 命令中絕對不能出現 HTML 實體編碼**（如 &amp; &lt; &gt; &quot; 等）
- **所有傳遞給 Bash 工具的參數必須是純文本格式**
- **使用 Bash 原生轉義方式（引號、反斜杠）而不是 HTML 編碼**

**錯誤示例**：
bash
# ❌ HTML 實體編碼導致語法錯誤
cd "F:/Tests/month-report" &amp;&amp; node -e "console.log('test')"
# 報錯：syntax error near unexpected token `;&'

# ❌ 其他 HTML 實體也會導致問題
git add . &amp;&amp; git commit -m &quot;fix bug&quot;
# Bash 無法識別 &quot;

# ❌ 特殊字符被錯誤編碼
ls -la | grep &lt;pattern&gt;
# &lt; 和 &gt; 不是 Bash 的重定向符號

**正確示例**：
bash
# ✅ 使用正確的 Bash 運算符
cd "F:/Tests/month-report" && node -e "console.log('test')"

# ✅ 使用 Bash 雙引號包裹含空格的字符串
git add . && git commit -m "fix bug"

# ✅ 使用 Bash 原生重定向符號
ls -la | grep "<pattern>"

**常見錯誤來源與預防**：

| 錯誤來源 | 表現形式 | 預防措施 |
|---------|---------|---------|
| 從網頁覆制命令 | &amp; &lt; &gt; | 粘貼前檢查，使用純文本編輯器中轉 |
| 富文本編輯器 | 自動轉義特殊字符 | 使用 VS Code、Notepad++ 等代碼編輯器 |
| 工具/框架自動編碼 | 命令參數被 HTML 轉義 | 檢查工具配置，關閉自動轉義 |
| 從日志/報告覆制 | HTML 格式的錯誤信息 | 從終端或純文本日志中覆制 |

**特殊字符處理對照表**：

| 場景 | 錯誤寫法（HTML） | 正確寫法（Bash） |
|------|----------------|----------------|
| 邏輯與 | command1 &amp;&amp; command2 | command1 && command2 |
| 重定向輸入 | program &lt; input.txt | program < input.txt |
| 重定向輸出 | program &gt; output.txt | program > output.txt |
| 引號包裹 | echo &quot;hello&quot; | echo "hello" |
| 管道符 | ls &brvbar; grep txt | ls | grep txt |

**調試建議**：

如果遇到類似 syntax error near unexpected token 的錯誤：

1. **檢查命令字符串**：查找是否包含 &amp; &lt; &gt; 等 HTML 實體
2. **驗證來源**：確認命令是從純文本源覆制的，而非網頁或富文本
3. **手動校正**：將所有 HTML 實體替換為對應的 Bash 字符
   - &amp; → `&`
   - &lt; → `<`
   - &gt; → `>`
   - &quot; → `"`
4. **使用專用工具檢查**：可用 echo 命令驗證字符串內容

**示例驗證命令**：
bash
# 驗證命令字符串是否包含 HTML 實體
echo 'cd "F:/Tests" &amp;&amp; node -e "test"' | grep -o '&[a-z]*;'
# 如果有輸出，說明存在 HTML 實體編碼

# 正確的命令應該不包含任何 HTML 實體
echo 'cd "F:/Tests" && node -e "test"' | grep -o '&[a-z]*;'
# 無輸出，說明是純 Bash 命令

---

#### 4. 換行符設置（推薦配置）

Windows 使用 CRLF，Linux 使用 LF，Git 自動轉換可能導致問題。

**推薦配置**：
bash
# 自動轉換：檢出時 LF→CRLF，提交時 CRLF→LF
git config --global core.autocrlf true

# 檢查當前設置
git config --global core.autocrlf

**影響範圍**：
- Git diff 顯示（避免"整個文件被修改"的假象）
- ESLint、Prettier 等工具的換行符檢查
- 部署到 Linux 服務器的兼容性

---

#### 5. 大小寫敏感性警告

⚠️ **Windows 文件系統不區分大小寫，但 Linux 區分**

**常見問題**：
typescript
// ❌ Windows 能跑，Linux 會報錯
import { MyComponent } from './mycomponent'  // 實際文件名：MyComponent.tsx

// ✅ 嚴格匹配文件名大小寫
import { MyComponent } from './MyComponent'

**檢查建議**：
- 保持 import 路徑與實際文件名大小寫完全一致
- 部署前在 WSL 或 Docker 中測試
- 使用 ESLint 插件：`eslint-plugin-import`（檢查路徑大小寫）

---

#### 6. 工具依賴檢查

**首次使用前驗證**：
bash
# 檢查必需工具
git --version && pnpm --version && node --version

# 檢查 Git Bash 環境
which bash  # 應返回：/usr/bin/bash

**常見依賴問題**：
- Git 未安裝 → [下載 Git for Windows](https://git-scm.com/download/win)
- pnpm 未安裝 → npm install -g pnpm
- Node.js 版本過低 → 使用 nvm-windows 管理版本

---

### 文件修改工作流（必須遵守）

修改現有文件時，**嚴格**按以下順序操作：

1. **先用 Read 讀取文件**（獲取當前內容，必需步驟）
2. **使用 Edit 工具修改**（觸發 VSCode diff view）
3. **禁止用 Write 覆蓋現有文件**（除非創建新文件）

**原因**：
- Edit 工具會在 VSCode 中顯示修改前後的對比界面
- 方便用戶審查更改，避免誤操作
- Read 是 Edit 的前置條件，否則會報錯

**錯誤做法**：
bash
# ❌ 直接用 Write 覆蓋現有文件
Write(file_path="src/App.tsx", content="...")

# ❌ 沒有先 Read 就 Edit
Edit(file_path="src/App.tsx", old_string="...", new_string="...")

**正確做法**：
bash
# ✅ 先 Read 再 Edit
Read(file_path="src/App.tsx")
Edit(file_path="src/App.tsx", old_string="...", new_string="...")

# ✅ 創建新文件可以直接 Write
Write(file_path="src/NewComponent.tsx", content="...")

---

### 常見問題與解決方案

#### Q1: pnpm link 失敗提示權限錯誤？
**原因**：Windows 創建符號鏈接需要管理員權限或開發者模式

**解決方案**：
1. 開啟 Windows 開發者模式：
   - 設置 → 更新和安全 → 開發者選項 → 開啟"開發人員模式"
2. 或使用管理員權限運行終端

---

#### Q2: PowerShell 腳本被阻止執行？
**原因**：某些工具（nvm、fnm）可能調用 PowerShell 腳本

**解決方案**：
powershell
# 在 PowerShell 中執行（僅需一次）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

---

#### Q3: WSL 環境支持嗎？
**說明**：當前配置針對 **Git Bash**，不支持 WSL

**WSL 環境差異**：
- 路徑格式：`/mnt/c/Users/張三`（而非 `/c/Users/張三`）
- 文件權限：需要設置 metadata 支持
- 工具安裝：需要在 WSL 內部重新安裝 Node.js、pnpm 等

**如需 WSL 支持**：需要單獨配置，暫不在此規範範圍內

---

#### Q4: 路徑中包含 `()` 等特殊字符？
**解決方案**：統一用雙引號包裹
bash
# ✅ 正確
cd "C:/Program Files (x86)/nodejs"
git add "src/utils(deprecated).ts"

---

#### Q5: Git 報告 "LF will be replaced by CRLF" 警告？
**說明**：這是 core.autocrlf 自動轉換的正常提示，可忽略

**關閉警告**（不推薦）：
bash
git config --global core.safecrlf false

---

#### Q6: 命令報錯 "syntax error near unexpected token"？
**原因**：命令字符串包含 HTML 實體編碼（如 &amp;&amp; 而不是 `&&`）

**典型錯誤信息**：
/usr/bin/bash: eval: line 37: syntax error near unexpected token `;&'
/usr/bin/bash: eval: line 37: `cd "F:/Tests" &amp;&amp; node -e "'

**解決方案**：

1. **檢查命令來源**：確認是否從網頁、富文本編輯器或 HTML 日志覆制
2. **識別 HTML 實體**：查找 &amp; &lt; &gt; &quot; 等字符
3. **手動替換為 Bash 字符**：
   
bash
   # 錯誤：&amp;&amp;
   cd "F:/Tests" &amp;&amp; node -e "test"

   # 正確：&&
   cd "F:/Tests" && node -e "test"
   


4. **使用純文本編輯器**：通過 VS Code 或 Notepad++ 中轉命令
5. **參考規範**：查看 "命令字符串規範" 章節的完整對照表

**快速驗證**：
bash
# 檢查是否包含 HTML 實體
echo '你的命令' | grep -o '&[a-z]*;'
# 有輸出 = 存在問題，無輸出 = 正常

---

  ## 網絡訪問策略（強制執行）

  ### 工具優先級（按順序嘗試）

  **標準訪問**（默認優先）：
  1. WebFetch — 獲取網頁內容並分析
  2. WebSearch — 搜索引擎查詢

  **網絡受限時的備選方案**：
  當 WebFetch/WebSearch 返回網絡錯誤（403、超時、連接失敗）時，**必須立即**切換到 MCP 代理工具：

  1. mcp__mcp-router__fetch_markdown — 獲取網頁（Markdown 格式）
  2. mcp__mcp-router__fetch_html — 獲取網頁（HTML 格式）
  3. mcp__mcp-router__fetch_txt — 獲取網頁（純文本）
  4. mcp__mcp-router__fetch_json — 獲取 JSON 數據

  **終極備選方案**：
  當 MCP 代理工具也失敗時，使用瀏覽器自動化：

  - Playwright 無頭模式 — 模擬真實瀏覽器訪問（可繞過反爬、JS 渲染、登錄驗證）
    - 使用 browser_navigate 訪問目標 URL
    - 使用 browser_snapshot 或 browser_take_screenshot 獲取內容
    - 適用場景：需要 JS 渲染、有反爬機制、需要模擬用戶行為

  ### 強制重試流程

  遇到網絡錯誤時，**嚴格**按以下順序重試：

  
text
  1. 嘗試 WebFetch/WebSearch
     ↓ (失敗)
  2. 立即切換到 mcp__mcp-router__fetch_markdown
     ↓ (失敗)
  3. 嘗試 mcp__mcp-router__fetch_html
     ↓ (失敗)
  4. 啟動 Playwright 無頭模式獲取頁面
     ↓ (失敗)
  5. 告知用戶網絡問題，提供替代方案
  


  ### 禁止行為

  - ❌ 遇到網絡錯誤就放棄，不嘗試備用工具
  - ❌ 只告訴用戶"訪問不了"而不嘗試其他方法
  - ❌ 跳過重試流程直接讓用戶提供內容
  - ❌ 在 MCP 工具失敗後不嘗試 Playwright 就放棄

  ### 示例

  **錯誤做法**：
  

  我：嘗試 WebFetch → 403 錯誤
  我：哎呀訪問不了，你把內容發我吧！❌
  


  **正確做法（標準流程）**：
  

  我：嘗試 WebFetch → 403 錯誤
  我：切換到 mcp__mcp-router__fetch_markdown → 成功 ✅
  


  **正確做法（終極流程）**：
  

  我：嘗試 WebFetch → 403 錯誤
  我：切換到 mcp__mcp-router__fetch_markdown → 超時
  我：切換到 mcp__mcp-router__fetch_html → 超時
  我：啟動 Playwright 無頭瀏覽器 → 成功獲取內容 ✅
  


  ---


## 特定場景規則

### Playwright 自動化注意事項

- **空白頁 Bug**：頻繁使用 browser_tabs 創建新標簽頁會導致空白頁累積
  - 優先在當前頁面操作，避免頻繁開新標簽
  - 測試完成後及時關閉不需要的標簽頁
  - 必要時使用 browser_navigate 在同一標簽內切換

- **頁面刷新優先**：測試頁面功能時多用刷新代替跳轉
  - 使用 page.reload() 或 browser_navigate 到當前 URL 刷新
  - 避免頻繁使用 browser_navigate 跳轉到新 URL
  - 刷新可保持頁面狀態，跳轉可能導致回溯

- **交互式元素**：某些模塊需要用戶交互才會激活
  - 下拉菜單、彈窗等需要先 browser_click 觸發
  - 懶加載內容需要滾動或點擊才會渲染
  - 動態加載的元素要用 browser_wait_for 等待出現

- **頁面回溯問題**：頻繁跳轉會導致瀏覽器歷史混亂
  - 盡量在單頁面內完成測試流程
  - 需要切換場景時考慮用標簽頁而非歷史跳轉
  - 避免依賴瀏覽器後退按鈕進行導航

### 縮寫解釋

用戶可能使用以下縮寫進行快速交互：

- y = 是 (Yes)
- n = 否 (No)
- c = 繼續 (Continue)
- r = 確認 (Review)
- u = 撤銷 (Undo)

---

## 執行規則

### 立即執行（無需確認）

- **代碼操作**：Bug 修覆、重構、性能改進
- **文件編輯**：現有文件的修改與更新
- **文檔**：README、規範文檔的更新（僅在要求時創建新文檔）
- **依賴關系**：包的添加、更新與刪除
- **測試**：單元測試與集成測試的實現（遵循 TDD 周期）
- **設置**：配置值更改、應用格式化

### 必須確認

- **創建新文件**：說明必要性並確認
- **刪除文件**：重要文件的刪除
- **結構變更**：架構、文件夾結構的大規模變更
- **外部集成**：新 API、外部庫的引入
- **安全**：認證與授權功能的實現
- **數據庫**：schema 變更、遷移
- **生產環境**：部署設置、環境變量變更

### Git push 授權

- 若用戶在任務目標或後續訊息中明確要求 `git push origin main` 與指定 tag push，且已明確表示了解這會推送到外部 GitHub 並批准，後續同一任務內可直接執行相同 push，不需要重複詢問。
- 嚴禁 `git push --force` 或任何 force push，除非用戶在當前回合以完整命令明確要求，且系統/工具審核允許。
- 若系統、工具或安全審核仍要求再次取得 approval，必須以系統、工具或安全審核結果為準。

---

## 執行流程

```text
1. 接收任務
   ↓
2. 判斷
