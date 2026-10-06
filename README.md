# Financial Market Analyzer

> Full MLOps pipeline predicting stock market direction (UP/DOWN) using XGBoost, MLflow, DVC, and Evidently — with JWT auth, PostgreSQL, FastAPI backend, and React frontend.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange)
![MLflow](https://img.shields.io/badge/MLflow-2.13-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | FastAPI, PostgreSQL, SQLAlchemy async, Alembic |
| ML | XGBoost, scikit-learn (TimeSeriesSplit), yfinance, FRED API |
| MLOps | MLflow (experiment tracking), DVC (pipeline), Evidently (drift detection) |
| Auth | JWT access token (in-memory) + refresh token (httpOnly cookie) |
| Frontend | React, Vite, Axios |
| Infra | Docker Compose |

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.11+ (local — required for data download only)
- Free FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/financial-market-analyzer.git
cd financial-market-analyzer
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Fill in your FRED API key in `.env`:

```env
FRED_API_KEY=your_key_here
```

### 3. Download market data (locally — not from Docker)

> ⚠️ Docker containers have no access to Yahoo Finance. This step must be run locally.
> ⚠️ Use `yf.download()` without `auto_adjust` — yfinance 1.7.0+ returns an empty DataFrame silently when `auto_adjust=True`.

```bash
pip install yfinance
python -c "
import yfinance as yf

tickers = ['SPY', 'AAPL', 'MSFT', 'GOOGL', 'NVDA']
for ticker in tickers:
    df = yf.download(ticker, period='5y')
    df.columns = [c[0].lower().replace(' ', '_') for c in df.columns]
    df.to_csv(f'backend/data/raw/{ticker}_ohlcv.csv')
    print(f'{ticker}: {len(df)} rows downloaded')
"
```

### 4. Start the containers

```bash
docker compose up -d
```

### 5. Run the ML pipeline (features → train → drift)

```bash
docker compose exec backend sh -c "cd /app && dvc init --no-scm && dvc repro"
```

The pipeline runs 3 stages:

1. **features** — computes technical indicators (RSI, MACD, volatility, SMA ratio...)
2. **train** — trains XGBoost with TimeSeriesSplit (5 folds), logs to MLflow
3. **drift** — detects data drift with Evidently, generates HTML report

## Services

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API docs | http://localhost:8000/docs |
| MLflow UI | http://localhost:5000 |

## Usage

1. Register at http://localhost:5173/register
2. Log in
3. On the dashboard, select a ticker from the dropdown (SPY, AAPL, MSFT, GOOGL, NVDA)
4. The model returns direction (UP/DOWN) with a confidence score
5. The drift card shows data stability (Evidently report)

## DVC Pipeline

The pipeline runs 15 stages — one set per ticker (features → train → drift):

```
data/raw/{TICKER}_ohlcv.csv ──┐
data/raw/macro.csv ────────────┼──► features-{TICKER} ──► train-{TICKER} ──► drift-{TICKER}
params.yaml ───────────────────┘
```

To change hyperparameters, edit `backend/params.yaml` and re-run:

```bash
docker compose exec backend sh -c "cd /app && dvc repro"
```

DVC only re-runs stages affected by the change.

## CI/CD

| Workflow | Trigger | Action |
|----------|---------|--------|
| `ci.yml` | Every push / PR | Lint + tests |
| `retrain.yml` | Every Monday 2am UTC (or manual) | Full DVC pipeline rerun |

GitHub secrets to configure (Settings → Secrets):

```
FRED_API_KEY
MLFLOW_TRACKING_URI
```

## Project Structure

```
financial-market-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routes (auth, predict, monitoring)
│   │   ├── core/           # Security, config
│   │   ├── models/         # SQLAlchemy models
│   │   └── schemas/        # Pydantic schemas
│   ├── pipeline/
│   │   ├── features.py     # Technical indicators computation
│   │   └── train.py        # XGBoost training with MLflow logging
│   ├── monitoring/
│   │   └── drift.py        # Evidently drift detection
│   ├── data/
│   │   ├── raw/            # Raw data (not committed to Git)
│   │   └── processed/      # Computed features
│   ├── models/             # Saved XGBoost models (.json)
│   ├── dvc.yaml            # DVC pipeline definition
│   └── params.yaml         # Hyperparameters
├── frontend/
│   └── src/
│       ├── pages/          # Dashboard, Login, Register
│       └── api/            # Axios with automatic token refresh
├── .github/
│   └── workflows/          # GitHub Actions CI/CD
└── docker-compose.yml
```

## Architecture

```
Browser
  │
  ├── /auth/*      ──► FastAPI (JWT auth, httpOnly refresh cookie)
  ├── /predict/*   ──► FastAPI ──► XGBoost model (.json)
  └── /monitoring/*──► FastAPI ──► Evidently drift report
                           │
                      PostgreSQL (users)
                      MLflow (experiment tracking)
```

## Author

**Adnane EL HISSEN** — ML Engineer | Backend & Embedded Systems  
Casablanca, Morocco  
[GitHub](https://github.com/adnane-ml)

