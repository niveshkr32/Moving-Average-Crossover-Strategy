# Moving-Average-Crossover-Strategy

import yfinance as yf
import pandas as pd
# import ta
import requests
import os

# stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

stocks = [
"RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
"KOTAKBANK.NS","LT.NS","SBIN.NS","AXISBANK.NS","ITC.NS",
"HINDUNILVR.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS",
"HCLTECH.NS","WIPRO.NS","ULTRACEMCO.NS","TITAN.NS","SUNPHARMA.NS",
"NTPC.NS","ONGC.NS","POWERGRID.NS","TMCV.NS","TATASTEEL.NS",
"JSWSTEEL.NS","COALINDIA.NS","INDUSINDBK.NS","BAJAJFINSV.NS",
"NESTLEIND.NS","DRREDDY.NS","CIPLA.NS","ADANIENT.NS",
"ADANIPORTS.NS","GRASIM.NS","HEROMOTOCO.NS","BRITANNIA.NS",
"EICHERMOT.NS","DIVISLAB.NS","APOLLOHOSP.NS","TECHM.NS",
"SBILIFE.NS","HDFCLIFE.NS","BAJAJ-AUTO.NS","TATACONSUM.NS",
"UPL.NS","SHREECEM.NS","BPCL.NS","IOC.NS","HINDALCO.NS"
]

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

    #ema20 = float(latest["EMA20"])
    #ema50 = float(latest["EMA50"])
    #rsi = float(latest["RSI"])
    #vol = latest["Volume"]
    #vol_avg = latest["VOL_AVG"]
    
    ema20 = float(latest["EMA20"].iloc[0])
    ema50 = float(latest["EMA50"].iloc[0])
    rsi = float(latest["RSI"].iloc[0])
    vol = float(df["Volume"].iloc[-1])   # 👈 important fix
    vol_avg = float(df["Volume"].rolling(20).mean().iloc[-1])
    
    signal = "NO SIGNAL"
    
    if ema20 > ema50 and rsi > 55 and vol > vol_avg:
        signal = "BUY"
    
    elif ema20 < ema50 and rsi < 45 and vol > vol_avg:
        signal = "SELL"
    
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
