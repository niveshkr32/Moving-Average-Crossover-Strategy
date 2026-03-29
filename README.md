# Moving-Average-Crossover-Strategy

import yfinance as yf
import pandas as pd
import requests
import os

stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

results = []

for stock in stocks:
    df = yf.download(stock, period="3mo", interval="1d")

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    latest = df.iloc[-1]

    if latest["EMA20"] > latest["EMA50"]:
        signal = "BUY"
    else:
        signal = "SELL"

    results.append(f"{stock}: {signal}")

# Save report
os.makedirs("output", exist_ok=True)
pd.DataFrame(results).to_csv("output/report.csv", index=False)

# Telegram Alert
TOKEN = os.getenv("8652752416:AAHRHdMM5FCaSfKXKtFCnmmcIwLzYwpalpc")
CHAT_ID = os.getenv("1517706156")

message = "\n".join(results)

if TOKEN:
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message}
    )

print(message)
