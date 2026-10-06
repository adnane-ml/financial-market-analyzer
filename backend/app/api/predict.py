from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.schemas.predict import PredictionResponse
import xgboost as xgb
import pandas as pd
import os

router = APIRouter()

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../../models")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "../../data/processed")

FEATURES = [
    "return_1d", "return_5d", "return_20d",
    "volatility_5d", "volatility_20d", "sma_ratio",
    "rsi_14", "macd", "macd_signal", "macd_hist",
    "volume_ratio", "fed_rate", "inflation", "vix", "unemployment"
]

def load_model(ticker: str) -> xgb.XGBClassifier:
    path = os.path.join(MODELS_DIR, f"{ticker}_xgb.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Modèle introuvable pour {ticker}")
    model = xgb.XGBClassifier()
    model.load_model(path)
    return model

def get_latest_features(ticker: str) -> pd.DataFrame:
    path = os.path.join(PROCESSED_DIR, f"{ticker}_features.csv")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Features introuvables pour {ticker}")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df[FEATURES].iloc[[-1]]  # dernière ligne seulement

@router.get("/{ticker}", response_model=PredictionResponse)
async def predict(ticker: str, user=Depends(get_current_user)):
    ticker = ticker.upper()
    model = load_model(ticker)
    X = get_latest_features(ticker)
    proba = model.predict_proba(X)[0]
    direction = "UP" if proba[1] >= 0.5 else "DOWN"
    confidence = float(max(proba))
    return PredictionResponse(ticker=ticker, direction=direction, confidence=confidence)