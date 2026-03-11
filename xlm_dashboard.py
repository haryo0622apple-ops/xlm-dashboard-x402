import requests
import streamlit as st

st.title("XLM x402 投資家向けダッシュボード")

# --- 安全に価格と24h変動を取得 ---
def get_xlm_data():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "stellar",
        "vs_currencies": "jpy",
        "include_24hr_change": "true"
    }
    try:
        data = requests.get(url, params=params, timeout=10).json()
        # もしstellarキーがなければ0を返す
        if "stellar" in data:
            price = data["stellar"].get("jpy", 0)
            change_24h = data["stellar"].get("jpy_24h_change", 0)
            return price, change_24h
        else:
            return 0, 0
    except Exception as e:
        # APIが使えない場合も落ちない
        print("API取得エラー:", e)
        return 0, 0

# --- 過去データ取得（RSI用） ---
def get_xlm_prices():
    try:
        url = "https://api.coingecko.com/api/v3/coins/stellar/market_chart"
        params = {"vs_currency":"jpy","days":"1","interval":"hourly"}
        data = requests.get(url, params=params, timeout=10).json()
        return [p[1] for p in data.get("prices", [])]
    except Exception as e:
        print("過去データ取得エラー:", e)
        return []

# --- RSI計算 ---
def get_rsi(prices, period=14):
    if len(prices) < period:
        return 50  # データが足りない場合は中立値
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
