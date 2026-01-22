# 📈 台股全方位分析儀表板 (Stock Analysis Dashboard)

這是一個基於 Python 與 Streamlit 開發的互動式台股分析工具。結合了 **Google Gemini AI** 的強大語言能力，為使用者提供即時的股價數據、技術指標視覺化以及專業的 AI 投資診斷報告。

## ✨ 功能特色

*   **即時數據獲取**：輸入股票代號（如 `2330.TW`），自動抓取近半年股價與基本面資料（本益比、EPS、市值等）。
*   **互動式 K 線圖**：使用 Plotly 繪製專業的蠟燭圖，並疊加 20 日移動平均線 (20MA)，趨勢一目瞭然。
*   **AI 智能診斷**：利用 **Google Gemini 模型** 扮演華爾街分析師，針對當前數據提供：
    *   市場趨勢判斷
    *   基本面亮點與風險
    *   **財報深度解讀** (New!)：結合最新法說會與財報重點進行分析
    *   短/長線投資建議
*   **基本面 AI 分析** (New!)：
    *   **三大報表視覺化**：損益表、資產負債表、現金流量表關鍵指標圖表。
    *   **AI 財務診斷**：深入解讀財務結構、獲利能力與現金流品質。
*   **投資組合健檢** (New!)：
    *   視覺化資產配置（圓餅圖）。
    *   AI 擔任投資教練，評估風險集中度並給予心態建議。
*   **定期定額 (DCA) 回測** (New!)：
    *   模擬歷史定期定額投資績效。
    *   計算總報酬、最大回撤 (MDD) 與年化波動率。
    *   AI 分析策略風險與微笑曲線效應。
*   **自動化日報助理** (New!)：
    *   一鍵生成每日市場摘要與 AI 點評。
    *   整合 Email 寄送功能，輕鬆訂閱自己的投資日報。
*   **LINE Bot 串接** (New!)：
    *   透過 LINE 聊天室直接查詢個股 AI 分析報告。
    *   整合 n8n 自動化流程與 Python API。
*   **直觀的操作介面**：簡潔的 Streamlit 側邊欄與儀表板設計，操作流暢。

## 🛠️ 技術堆疊

*   **介面 (UI)**: [Streamlit](https://streamlit.io/)
*   **API 服務**: [FastAPI](https://fastapi.tiangolo.com/)
*   **數據源 (Data)**: [yfinance](https://pypi.org/project/yfinance/)
*   **AI 核心 (LLM)**: [Google Generative AI (Gemini)](https://ai.google.dev/)
*   **繪圖 (Charts)**: [Plotly](https://plotly.com/python/)
*   **PDF 解析**: [pdfplumber](https://github.com/jsvine/pdfplumber)
*   **郵件發送**: Python `smtplib`
*   **自動化**: [n8n](https://n8n.io/)
*   **雲端部署**: [Railway](https://railway.app/)

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

### 1. 個股全方位分析
*   輸入股票代號（如 `2330.TW`）。
*   (選填) 上傳財報 PDF 以進行更深度的 RAG 分析。
*   點擊「開始 AI 診斷」查看報告。

### 2. 基本面 AI 分析
*   輸入股票代號。
*   查看三大報表視覺化圖表。
*   閱讀 AI 針對財務健康的深度診斷。

### 3. 投資組合健檢
*   在表格中輸入您的持倉與比例。
*   點擊「分析投資組合」查看資產分佈與 AI 風險評估。

### 4. 定期定額 (DCA) 回測
*   輸入股票代號、每月扣款金額與回測年數。
*   查看資產成長曲線與累積成本。
*   閱讀 AI 針對此策略的風險報酬分析。

### 5. 自動化日報助理
*   設定觀察名單 (Watchlist)。
*   生成今日市場摘要與 AI 點評。
*   一鍵寄送 Email 給自己。

### 6. LINE Bot 串接 (進階)
本專案支援透過 LINE 聊天機器人進行互動。您可以選擇：
*   **Railway 雲端部署**（推薦）：獲得固定網址，24/7 穩定運行
*   **Ngrok 本地測試**：適合開發階段快速測試

詳細設定步驟請參考：
👉 **[LINE + n8n + Python 串接指南](n8n_guide.md)**

## ⚠️ 注意事項

*   請確保 `.env` 檔案已正確設定，否則 AI 功能將無法運作。
*   股票代號需符合 Yahoo Finance 格式（台股請加上 `.TW` 後綴）。
*   本工具僅供參考，投資請自行審慎評估風險。


