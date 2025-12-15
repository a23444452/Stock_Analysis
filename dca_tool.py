import yfinance as yf
import pandas as pd
import numpy as np

def calculate_dca_performance(ticker, monthly_amount, years):
    """
    計算定期定額 (DCA) 回測績效
    
    Args:
        ticker (str): 股票代號
        monthly_amount (float): 每月扣款金額
        years (int): 投資年數
        
    Returns:
        df_result (pd.DataFrame): 每日資產價值變化 (用於繪圖)
        metrics (dict): 績效指標 (總報酬, 最大回撤, 波動率)
    """
    try:
        # 1. 獲取歷史數據
        # yfinance 的 period 參數: '1y', '2y', '5y', '10y', 'max'
        period = f"{years}y"
        stock = yf.Ticker(ticker)
        # 獲取日資料
        hist = stock.history(period=period)
        
        if hist.empty:
            return None, {"error": "無法獲取歷史數據"}

        # 2. 模擬每月定期定額
        # 將數據重取樣為每月第一天 (Month Start)
        monthly_data = hist['Close'].resample('MS').first()
        
        # 建立投資紀錄
        investments = []
        total_shares = 0
        total_cost = 0
        
        for date, price in monthly_data.items():
            # 買入股數 (金額 / 股價)
            shares_bought = monthly_amount / price
            total_shares += shares_bought
            total_cost += monthly_amount
            
            investments.append({
                'Date': date,
                'Price': price,
                'Shares_Bought': shares_bought,
                'Total_Shares': total_shares,
                'Total_Cost': total_cost,
                'Portfolio_Value': total_shares * price
            })
            
        df_invest = pd.DataFrame(investments).set_index('Date')
        
        # 3. 結合日資料計算每日資產價值 (為了畫出平滑曲線與計算 MDD)
        # 將投資紀錄合併回日資料
        df_daily = hist[['Close']].copy()
        # df_daily['Total_Shares'] = np.nan (Removed to avoid overlap error)
        
        # 填入每月的累積股數
        # 注意：這裡簡化處理，假設每月1號買入後，直到下個月1號前股數不變
        # 使用 asof 或 reindex + ffill
        df_daily = df_daily.join(df_invest[['Total_Shares']], how='left')
        df_daily['Total_Shares'] = df_daily['Total_Shares'].ffill()
        
        # 處理期初尚未開始投資的 NaN (填 0)
        df_daily['Total_Shares'] = df_daily['Total_Shares'].fillna(0)
        
        # 計算每日資產價值
        df_daily['Portfolio_Value'] = df_daily['Close'] * df_daily['Total_Shares']
        
        # 計算每日投入成本 (為了畫圖比較)
        df_daily = df_daily.join(df_invest[['Total_Cost']], how='left')
        df_daily['Total_Cost'] = df_daily['Total_Cost'].ffill().fillna(0)

        # 4. 計算績效指標
        final_value = df_daily['Portfolio_Value'].iloc[-1]
        final_cost = df_daily['Total_Cost'].iloc[-1]
        
        if final_cost == 0:
            return None, {"error": "投資成本為 0"}

        total_return = final_value - final_cost
        total_return_pct = (total_return / final_cost) * 100
        
        # 計算最大回撤 (Max Drawdown)
        # 每日資產價值的累積最大值
        rolling_max = df_daily['Portfolio_Value'].cummax()
        drawdown = (df_daily['Portfolio_Value'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100  # 轉為百分比
        
        # 計算年化波動率 (Volatility)
        # 使用日報酬率的標準差 * sqrt(252)
        daily_returns = df_daily['Portfolio_Value'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100

        metrics = {
            "total_cost": final_cost,
            "final_value": final_value,
            "total_return": total_return,
            "total_return_pct": total_return_pct,
            "max_drawdown": max_drawdown,
            "volatility": volatility,
            "years": years
        }
        
        return df_daily, metrics

    except Exception as e:
        return None, {"error": str(e)}
