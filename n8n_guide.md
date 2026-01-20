# LINE + n8n + Python Stock Analysis 串接指南

本指南將協助您將 LINE 聊天機器人透過 n8n 自動化流程，串接到您的 Python 股票分析 API。

## 系統架構

```mermaid
graph LR
    User((使用者)) -- 輸入股票代號 --> LINE[LINE Messaging API]
    LINE -- Webhook --> n8n[n8n 自動化流程]
    n8n -- HTTP POST --> Ngrok[Ngrok Tunnel]
    Ngrok -- Forward --> API[Python FastAPI (Local)]
    API -- 回傳分析結果 --> n8n
    n8n -- Reply Message --> LINE
    LINE -- 顯示結果 --> User
```

---

## 步驟 1：準備 Python API 環境

我們已經更新了 `api.py` 與 `requirements.txt`。請先確保環境安裝完成並啟動 API。

1.  **安裝套件**
    ```bash
    pip install -r requirements.txt
    ```

2.  **啟動 API Server**
    在終端機執行以下指令：
    ```bash
    uvicorn api:app --reload --port 8001
    ```
    *成功啟動後，您應該會看到 `Uvicorn running on http://0.0.0.0:8001`*

---

## 步驟 2：讓外網能存取您的 API (使用 Ngrok)

由於 n8n (如果是雲端版) 或 LINE 無法直接存取您電腦上的 `localhost:8001`，我們需要使用 Ngrok 建立一個臨時通道。

1.  **下載並安裝 Ngrok**: [https://ngrok.com/download](https://ngrok.com/download)
2.  **啟動 Ngrok**
    開啟一個新的終端機視窗，執行：
    ```bash
    ngrok http 8001
    ```
3.  **複製 Forwarding URL**
    複製顯示的 HTTPS 網址，例如：`https://xxxx-xxxx.ngrok-free.app`。
    *請記住這個網址，稍後在 n8n 設定時會用到。*

---

## 步驟 3：設定 LINE Developers

1.  前往 [LINE Developers Console](https://developers.line.biz/)。
2.  建立一個新的 **Provider** (如果還沒有)。
3.  建立一個新的 **Messaging API** Channel。
4.  在 **Basic settings** 頁籤，記下 **Channel Secret**。
5.  在 **Messaging API** 頁籤，產生並記下 **Channel Access Token**。
6.  (稍後設定) **Webhook URL** 將填入 n8n 產生的 Webhook 網址。

---

## 步驟 4：設定 n8n 自動化流程

請開啟您的 n8n (桌面版或雲端版)，建立一個新的 Workflow。

### 節點 1: Webhook (接收 LINE 訊息)
1.  新增節點：搜尋 **Webhook**。
2.  設定：
    - **HTTP Method**: `POST`
    - **Path**: `line-webhook` (自訂)
    - **Authentication**: None
3.  複製 **Production URL** (如果是測試階段可用 Test URL)。
    - *將此 URL 貼回 LINE Developers Console 的 Webhook URL 欄位，並啟用 "Use webhook"。*

### 節點 2: Function / Code (驗證與解析 - 選用但推薦)
LINE 會傳送 JSON 格式，我們需要取出使用者輸入的文字。
1.  新增節點：**Code**。
2.  程式碼 (JavaScript):
    ```javascript
    // 取得 LINE 傳來的訊息文字
    const events = items[0].json.body.events;
    if (events && events.length > 0 && events[0].type === 'message' && events[0].message.type === 'text') {
        const userMessage = events[0].message.text;
        const replyToken = events[0].replyToken;
        return [
            {
                json: {
                    stock_id: userMessage.trim(),
                    replyToken: replyToken
                }
            }
        ];
    }
    return [];
    ```

### 節點 3: HTTP Request (呼叫 Python API)
1.  新增節點：**HTTP Request**。
2.  設定：
    - **Method**: `POST`
    - **URL**: `https://xxxx-xxxx.ngrok-free.app/analyze` (貼上您的 Ngrok 網址)
    - **Authentication**: None
    - **Send Body**: Toggle On
    - **Body Content Type**: JSON
    - **Specify Body**:
        ```json
        {
            "stock_id": "{{ $json.stock_id }}"
        }
        ```
3.  執行測試，確認能收到 Python API 回傳的 `message`。

### 節點 4: HTTP Request (回覆 LINE)
1.  新增節點：**HTTP Request**。
2.  設定：
    - **Method**: `POST`
    - **URL**: `https://api.line.me/v2/bot/message/reply`
    - **Authentication**: Generic Credential Type -> **Header Auth**
        - Name: `Authorization`
        - Value: `Bearer <您的 Channel Access Token>`
    - **Send Body**: Toggle On
    - **Body Content Type**: JSON
    - **Specify Body**:
        ```json
        {
            "replyToken": "{{ $node['Code'].json.replyToken }}",
            "messages": [
                {
                    "type": "text",
                    "text": "{{ $json.message }}"
                }
            ]
        }
        ```

---

## 測試流程

1.  確保 Python API 正在執行 (`uvicorn ...`).
2.  確保 Ngrok 正在執行。
3.  確保 n8n Workflow 處於 **Active** 狀態 (或是在測試模式)。
4.  用手機 LINE 加入您的機器人好友。
5.  輸入股票代號 (例如 `2330`)。
6.  您應該會在幾秒後收到 AI 分析的完整報告！
