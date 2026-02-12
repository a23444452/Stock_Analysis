import streamlit as st
import yfinance as yf
from google import genai
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv
import os
import pandas as pd
import requests
import time
import pdfplumber
import datetime
import json
from streamlit_js_eval import streamlit_js_eval, get_page_location
from daily_report import get_market_summary, generate_ai_report, send_email
from dca_tool import calculate_dca_performance

# Step 1: 環境設定 - 載入環境變數
load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_TO = os.getenv("MAIL_TO")

# 設定 Streamlit 頁面配置
st.set_page_config(page_title="台股全方位 AI 助理", layout="wide", page_icon="📊")

# ==========================================
# 現代化金融主題 CSS 樣式
# ==========================================

CUSTOM_CSS = """
<style>
    /* ===== Google Fonts 導入 ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');
    
    /* ===== 根元素變數 ===== */
    :root {
        --bg-primary: #0E1117;
        --bg-secondary: #1E2530;
        --bg-card: rgba(30, 41, 59, 0.7);
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --accent-blue: #60A5FA;
        --accent-purple: #A78BFA;
        --accent-cyan: #22D3EE;
        --up-color: #10B981;
        --down-color: #EF4444;
        --border-subtle: rgba(148, 163, 184, 0.15);
        --shadow-glow: 0 0 20px rgba(96, 165, 250, 0.15);
    }
    
    /* ===== 主區域背景 ===== */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        font-family: 'Noto Sans TC', 'Inter', sans-serif;
    }
    
    /* ===== 側邊欄樣式 ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(14, 17, 23, 0.95) 0%, rgba(30, 37, 48, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid var(--border-subtle);
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2 {
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* ===== Radio Button (導航) 樣式 ===== */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label {
        background: transparent;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        border: 1px solid transparent;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: var(--bg-card);
        border-color: var(--border-subtle);
        transform: translateX(4px);
    }
    
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.2), rgba(167, 139, 250, 0.1));
        border-color: var(--accent-blue);
        box-shadow: var(--shadow-glow);
    }
    
    /* ===== 標題樣式 ===== */
    h1, h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2rem !important;
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    
    /* ===== 指標卡片 (Metrics) 樣式 ===== */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.25rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-glow), 0 8px 16px rgba(0, 0, 0, 0.3);
        border-color: var(--accent-blue);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 1.75rem !important;
        font-weight: 700;
        font-family: 'Inter', monospace;
    }
    
    /* ===== 主按鈕樣式 ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px rgba(96, 165, 250, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98);
    }
    
    /* ===== 輸入框樣式 ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2) !important;
    }
    
    /* ===== 下拉選單樣式 ===== */
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
    }
    
    /* ===== 標籤頁 (Tabs) 樣式 ===== */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: rgba(96, 165, 250, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)) !important;
        color: white !important;
    }
    
    /* ===== 圖表容器樣式 ===== */
    [data-testid="stPlotlyChart"] {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1rem;
        backdrop-filter: blur(12px);
    }
    
    /* ===== 資訊框樣式 ===== */
    .stAlert {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        backdrop-filter: blur(12px);
    }
    
    [data-testid="stAlertContentInfo"] {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(167, 139, 250, 0.05)) !important;
        border-left: 4px solid var(--accent-blue) !important;
    }
    
    /* ===== 成功/警告/錯誤框樣式 ===== */
    [data-testid="stAlertContentSuccess"] {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid var(--up-color) !important;
    }
    
    [data-testid="stAlertContentWarning"] {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid #F59E0B !important;
    }
    
    [data-testid="stAlertContentError"] {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid var(--down-color) !important;
    }
    
    /* ===== 資料表格樣式 ===== */
    .stDataFrame {
        background: var(--bg-card);
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* ===== 檔案上傳器樣式 ===== */
    [data-testid="stFileUploader"] {
        background: var(--bg-card);
        border: 2px dashed var(--border-subtle);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-blue);
    }
    
    /* ===== Spinner 樣式 ===== */
    .stSpinner > div {
        border-top-color: var(--accent-blue) !important;
    }
    
    /* ===== 分隔線 ===== */
    hr {
        border-color: var(--border-subtle) !important;
    }
    
    /* ===== 自定義滾動條 ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-subtle);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-blue);
    }
    
    /* ===== 動畫效果 ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* ===== Expander 樣式 ===== */
    [data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
    }
    
    /* ===== 數據編輯器樣式 ===== */
    [data-testid="stDataFrameResizable"] {
        background: var(--bg-card) !important;
        border-radius: 12px;
    }
</style>
"""

# 注入自定義 CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 共用函數 (Utilities)
# ==========================================

# Plotly 深色金融主題配置
PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#F1F5F9', family='Noto Sans TC, Inter, sans-serif'),
    title_font=dict(size=16, color='#F1F5F9'),
    xaxis=dict(
        gridcolor='rgba(148, 163, 184, 0.1)',
        linecolor='rgba(148, 163, 184, 0.2)',
        tickfont=dict(color='#94A3B8')
    ),
    yaxis=dict(
        gridcolor='rgba(148, 163, 184, 0.1)',
        linecolor='rgba(148, 163, 184, 0.2)',
        tickfont=dict(color='#94A3B8')
    ),
    legend=dict(
        bgcolor='rgba(30, 41, 59, 0.8)',
        bordercolor='rgba(148, 163, 184, 0.2)',
        font=dict(color='#F1F5F9')
    ),
    hoverlabel=dict(
        bgcolor='#1E2530',
        font_size=13,
        font_color='#F1F5F9',
        bordercolor='#60A5FA'
    )
)

# Plotly 配色方案
CHART_COLORS = ['#60A5FA', '#10B981', '#A78BFA', '#F59E0B', '#EC4899', '#22D3EE']

def apply_chart_theme(fig, title=None):
    """套用統一的深色金融主題到 Plotly 圖表"""
    fig.update_layout(
        **PLOTLY_THEME,
        margin=dict(l=20, r=20, t=50 if title else 20, b=20)
    )
    if title:
        fig.update_layout(title=dict(text=title, x=0.5, xanchor='center'))
    return fig

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

def save_to_local_storage(key, data):
    """
    儲存資料到瀏覽器 localStorage

    Args:
        key: 儲存的鍵名
        data: 要儲存的資料 (會轉換為 JSON)
    """
    try:
        # 將資料轉為 JSON 字串
        data_json = json.dumps(data, ensure_ascii=False)
        # 轉義單引號以避免 JavaScript 語法錯誤
        data_json_escaped = data_json.replace("'", "\\'")

        # 使用 streamlit_js_eval 執行 JavaScript (使用 js_expressions 參數)
        js_code = f"localStorage.setItem('{key}', '{data_json_escaped}')"
        streamlit_js_eval(
            js_expressions=js_code,
            key=f"save_{key}_{hash(str(data))}"  # 使用 hash 確保 key 唯一性
        )
    except Exception as e:
        # 靜默失敗,不顯示錯誤訊息 (localStorage 是增強功能,非必要)
        pass

def load_from_local_storage(key, default=None):
    """
    從瀏覽器 localStorage 載入資料

    Args:
        key: 儲存的鍵名
        default: 預設值

    Returns:
        載入的資料或預設值
    """
    try:
        # 使用 streamlit_js_eval 執行 JavaScript 取得資料
        js_code = f"localStorage.getItem('{key}')"
        result = streamlit_js_eval(
            js_expressions=js_code,
            key=f"load_{key}"
        )
        if result:
            return json.loads(result)
    except Exception:
        pass
    return default

def normalize_ticker(ticker):
    """
    正規化股票代號 - 自動補上 .TW 後綴

    Args:
        ticker: 使用者輸入的股票代號

    Returns:
        正規化後的股票代號

    Examples:
        normalize_ticker("2330") -> "2330.TW"
        normalize_ticker("2330.TW") -> "2330.TW"
        normalize_ticker("0050") -> "0050.TW"
    """
    if not ticker:
        return ticker

    # 移除前後空白
    ticker = ticker.strip()

    # 如果已經有後綴,直接返回
    if '.' in ticker:
        return ticker.upper()

    # 純數字代號,自動加上 .TW
    if ticker.isdigit():
        return f"{ticker}.TW"

    # 其他情況(可能是美股等),原樣返回
    return ticker.upper()

def format_market_cap(value):
    """將市值轉換為 '億' 單位"""
    try:
        if value and isinstance(value, (int, float)):
            return f"{value / 100000000:.2f} 億"
        return "N/A"
    except:
        return "N/A"

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

    # 初始化 session state
    if 'stock_analysis' not in st.session_state:
        st.session_state.stock_analysis = {
            'ticker': '2330.TW',
            'history': None,
            'info': None,
            'ai_report': None,
            'analyzed': False
        }

    # 載入上次使用的股票代號
    if 'last_ticker' not in st.session_state:
        last_ticker = load_from_local_storage('last_stock_ticker', '2330.TW')
        if last_ticker:
            st.session_state.stock_analysis['ticker'] = last_ticker

    col1, col2 = st.columns([1, 3])
    with col1:
        ticker_input_raw = st.text_input(
            "輸入股票代號",
            value=st.session_state.stock_analysis['ticker'],
            key="ticker_input",
            help="輸入數字代號即可 (例如: 2330),系統會自動補上 .TW"
        )

        # 正規化股票代號
        ticker_input = normalize_ticker(ticker_input_raw)

        # 當股票代號改變時,清除舊的分析結果
        if ticker_input != st.session_state.stock_analysis['ticker']:
            st.session_state.stock_analysis['analyzed'] = False
            st.session_state.stock_analysis['ticker'] = ticker_input

        # 顯示正規化後的代號
        if ticker_input != ticker_input_raw:
            st.caption(f"✓ 使用代號: {ticker_input}")

        uploaded_file = st.file_uploader("上傳財報 PDF (選填)", type="pdf")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            run_analysis = st.button("🔍 開始分析", type="primary")
        with col_btn2:
            if st.button("🗑️ 清除"):
                st.session_state.stock_analysis = {
                    'ticker': '2330.TW',
                    'history': None,
                    'info': None,
                    'ai_report': None,
                    'analyzed': False
                }
                st.rerun()

    if run_analysis:
        # 儲存股票代號到 localStorage
        save_to_local_storage('last_stock_ticker', ticker_input)

        with st.spinner("正在獲取數據..."):
            history, info = get_stock_data(ticker_input)

        if history is not None and not history.empty:
            # 儲存數據到 session state
            st.session_state.stock_analysis['history'] = history
            st.session_state.stock_analysis['info'] = info
            # 1. 數據概覽
            latest_close = history['Close'].iloc[-1]
            change = latest_close - history['Close'].iloc[-2]
            pct_change = (change / history['Close'].iloc[-2]) * 100
            
            c1, c2, c3 = st.columns(3)
            c1.metric("目前股價", f"{latest_close:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
            c2.metric("本益比 (PE)", f"{info.get('trailingPE', 'N/A')}")
            c3.metric("市值", format_market_cap(info.get('marketCap')))

            # 2. K線圖
            history['MA20'] = history['Close'].rolling(window=20).mean()
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=history.index, 
                open=history['Open'], 
                high=history['High'],
                low=history['Low'], 
                close=history['Close'], 
                name='K線',
                increasing_line_color='#10B981',  # 上漲顏色
                decreasing_line_color='#EF4444',  # 下跌顏色
                increasing_fillcolor='#10B981',
                decreasing_fillcolor='#EF4444'
            ))
            fig.add_trace(go.Scatter(
                x=history.index, 
                y=history['MA20'], 
                mode='lines', 
                name='MA20', 
                line=dict(color='#F59E0B', width=2)
            ))
            fig.update_layout(height=450, xaxis_rangeslider_visible=False)
            apply_chart_theme(fig, f"📈 {ticker_input} 股價走勢圖")
            st.plotly_chart(fig, width='stretch')


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
                    client = genai.Client(api_key=GOOGLE_API_KEY)

                    market_cap_str = format_market_cap(info.get('marketCap'))
                    prompt = f"""
                    請分析台股 {ticker_input}。
                    【技術面數據】收盤: {latest_close}, MA20: {history['MA20'].iloc[-1]}, 市值: {market_cap_str}
                    【財報/法說會內容】
                    {report_text[:10000]} (內容過長已截斷)

                    請提供：
                    1. 市場趨勢判斷
                    2. 財報重點解讀 (RAG 分析)
                    3. 投資建議
                    """
                    with st.spinner("Gemini 正在思考中..."):
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        # 儲存 AI 報告到 session state
                        st.session_state.stock_analysis['ai_report'] = response.text
                        st.session_state.stock_analysis['analyzed'] = True
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI 分析錯誤: {e}")
            else:
                st.warning("請設定 GOOGLE_API_KEY")
        else:
            st.error("找不到股票數據")

    # 顯示快取的分析結果 (切換頁面後回來時顯示)
    elif st.session_state.stock_analysis['analyzed']:
        st.info("💡 以下是您上次的分析結果,如需重新分析請點擊「🔍 開始分析」")

        history = st.session_state.stock_analysis['history']
        info = st.session_state.stock_analysis['info']
        ticker_input = st.session_state.stock_analysis['ticker']

        if history is not None and not history.empty:
            # 1. 數據概覽
            latest_close = history['Close'].iloc[-1]
            change = latest_close - history['Close'].iloc[-2]
            pct_change = (change / history['Close'].iloc[-2]) * 100

            c1, c2, c3 = st.columns(3)
            c1.metric("目前股價", f"{latest_close:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
            c2.metric("本益比 (PE)", f"{info.get('trailingPE', 'N/A')}")
            c3.metric("市值", format_market_cap(info.get('marketCap')))

            # 2. K線圖
            history['MA20'] = history['Close'].rolling(window=20).mean()
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=history.index,
                open=history['Open'],
                high=history['High'],
                low=history['Low'],
                close=history['Close'],
                name='K線',
                increasing_line_color='#10B981',
                decreasing_line_color='#EF4444',
                increasing_fillcolor='#10B981',
                decreasing_fillcolor='#EF4444'
            ))
            fig.add_trace(go.Scatter(
                x=history.index,
                y=history['MA20'],
                mode='lines',
                name='MA20',
                line=dict(color='#F59E0B', width=2)
            ))
            fig.update_layout(height=450, xaxis_rangeslider_visible=False)
            apply_chart_theme(fig, f"📈 {ticker_input} 股價走勢圖")
            st.plotly_chart(fig, width='stretch')

            # 3. 顯示快取的 AI 分析
            if st.session_state.stock_analysis['ai_report']:
                st.subheader("🤖 Gemini 深度分析報告")
                st.markdown(st.session_state.stock_analysis['ai_report'])

# ==========================================
# 頁面 2: 投資組合與心態
# ==========================================

def page_portfolio():
    st.header("🧘 投資組合與心態健檢")

    st.info("💡 您的投資組合會永久儲存在瀏覽器中，下次使用時會自動載入。")

    # 初始化 session state - 嘗試從 localStorage 載入
    if 'portfolio_data' not in st.session_state:
        # 嘗試從 localStorage 載入
        stored_data = load_from_local_storage('stock_portfolio')

        if stored_data:
            try:
                st.session_state.portfolio_data = pd.DataFrame(stored_data)
                st.success("✓ 已載入您上次儲存的投資組合")
            except Exception:
                # 載入失敗,使用預設範例
                st.session_state.portfolio_data = pd.DataFrame({
                    "股票代號": ["2330.TW", "2454.TW", "0050.TW"],
                    "持有比例(%)": [40.0, 30.0, 30.0]
                })
        else:
            # 首次使用,顯示預設範例
            st.session_state.portfolio_data = pd.DataFrame({
                "股票代號": ["2330.TW", "2454.TW", "0050.TW"],
                "持有比例(%)": [40.0, 30.0, 30.0]
            })
            st.info("👋 首次使用!以下是範例投資組合,您可以直接修改。")

    # 編輯表格 (移到按鈕前面,避免重新渲染問題)
    edited_df = st.data_editor(
        st.session_state.portfolio_data,
        num_rows="dynamic",
        use_container_width=True,
        key="portfolio_editor"
    )

    # 操作按鈕列
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("💾 儲存組合"):
            # 更新 session state 並儲存到 localStorage
            st.session_state.portfolio_data = edited_df
            portfolio_dict = edited_df.to_dict('records')
            save_to_local_storage('stock_portfolio', portfolio_dict)
            st.success("✓ 投資組合已儲存!")
            st.rerun()
    with col2:
        if st.button("🗑️ 清空組合"):
            st.session_state.portfolio_data = pd.DataFrame(columns=["股票代號", "持有比例(%)"])
            save_to_local_storage('stock_portfolio', [])
            st.rerun()
    with col3:
        st.caption("提示：編輯後請點擊「💾 儲存組合」以永久保存")

    # 分析按鈕
    if st.button("📊 分析投資組合", type="primary"):
        # 先更新 session state
        st.session_state.portfolio_data = edited_df
        if not edited_df.empty:
            # 繪製圓餅圖
            fig = px.pie(
                edited_df, 
                values='持有比例(%)', 
                names='股票代號',
                color_discrete_sequence=CHART_COLORS,
                hole=0.4  # 甜甜圈效果
            )
            apply_chart_theme(fig, "💰 資產配置分佈")
            st.plotly_chart(fig, width='stretch')

            # AI 分析
            if GOOGLE_API_KEY:
                try:
                    client = genai.Client(api_key=GOOGLE_API_KEY)

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
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
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
# 頁面 4: 基本面 AI 分析
# ==========================================

def page_fundamental_analysis():
    st.header("📊 基本面 AI 分析")
    st.info("深入分析公司財務報表：損益表、資產負債表與現金流量表。")

    ticker_input_raw = st.text_input(
        "輸入股票代號",
        value="2330.TW",
        key="fund_ticker",
        help="輸入數字代號即可 (例如: 2330),系統會自動補上 .TW"
    )
    ticker_input = normalize_ticker(ticker_input_raw)

    # 顯示正規化後的代號
    if ticker_input != ticker_input_raw:
        st.caption(f"✓ 使用代號: {ticker_input}")

    if st.button("開始基本面分析"):
        # 只在 spinner 內做數據獲取
        with st.spinner("正在獲取財務數據..."):
            try:
                stock = yf.Ticker(ticker_input)
                info = stock.info

                # 獲取三大報表 (年報)
                financials = stock.financials.T  # 損益表
                balance_sheet = stock.balance_sheet.T  # 資產負債表
                cashflow = stock.cashflow.T  # 現金流量表
            except Exception as e:
                st.error(f"發生錯誤: {e}")
                st.stop()

        # UI 元素移到 spinner 外面
        try:
            # 顯示基本資訊
            col1, col2, col3 = st.columns(3)
            col1.metric("目前股價", f"{info.get('currentPrice', 'N/A')}")
            col2.metric("市值", format_market_cap(info.get('marketCap')))
            col3.metric("產業", f"{info.get('industry', 'N/A')}")

            # 建立分頁 (workaround for Streamlit tabs bug #8676)
            tabs_wrapper = st.columns([0.999, 0.001])
            with tabs_wrapper[0]:
                tab1, tab2, tab3, tab4 = st.tabs(["損益表分析", "資產負債表分析", "現金流量表分析", "AI 綜合診斷"])

                # 1. 損益表分析
                with tab1:
                    st.subheader("損益表關鍵指標")
                    if not financials.empty:
                        # 嘗試選取關鍵欄位 (yfinance 欄位名稱可能會變，需做容錯)
                        cols_to_plot = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income']
                        available_cols = [c for c in cols_to_plot if c in financials.columns]
                        
                        # 中文對照表
                        col_map = {
                            'Total Revenue': '總營收', 
                            'Gross Profit': '毛利', 
                            'Operating Income': '營業利益', 
                            'Net Income': '淨利'
                        }

                        if available_cols:
                            df_plot = financials[available_cols].sort_index()
                            # 重新命名欄位為中文
                            df_plot = df_plot.rename(columns=col_map)
                            
                            fig = px.bar(df_plot, barmode='group', color_discrete_sequence=CHART_COLORS)
                            apply_chart_theme(fig, "📈 年度營收與獲利趨勢")
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, width='stretch', key="chart_income")
                            st.dataframe(financials.head().reset_index(), key="df_income", hide_index=True)
                        else:
                            st.warning("無法抓取完整的損益表欄位")
                            st.dataframe(financials.reset_index(), key="df_income_full", hide_index=True)
                    else:
                        st.warning("無損益表數據")

                # 2. 資產負債表分析
                with tab2:
                    st.subheader("資產負債結構")
                    if not balance_sheet.empty:
                        cols_to_plot = ['Total Assets', 'Total Liabilities Net Minority Interest', 'Stockholders Equity']
                        # 修正：有些版本 yfinance 欄位名稱不同
                        if 'Total Liabilities Net Minority Interest' not in balance_sheet.columns:
                             if 'Total Liabilities' in balance_sheet.columns:
                                 cols_to_plot[1] = 'Total Liabilities'
                        
                        available_cols = [c for c in cols_to_plot if c in balance_sheet.columns]
                        
                        # 中文對照表
                        col_map = {
                            'Total Assets': '總資產',
                            'Total Liabilities Net Minority Interest': '總負債',
                            'Total Liabilities': '總負債',
                            'Stockholders Equity': '股東權益'
                        }

                        if available_cols:
                            df_plot = balance_sheet[available_cols].sort_index()
                            # 重新命名欄位為中文
                            df_plot = df_plot.rename(columns=col_map)

                            fig = px.bar(df_plot, barmode='group', color_discrete_sequence=CHART_COLORS)
                            apply_chart_theme(fig, "🏦 資產負債結構趨勢")
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, width='stretch', key="chart_balance")
                            st.dataframe(balance_sheet.head().reset_index(), key="df_balance", hide_index=True)
                        else:
                            st.warning("無法抓取完整的資產負債表欄位")
                            st.dataframe(balance_sheet.reset_index(), key="df_balance_full", hide_index=True)
                    else:
                        st.warning("無資產負債表數據")

                # 3. 現金流量表分析
                with tab3:
                    st.subheader("現金流量分析")
                    if not cashflow.empty:
                        cols_to_plot = ['Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow']
                        available_cols = [c for c in cols_to_plot if c in cashflow.columns]
                        
                        # 中文對照表
                        col_map = {
                            'Operating Cash Flow': '營運現金流',
                            'Investing Cash Flow': '投資現金流',
                            'Financing Cash Flow': '籌資現金流'
                        }

                        if available_cols:
                            df_plot = cashflow[available_cols].sort_index()
                            # 重新命名欄位為中文
                            df_plot = df_plot.rename(columns=col_map)

                            fig = px.bar(df_plot, barmode='group', color_discrete_sequence=CHART_COLORS)
                            apply_chart_theme(fig, "💵 現金流量趨勢")
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, width='stretch', key="chart_cashflow")
                            st.dataframe(cashflow.head().reset_index(), key="df_cashflow", hide_index=True)
                        else:
                            st.warning("無法抓取完整的現金流量表欄位")
                            st.dataframe(cashflow.reset_index(), key="df_cashflow_full", hide_index=True)
                    else:
                        st.warning("無現金流量表數據")

                # 4. AI 綜合診斷
                with tab4:
                    st.subheader("🤖 Gemini 財務健康診斷書")
                    
                    if GOOGLE_API_KEY:
                        with st.spinner("AI 正在閱讀財報並進行分析..."):
                            # 準備數據給 AI (取最近兩年)
                            fin_summary = financials.iloc[:2].to_string() if not financials.empty else "無數據"
                            bs_summary = balance_sheet.iloc[:2].to_string() if not balance_sheet.empty else "無數據"
                            cf_summary = cashflow.iloc[:2].to_string() if not cashflow.empty else "無數據"

                            prompt = f"""
                            請擔任專業的財務分析師，針對 {ticker_input} 的財務報表進行深度分析。

                            【損益表摘要 (近兩年)】
                            {fin_summary}

                            【資產負債表摘要 (近兩年)】
                            {bs_summary}

                            【現金流量表摘要 (近兩年)】
                            {cf_summary}

                            請提供以下分析報告 (使用繁體中文 Markdown)：
                            1. **獲利能力分析**：營收成長率、毛利率、淨利率的變化趨勢。
                            2. **財務結構與償債能力**：資產負債配置是否健康？有無流動性風險？
                            3. **現金流品質**：營業現金流是否充足？投資活動是否積極？
                            4. **綜合評價**：給予該公司基本面評分 (1-10分) 與投資建議。
                            """

                            try:
                                client = genai.Client(api_key=GOOGLE_API_KEY)
                                response = client.models.generate_content(
                                    model='gemini-2.5-flash',
                                    contents=prompt
                                )
                                st.markdown(response.text)
                            except Exception as e:
                                st.error(f"AI 分析失敗: {e}")
                    else:
                        st.warning("請設定 GOOGLE_API_KEY 以啟用 AI 分析功能")

        except Exception as e:
            st.error(f"發生錯誤: {e}")

# ==========================================
# 頁面 5: 定期定額回測
# ==========================================

def page_dca_backtest():
    st.header("⏳ 定期定額 (DCA) 歷史回測")
    st.info("模擬每月固定金額投資，計算歷史報酬與風險，並由 AI 進行策略分析。")

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("參數設定")
        ticker_input_raw = st.text_input(
            "輸入股票代號",
            value="2330.TW",
            key="dca_ticker",
            help="輸入數字代號即可 (例如: 2330),系統會自動補上 .TW"
        )
        ticker_input = normalize_ticker(ticker_input_raw)

        # 顯示正規化後的代號
        if ticker_input != ticker_input_raw:
            st.caption(f"✓ 使用代號: {ticker_input}")

        monthly_amount = st.number_input("每月扣款金額 (TWD)", min_value=1000, value=10000, step=1000)
        years = st.selectbox("回測年數", [1, 3, 5, 10], index=1)
        
        run_dca = st.button("開始回測")

    if run_dca:
        with st.spinner(f"正在回測 {ticker_input} 過去 {years} 年的表現..."):
            df_result, metrics = calculate_dca_performance(ticker_input, monthly_amount, years)
            
            if df_result is not None:
                # 1. 顯示績效指標
                st.subheader("📊 回測結果")
                m1, m2, m3, m4 = st.columns(4)
                
                total_cost = metrics['total_cost']
                final_val = metrics['final_value']
                ret_pct = metrics['total_return_pct']
                mdd = metrics['max_drawdown']
                
                m1.metric("總投入成本", f"${total_cost:,.0f}")
                m2.metric("最終資產價值", f"${final_val:,.0f}", f"{metrics['total_return']:,.0f} ({ret_pct:.2f}%)")
                m3.metric("最大回撤 (MDD)", f"{mdd:.2f}%", delta_color="inverse") # MDD 越小越好，所以用 inverse
                m4.metric("年化波動率", f"{metrics['volatility']:.2f}%", delta_color="inverse")

                # 2. 繪製資產曲線圖
                st.subheader("📈 資產成長曲線")
                fig = go.Figure()
                
                # 繪製資產價值
                fig.add_trace(go.Scatter(
                    x=df_result.index, 
                    y=df_result['Portfolio_Value'], 
                    mode='lines', 
                    name='資產價值',
                    line=dict(color='#10B981', width=2.5),
                    fill='tozeroy',
                    fillcolor='rgba(16, 185, 129, 0.15)'
                ))
                
                # 繪製投入成本 (階梯狀)
                fig.add_trace(go.Scatter(
                    x=df_result.index, 
                    y=df_result['Total_Cost'], 
                    mode='lines', 
                    name='累積投入成本',
                    line=dict(color='#60A5FA', width=2, dash='dash')
                ))

                fig.update_layout(
                    xaxis_title="日期",
                    yaxis_title="金額 (TWD)",
                    hovermode="x unified",
                    legend=dict(orientation="h", y=1.02, yanchor="bottom", x=1, xanchor="right"),
                    height=450
                )
                apply_chart_theme(fig, f"📊 {ticker_input} 定期定額 {years} 年績效走勢")
                st.plotly_chart(fig, width='stretch')


                # 3. AI 策略分析
                st.subheader("🤖 Gemini 策略分析報告")
                if GOOGLE_API_KEY:
                    with st.spinner("AI 正在分析此策略的風險與報酬..."):
                        prompt = f"""
                        請分析以下「定期定額 (DCA)」投資策略的績效：

                        *   **標的**：{ticker_input}
                        *   **期間**：過去 {years} 年
                        *   **每月投入**：{monthly_amount} TWD
                        *   **總報酬率**：{ret_pct:.2f}%
                        *   **最大回撤 (MDD)**：{mdd:.2f}% (這段期間資產從高點下跌的最大幅度)
                        *   **年化波動率**：{metrics['volatility']:.2f}%

                        請提供一份專業的分析報告 (使用繁體中文 Markdown)：
                        1.  **績效評價**：這樣的報酬率在該期間是否優於大盤或定存？
                        2.  **風險分析**：MDD {mdd:.2f}% 代表投資人需承受多大的心理壓力？波動率是否過高？
                        3.  **微笑曲線效應**：根據走勢 (AI 無法看圖，請根據一般 DCA 特性說明)，這段期間是否有發揮定期定額「低檔多買」的優勢？
                        4.  **投資建議**：適合哪種類型的投資人？(保守/穩健/積極)
                        """

                        try:
                            client = genai.Client(api_key=GOOGLE_API_KEY)
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=prompt
                            )
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"AI 分析失敗: {e}")
                else:
                    st.warning("請設定 GOOGLE_API_KEY 以啟用 AI 分析功能")
            else:
                st.error(f"回測失敗: {metrics.get('error')}")

# ==========================================
# 主程式路由
# ==========================================

def main():
    # ===== 側邊欄 Logo 區塊 =====
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">📊</div>
        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700; 
            background: linear-gradient(135deg, #60A5FA, #22D3EE);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;">
            台股 AI 助理
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.25rem;">
            智能投資決策平台
        </p>
    </div>
    <hr style="border-color: rgba(148, 163, 184, 0.15); margin: 0.5rem 0 1.5rem 0;">
    """, unsafe_allow_html=True)
    
    # ===== 功能選單 (帶圖標) =====
    menu_options = {
        "📈 個股全方位分析": "個股全方位分析",
        "📊 基本面 AI 分析": "基本面 AI 分析",
        "🧘 投資組合健檢": "投資組合健檢",
        "⏳ 定期定額回測": "定期定額回測",
        "🤖 自動化日報助理": "自動化日報助理"
    }
    
    st.sidebar.markdown("<p style='color: #94A3B8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;'>功能選單</p>", unsafe_allow_html=True)
    
    page = st.sidebar.radio("功能選單", list(menu_options.keys()), label_visibility="collapsed")
    selected_page = menu_options[page]
    
    # ===== 頁尾資訊 =====
    st.sidebar.markdown("""
    <div style="position: fixed; bottom: 1rem; left: 1rem; right: 1rem; max-width: 280px;">
        <hr style="border-color: rgba(148, 163, 184, 0.15); margin-bottom: 1rem;">
        <p style="color: #64748B; font-size: 0.75rem; text-align: center;">
            Powered by <span style="color: #60A5FA;">Gemini AI</span> & yfinance
        </p>
    </div>
    """, unsafe_allow_html=True)

    if selected_page == "個股全方位分析":
        page_stock_analysis()
    elif selected_page == "基本面 AI 分析":
        page_fundamental_analysis()
    elif selected_page == "投資組合健檢":
        page_portfolio()
    elif selected_page == "定期定額回測":
        page_dca_backtest()
    elif selected_page == "自動化日報助理":
        page_daily_report()


if __name__ == "__main__":
    main()
