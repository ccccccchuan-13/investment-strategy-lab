import yfinance as yf
import pandas as pd
from pathlib import Path

# ==========================================
# Investment Strategy Lab
# 真實歷史股價自動下載程式
# ==========================================

# ETF 與個股清單
tickers = {
    # 台股 ETF
    "0050": "0050.TW",
    "00646": "00646.TW",
    "00662": "00662.TW",
    "00830": "00830.TW",

    # AI 半導體
    "NVDA": "NVDA",
    "AMD": "AMD",
    "AVGO": "AVGO",
    "MRVL": "MRVL",
    "QCOM": "QCOM",
    "TSM": "TSM",

    # 美國科技巨頭
    "GOOGL": "GOOGL",
    "MSFT": "MSFT",
    "AMZN": "AMZN",
    "META": "META",

    # AI 雲端
    "ORCL": "ORCL",
    "CRWV": "CRWV",
    "NBIS": "NBIS",

    # 其他 AI 相關企業
    "LITE": "LITE",
    "PLTR": "PLTR"
}

records = []
success_count = 0
failed_tickers = []

# ==========================================
# 下載歷史股價
# ==========================================

for name, symbol in tickers.items():

    print(f"正在下載 {name} ({symbol})")

    try:
        stock = yf.Ticker(symbol)

        history = stock.history(
            start="2015-01-01",
            auto_adjust=True
        )

        if history.empty:
            print(f"{name} 沒有取得資料")
            failed_tickers.append(name)
            continue

        # 使用每月最後一個實際交易日的收盤價格
        monthly = (
            history["Close"]
            .groupby(history.index.strftime("%Y-%m"))
            .tail(1)
            .dropna()
        )

        # 判斷交易貨幣
        currency = "TWD" if symbol.endswith(".TW") else "USD"

        # 整理資料
        for date, price in monthly.items():

            records.append({
                "ticker": name,
                "date": date.strftime("%Y-%m-%d"),
                "close": round(float(price), 6),
                "currency": currency
            })

        success_count += 1

        print(f"{name} 下載成功，共 {len(monthly)} 筆月度資料")

    except Exception as e:

        print(f"{name} 下載失敗：{e}")
        failed_tickers.append(name)


# ==========================================
# 檢查下載結果
# ==========================================

if not records:
    raise RuntimeError("沒有取得任何歷史價格，請檢查資料來源。")

# 避免部分下載失敗時覆蓋原本完整的歷史資料
if failed_tickers:
    raise RuntimeError(
        f"以下股票下載失敗：{', '.join(failed_tickers)}。"
        "已停止更新，保留原本的 CSV。"
    )


# ==========================================
# 整理並儲存 CSV
# ==========================================

df = pd.DataFrame(records)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(
    by=["ticker", "date"]
)

df = df.drop_duplicates(
    subset=["ticker", "date"],
    keep="last"
)

df["date"] = df["date"].dt.strftime("%Y-%m-%d")

# 建立資料夾
Path("data").mkdir(exist_ok=True)

# 匯出歷史資料
df.to_csv(
    "data/prices.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 顯示執行結果
# ==========================================

print("\n====================================")
print("Investment Strategy Lab")
print("歷史股價更新完成")
print("====================================")

print(f"成功下載股票數量：{success_count}")
print(f"歷史價格資料總筆數：{len(df)}")
print(f"最早日期：{df['date'].min()}")
print(f"最新日期：{df['date'].max()}")

print("\n資料已儲存至：data/prices.csv")
print("====================================")
