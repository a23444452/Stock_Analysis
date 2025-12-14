# 📈 台股全方位分析儀表板 (Stock Analysis Dashboard)

這是一個基於 Python 與 Streamlit 開發的互動式台股分析工具。結合了 **Google Gemini AI** 的強大語言能力，為使用者提供即時的股價數據、技術指標視覺化以及專業的 AI 投資診斷報告。

## ✨ 功能特色

*   **即時數據獲取**：輸入股票代號（如 `2330.TW`），自動抓取近半年股價與基本面資料（本益比、EPS、市值等）。
*   **互動式 K 線圖**：使用 Plotly 繪製專業的蠟燭圖，並疊加 20 日移動平均線 (20MA)，趨勢一目瞭然。
*   **AI 智能診斷**：利用 **Google Gemini 模型** 扮演華爾街分析師，針對當前數據提供：
    *   市場趨勢判斷
    *   基本面亮點與風險
    *   短/長線投資建議
*   **直觀的操作介面**：簡潔的 Streamlit 側邊欄與儀表板設計，操作流暢。

## 🛠️ 技術堆疊

*   **介面 (UI)**: [Streamlit](https://streamlit.io/)
*   **數據源 (Data)**: [yfinance](https://pypi.org/project/yfinance/)
*   **AI 核心 (LLM)**: [Google Generative AI (Gemini)](https://ai.google.dev/)
*   **繪圖 (Charts)**: [Plotly](https://plotly.com/python/)

## 🚀 快速開始

### 1. 環境需求

請確保您的電腦已安裝 Python 3.8 或以上版本。

### 2. 安裝套件

複製專案後，執行以下指令安裝所需套件：

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

在專案根目錄建立一個 `.env` 檔案，並填入您的 Google API Key：

```text
GOOGLE_API_KEY=您的_Google_API_Key
```

> 💡 **提示**：您可以前往 [Google AI Studio](https://aistudio.google.com/) 免費獲取 API Key。

### 4. 啟動應用程式

在終端機執行：

```bash
streamlit run app.py
```

程式啟動後，瀏覽器將自動開啟應用程式頁面（預設為 `http://localhost:8501`）。

## 📖 操作說明

1.  在左側 **側邊欄** 輸入欲查詢的 **台股代號**（例如：`2330.TW` 台積電, `2454.TW` 聯發科）。
2.  點擊 **「開始 AI 診斷」** 按鈕。
3.  系統將自動：
    *   顯示即時股價、漲跌幅與本益比。
    *   繪製 K 線圖與 20MA 均線。
    *   生成並顯示 Gemini AI 的專業分析報告。

## ⚠️ 注意事項

*   請確保 `.env` 檔案已正確設定，否則 AI 功能將無法運作。
*   股票代號需符合 Yahoo Finance 格式（台股請加上 `.TW` 後綴）。
*   本工具僅供參考，投資請自行審慎評估風險。

---
Created by [Your Name]
