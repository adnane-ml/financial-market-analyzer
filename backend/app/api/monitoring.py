from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from monitoring.drift import run_drift_report

router = APIRouter()

@router.get("/{ticker}")
async def drift_report(ticker: str, user=Depends(get_current_user)):
    ticker = ticker.upper()
    summary = run_drift_report(ticker)
    return summary