import os

import pandas as pd
from evidently import ColumnMapping
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import DatasetDriftMetric
from evidently.report import Report

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "../data/processed")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "../data/reports")

FEATURES = [
    "return_1d", "return_5d", "return_20d",
    "volatility_5d", "volatility_20d", "sma_ratio",
    "rsi_14", "macd", "macd_signal", "macd_hist",
    "volume_ratio", "fed_rate", "inflation", "vix", "unemployment"
]

def run_drift_report(ticker: str = "SPY") -> dict:
    path = os.path.join(PROCESSED_DIR, f"{ticker}_features.csv")
    df = pd.read_csv(path, index_col=0, parse_dates=True)

    split = int(len(df) * 0.8)
    reference = df.iloc[:split][FEATURES]
    current = df.iloc[split:][FEATURES]

    column_mapping = ColumnMapping(target=None, numerical_features=FEATURES)

    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset(),
        DatasetDriftMetric(),
    ])
    report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    report.save_html(os.path.join(REPORTS_DIR, f"{ticker}_drift_report.html"))

    result = report.as_dict()
    # Cherche DatasetDriftMetric dans les résultats
    dataset_metric = next(
        m for m in result["metrics"]
        if m["metric"] == "DatasetDriftMetric"
    )
    dr = dataset_metric["result"]

    return {
        "ticker": ticker,
        "dataset_drift": dr.get("dataset_drift", False),
        "drift_share": dr.get("share_of_drifted_columns", 0),
        "n_drifted": dr.get("number_of_drifted_columns", 0),
        "n_features": dr.get("number_of_columns", len(FEATURES)),
    }

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "SPY"
    summary = run_drift_report(ticker)
    print(summary)