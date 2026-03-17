# lo-dev-skills

適用於 LibreOffice 核心開發的 [Claude Code](https://claude.ai/code) skills。

這些 skills 為 Claude Code 注入 LibreOffice 建置系統、UNO 元件模型、偵錯基礎設施、spec workflow 及開發慣例等領域知識，讓它能準確且高效地協助 LO 開發工作。

## Skills 一覽

### lo-uno-api — UNO API 開發指引

涵蓋完整的 UNO API 開發流程：撰寫 IDL 檔案、註冊至建置系統、C++ 實作、service 註冊、編譯與測試。所有範例均取自 LO 原始碼。

**觸發情境：** 建立或修改 `offapi/` 中的 UNO IDL interface、struct、enum、service 或 listener；以 C++ 實作 UNO service；操作 `.component` XML 或 `gb_UnoApi` 建置規則。

**參考文件：**

| 檔案 | 內容 |
|------|------|
| `references/idl-syntax.md` | Interface、struct、enum、service、listener 的 IDL 語法 |
| `references/cpp-implementation.md` | C++ 實作模式：WeakImplHelper、VCL 橋接、listener multiplexer、dispose |
| `references/build-registration.md` | `UnoApi_offapi.mk` 巨集選擇、`.component` XML 格式、`Library_*.mk` |
| `references/common-base-interfaces.md` | XInterface、XServiceInfo、XComponent 等常用介面速查 |

**輔助腳本：**

| 腳本 | 用途 |
|------|------|
| `scripts/gen_idl.py` | 產生含 MPL-2.0 授權標頭和正確 module 巢狀結構的 IDL 模板 |
| `scripts/check_build_registration.py` | 驗證 IDL 是否已在 `UnoApi_offapi.mk` 中以正確的巨集註冊 |
| `scripts/validate_component.py` | 驗證 `.component` XML 的 constructor 命名一致性 |

### lo-spec-writing — Spec 撰寫指引

協助在實作前先寫出可落地的 LibreOffice 開發規格，特別適合公開 UNO/VCL contract、分階段導入、fallback 策略與 extension 驗證計畫。

**觸發情境：** 撰寫或整理 spec、phase plan、驗證計畫、fallback 設計，或在 coding 前先定義 API contract。

**參考文件：**

| 檔案 | 內容 |
|------|------|
| `references/spec-template.md` | 可直接套用的 implementation-ready spec 結構 |
| `references/contract-questions.md` | 公開 UNO/VCL contract 精確化檢查表 |
| `references/staged-validation.md` | 分階段 rollout、能力探測與 extension 驗證模式 |

### lo-spec-review — Spec-driven Code Review 指引

協助以 spec 為基準審查 LibreOffice patches，重點放在 published contract、UNO-to-VCL bridge、lifecycle 風險、相容性與驗證證據。

**觸發情境：** 對照 spec review patch、審查公開 UNO API、檢查 listener/lifecycle 行為，或要求 spec-driven review findings。

**參考文件：**

| 檔案 | 內容 |
|------|------|
| `references/published-api-review-checklist.md` | 公開 contract 與 bridge code 的 review checklist |
| `references/validation-evidence.md` | 如何判讀測試、手動驗證與 headless-safe coverage |

### lo-debug — 偵錯指引

涵蓋日誌系統（SAL_LOG）、GDB 整合、測試偵錯、記憶體工具、效能分析、編譯器外掛及 Writer 專用偵錯設施。

**觸發情境：** 診斷 crash、加入 log 輸出、在 GDB/Valgrind/rr 下執行測試、效能分析、core dump 分析、操作 SAL_LOG、loplugins 或 sanitizers。

**參考文件：**

| 檔案 | 內容 |
|------|------|
| `references/logging.md` | SAL_INFO/SAL_WARN 巨集、SAL_LOG 環境變數過濾語法、例外日誌 |
| `references/gdb-debugging.md` | `make debugrun`、pretty printers、core dump 分析、backtrace API |
| `references/test-debugging.md` | CppUnit/UITest/PythonTest 在 GDB、Valgrind、rr 下的偵錯方式 |
| `references/memory-tools.md` | AddressSanitizer、UBSan、Valgrind memcheck |
| `references/profiling.md` | Chrome trace events、ProfileZone、callgrind、perf |
| `references/loplugins.md` | Clang 編譯器外掛系統及常見檢查項目 |
| `references/writer-debugging.md` | Writer 排版 dump（F12）、`dbg_out()` 函式、Writer 偵錯環境變數 |

**輔助腳本：**

| 腳本 | 用途 |
|------|------|
| `scripts/find_log_areas.py` | 搜尋、列出及驗證各模組中的 SAL_LOG areas |
| `scripts/parse_sal_log.py` | 依 area、level 或檔案過濾和解析 SAL_LOG 輸出 |

## 安裝方式

### Claude Code

將 skill 目錄加入 Claude Code 設定檔（`.claude/settings.json`）：

```json
{
  "skills": [
    "/path/to/lo-dev-skills/lo-spec-writing",
    "/path/to/lo-dev-skills/lo-spec-review",
    "/path/to/lo-dev-skills/lo-uno-api",
    "/path/to/lo-dev-skills/lo-debug"
  ]
}
```

也可以針對特定專案設定，將路徑加入 LO-core checkout 中的 `.claude/settings.local.json`。

### 獨立使用腳本

各 skill 的 `scripts/` 目錄下的腳本可獨立執行，僅需 Python 3.11+，無外部相依。腳本會自動偵測 LO 原始碼根目錄，或透過 `--lo-root` 指定：

```bash
# 產生 IDL 模板
python lo-uno-api/scripts/gen_idl.py --type interface --module com.sun.star.awt --name XMyWidget

# 檢查 IDL 是否已註冊在建置系統
python lo-uno-api/scripts/check_build_registration.py --idl-path com/sun/star/awt/Toolkit.idl

# 列出模組中使用的 log areas
python lo-debug/scripts/find_log_areas.py --module sw

# 過濾 SAL_LOG 輸出
SAL_LOG="+INFO.sw" ./instdir/program/soffice 2>&1 | python lo-debug/scripts/parse_sal_log.py --area sw.core
```

## 相容性

- 基於 LibreOffice core（master 分支，2026 年）開發
- 腳本需要 Python 3.11+（僅使用標準函式庫，無需 pip 安裝）
- 參考資料基於 LO 的 gbuild 建置系統、UNO IDL 編譯器及 SAL 日誌框架——這些在多個 LO 版本間保持穩定

## 授權

MPL-2.0——與 LibreOffice 相同。
