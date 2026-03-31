
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

    df.columns = df.columns.get_level_values(0)    
    
    # EMA
    # df["EMA20"] = df["Close"].ewm(span=20).mean()
    # df["EMA50"] = df["Close"].ewm(span=50).mean()

    # RSI
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
        

    # Indicators
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["Vol_Avg"] = df["Volume"].rolling(20).mean()
    
    # 1️⃣ Tight Range Detection (last 5 days)
    df["Range"] = df["High"] - df["Low"]
    df["Tight_Range"] = df["Range"].rolling(5).mean() < df["Range"].rolling(20).mean()
    
    # 2️⃣ Volume Build-up
    df["Vol_Buildup"] = df["Volume"] > df["Vol_Avg"]
    
    # 3️⃣ Breakout Condition
    df["Resistance"] = df["High"].rolling(10).max().shift(1)
    df["Breakout"] = df["Close"] > df["Resistance"]
    
    # 4️⃣ Smart Money Signal
    df["SMART_SIGNAL"] = (
        df["Tight_Range"] &
        df["Vol_Buildup"] &
        df["Breakout"]
    )


#    latest = df.iloc[-1]    # Latest row
    
#    ema20 = float(latest["EMA20"].iloc[0])
#    ema50 = float(latest["EMA50"].iloc[0])
#    rsi = float(latest["RSI"].iloc[0])
#    vol = float(df["Volume"].iloc[-1])   # 👈 important fix
#    vol_avg = float(df["Volume"].rolling(20).mean().iloc[-1])
    
#    signal = "NO SIGNAL"
    
#    if ema20 > ema50 and rsi > 55 and vol > vol_avg:
#        signal = "BUY"
    
#    elif ema20 < ema50 and rsi < 45 and vol > vol_avg:
#        signal = "SELL"
    
#    else:
#        signal = "NO SIGNAL"



    # Show signals
    signal = df[df["SMART_SIGNAL"] == True]
    
    print(signal[["Close", "Volume"]])


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

