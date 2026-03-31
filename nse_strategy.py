# Moving-Average-Crossover-Strategy

import yfinance as yf
import pandas as pd
# import ta
import requests
import os

stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

results = []

for stock in stocks:
    df = yf.download(stock, period="3mo", interval="1d")

    # EMA
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    # RSI
    #df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

    delta = df["Close"].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # Volume average
    df["VOL_AVG"] = df["Volume"].rolling(20).mean()
    
    latest = df.iloc[-1]    # Latest row

    ema20 = float(latest["EMA20"])
    ema50 = float(latest["EMA50"])
    rsi = float(latest["RSI"])
    
    vol = float(latest["Volume"])
    vol_avg = float(df["Volume"].rolling(20).mean().iloc[-1])
    
    #ema20 = float(latest["EMA20"])
    #ema50 = float(latest["EMA50"])
    #rsi = float(latest["RSI"])
    #vol = latest["Volume"]
    #vol_avg = latest["VOL_AVG"]
    
    signal = "NO SIGNAL"
    
    if ema20 > ema50 and rsi > 55 and vol > vol_avg:
        signal = "BUY 🚀"
    
    elif ema20 < ema50 and rsi < 45 and vol > vol_avg:
        signal = "SELL 🔻"
    
    else:
        signal = "NO SIGNAL"
        
    results.append(f"{stock}: {signal}")



# Save report
os.makedirs("output", exist_ok=True)
pd.DataFrame(results).to_csv("output/report.csv", index=False)



# Telegram Alert
## TOKEN = os.getenv("8652752416:AAHRHdMM5FCaSfKXKtFCnmmcIwLzYwpalpc")
## CHAT_ID = os.getenv("1517706156")

TOKEN = "8652752416:AAHRHdMM5FCaSfKXKtFCnmmcIwLzYwpalpc"
CHAT_ID = "1517706156"

#message = "\n".join(results)

#if TOKEN:
#    requests.post(
#        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
#        data={"chat_id": CHAT_ID, "text": message}
#    )

#print(message)



# Prepare message
if not results:
    message = "No signals today"
else:
    message = "\n".join(results)

print("MESSAGE:", message)

# Send to Telegram
if TOKEN and CHAT_ID:
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message}
    )
    
    print("TELEGRAM RESPONSE:", response.text)
else:
    print("TOKEN or CHAT_ID missing")
