import os
import pandas as pd
import yfinance as yf
import fredapi

DATA_RAW = os.path.join(os.path.dirname(__file__), "../data/raw")
os.makedirs(DATA_RAW, exist_ok=True)

FRED_API_KEY = os.getenv("FRED_API_KEY")

def ingest_ohlcv(ticker="SPY", period="5y"):
    path = os.path.join(DATA_RAW, f"{ticker}_ohlcv.csv")
    if os.path.exists(path):
        df_check = pd.read_csv(path)
        if len(df_check) > 0:
            print(f"[ingest] {ticker} OHLCV already exists — skipping")
            return
    df = yf.download(ticker, period=period, auto_adjust=True)
    df.columns = df.columns.get_level_values(0).str.lower()
    df.to_csv(path)
    print(f"[ingest] {ticker} OHLCV saved — {len(df)} rows")

def ingest_macro():
    fred = fredapi.Fred(api_key=FRED_API_KEY)
    series = {
        "fed_rate":     "FEDFUNDS",
        "inflation":    "CPIAUCSL",
        "vix":          "VIXCLS",
        "unemployment": "UNRATE",
    }
    frames = {}
    for name, sid in series.items():
        s = fred.get_series(sid)
        s.name = name
        frames[name] = s

    macro = pd.DataFrame(frames)
    macro.index.name = "date"
    macro = macro.resample("D").interpolate("linear")
    macro.to_csv(os.path.join(DATA_RAW, "macro.csv"))
    print(f"[ingest] macro saved - {len(macro)} rows")

if __name__ == "__main__":
    ingest_ohlcv("SPY")
    ingest_macro()