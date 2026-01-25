# 📈 台股全方位分析儀表板 (Stock Analysis Dashboard)

這是一個基於 Python 與 Streamlit 開發的互動式台股分析工具。結合了 **Google Gemini AI** 的強大語言能力，為使用者提供即時的股價數據、技術指標視覺化以及專業的 AI 投資診斷報告。

[![部署狀態](https://img.shields.io/badge/部署-Railway-blueviolet)](https://railway.app/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 功能特色

### 📊 個股全方位分析
*   **即時數據獲取**：輸入股票代號（如 `2330.TW`），自動抓取近半年股價與基本面資料（本益比、EPS、市值等）。
*   **互動式 K 線圖**：使用 Plotly 繪製專業的蠟燭圖，並疊加 20 日移動平均線 (20MA)，趨勢一目瞭然。
*   **AI 智能診斷**：利用 **Google Gemini 2.0 Flash** 扮演華爾街分析師，針對當前數據提供市場趨勢判斷、基本面分析與投資建議。
*   **財報深度解讀**：結合最新法說會與財報重點進行 RAG 分析。
*   **🆕 分析快取功能**：切換頁面不會遺失分析結果，節省 API 呼叫成本。
*   **🆕 智慧記憶**：自動記住上次分析的股票代號。

### 📈 基本面 AI 分析
*   **三大報表視覺化**：損益表、資產負債表、現金流量表關鍵指標圖表。
*   **AI 財務診斷**：深入解讀財務結構、獲利能力與現金流品質。
*   **趨勢分析**：年度營收、獲利、資產負債變化一目瞭然。

### 🧘 投資組合健檢
*   **視覺化資產配置**：圓餅圖呈現投資組合分佈。
*   **AI 投資教練**：評估風險集中度、產業配置並給予心態建議。
*   **🆕 永久儲存**：投資組合資料永久儲存在瀏覽器，下次自動載入。
*   **🆕 一鍵管理**：儲存、清空、編輯投資組合更便捷。

### ⏳ 定期定額 (DCA) 回測
*   **歷史績效模擬**：模擬定期定額投資策略的歷史表現。
*   **關鍵指標計算**：總報酬、最大回撤 (MDD)、年化波動率。
*   **AI 策略分析**：分析策略風險與微笑曲線效應。

### 🤖 自動化日報助理
*   **每日市場摘要**：一鍵生成觀察清單的市場數據。
*   **AI 點評**：Gemini AI 提供專業的盤後分析與建議。
*   **Email 整合**：自動寄送投資日報到指定信箱。

### 💬 LINE Bot 串接
*   **即時查詢**：透過 LINE 聊天室直接查詢個股 AI 分析報告。
*   **n8n 自動化**：整合 n8n 工作流程與 Python API。
*   **24/7 服務**：Railway 雲端部署，隨時隨地查詢。

### 🎨 現代化 UI/UX
*   **深色金融主題**：專業的漸層設計與配色方案。
*   **響應式設計**：卡片、按鈕、圖表統一風格。
*   **流暢動畫**：毛玻璃效果、陰影與過渡動畫。

## 🛠️ 技術堆疊

| 類別 | 技術 | 用途 |
|------|------|------|
| **前端框架** | [Streamlit](https://streamlit.io/) | 互動式網頁應用 |
| **API 服務** | [FastAPI](https://fastapi.tiangolo.com/) | RESTful API (LINE Bot) |
| **數據源** | [yfinance](https://pypi.org/project/yfinance/) | 股價與財報數據 |
| **AI 核心** | [Google Gemini 2.0 Flash](https://ai.google.dev/) | 自然語言分析 |
| **視覺化** | [Plotly](https://plotly.com/python/) | 互動式圖表 |
| **PDF 解析** | [pdfplumber](https://github.com/jsvine/pdfplumber) | 財報 PDF 擷取 |
| **本地儲存** | [streamlit-js-eval](https://github.com/aghasemi/streamlit_js_eval) | LocalStorage 持久化 |
| **郵件發送** | Python `smtplib` | Email 自動化 |
| **工作流程** | [n8n](https://n8n.io/) | LINE Bot 整合 |
| **雲端部署** | [Railway](https://railway.app/) | PaaS 平台 |

## 🚀 快速開始

### 1. 環境需求

請確保您的電腦已安裝 Python 3.8 或以上版本。

### 2. 安裝套件

複製專案後，執行以下指令安裝所需套件：

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

在專案根目錄建立一個 `.env` 檔案，並填入您的 Google API Key 與 Email 設定（若要使用自動寄信功能）：

```text
GOOGLE_API_KEY=您的_Google_API_Key
MAIL_USERNAME=您的Gmail帳號
MAIL_PASSWORD=您的Gmail應用程式密碼
MAIL_TO=接收報告的Email
```

> 💡 **提示**：
> 1. 您可以前往 [Google AI Studio](https://aistudio.google.com/) 免費獲取 API Key。
> 2. Gmail 需開啟「兩步驟驗證」並申請 **[應用程式密碼](https://myaccount.google.com/appwords)** 才能透過程式寄信。

### 4. 啟動應用程式

**使用啟動腳本（推薦）：**

```bash
# 啟動所有服務 (Streamlit + API)
./run.sh start

# 停止所有服務
./run.sh stop

# 查看服務狀態
./run.sh status

# 查看日誌
./run.sh logs
```

> 💡 腳本會自動偵測並終止佔用 port 的舊程序，無需手動清理。

**手動啟動：**

```bash
# 啟動 Streamlit 網頁介面
streamlit run app.py

# 啟動 API Server (供 LINE Bot 使用)
uvicorn api:app --reload --port 8001
```

## 📖 操作說明

### 1️⃣ 個股全方位分析
1. 輸入股票代號（如 `2330.TW`）
2. (選填) 上傳財報 PDF 以進行更深度的 RAG 分析
3. 點擊 **「🔍 開始分析」** 查看報告
4. 🆕 切換頁面後回來,分析結果自動保留
5. 🆕 下次開啟自動載入上次的股票代號

### 2️⃣ 基本面 AI 分析
1. 輸入股票代號
2. 查看三大報表視覺化圖表（損益表、資產負債表、現金流量表）
3. 閱讀 AI 財務健康診斷報告

### 3️⃣ 投資組合健檢
1. 在表格中輸入您的持倉與比例
2. 🆕 點擊 **「💾 儲存組合」** 永久保存
3. 點擊 **「📊 分析投資組合」** 查看 AI 風險評估
4. 🆕 下次開啟自動載入上次的投資組合

### 4️⃣ 定期定額 (DCA) 回測
1. 輸入股票代號、每月扣款金額與回測年數
2. 查看資產成長曲線與累積成本對比
3. 閱讀 AI 針對此策略的風險報酬分析

### 5️⃣ 自動化日報助理
1. 設定觀察名單 (Watchlist)
2. 生成今日市場摘要與 AI 點評
3. 一鍵寄送 Email 給自己

### 6️⃣ LINE Bot 串接 (進階)
本專案支援透過 LINE 聊天機器人進行互動。您可以選擇：
*   **Railway 雲端部署**（推薦）：獲得固定網址，24/7 穩定運行
*   **Ngrok 本地測試**：適合開發階段快速測試

詳細設定步驟請參考：
👉 **[LINE + n8n + Python 串接指南](n8n_guide.md)**

## 🎯 最新更新 (Recent Updates)

### v2.0.0 - 2026-01-25

#### 🆕 新功能
- ✅ **永久儲存投資組合**: 使用瀏覽器 localStorage,投資組合資料永久保存
- ✅ **分析結果快取**: 個股分析結果自動儲存,切換頁面不會遺失
- ✅ **智慧記憶**: 自動記住上次使用的股票代號
- ✅ **現代化 UI**: 深色金融主題,漸層設計與專業配色
- ✅ **Gemini 2.0 Flash**: 升級到最新的 Gemini API

#### 🔧 技術改進
- ⬆️ 更新 `google-genai` SDK (從 `google-generativeai` 遷移)
- 🛠️ 新增 `streamlit-js-eval` 支援本地儲存
- 🎨 統一 Plotly 圖表主題與配色方案
- 🐛 修復 Railway 部署問題
- 📦 套件版本管理優化

#### 🎨 UI/UX 改善
- 卡片式設計與毛玻璃效果
- 漸層按鈕與 hover 動畫
- 統一的深色金融配色
- 改進的側邊欄導航
- 更直觀的操作提示

## 🌐 線上 Demo

🔗 **Railway 部署版本**: [https://web-production-db967.up.railway.app/](https://web-production-db967.up.railway.app/)

> 💡 提示:線上版本已設定好 Gemini API,您可以直接體驗所有功能!

## 📸 截圖展示

### 個股全方位分析
![個股分析](docs/screenshots/stock_analysis.png)

### 投資組合健檢
![投資組合](docs/screenshots/portfolio.png)

### 定期定額回測
![DCA 回測](docs/screenshots/dca_backtest.png)

## 💾 資料儲存說明

本應用使用兩種儲存機制:

1. **Session State (會話儲存)**
   - 儲存當前頁面的分析結果
   - 在同一瀏覽器會話期間保留資料
   - 關閉瀏覽器後清除

2. **LocalStorage (永久儲存)**
   - 儲存投資組合配置
   - 儲存上次使用的股票代號
   - 永久保存在瀏覽器中,即使關閉瀏覽器也不會遺失
   - 清除瀏覽器快取會刪除資料

## 🔧 進階設定

### Railway 部署

1. Fork 此專案到您的 GitHub
2. 在 Railway 建立新專案並連接 GitHub repo
3. 設定環境變數:
   ```
   GOOGLE_API_KEY=your_api_key
   ```
4. Railway 會自動偵測 `Procfile` 並部署 Streamlit 應用

### 本地開發

```bash
# 安裝開發依賴
pip install -r requirements.txt

# 啟動開發模式
./run.sh start

# 查看日誌
./run.sh logs

# 停止服務
./run.sh stop
```

## 📝 變更日誌

詳細的變更記錄請參考 [CHANGELOG.md](CHANGELOG.md)

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request!

1. Fork 此專案
2. 建立您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## ⚠️ 注意事項

*   請確保 `.env` 檔案已正確設定，否則 AI 功能將無法運作。
*   股票代號需符合 Yahoo Finance 格式（台股請加上 `.TW` 後綴）。
*   本工具僅供參考，**投資一定有風險，基金投資有賺有賠，申購前應詳閱公開說明書**。
*   Gemini API 有免費額度限制，大量使用請注意配額。

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 👨‍💻 作者

**Vince Wang**

- GitHub: [@a23444452](https://github.com/a23444452)
- 專案連結: [https://github.com/a23444452/Stock_Analysis](https://github.com/a23444452/Stock_Analysis)

## 🙏 致謝

- [Streamlit](https://streamlit.io/) - 優秀的 Python 網頁框架
- [Google Gemini](https://ai.google.dev/) - 強大的 AI 模型
- [yfinance](https://github.com/ranaroussi/yfinance) - 免費的股價數據
- [Plotly](https://plotly.com/) - 互動式視覺化工具
- [Railway](https://railway.app/) - 簡單易用的部署平台

---

⭐ 如果這個專案對您有幫助，歡迎給個 Star!


