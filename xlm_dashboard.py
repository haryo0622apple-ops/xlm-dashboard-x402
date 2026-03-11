import requests
import streamlit as st

st.title("XLM x402 投資家向けダッシュボード")

# --- 価格と24h変動 ---
def get_xlm_data():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids":"stellar", "vs_currencies":"jpy", "include_24hr_change":"true"}
    data = requests.get(url, params=params).json()
    return data["stellar"]["jpy"], data["stellar"]["jpy_24h_change"]

# --- 過去データ（RSI用） ---
def get_xlm_prices():
    url = "https://api.coingecko.com/api/v3/coins/stellar/market_chart"
    params = {"vs_currency":"jpy","days":"1","interval":"hourly"}
    data = requests.get(url, params=params).json()
    return [p[1] for p in data["prices"]]

# --- RSI計算 ---
def get_rsi(prices, period=14):
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

# --- データ取得 ---
price, change_24h = get_xlm_data()
prices = get_xlm_prices()
rsi = get_rsi(prices)

# --- トレンド判定 ---
if rsi > 70:
    trend = "売りトレンド（RSI高め）"
elif rsi < 30:
    trend = "買いトレンド（RSI低め）"
else:
    trend = "レンジ相場"

# --- 表示 ---
st.metric("XLM価格 (JPY)", f"{price:.2f}円", f"{change_24h:.2f}%")
st.metric("RSI", f"{rsi:.2f}")
st.write("トレンド:", trend)
st.write("※投資判断の参考用です。")
