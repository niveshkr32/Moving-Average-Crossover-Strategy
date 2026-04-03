# Moving-Average-Crossover-Strategy + Prometheus

import yfinance as yf
import pandas as pd
import requests
import os
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRg3O5UZfwxhp9YIzL--xrT09H8E61yF45L4MhR58HWdvWsJu2LFnymtl2NJYp3Fr1Dkyc7uF30BMZg/pub?gid=0&single=true&output=csv"

df = pd.read_csv(sheet_url, header=None)
df = df.iloc[3:, [0, 1, 2, 3, 4, 24, 25, 26]]
df.columns = ["Stock Name", "Stock Symbol", "Buy Date", "Buy Qty", "Buy Price", "Sell Date", "Sell Qty", "Sell Price"]

unsold_stocks_df = df[df["Sell Price"].isna() | (df["Sell Price"] == '')]

results = []

# 👉 Prometheus counters
count = 0
smart_count = 0

for stock in unsold_stocks_df["Stock Symbol"]:
    count += 1

    stock = str(stock).strip()
    if not stock.endswith(".NS"):
        stock += ".NS"

    data = yf.download(stock, period="3mo", interval="1d")

    if data.empty:
        results.append(f"{stock} -> No Data")
        continue

    data.reset_index(inplace=True)
    data.columns = data.columns.get_level_values(0)

    # RSI
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    # Indicators
    data["EMA20"] = data["Close"].ewm(span=20).mean()
    data["Vol_Avg"] = data["Volume"].rolling(20).mean()

    data["Range"] = data["High"] - data["Low"]
    data["Tight_Range"] = data["Range"].rolling(5).mean() < data["Range"].rolling(20).mean()

    data["Vol_Buildup"] = data["Volume"] > data["Vol_Avg"]

    data["Resistance"] = data["High"].rolling(10).max().shift(1)
    data["Breakout"] = data["Close"] > data["Resistance"]

    data["SMART_SIGNAL"] = (
        data["Tight_Range"] &
        data["Vol_Buildup"] &
        data["Breakout"]
    )

    latest = data.iloc[-1]

    tight = latest["Tight_Range"]
    vol = latest["Vol_Buildup"]
    brk = latest["Breakout"]
    smart = latest["SMART_SIGNAL"]

    if smart:
        smart_count += 1

    results.append(f"{stock} -> TR:{tight} | VOL:{vol} | BO:{brk} | SM:{smart}")

# Save report
os.makedirs("output", exist_ok=True)
pd.DataFrame(results).to_csv("output/report.csv", index=False)

# Telegram
TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

message = "\n".join(results) if results else "No signals today"

if TOKEN and CHAT_ID:
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message}
    )

print("MESSAGE:", message)

# 👉 Prometheus Pushgateway
registry = CollectorRegistry()

total_stocks = Gauge('total_stocks', 'Total stocks processed', registry=registry)
smart_signals = Gauge('smart_signals', 'Smart signals count', registry=registry)

total_stocks.set(count)
smart_signals.set(smart_count)

push_to_gateway('pushgateway:9091', job='stock-job', registry=registry)

print("Metrics pushed 🚀")
