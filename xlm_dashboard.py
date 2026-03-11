import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="XLM x402 プロ向けダッシュボード", layout="wide")
st.title("XLM x402 投資家向けダッシュボード")

# --- 過去7日分の時間別データ取得 ---
def get_historical_prices(days=7):
    try:
        url = "https://api.coingecko.com/api/v3/coins/stellar/market_chart"
        params = {"vs_currency":"jpy","days":str(days),"interval":"hourly"}
        data = requests.get(url, params=params, timeout=10).json()
        prices = [p[1] for p in data.get("prices", [])]
        return prices
    except:
        return []

# --- RSI計算 ---
def get_rsi(prices, period=14):
    if len(prices) < period:
        return None
    deltas = [prices[i+1]-prices[i] for i in range(len(prices)-1)]
    gains = [max(d,0) for d in deltas]
    losses = [abs(min(d,0)) for d in deltas]
    avg_gain = sum(gains[:period])/period
    avg_loss = sum(losses[:period])/period
    for i in range(period,len(deltas)):
        avg_gain = (avg_gain*(period-1)+gains[i])/period
        avg_loss = (avg_loss*(period-1)+losses[i])/period
    rs = avg_gain/avg_loss if avg_loss != 0 else 0
    return 100-(100/(1+rs))

# --- 移動平均（SMA）計算 ---
def get_sma(prices, period=14):
    if len(prices) < period:
        return []
    return pd.Series(prices).rolling(window=period).mean().tolist()

# --- 現在価格・24h変動 ---
def get_current_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids":"stellar","vs_currencies":"jpy","include_24hr_change":"true"}
        data = requests.get(url, params=params, timeout=10).json()
        if "stellar" in data:
            return data["stellar"].get("jpy",0), data["stellar"].get("jpy_24h_change",0)
        else:
            return 0,0
    except:
        return 0,0

# --- データ取得 ---
prices = get_historical_prices(7)
current_price, change_24h = get_current_price()
rsi = get_rsi(prices)
sma14 = get_sma(prices, 14)
sma50 = get_sma(prices, 50)

# --- トレンド判定 ---
if rsi is not None:
    if rsi > 70:
        trend = "売りトレンド（RSI高め）"
    elif rsi < 30:
        trend = "買いトレンド（RSI低め）"
    else:
        trend = "レンジ相場"
else:
    trend = "RSI計算不可"

# --- 表示 ---
col1, col2, col3 = st.columns(3)
col1.metric("XLM価格 (JPY)", f"{current_price:.2f}円", f"{change_24h:.2f}%")
col2.metric("RSI", f"{rsi:.2f}" if rsi else "N/A")
col3.write(f"トレンド: {trend}")  # ← f文字列で安全

# --- チャート表示 ---
st.subheader("価格チャート（過去7日）")
df = pd.DataFrame({
    "Price": prices,
    "SMA14": sma14 + [None]*(len(prices)-len(sma14)),
    "SMA50": sma50 + [None]*(len(prices)-len(sma50))
})
st.line_chart(df)
st.write("※投資判断の参考用です。")
