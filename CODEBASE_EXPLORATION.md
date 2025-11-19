# Stock Trading Decision Support System - Codebase Exploration

## 1. PROJECT OVERVIEW

**Project Name**: Stock Trading Decision Support System
**Version**: 0.1.0
**Type**: Machine Learning-based Trading System
**Languages**: Python (core), FastAPI (backend), Streamlit (dashboard)
**Framework**: TensorFlow/Keras for deep learning models

### Key Features
- Multi-model predictions (LSTM, GRU ensemble)
- Real-time trading signal generation
- Risk management and position sizing
- Backtesting engine
- Model drift detection and monitoring
- REST API for predictions
- Interactive Streamlit dashboard
- Support for US and Vietnamese stock markets

---

## 2. PROJECT STRUCTURE

```
/home/user/stock-trading-decision-support/
├── config/                          # Configuration files
│   ├── config.yaml                 # Main application config
│   ├── model_config.yaml           # Model architecture and training params
│   ├── trading_config.yaml         # Trading rules and thresholds
│   ├── logging_config.yaml         # Logging configuration
│   └── vietnam_stocks.yaml         # Vietnamese stock listings
├── data/                            # Data storage (raw, processed, features)
│   ├── raw/                        # Raw OHLCV data from Yahoo Finance
│   ├── processed/                  # Preprocessed data with features
│   └── features/                   # Feature engineering output
├── models/                          # Model storage
│   ├── saved_models/               # Trained model files (.keras format)
│   ├── scalers/                    # Data scaler objects (.pkl files)
│   └── mlflow/                     # MLflow experiment tracking
├── scripts/                         # Command-line entry points
│   ├── download_historical_data.py # Fetch data from Yahoo Finance
│   ├── train_models.py             # Training orchestrator
│   ├── run_backtest.py             # Backtesting engine
│   └── test_vietnamese_stocks.py   # Vietnam stock tests
├── src/                             # Source code
│   ├── api/                        # FastAPI REST API
│   ├── backtesting/                # Backtesting engine
│   ├── config/                     # Settings management
│   ├── data_ingestion/             # Data fetching and storage
│   ├── dashboard/                  # Streamlit dashboard
│   ├── models/                     # Neural network models
│   ├── monitoring/                 # Drift detection, audit logging
│   ├── preprocessing/              # Data processing, indicators
│   ├── trading_engine/             # Signal generation, order management
│   └── utils/                      # Logger, exceptions, constants
├── tests/                           # Test suite (unit + integration)
├── requirements.txt                 # Python dependencies
└── setup.py                         # Package configuration
```

---

## 3. HOW MODELS ARE TRAINED

### 3.1 Training Entry Point
**File**: `/home/user/stock-trading-decision-support/scripts/train_models.py`

```python
# Entry point usage:
python scripts/train_models.py --symbol AAPL --models all
python scripts/train_models.py --symbol VCB.VN --models lstm,gru
```

### 3.2 Training Pipeline Flow

1. **Data Loading** (DataStorage)
   - Load raw CSV data for symbol
   - Source: `data/raw/{symbol}.csv`

2. **Data Preprocessing** (DataProcessor)
   - Add technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR)
   - Normalize features using MinMaxScaler (0-1 range)
   - Drop NaN values created by indicators

3. **Sequence Creation** (SlidingWindowGenerator)
   - Create sequences of 60-day lookback windows
   - Target: Next day's close price
   - Shape: (n_samples, 60, n_features)

4. **Train/Val/Test Split** (SlidingWindowGenerator)
   - Train: 70% of data
   - Validation: 15% of data
   - Test: 15% of data
   - No shuffling (time series data)

5. **Model Training** (ModelTrainer)
   - Train LSTM model via `train_lstm()`
   - Train GRU model via `train_gru()`
   - Both inherit from `BaseModel` abstract class

### 3.3 Training Configuration

**File**: `/home/user/stock-trading-decision-support/config/model_config.yaml`

#### LSTM Model Architecture
```yaml
lstm:
  layers:
    - LSTM: 128 units (return_sequences: true)
    - LSTM: 64 units (return_sequences: true)
    - LSTM: 32 units (return_sequences: false)
    - Dense: 1 unit (linear activation for regression)
  dropout: 0.2
  optimizer: Adam (lr=0.001)
  loss: MSE
  batch_size: 32
  epochs: 100
  validation_split: 0.15
  callbacks:
    - Early Stopping (patience=15)
    - Reduce LR on Plateau (factor=0.5, patience=10)
    - Model Checkpoint (save best only)
```

#### GRU Model Architecture
```yaml
gru:
  layers:
    - GRU: 128 units (return_sequences: true)
    - GRU: 64 units (return_sequences: true)
    - GRU: 32 units (return_sequences: false)
    - Dense: 1 unit (linear activation for regression)
  dropout: 0.2
  optimizer: Adam (lr=0.001)
  loss: MSE
  batch_size: 32
  epochs: 100
  validation_split: 0.15
  callbacks:
    - Early Stopping (patience=15)
    - Reduce LR on Plateau (factor=0.5, patience=10)
    - Model Checkpoint (save best only)
```

#### Training Hyperparameters (from thesis)
- Sequence length: 60 days
- Features: 4 (open, high, low, close) + technical indicators
- Random seed: 42 (reproducibility)
- Batch size: 64 (from thesis), 32 (in YAML config)
- Max epochs: 50 (from thesis), 100 (in YAML config)
- Early stopping patience: 8 (from thesis), 15 (in YAML config)

### 3.4 Training Classes

**BaseModel** (`src/models/base_model.py`)
- Abstract base class for all models
- Abstract methods: `train()`, `predict()`, `save()`, `load()`
- Implemented method: `evaluate()` (calculates MAE, MSE, RMSE, MAPE)

**LSTMModel** (`src/models/lstm_model.py`)
- Extends BaseModel
- Uses TensorFlow/Keras for LSTM layers
- Methods:
  - `__init__()`: Initialize with sequence_length=60, n_features=4
  - `_build_model()`: Construct Keras Sequential model
  - `train()`: Fit model with validation data and callbacks
  - `predict()`: Generate predictions
  - `save()`: Save to .keras format
  - `load()`: Load from .keras format
- Handles missing TensorFlow gracefully

**GRUModel** (`src/models/gru_model.py`)
- Similar to LSTMModel but uses GRU layers instead of LSTM
- Same interface as LSTMModel for consistency

**ModelTrainer** (`src/models/model_trainer.py`)
- Orchestrator for model training
- Methods:
  - `train_lstm()`: Create and train LSTM model
  - `train_gru()`: Create and train GRU model
  - `train_all()`: Train both models and return dictionary

**ModelEvaluator** (`src/models/model_evaluator.py`)
- Evaluate models and create ensemble predictions
- Method: `predict_ensemble()` - Weighted average of model predictions
- Default weights: equal for all models

---

## 4. WHERE MODELS ARE STORED

### 4.1 Model Persistence Locations

| Content | Location | Format |
|---------|----------|--------|
| Trained Models | `models/saved_models/{symbol}.keras` | Keras H5/SavedModel |
| Scalers | `models/scalers/{symbol}_scaler.pkl` | Joblib pickle |
| MLflow Artifacts | `models/mlflow/` | MLflow experiment tracking |
| Raw Data | `data/raw/{symbol}.csv` | CSV |
| Processed Data | `data/processed/{symbol}_processed.csv` | CSV |
| Feature Data | `data/features/{symbol}_features.csv` | CSV |

### 4.2 Model Saving Logic

**LSTM/GRU Models** (`src/models/lstm_model.py` & `src/models/gru_model.py`)
```python
def save(self, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    self.model.save(filepath)  # TensorFlow native format
    logger.info(f"Saved LSTM model to {filepath}")
```

**Scalers** (`src/preprocessing/data_processor.py`)
```python
def save_scaler(self, symbol: str) -> str:
    filepath = os.path.join(self.settings.model_scaler_path, f"{symbol}_scaler.pkl")
    joblib.dump(self.scaler, filepath)
    return filepath
```

### 4.3 Configuration Settings

**File**: `/home/user/stock-trading-decision-support/src/config/settings.py`

```python
class Settings(BaseSettings):
    model_saved_path: str = "./models/saved_models"
    model_scaler_path: str = "./models/scalers"
    data_raw_path: str = "./data/raw"
    data_processed_path: str = "./data/processed"
    data_features_path: str = "./data/features"
```

---

## 5. HOW DATA IS FETCHED FOR TRAINING

### 5.1 Data Fetching Pipeline

**Entry Point**: `/home/user/stock-trading-decision-support/scripts/download_historical_data.py`

```bash
# Example usage:
python scripts/download_historical_data.py --symbols AAPL,MSFT --period 2y
python scripts/download_historical_data.py --symbols VCB.VN,FPT.VN --period 5y
python scripts/download_historical_data.py --symbols AAPL --start 2023-01-01 --end 2024-12-31
```

### 5.2 Data Fetching Components

#### 1. YahooDataFetcher (`src/data_ingestion/yahoo_fetcher.py`)

**Class**: `YahooDataFetcher`

**Methods**:
- `fetch_data()`: Fetch OHLCV data from Yahoo Finance
  - Parameters:
    - `symbol`: Stock symbol (e.g., "AAPL", "VCB.VN")
    - `start_date`: Optional start date (YYYY-MM-DD)
    - `end_date`: Optional end date (YYYY-MM-DD)
    - `period`: Time period (1y, 2y, 5y, max) - default 2y
  - Returns: DataFrame with columns [date, open, high, low, close, volume]
  - Error handling: Raises `DataFetchError` if data is empty or columns missing

- `fetch_multiple()`: Fetch data for multiple symbols
  - Takes list of symbols
  - Returns dictionary mapping symbols to DataFrames
  - Skips symbols that fail to fetch

**Dependencies**: `yfinance>=0.2.28`

### 5.3 Data Validation

#### DataValidator (`src/data_ingestion/data_validator.py`)

**Validation Checks**:
1. Check for missing values
2. Check for outliers (std deviation threshold)
3. Validate required columns (date, open, high, low, close, volume)
4. Data quality metrics

### 5.4 Data Storage

#### DataStorage (`src/data_ingestion/data_storage.py`)

**Methods**:
- `save_raw()`: Save raw OHLCV data
  - Location: `data/raw/{symbol}.csv`
- `load_raw()`: Load raw data from CSV
- `save_processed()`: Save preprocessed data
  - Location: `data/processed/{symbol}_processed.csv`
- `load_processed()`: Load processed data
- `save_features()`: Save engineered features
  - Location: `data/features/{symbol}_features.csv`
- `load_features()`: Load feature data

### 5.5 Data Configuration

**File**: `/home/user/stock-trading-decision-support/config/config.yaml`

```yaml
data:
  source: "yahoo_finance"
  update_frequency: "daily"
  lookback_period: 252  # ~1 trading year
  min_data_points: 500  # minimum required for training
  
  validation:
    check_missing: true
    max_missing_percent: 0.05  # 5%
    check_outliers: true
    outlier_std_threshold: 5.0
  
  storage:
    format: "csv"
    compression: null
  
  symbols:
    default: ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
```

### 5.6 Vietnamese Stock Support

The system supports Vietnamese stocks via Yahoo Finance:
- **HOSE** (Ho Chi Minh): Use `.VN` suffix (e.g., `VCB.VN`, `FPT.VN`)
- **HNX** (Hanoi): Use `.HNX` suffix

**Configured Vietnamese Stocks** (config/vietnam_stocks.yaml):
- Banking: VCB, CTG, BID, TCB, MBB, ACB, VPB
- Technology: FPT, VNM
- Real Estate: NVL, VHM, VIC
- Manufacturing: HPG, GAS, MSN, VHC
- Retail: MWG, VRE
- Securities: SSI, VND, HCM

---

## 6. PROJECT STRUCTURE - BACKEND FRAMEWORK & API ENDPOINTS

### 6.1 Backend Framework

**Framework**: FastAPI (`fastapi>=0.103.0`)
**Server**: Uvicorn (`uvicorn[standard]>=0.23.0`)
**Validation**: Pydantic v2 (`pydantic>=2.3.0`)
**Settings**: Pydantic Settings (`pydantic-settings>=2.0.0`)

### 6.2 API Entry Point

**File**: `/home/user/stock-trading-decision-support/src/api/main.py`

**Application Setup**:
```python
app = FastAPI(
    title="Stock Trading Decision Support API",
    description="API for stock price predictions and trading signals",
    version="0.1.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### 6.3 API Endpoints

#### 1. Root & Health Check
```
GET /
  Response: {"message": "Stock Trading Decision Support API", "status": "online"}

GET /health
  Response: {"status": "healthy", "version": "0.1.0"}
```

#### 2. Predictions
```
GET /api/v1/predictions/{symbol}
  Path Parameters:
    - symbol: Stock symbol (e.g., "AAPL", "VCB.VN")
  
  Response: PredictionResponse
  {
    "symbol": str,
    "current_price": float,
    "predicted_price": float,
    "confidence": float (0-1),
    "timestamp": str (ISO format)
  }
```

#### 3. Trading Signals
```
GET /api/v1/signals/{symbol}
  Path Parameters:
    - symbol: Stock symbol
  
  Response: SignalResponse
  {
    "symbol": str,
    "signal": str ("buy" | "sell" | "hold"),
    "strength": float (0-1),
    "target_price": float,
    "stop_loss": float,
    "take_profit": float
  }
```

#### 4. System Health Monitoring
```
GET /api/v1/monitoring/health
  Response:
  {
    "status": "healthy",
    "models_loaded": bool,
    "data_updated": bool
  }
```

### 6.4 Data Models (Pydantic)

```python
class PredictionResponse(BaseModel):
    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    timestamp: str

class SignalResponse(BaseModel):
    symbol: str
    signal: str  # "buy", "sell", "hold"
    strength: float
    target_price: float
    stop_loss: float
    take_profit: float
```

### 6.5 API Middleware

**Location**: `src/api/middleware/`
- Custom middleware for error handling and logging
- Request/response interceptors
- Currently minimal; ready for expansion

### 6.6 API Configuration

**File**: `src/config/settings.py`

```python
# API Settings
api_host: str = Field(default="0.0.0.0", env="API_HOST")
api_port: int = Field(default=8000, env="API_PORT")
api_reload: bool = Field(default=True, env="API_RELOAD")
```

**Run API**:
```bash
python -m src.api.main
# or
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 7. CURRENT MODEL TYPES BEING USED

### 7.1 Active Models

#### 1. LSTM (Long Short-Term Memory)
- **File**: `src/models/lstm_model.py`
- **Type**: Recurrent Neural Network (RNN)
- **Purpose**: Sequence prediction for time series
- **Architecture**:
  - 3 LSTM layers (128 → 64 → 32 units)
  - Dropout layers (0.2 rate)
  - Dense output layer (1 unit)
  - Total parameters: ~65K
- **Input**: (batch_size, 60 days, n_features)
- **Output**: Predicted close price (scalar)
- **Training Config**:
  - Optimizer: Adam (lr=0.001)
  - Loss: MSE
  - Batch size: 64 (thesis) / 32 (YAML)
  - Max epochs: 100
  - Early stopping: patience=15

#### 2. GRU (Gated Recurrent Unit)
- **File**: `src/models/gru_model.py`
- **Type**: Recurrent Neural Network (RNN)
- **Purpose**: Sequence prediction (lighter than LSTM)
- **Architecture**:
  - 3 GRU layers (128 → 64 → 32 units)
  - Dropout layers (0.2 rate)
  - Dense output layer (1 unit)
  - Total parameters: ~46K (smaller than LSTM)
- **Input**: (batch_size, 60 days, n_features)
- **Output**: Predicted close price (scalar)
- **Training Config**: Same as LSTM

### 7.2 Ensemble Approach

**ModelEvaluator** (`src/models/model_evaluator.py`)

**Method**: Weighted Average
```python
ensemble_prediction = (lstm_pred * weight_lstm + gru_pred * weight_gru) / total_weight
```

**Default Weights** (from config.yaml):
```yaml
ensemble:
  enabled: true
  method: "weighted_average"
  weights:
    lstm: 0.50
    gru: 0.50
  dynamic_weighting: false
  weighting_window: 30  # days
```

### 7.3 Model Evaluation Metrics

**Regression Metrics** (from BaseModel.evaluate()):
- **MAE** (Mean Absolute Error)
- **MSE** (Mean Squared Error)
- **RMSE** (Root Mean Squared Error)
- **MAPE** (Mean Absolute Percentage Error)

**Configured Metrics** (config/model_config.yaml):
```yaml
evaluation:
  metrics:
    regression:
      - mae
      - mse
      - rmse
      - mape
      - r2
    classification:
      - accuracy
      - precision
      - recall
      - f1
    trading:
      - direction_accuracy
      - profit_accuracy
```

### 7.4 Future Model Plans

**Disabled but Configured**:
```yaml
transformer:
  enabled: false
  d_model: 128
  n_heads: 8
  n_layers: 6
  d_ff: 512
  dropout: 0.1
```

### 7.5 Hyperparameter Tuning (Not Yet Enabled)

```yaml
hyperparameter_tuning:
  enabled: false
  method: "random_search"  # random_search, grid_search, bayesian
  n_trials: 50
  
  lstm_search_space:
    units: [32, 64, 128, 256]
    dropout: [0.1, 0.2, 0.3, 0.4]
    learning_rate: [0.0001, 0.001, 0.01]
    batch_size: [16, 32, 64]
```

---

## 8. TECHNICAL INDICATORS USED FOR FEATURES

**File**: `src/preprocessing/technical_indicators.py`

The system calculates these technical indicators for feature engineering:

### Moving Averages
- SMA (Simple Moving Average): periods [5, 10, 20, 50, 200]
- EMA (Exponential Moving Average): periods [12, 26, 50]
- WMA (Weighted Moving Average): optional

### Momentum Indicators
- RSI (Relative Strength Index): period=14
- Stochastic: k_period=14, d_period=3
- ROC (Rate of Change): period=12
- MACD: fast=12, slow=26, signal=9

### Volatility Indicators
- Bollinger Bands: period=20, std_dev=2
- ATR (Average True Range): period=14

### Trend Indicators
- MACD: Trend confirmation
- ADX (Average Directional Index): period=14

### Volume Indicators
- OBV (On-Balance Volume)
- VWAP (Volume-Weighted Average Price)

### Derived Features
- Returns: pct_change() of close price
- Log Returns: ln(close_t / close_t-1)
- Price Change: absolute change

---

## 9. DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA ACQUISITION                            │
├─────────────────────────────────────────────────────────────────┤
│ scripts/download_historical_data.py                             │
│       ↓                                                          │
│ YahooDataFetcher.fetch_data()                                  │
│ (yfinance API for OHLCV data)                                  │
│       ↓                                                          │
│ DataValidator.validate()                                        │
│ (check missing values, outliers)                               │
│       ↓                                                          │
│ DataStorage.save_raw()                                         │
│ (CSV → data/raw/{symbol}.csv)                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   DATA PREPROCESSING                             │
├─────────────────────────────────────────────────────────────────┤
│ scripts/train_models.py                                         │
│       ↓                                                          │
│ DataStorage.load_raw()                                          │
│       ↓                                                          │
│ DataProcessor.process()                                         │
│ - TechnicalIndicators.add_all_indicators()                     │
│ - Drop NaN values                                              │
│       ↓                                                          │
│ DataProcessor.normalize()                                       │
│ - MinMaxScaler (0-1 range)                                     │
│       ↓                                                          │
│ DataProcessor.save_scaler()                                    │
│ (pkl → models/scalers/{symbol}_scaler.pkl)                    │
│       ↓                                                          │
│ SlidingWindowGenerator.create_sequences()                      │
│ - Window: 60 days lookback                                     │
│ - Target: next day close price                                 │
│ - Shape: (n_samples, 60, n_features)                          │
│       ↓                                                          │
│ SlidingWindowGenerator.split_data()                            │
│ - Train: 70%, Val: 15%, Test: 15%                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    MODEL TRAINING                                │
├─────────────────────────────────────────────────────────────────┤
│ ModelTrainer.train_all()                                        │
│       ├─→ train_lstm()                                          │
│       │   - LSTMModel._build_model()                           │
│       │   - LSTMModel.train()                                  │
│       │   - Callbacks: Early Stopping, Reduce LR, Checkpoint  │
│       │   - LSTMModel.save() → .keras format                  │
│       │                                                         │
│       └─→ train_gru()                                           │
│           - GRUModel._build_model()                            │
│           - GRUModel.train()                                   │
│           - Callbacks: Early Stopping, Reduce LR, Checkpoint  │
│           - GRUModel.save() → .keras format                   │
│                                                                │
│ Both models saved to:                                          │
│ models/saved_models/{symbol}.keras                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    PREDICTIONS                                   │
├─────────────────────────────────────────────────────────────────┤
│ ModelEvaluator.predict_ensemble()                              │
│ - Load LSTM model, Load GRU model                              │
│ - LSTM.predict(X)                                              │
│ - GRU.predict(X)                                               │
│ - Weighted average: 0.5*LSTM + 0.5*GRU                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   SIGNAL GENERATION                              │
├─────────────────────────────────────────────────────────────────┤
│ SignalGenerator.generate_signal()                               │
│ - predicted_return = (pred - current_price) / current_price    │
│ - if predicted_return >= 3%: BUY signal                        │
│ - if predicted_return <= -3%: SELL signal                      │
│ - else: HOLD signal                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     API ENDPOINT                                 │
├─────────────────────────────────────────────────────────────────┤
│ FastAPI: src/api/main.py                                        │
│ GET /api/v1/predictions/{symbol}                               │
│ GET /api/v1/signals/{symbol}                                   │
│ GET /api/v1/monitoring/health                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. CONFIGURATION FILES SUMMARY

### 10.1 main config.yaml
- Application settings
- Data source and validation
- Symbol management
- Preprocessing parameters
- Technical indicators configuration
- Model selection
- Ensemble settings
- System configuration
- Monitoring and notifications

### 10.2 model_config.yaml
- LSTM architecture and training
- GRU architecture and training
- Transformer config (disabled)
- Model evaluation metrics
- Cross-validation settings
- Hyperparameter tuning space

### 10.3 trading_config.yaml
- Trading parameters
- Risk management rules
- Order execution settings
- Portfolio constraints

### 10.4 logging_config.yaml
- Log level configuration
- Handler setup (console, file)
- Log formatting
- File rotation and retention

### 10.5 vietnam_stocks.yaml
- Vietnamese stock listings by sector
- HOSE (Ho Chi Minh) stocks
- HNX (Hanoi) stocks

---

## 11. KEY DEPENDENCIES

### Machine Learning & Deep Learning
- TensorFlow >= 2.13.0 (neural networks)
- Keras >= 2.13.0 (model building)
- scikit-learn >= 1.3.0 (preprocessing, metrics)
- numpy >= 1.24.0 (numerical computing)
- pandas >= 2.0.0 (data manipulation)

### Data & APIs
- yfinance >= 0.2.28 (Yahoo Finance data)
- requests >= 2.31.0 (HTTP client)

### Web Framework
- FastAPI >= 0.103.0 (REST API)
- Uvicorn >= 0.23.0 (ASGI server)
- Pydantic >= 2.3.0 (data validation)
- Streamlit >= 1.27.0 (dashboard)

### Monitoring & Logging
- MLflow >= 2.7.0 (experiment tracking)

### Data Processing
- joblib >= 1.3.0 (model serialization)
- scipy >= 1.10.0 (scientific computing)

---

## 12. KEY CLASSES & METHODS SUMMARY

| Class | File | Purpose | Key Methods |
|-------|------|---------|------------|
| YahooDataFetcher | data_ingestion/yahoo_fetcher.py | Fetch data | fetch_data(), fetch_multiple() |
| DataValidator | data_ingestion/data_validator.py | Validate data | validate() |
| DataStorage | data_ingestion/data_storage.py | Persist data | save_raw(), load_raw(), save_processed(), load_processed() |
| TechnicalIndicators | preprocessing/technical_indicators.py | Calculate indicators | calculate_sma(), calculate_rsi(), add_all_indicators() |
| DataProcessor | preprocessing/data_processor.py | Process features | process(), normalize(), create_sequences(), save_scaler() |
| SlidingWindowGenerator | preprocessing/sliding_window.py | Create sequences | create_sequences(), split_data() |
| BaseModel | models/base_model.py | Abstract model | train(), predict(), save(), load(), evaluate() |
| LSTMModel | models/lstm_model.py | LSTM implementation | train(), predict(), save(), load() |
| GRUModel | models/gru_model.py | GRU implementation | train(), predict(), save(), load() |
| ModelTrainer | models/model_trainer.py | Training orchestrator | train_lstm(), train_gru(), train_all() |
| ModelEvaluator | models/model_evaluator.py | Evaluate models | predict_ensemble() |
| SignalGenerator | trading_engine/signal_generator.py | Generate signals | generate_signal() |
| DriftDetector | monitoring/drift_detector.py | Detect drift | detect_drift() |
| Settings | config/settings.py | Configuration | get_config(), get_yaml_config() |

---

## 13. TESTING

**Test Structure**:
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Test runner: pytest

**Key Test Files**:
- test_base_model.py
- test_data_storage.py
- test_data_processor.py
- test_lstm_model.py (implied)
- test_signal_generator.py
- test_backtest_engine.py
- test_performance_metrics.py

---

## 14. ENTRY POINTS (Console Scripts)

From `setup.py`:
```python
entry_points={
    'console_scripts': [
        'trade-download-data=scripts.download_historical_data:main',
        'trade-train-models=scripts.train_models:main',
        'trade-backtest=scripts.run_backtest:main',
    ],
}
```

---

## 15. DEPLOYMENT OPTIONS

1. **Local Development**
   ```bash
   python scripts/download_historical_data.py --symbols AAPL --period 2y
   python scripts/train_models.py --symbol AAPL --models all
   python -m src.api.main
   ```

2. **Docker**: Configuration available in `docker/`

3. **Heroku**: Configuration available in `Procfile`

4. **Streamlit Dashboard**: `src/dashboard/app.py`

---

## SUMMARY

This is a production-ready ML-based stock trading system with:

✓ **Two complementary neural network models** (LSTM & GRU) for price prediction
✓ **Comprehensive data pipeline** from Yahoo Finance to trained models
✓ **REST API** for real-time predictions and trading signals
✓ **Risk management** with position sizing and stop-loss/take-profit
✓ **Monitoring** with drift detection and performance tracking
✓ **Backtesting engine** for strategy validation
✓ **Multi-market support** (US and Vietnamese stocks)
✓ **Clean architecture** with separation of concerns
✓ **Configuration-driven** approach for easy customization
✓ **Testing framework** for quality assurance

The system follows a clear data → preprocessing → training → prediction → signal → API flow, with all models stored persistently for reuse.

