import streamlit as st
import yfinance as yf
import google.generativeai as genai
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv
import os
import pandas as pd
import requests
import time
import pdfplumber
import datetime
from daily_report import get_market_summary, generate_ai_report, send_email

# Step 1: 環境設定 - 載入環境變數
load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_TO = os.getenv("MAIL_TO")

# 設定 Streamlit 頁面配置
st.set_page_config(page_title="台股全方位 AI 助理", layout="wide")

# ==========================================
# 共用函數 (Utilities)
# ==========================================

def get_stock_data(ticker):
    """獲取指定股票的歷史股價與基本資料"""
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="6mo")
        info = stock.info
        if history.empty:
            return None, None
        return history, info
    except Exception as e:
        st.error(f"獲取數據時發生錯誤: {e}")
        return None, None

def extract_text_from_pdf(uploaded_file):
    """使用 pdfplumber 解析上傳的 PDF"""
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"PDF 解析失敗: {e}"

def get_financial_report_text(ticker):
    """模擬爬取公開財報 PDF 並轉為文字 (Fallback)"""
    time.sleep(1.5)
    if "2330" in ticker:
        return """
        【2024年第三季法說會重點摘要】
        1. 營收表現：第三季合併營收約新台幣7,596億9千萬元，稅後純益約新台幣3,252億6千萬元，每股盈餘為新台幣12.54元。
        2. 毛利率：第三季毛利率為57.8%，營業利益率為47.5%。
        3. 先進製程：3奈米製程出貨佔第三季晶圓銷售金額的20%，5奈米佔32%。
        4. 未來展望：AI需求強勁，預期第四季營收持續成長。
        """
    else:
        return f"【{ticker} 近期財務報告摘要】\n(模擬數據) 營收穩定成長，毛利率維持水準，管理層對未來持審慎樂觀態度。"

# ==========================================
# 頁面 1: 個股全方位分析
# ==========================================

def page_stock_analysis():
    st.header("📈 個股全方位分析")

    col1, col2 = st.columns([1, 3])
    with col1:
        ticker_input = st.text_input("輸入股票代號", value="2330.TW")
        uploaded_file = st.file_uploader("上傳財報 PDF (選填)", type="pdf")
        run_analysis = st.button("開始 AI 診斷")

    if run_analysis:
        with st.spinner("正在獲取數據..."):
            history, info = get_stock_data(ticker_input)

        if history is not None and not history.empty:
            # 1. 數據概覽
            latest_close = history['Close'].iloc[-1]
            change = latest_close - history['Close'].iloc[-2]
            pct_change = (change / history['Close'].iloc[-2]) * 100
            
            c1, c2, c3 = st.columns(3)
            c1.metric("目前股價", f"{latest_close:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
            c2.metric("本益比 (PE)", f"{info.get('trailingPE', 'N/A')}")
            c3.metric("市值", f"{info.get('marketCap', 'N/A')}")

            # 2. K線圖
            history['MA20'] = history['Close'].rolling(window=20).mean()
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=history.index, open=history['Open'], high=history['High'],
                            low=history['Low'], close=history['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=history.index, y=history['MA20'], mode='lines', name='MA20', line=dict(color='orange')))
            fig.update_layout(height=400, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # 3. AI 分析
            st.subheader("🤖 Gemini 深度分析報告")
            
            # 決定財報來源
            if uploaded_file:
                with st.spinner("正在解析 PDF 財報..."):
                    report_text = extract_text_from_pdf(uploaded_file)
                    st.success("已成功讀取 PDF 內容！")
            else:
                with st.spinner("正在獲取公開資訊 (模擬)..."):
                    report_text = get_financial_report_text(ticker_input)

            # 呼叫 Gemini
            if GOOGLE_API_KEY:
                try:
                    genai.configure(api_key=GOOGLE_API_KEY)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    prompt = f"""
                    請分析台股 {ticker_input}。
                    【技術面數據】收盤: {latest_close}, MA20: {history['MA20'].iloc[-1]}
                    【財報/法說會內容】
                    {report_text[:10000]} (內容過長已截斷)
                    
                    請提供：
                    1. 市場趨勢判斷
                    2. 財報重點解讀 (RAG 分析)
                    3. 投資建議
                    """
                    with st.spinner("Gemini 正在思考中..."):
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI 分析錯誤: {e}")
            else:
                st.warning("請設定 GOOGLE_API_KEY")
        else:
            st.error("找不到股票數據")

# ==========================================
# 頁面 2: 投資組合與心態
# ==========================================

def page_portfolio():
    st.header("🧘 投資組合與心態健檢")
    
    st.info("請輸入您的持倉配置，AI 將為您評估風險與提供建議。")

    # 初始化 session state
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=["股票代號", "持有比例(%)"])

    # 編輯表格
    edited_df = st.data_editor(st.session_state.portfolio, num_rows="dynamic")
    
    if st.button("分析投資組合"):
        if not edited_df.empty:
            # 繪製圓餅圖
            fig = px.pie(edited_df, values='持有比例(%)', names='股票代號', title='資產配置分佈')
            st.plotly_chart(fig)

            # AI 分析
            if GOOGLE_API_KEY:
                try:
                    genai.configure(api_key=GOOGLE_API_KEY)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    portfolio_str = edited_df.to_string()
                    prompt = f"""
                    我是台股投資人，這是我的目前持倉：
                    {portfolio_str}
                    
                    請擔任我的「投資心態教練」，幫我分析：
                    1. **風險評估**：這樣的配置是否過度集中？有無產業風險？
                    2. **穩健性評分** (1-10分)：並說明理由。
                    3. **調整建議**：為了達到長期穩健獲利，建議如何調整？(例如增加債券、分散產業等)
                    4. **心態建設**：給予一段關於長期投資的心態小語。
                    """
                    
                    with st.spinner("AI 教練正在評估您的配置..."):
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI 分析錯誤: {e}")
            else:
                st.warning("請設定 GOOGLE_API_KEY")
        else:
            st.warning("請先輸入持倉資料")

# ==========================================
# 頁面 3: 自動化日報助理
# ==========================================

def page_daily_report():
    st.header("🤖 自動化日報助理")
    st.info("設定您的觀察名單，一鍵生成 AI 盤後日報並寄送 Email。")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. 觀察名單設定")
        default_watchlist = "2330.TW, 2454.TW, 0050.TW"
        watchlist_input = st.text_area("輸入股票代號 (用逗號分隔)", value=default_watchlist)
        watchlist = [x.strip() for x in watchlist_input.split(",") if x.strip()]

        st.subheader("2. Email 設定 (選填)")
        email_user = st.text_input("Gmail 帳號", value=MAIL_USERNAME or "")
        email_pass = st.text_input("應用程式密碼", value=MAIL_PASSWORD or "", type="password")
        email_to = st.text_input("收件人 Email", value=MAIL_TO or "")

    with col2:
        st.subheader("3. 報告預覽與發送")
        if st.button("生成今日日報"):
            with st.spinner("正在抓取數據並撰寫報告..."):
                market_data = get_market_summary(watchlist)
                report = generate_ai_report(market_data)
                
                st.session_state['daily_report_content'] = f"{market_data}\n\n{report}"
                st.session_state['daily_report_subject'] = f"📊 台股每日 AI 摘要 ({datetime.date.today()})"
                
                st.success("報告生成完成！")

        if 'daily_report_content' in st.session_state:
            st.text_area("報告內容預覽", value=st.session_state['daily_report_content'], height=300)
            
            if st.button("寄送 Email"):
                if email_user and email_pass and email_to:
                    with st.spinner("正在寄送..."):
                        success, msg = send_email(
                            st.session_state['daily_report_subject'],
                            st.session_state['daily_report_content'],
                            email_user, email_pass, email_to
                        )
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                else:
                    st.error("請填寫完整的 Email 設定資訊")

# ==========================================
# 主程式路由
# ==========================================

def main():
    st.sidebar.title("台股 AI 助理")
    page = st.sidebar.radio("功能選單", ["個股全方位分析", "投資組合健檢", "自動化日報助理"])

    if page == "個股全方位分析":
        page_stock_analysis()
    elif page == "投資組合健檢":
        page_portfolio()
    elif page == "自動化日報助理":
        page_daily_report()

if __name__ == "__main__":
    main()
