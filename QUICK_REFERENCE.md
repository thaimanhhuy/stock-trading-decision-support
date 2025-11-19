# Stock Trading System - Quick Reference Guide

## Quick Command Reference

### 1. Download Historical Data
```bash
# Download US stock data
python scripts/download_historical_data.py --symbols AAPL,MSFT --period 2y

# Download Vietnamese stock data
python scripts/download_historical_data.py --symbols VCB.VN,FPT.VN,CTG.VN --period 2y

# Download specific date range
python scripts/download_historical_data.py --symbols AAPL --start 2023-01-01 --end 2024-12-31
```

### 2. Train Models
```bash
# Train all models (LSTM + GRU)
python scripts/train_models.py --symbol AAPL --models all

# Train specific model
python scripts/train_models.py --symbol AAPL --models lstm
python scripts/train_models.py --symbol VCB.VN --models gru

# Train multiple models in one command
python scripts/train_models.py --symbol AAPL --models lstm,gru
```

### 3. Run Backtests
```bash
python scripts/run_backtest.py --symbol AAPL --start 2023-01-01 --end 2024-01-01
```

### 4. Start API Server
```bash
python -m src.api.main
# API runs on http://localhost:8000
```

### 5. Run Dashboard
```bash
streamlit run src/dashboard/app.py
```

---

## File Locations Map

### Models (Trained & Saved)
- **Location**: `models/saved_models/{symbol}.keras`
- **Format**: TensorFlow SavedModel
- **What's saved**: 
  - LSTM model: `models/saved_models/AAPL.keras` (contains LSTM when trained)
  - GRU model: Same file (replaces when trained)

### Scalers (Data Normalization)
- **Location**: `models/scalers/{symbol}_scaler.pkl`
- **Format**: Joblib pickle
- **Used for**: Normalizing new data to [0, 1] range before predictions

### Raw Data
- **Location**: `data/raw/{symbol}.csv`
- **Columns**: date, open, high, low, close, volume
- **Source**: Yahoo Finance via yfinance library

### Processed Data
- **Location**: `data/processed/{symbol}_processed.csv`
- **Contains**: Raw data + technical indicators

### Features
- **Location**: `data/features/{symbol}_features.csv`
- **Contains**: Normalized features for training

---

## Configuration Files Map

### Main Config
- **File**: `config/config.yaml`
- **Controls**: 
  - Data source and validation
  - Symbol lists
  - Technical indicator parameters
  - Model selection (LSTM, GRU)
  - Ensemble settings
  - Monitoring and drift detection

### Model Architecture Config
- **File**: `config/model_config.yaml`
- **Controls**:
  - LSTM layer sizes, dropout rates
  - GRU layer sizes, dropout rates
  - Training parameters (epochs, batch size)
  - Callbacks (early stopping, learning rate reduction)
  - Evaluation metrics

### Trading Config
- **File**: `config/trading_config.yaml`
- **Controls**:
  - Risk management parameters
  - Position sizing
  - Stop-loss and take-profit levels
  - Order execution rules

### Vietnamese Stocks
- **File**: `config/vietnam_stocks.yaml`
- **Contains**: List of Vietnamese stocks by sector

---

## Model Training Architecture

### LSTM Model
```
Input (60 days, n_features)
  ↓
LSTM Layer (128 units) + Dropout (0.2)
  ↓
LSTM Layer (64 units) + Dropout (0.2)
  ↓
LSTM Layer (32 units) + Dropout (0.2)
  ↓
Dense Layer (1 unit, linear) → Output (next day price)
```

### GRU Model
```
Input (60 days, n_features)
  ↓
GRU Layer (128 units) + Dropout (0.2)
  ↓
GRU Layer (64 units) + Dropout (0.2)
  ↓
GRU Layer (32 units) + Dropout (0.2)
  ↓
Dense Layer (1 unit, linear) → Output (next day price)
```

### Ensemble Prediction
```
LSTM Prediction (weight 0.5)
  + GRU Prediction (weight 0.5)
  = Ensemble Prediction
```

---

## API Endpoints

### Health Check
```
GET /health
Response: {"status": "healthy", "version": "0.1.0"}
```

### Get Prediction
```
GET /api/v1/predictions/{symbol}
Example: GET /api/v1/predictions/AAPL

Response:
{
  "symbol": "AAPL",
  "current_price": 150.0,
  "predicted_price": 155.0,
  "confidence": 0.75,
  "timestamp": "2024-01-01T00:00:00"
}
```

### Get Trading Signal
```
GET /api/v1/signals/{symbol}
Example: GET /api/v1/signals/AAPL

Response:
{
  "symbol": "AAPL",
  "signal": "buy",
  "strength": 0.8,
  "target_price": 155.0,
  "stop_loss": 145.0,
  "take_profit": 160.0
}
```

### System Health
```
GET /api/v1/monitoring/health
Response:
{
  "status": "healthy",
  "models_loaded": true,
  "data_updated": true
}
```

---

## Key Classes & Methods

### Data Pipeline
| Class | Method | Purpose |
|-------|--------|---------|
| YahooDataFetcher | fetch_data() | Download OHLCV data |
| DataValidator | validate() | Check data quality |
| DataStorage | save_raw() / load_raw() | Store/retrieve raw data |
| DataProcessor | process() | Add indicators & normalize |

### Training
| Class | Method | Purpose |
|-------|--------|---------|
| ModelTrainer | train_all() | Train LSTM + GRU |
| LSTMModel | train() | Train LSTM model |
| GRUModel | train() | Train GRU model |
| BaseModel | evaluate() | Calculate metrics |

### Predictions
| Class | Method | Purpose |
|-------|--------|---------|
| ModelEvaluator | predict_ensemble() | Weighted average |
| SignalGenerator | generate_signal() | Buy/Sell/Hold signal |

---

## Technical Indicators Used

**Implemented**:
- SMA (5, 10, 20, 50, 200 periods)
- EMA (12, 26, 50 periods)
- RSI (14 period)
- MACD (12/26/9)
- Bollinger Bands (20 period, 2 std dev)
- ATR (14 period)
- Returns & Log Returns

**Formula for Trading Signal**:
```
predicted_return = (predicted_price - current_price) / current_price

if predicted_return >= 3%: BUY
elif predicted_return <= -3%: SELL
else: HOLD
```

---

## Directory Structure Summary

```
├── config/                    # YAML configurations
├── data/
│   ├── raw/                  # Yahoo Finance OHLCV data
│   ├── processed/            # Data with indicators
│   └── features/             # Normalized features
├── models/
│   ├── saved_models/         # Trained .keras files
│   ├── scalers/              # MinMaxScaler objects
│   └── mlflow/               # Experiment tracking
├── scripts/                   # Entry points
├── src/
│   ├── api/                  # FastAPI server
│   ├── models/               # LSTM, GRU classes
│   ├── data_ingestion/       # Yahoo fetcher, storage
│   ├── preprocessing/        # Indicators, sequences
│   ├── trading_engine/       # Signal generation
│   ├── monitoring/           # Drift detection
│   └── utils/                # Logger, constants
└── tests/                     # Unit & integration tests
```

---

## Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables (Optional)
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Tests
```bash
pytest tests/
```

### 4. Check Code Quality
```bash
black src/
flake8 src/
mypy src/
```

---

## Common Workflows

### Workflow 1: Train on New Stock
```bash
# 1. Download data
python scripts/download_historical_data.py --symbols NVDA --period 2y

# 2. Train models
python scripts/train_models.py --symbol NVDA --models all

# 3. Run backtest
python scripts/run_backtest.py --symbol NVDA --start 2023-01-01 --end 2024-01-01
```

### Workflow 2: Get Real-time Predictions
```bash
# 1. Start API
python -m src.api.main &

# 2. Query predictions
curl http://localhost:8000/api/v1/predictions/AAPL
curl http://localhost:8000/api/v1/signals/AAPL
```

### Workflow 3: Vietnamese Stock Analysis
```bash
# 1. Download Vietnamese banks
python scripts/download_historical_data.py --symbols VCB.VN,CTG.VN,BID.VN --period 5y

# 2. Train models
python scripts/train_models.py --symbol VCB.VN --models all

# 3. Get predictions
curl http://localhost:8000/api/v1/predictions/VCB.VN
```

---

## Troubleshooting

### Models Not Saving
- Check: `models/saved_models/` directory exists
- Check: Write permissions in models directory
- Check: TensorFlow installed correctly

### Data Fetch Failures
- Check: Internet connection
- Check: Stock symbol is valid (AAPL, VCB.VN, etc.)
- Check: Yahoo Finance is not blocked

### Training Takes Too Long
- Reduce epochs in config/model_config.yaml
- Reduce data size (use smaller period)
- Enable GPU: Set use_gpu=true in config.yaml

### API Not Responding
- Check: Uvicorn is running on port 8000
- Check: Firewall isn't blocking port 8000
- Check: Try: curl http://localhost:8000/health

---

## Key Parameters to Tune

### For Better Predictions
- Increase sequence_length (60 → 90 days)
- Add more features (additional indicators)
- Increase model capacity (units in layers)
- Use more training data (longer period)

### For Faster Training
- Reduce epochs (100 → 50)
- Increase batch_size (32 → 64)
- Reduce sequence_length (60 → 30)
- Reduce number of indicators

### For Better Risk Management
- Lower stop_loss_percent (5% → 3%)
- Raise take_profit_percent (10% → 15%)
- Reduce max_position_size (10% → 5%)

