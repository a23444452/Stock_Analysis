import streamlit as st
import yfinance as yf
import google.generativeai as genai
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import pandas as pd
import requests
import time

# Step 1: 環境設定 - 載入環境變數
load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 設定 Streamlit 頁面配置
st.set_page_config(page_title="台股全方位分析儀表板", layout="wide")

# Step 2: 數據獲取模組
def get_stock_data(ticker):
    """
    獲取指定股票的歷史股價與基本資料
    """
    try:
        stock = yf.Ticker(ticker)
        
        # 下載近半年的歷史股價
        history = stock.history(period="6mo")
        
        # 獲取基本資料
        info = stock.info
        
        if history.empty:
            return None, None
            
        return history, info
    except Exception as e:
        st.error(f"獲取數據時發生錯誤: {e}")
        return None, None

def get_financial_report_text(ticker):
    """
    模擬爬取公開財報 PDF 並轉為文字。
    真實情境可使用 requests + pdfplumber 針對公開資訊觀測站 (MOPS) 進行爬取。
    """
    # 模擬網路請求延遲
    time.sleep(1.5)
    
    # 針對台積電 (2330.TW) 提供較真實的模擬數據
    if "2330" in ticker:
        return """
        【2024年第三季法說會重點摘要】
        1. 營收表現：第三季合併營收約新台幣7,596億9千萬元，稅後純益約新台幣3,252億6千萬元，每股盈餘為新台幣12.54元。
        2. 毛利率：第三季毛利率為57.8%，營業利益率為47.5%，稅後純益率為42.8%。
        3. 先進製程：3奈米製程出貨佔第三季晶圓銷售金額的20%，5奈米製程出貨佔全季晶圓銷售金額的32%；7奈米及更先進製程佔全季晶圓銷售金額的69%。
        4. 未來展望：受惠於AI需求強勁，預期第四季營收將持續成長。HPC（高效能運算）平台需求依然是主要成長動能。
        5. 資本支出：維持全年資本支出目標不變，約在300億至320億美元之間。
        """
    else:
        # 其他股票的通用模擬數據
        return f"""
        【{ticker} 近期財務報告摘要】
        1. 營運概況：本季營收較去年同期呈現穩定趨勢，主要受惠於市場需求回溫。
        2. 獲利能力：毛利率維持在產業平均水準，公司持續優化成本結構。
        3. 市場展望：管理層對未來兩季持審慎樂觀態度，將持續投入研發以增強競爭力。
        4. 風險提示：需留意匯率波動及原物料價格變化對獲利的影響。
        (註：此為模擬生成的通用財報文字，僅供系統測試使用)
        """

# Step 3: Gemini AI 分析模組
def analyze_with_gemini(ticker, price_data, stock_info, report_text):
    """
    使用 Gemini AI 進行專業財報與趨勢分析
    """
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "你的金鑰":
        return "⚠️ 請先在 .env 檔案中設定有效的 GOOGLE_API_KEY。"

    try:
        # 設定 Gemini API
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 整理數據供 AI 分析
        latest_close = price_data['Close'].iloc[-1]
        ma_20 = price_data['Close'].rolling(window=20).mean().iloc[-1]
        pe_ratio = stock_info.get('trailingPE', 'N/A')
        eps = stock_info.get('trailingEps', 'N/A')
        market_cap = stock_info.get('marketCap', 'N/A')
        
        # 構建 Prompt
        prompt = f"""
        請針對台股代號 {ticker} 進行專業分析。
        
        【數據概覽】
        - 今日收盤價: {latest_close:.2f}
        - 20日均線 (月線): {ma_20:.2f}
        - 本益比 (PE): {pe_ratio}
        - 每股盈餘 (EPS): {eps}
        - 市值: {market_cap}
        
        【最新財報/法說會重點 (模擬數據)】
        {report_text}
        
        【分析要求】
        你一位華爾街等級的專業台股分析師，請針對提供的數據與財報內容進行診斷。
        請使用繁體中文，並以 Markdown 格式輸出。
        報告結構需包含：
        1. 市場趨勢判斷（多/空/盤整）：結合技術面(均線)與基本面數據。
        2. 財報深度解讀：請具體引用【最新財報】中的內容進行分析（如毛利率、AI需求等）。
        3. 投資建議（短線/長線）：給出具體的操作建議。
        """

        # 呼叫 API
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"AI 分析失敗: {e}"

# Step 4: Streamlit 儀表板 UI
def main():
    st.title("📈 台股全方位分析儀表板 (Powered by Gemini)")

    # 側邊欄
    st.sidebar.header("設定")
    ticker_input = st.sidebar.text_input("輸入股票代號", value="2330.TW")
    run_analysis = st.sidebar.button("開始 AI 診斷")

    if run_analysis:
        with st.spinner("正在獲取數據..."):
            history, info = get_stock_data(ticker_input)

        if history is not None and not history.empty:
            # 計算必要指標
            latest_close = history['Close'].iloc[-1]
            prev_close = history['Close'].iloc[-2]
            change = latest_close - prev_close
            pct_change = (change / prev_close) * 100
            pe_ratio = info.get('trailingPE', 'N/A')

            # 主畫面區塊 1: 數據概覽
            col1, col2, col3 = st.columns(3)
            col1.metric("目前股價", f"{latest_close:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
            col2.metric("本益比 (PE)", f"{pe_ratio}")
            col3.metric("最高價 (近半年)", f"{history['High'].max():.2f}")

            # 主畫面區塊 2: K線圖
            st.subheader(f"{ticker_input} 股價走勢與均線")
            
            # 計算 20MA
            history['MA20'] = history['Close'].rolling(window=20).mean()

            fig = go.Figure()
            
            # K線圖
            fig.add_trace(go.Candlestick(x=history.index,
                            open=history['Open'],
                            high=history['High'],
                            low=history['Low'],
                            close=history['Close'],
                            name='K線'))
            
            # 20MA 線
            fig.add_trace(go.Scatter(x=history.index, y=history['MA20'], 
                                     mode='lines', name='20日均線 (MA20)',
                                     line=dict(color='orange', width=1.5)))

            fig.update_layout(xaxis_rangeslider_visible=False, height=500)
            st.plotly_chart(fig, use_container_width=True)

            # 主畫面區塊 3: AI 報告
            st.subheader("🤖 Gemini 投資顧問分析報告")
            
            # 新增：獲取財報文字
            with st.spinner("正在爬取最新財報與法說會資料 (模擬)..."):
                report_text = get_financial_report_text(ticker_input)
                st.info("已成功獲取財報文字數據，AI 正在進行深度解讀...")
            
            with st.spinner("Gemini 正在撰寫分析報告..."):
                analysis_result = analyze_with_gemini(ticker_input, history, info, report_text)
                st.markdown(analysis_result)

        else:
            st.error("無法獲取數據，請檢查股票代號是否正確 (例如: 2330.TW)。")

if __name__ == "__main__":
    main()
