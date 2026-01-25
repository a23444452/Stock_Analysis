import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yfinance as yf
from google import genai
from dotenv import load_dotenv
import datetime

# 載入環境變數
load_dotenv(override=True)

# 設定
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")  # 您的 Gmail
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  # 您的 Gmail 應用程式密碼
MAIL_TO = os.getenv("MAIL_TO")              # 收件人 Email

# 監控清單
WATCHLIST = ["2330.TW", "2454.TW", "0050.TW"]

def get_market_summary(tickers):
    summary = ""
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                close = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = close - prev
                pct = (change / prev) * 100
                summary += f"- {ticker}: {close:.2f} ({change:+.2f} / {pct:+.2f}%)\n"
        except Exception as e:
            summary += f"- {ticker}: 獲取失敗 ({e})\n"
    return summary

def generate_ai_report(market_data):
    if not GOOGLE_API_KEY:
        return "錯誤：未設定 GOOGLE_API_KEY"
    
    client = genai.Client(api_key=GOOGLE_API_KEY)

    prompt = f"""
    請撰寫一份簡短的台股收盤日報。

    【今日市場數據】
    {market_data}

    【撰寫要求】
    1. 總結今日重點個股表現。
    2. 給予明日操作的一句話建議。
    3. 語氣專業且激勵人心。
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI 生成失敗: {e}"

def send_email(subject, body, username=None, password=None, to_addr=None):
    # 使用傳入參數或環境變數
    username = username or MAIL_USERNAME
    password = password or MAIL_PASSWORD
    to_addr = to_addr or MAIL_TO

    if not username or not password or not to_addr:
        return False, "⚠️ 未設定 Email 帳號、密碼或收件人。"

    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(username, password)
        text = msg.as_string()
        server.sendmail(username, to_addr, text)
        server.quit()
        return True, "✅ Email 發送成功！"
    except Exception as e:
        return False, f"❌ Email 發送失敗: {e}"

def main():
    print(f"[{datetime.datetime.now()}] 開始執行每日自動分析...")
    
    # 1. 獲取數據
    market_data = get_market_summary(WATCHLIST)
    print("數據獲取完成。")
    
    # 2. AI 分析
    report = generate_ai_report(market_data)
    print("AI 報告生成完成。")
    
    # 3. 寄送 Email
    subject = f"📊 台股每日 AI 摘要 ({datetime.date.today()})"
    send_email(subject, f"{market_data}\n\n{report}")

if __name__ == "__main__":
    main()
