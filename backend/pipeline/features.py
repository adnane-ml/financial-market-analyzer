import os
import sys

import numpy as np
import pandas as pd

DATA_RAW = os.path.join(os.path.dirname(__file__), "../data/raw")
DATA_PROCESSED = os.path.join(os.path.dirname(__file__), "../data/processed")


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def compute_macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def build_features(ticker: str = "SPY") -> pd.DataFrame:
    print(f"[features] Building features for {ticker}...")

    # --- Charger les données brutes ---
    ohlcv_path = os.path.join(DATA_RAW, f"{ticker}_ohlcv.csv")
    macro_path = os.path.join(DATA_RAW, "macro.csv")

    df = pd.read_csv(ohlcv_path, index_col=0, parse_dates=True)
    macro = pd.read_csv(macro_path, index_col=0, parse_dates=True)

    # Aplatir les colonnes multi-niveau si yfinance les a générées
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0].lower() for c in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]

    # --- Features de prix ---
    df["return_1d"] = df["close"].pct_change(1)
    df["return_5d"] = df["close"].pct_change(5)
    df["return_20d"] = df["close"].pct_change(20)

    df["volatility_5d"] = df["return_1d"].rolling(5).std()
    df["volatility_20d"] = df["return_1d"].rolling(20).std()

    # --- Moyennes mobiles ---
    df["sma_20"] = df["close"].rolling(20).mean()
    df["sma_50"] = df["close"].rolling(50).mean()
    df["sma_ratio"] = df["sma_20"] / df["sma_50"]
    
    # --- RSI ---
    df["rsi_14"] = compute_rsi(df["close"], 14)

    # --- MACD ---
    df["macd"], df["macd_signal"], df["macd_hist"] = compute_macd(df["close"])

    # --- Volume ---
    df["volume_ratio"] = df["volume"] / df["volume"].rolling(20).mean()

    # --- Merge macro (forward-fill sur les jours de marché) ---
    df = df.join(macro.reindex(df.index, method="ffill"), how="left")

    # --- Target : direction du lendemain ---
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    # --- Supprimer les lignes avec NaN (warm-up des indicateurs) ---
    df.dropna(inplace=True)

    # --- Sauvegarder ---
    os.makedirs(DATA_PROCESSED, exist_ok=True)
    out_path = os.path.join(DATA_PROCESSED, f"{ticker}_features.csv")
    df.to_csv(out_path)
    print(f"[features] {len(df)} lignes -> {out_path}")
    print(f"[features] Colonnes : {list(df.columns)}")
    return df

if __name__ == "__main__":

    ticker = sys.argv[1] if len(sys.argv) > 1 else "SPY"
    build_features(ticker)