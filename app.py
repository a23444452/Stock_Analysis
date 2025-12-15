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
from dca_tool import calculate_dca_performance

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
            c3.metric("市值", format_market_cap(info.get('marketCap')))

            # 2. K線圖
            history['MA20'] = history['Close'].rolling(window=20).mean()
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=history.index, open=history['Open'], high=history['High'],
                            low=history['Low'], close=history['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=history.index, y=history['MA20'], mode='lines', name='MA20', line=dict(color='orange')))
            fig.update_layout(height=400, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, width="stretch")

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
# 頁面 4: 基本面 AI 分析
# ==========================================

def page_fundamental_analysis():
    st.header("📊 基本面 AI 分析")
    st.info("深入分析公司財務報表：損益表、資產負債表與現金流量表。")

    ticker_input = st.text_input("輸入股票代號", value="2330.TW", key="fund_ticker")
    
    if st.button("開始基本面分析"):
        with st.spinner("正在獲取財務數據..."):
            try:
                stock = yf.Ticker(ticker_input)
                info = stock.info
                
                # 獲取三大報表 (年報)
                financials = stock.financials.T  # 損益表
                balance_sheet = stock.balance_sheet.T  # 資產負債表
                cashflow = stock.cashflow.T  # 現金流量表
                
                # 顯示基本資訊
                col1, col2, col3 = st.columns(3)
                col1.metric("目前股價", f"{info.get('currentPrice', 'N/A')}")
                col2.metric("市值", format_market_cap(info.get('marketCap')))
                col3.metric("產業", f"{info.get('industry', 'N/A')}")

                # 建立分頁
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
                            
                            fig = px.bar(df_plot, barmode='group', title="年度營收與獲利趨勢")
                            st.plotly_chart(fig, width="stretch")
                            st.dataframe(financials.head())
                        else:
                            st.warning("無法抓取完整的損益表欄位")
                            st.dataframe(financials)
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

                            fig = px.bar(df_plot, barmode='group', title="資產負債結構趨勢")
                            st.plotly_chart(fig, width="stretch")
                            st.dataframe(balance_sheet.head())
                        else:
                            st.warning("無法抓取完整的資產負債表欄位")
                            st.dataframe(balance_sheet)
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

                            fig = px.bar(df_plot, barmode='group', title="現金流量趨勢")
                            st.plotly_chart(fig, width="stretch")
                            st.dataframe(cashflow.head())
                        else:
                            st.warning("無法抓取完整的現金流量表欄位")
                            st.dataframe(cashflow)
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
                                genai.configure(api_key=GOOGLE_API_KEY)
                                model = genai.GenerativeModel('gemini-2.5-flash')
                                response = model.generate_content(prompt)
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
        ticker_input = st.text_input("輸入股票代號", value="2330.TW", key="dca_ticker")
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
                    line=dict(color='#00CC96', width=2),
                    fill='tozeroy', # 填滿下方區域
                    fillcolor='rgba(0, 204, 150, 0.1)'
                ))
                
                # 繪製投入成本 (階梯狀)
                fig.add_trace(go.Scatter(
                    x=df_result.index, 
                    y=df_result['Total_Cost'], 
                    mode='lines', 
                    name='累積投入成本',
                    line=dict(color='#EF553B', width=2, dash='dash')
                ))

                fig.update_layout(
                    title=f"{ticker_input} 定期定額 {years} 年績效走勢",
                    xaxis_title="日期",
                    yaxis_title="金額 (TWD)",
                    hovermode="x unified",
                    legend=dict(orientation="h", y=1.02, yanchor="bottom", x=1, xanchor="right")
                )
                st.plotly_chart(fig, width="stretch")

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
                            genai.configure(api_key=GOOGLE_API_KEY)
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            response = model.generate_content(prompt)
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
    st.sidebar.title("台股 AI 助理")
    page = st.sidebar.radio("功能選單", ["個股全方位分析", "基本面 AI 分析", "投資組合健檢", "定期定額回測", "自動化日報助理"])

    if page == "個股全方位分析":
        page_stock_analysis()
    elif page == "基本面 AI 分析":
        page_fundamental_analysis()
    elif page == "投資組合健檢":
        page_portfolio()
    elif page == "定期定額回測":
        page_dca_backtest()
    elif page == "自動化日報助理":
        page_daily_report()

if __name__ == "__main__":
    main()
