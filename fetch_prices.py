import yfinance as yf
import pandas as pd
from pathlib import Path

# ETF 與個股
tickers = {
    "0050": "0050.TW",
    "00646": "00646.TW",
    "00662": "00662.TW",
    "00830": "00830.TW",
    "NVDA": "NVDA",
    "AMD": "AMD",
    "AVGO": "AVGO",
    "GOOGL": "GOOGL",
    "MSFT": "MSFT",
    "AMZN": "AMZN",
    "META": "META",
    "ORCL": "ORCL",
    "CRWV": "CRWV",
    "NBIS": "NBIS",
    "MRVL": "MRVL",
    "QCOM": "QCOM",
    "TSM": "TSM",
    "LITE": "LITE",
    "PLTR": "PLTR"
}

records = []

for name, symbol in tickers.items():
    print(f"正在下載 {name}")

    try:
        stock = yf.Ticker(symbol)

        history = stock.history(
            start="2015-01-01",
            auto_adjust=True
        )

        if history.empty:
            print(f"{name} 沒有取得資料")
            continue

        # 網站使用每月最後一個交易日價格
        monthly = history["Close"].resample("ME").last().dropna()

        currency = "TWD" if symbol.endswith(".TW") else "USD"

        for date, price in monthly.items():
            records.append({
                "ticker": name,
                "date": date.strftime("%Y-%m-%d"),
                "close": round(float(price), 6),
                "currency": currency
            })

    except Exception as e:
        print(f"{name} 下載失敗：{e}")

if not records:
    raise RuntimeError("沒有取得任何歷史價格")

df = pd.DataFrame(records)

Path("data").mkdir(exist_ok=True)

df.to_csv(
    "data/prices.csv",
    index=False,
    encoding="utf-8-sig"
)

print("歷史資料已儲存至 data/prices.csv")
