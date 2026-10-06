from pydantic import BaseModel

class PredictionResponse(BaseModel):
    ticker: str
    direction: str   # "UP" ou "DOWN"
    confidence: float