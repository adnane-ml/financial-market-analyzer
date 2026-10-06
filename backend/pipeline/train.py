import os
import sys
import json
import yaml
import numpy as np
import pandas as pd
import mlflow
import mlflow.xgboost
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

BASE_DIR      = os.path.dirname(__file__)
PARAMS_FILE   = os.path.join(BASE_DIR, "../params.yaml")
PROCESSED_DIR = os.path.join(BASE_DIR, "../data/processed")
MODELS_DIR    = os.path.join(BASE_DIR, "../models")
METRICS_DIR   = os.path.join(BASE_DIR, "../data/metrics")

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")

FEATURES = [
    "return_1d", "return_5d", "return_20d",
    "volatility_5d", "volatility_20d",
    "sma_ratio", "rsi_14",
    "macd", "macd_signal", "macd_hist",
    "volume_ratio",
    "fed_rate", "inflation", "vix", "unemployment",
]


def load_params() -> dict:
    with open(PARAMS_FILE, "r") as f:
        return yaml.safe_load(f)


def load_data(ticker: str) -> tuple[pd.DataFrame, pd.Series]:
    path = os.path.join(PROCESSED_DIR, f"{ticker}_features.csv")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    available = [f for f in FEATURES if f in df.columns]
    X = df[available]
    y = df["target"]
    return X, y


def train(ticker: str = None):
    params    = load_params()
    ticker    = ticker or params["ticker"]
    n_splits  = params["train"]["n_splits"]

    xgb_params = {
        "n_estimators":      params["train"]["n_estimators"],
        "max_depth":         params["train"]["max_depth"],
        "learning_rate":     params["train"]["learning_rate"],
        "subsample":         params["train"]["subsample"],
        "colsample_bytree":  params["train"]["colsample_bytree"],
        "random_state":      params["train"]["random_state"],
        "eval_metric":       "logloss",
        "use_label_encoder": False,
    }

    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(f"fma-{ticker}")

    X, y = load_data(ticker)
    print(f"[train] {ticker} — {len(X)} échantillons, {X.shape[1]} features")

    tscv         = TimeSeriesSplit(n_splits=n_splits)
    metrics_list = []

    with mlflow.start_run(run_name=f"{ticker}-xgb"):
        mlflow.log_params({**xgb_params, "ticker": ticker, "n_splits": n_splits,
                           "n_features": X.shape[1], "n_samples": len(X)})

        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

            model = xgb.XGBClassifier(**xgb_params)
            model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)

            preds = model.predict(X_val)
            proba = model.predict_proba(X_val)[:, 1]

            fm = {
                "accuracy": accuracy_score(y_val, preds),
                "f1":       f1_score(y_val, preds),
                "auc":      roc_auc_score(y_val, proba),
            }
            metrics_list.append(fm)
            print(f"  fold {fold+1}/{n_splits} - acc={fm['accuracy']:.3f}  f1={fm['f1']:.3f}  auc={fm['auc']:.3f}")

        avg = {k: float(np.mean([m[k] for m in metrics_list])) for k in ["accuracy", "f1", "auc"]}
        mlflow.log_metrics({f"cv_{k}": v for k, v in avg.items()})
        print(f"[train] CV moyen - acc={avg['accuracy']:.3f}  f1={avg['f1']:.3f}  auc={avg['auc']:.3f}")

        # Entraînement final sur tout le dataset
        final_model = xgb.XGBClassifier(**xgb_params)
        final_model.fit(X, y, verbose=False)

        mlflow.xgboost.log_model(final_model, artifact_path="model")

        os.makedirs(MODELS_DIR, exist_ok=True)
        model_path = os.path.join(MODELS_DIR, f"{ticker}_xgb.json")
        final_model.save_model(model_path)
        mlflow.log_artifact(model_path)
        print(f"[train] modèle -> {model_path}")

        # Métriques JSON pour DVC
        os.makedirs(METRICS_DIR, exist_ok=True)
        metrics_out = {"ticker": ticker, **avg, "n_splits": n_splits}
        metrics_path = os.path.join(METRICS_DIR, f"{ticker}_metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics_out, f, indent=2)

        run_id = mlflow.active_run().info.run_id
        print(f"[train] MLflow run_id : {run_id}")
        return final_model, run_id


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else None
    train(ticker)