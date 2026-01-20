from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from daily_report import get_market_summary, generate_ai_report

app = FastAPI()

class StockRequest(BaseModel):
    stock_id: str

@app.post("/analyze")
async def run_analysis(request: StockRequest):
    stock_id = request.stock_id.strip()
    print(f"收到分析請求：{stock_id}")

    try:
        # 1. 獲取市場數據
        # 如果使用者只輸入代號 (如 2330)，自動補上 .TW (如果是台股)
        if stock_id.isdigit():
            stock_id = f"{stock_id}.TW"
            
        market_data = get_market_summary([stock_id])
        
        if "獲取失敗" in market_data:
             return {"status": "error", "message": f"無法獲取 {stock_id} 的數據，請確認代號是否正確。"}

        # 2. AI 分析
        report = generate_ai_report(market_data)
        
        # 3. 組合回傳結果
        full_response = f"{market_data}\n\n{report}"
        
        return {"status": "success", "message": full_response}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # 讓 API 跑在 0.0.0.0:8001
    uvicorn.run(app, host="0.0.0.0", port=8001)
