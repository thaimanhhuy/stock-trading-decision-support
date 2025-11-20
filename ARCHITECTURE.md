# System Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STOCK TRADING DECISION SUPPORT SYSTEM                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         DATA LAYER                                    │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                        │  │
│  │  ┌──────────────────────┐  ┌──────────────────────────────────────┐ │  │
│  │  │  Yahoo Finance API   │  │  Data Storage                        │ │  │
│  │  │                      │  ├──────────────────────────────────────┤ │  │
│  │  │ • OHLCV data        │  │ • data/raw/                         │ │  │
│  │  │ • Daily prices      │  │   {symbol}.csv                      │ │  │
│  │  │ • US & Vietnam      │  │                                      │ │  │
│  │  │   stocks            │  │ • data/processed/                   │ │  │
│  │  └──────────────────────┘  │   {symbol}_processed.csv            │ │  │
│  │           │                 │                                      │ │  │
│  │           └────────→ YahooDataFetcher                              │ │  │
│  │                     ├─→ fetch_data()                               │ │  │
│  │                     └─→ fetch_multiple()                           │ │  │
│  │                                                                      │ │  │
│  │           ├────────→ DataValidator                                  │ │  │
│  │           │          ├─→ Check missing values                       │ │  │
│  │           │          ├─→ Check outliers                             │ │  │
│  │           │          └─→ Validate columns                           │ │  │
│  │           │                                                          │ │  │
│  │           └────────→ DataStorage                                    │ │  │
│  │                      ├─→ save_raw()                                 │ │  │
│  │                      ├─→ load_raw()                                 │ │  │
│  │                      └─→ save_processed()                           │ │  │
│  │                                                                      │ │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│           │                                                                  │
├───────────▼──────────────────────────────────────────────────────────────────┤
│                      PREPROCESSING LAYER                                      │
├────────────────────────────────────────────────────────────────────────────  │
│                                                                                │
│  Raw Data (OHLCV)                                                             │
│     │                                                                         │
│     ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐         │
│  │ TechnicalIndicators.add_all_indicators()                        │         │
│  │                                                                  │         │
│  │ SMA (5,10,20,50,200)  │  Momentum    │  Trend      │  Volume    │         │
│  │ EMA (12,26,50)        │  • RSI       │  • MACD     │  • OBV     │         │
│  │ WMA (optional)        │  • ROC       │  • ADX      │  • VWAP    │         │
│  │                       │  • Stoch     │             │            │         │
│  │ Volatility                                                       │         │
│  │ • Bollinger Bands     │  Derived Features                        │         │
│  │ • ATR                 │  • Returns  • Log Returns  • Price Chng  │         │
│  └─────────────────────────────────────────────────────────────────┘         │
│     │                                                                         │
│     ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐         │
│  │ DataProcessor.normalize()                                        │         │
│  │ MinMaxScaler (0-1 range)                                         │         │
│  │ Save: models/scalers/{symbol}_scaler.pkl                         │         │
│  └─────────────────────────────────────────────────────────────────┘         │
│     │                                                                         │
│     ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐         │
│  │ SlidingWindowGenerator.create_sequences()                        │         │
│  │ Windows: 60-day lookback                                         │         │
│  │ Target: Next day close price                                     │         │
│  │ Shape: (n_samples, 60 days, n_features)                          │         │
│  └─────────────────────────────────────────────────────────────────┘         │
│     │                                                                         │
│     ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐         │
│  │ SlidingWindowGenerator.split_data()                              │         │
│  │ Train: 70%  │  Val: 15%  │  Test: 15%                           │         │
│  │ (No shuffle - time series)                                       │         │
│  └─────────────────────────────────────────────────────────────────┘         │
│                                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                      MODEL TRAINING LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌────────────────────────────────┐  ┌──────────────────────────────┐       │
│  │   LSTM MODEL                   │  │   GRU MODEL                  │       │
│  ├────────────────────────────────┤  ├──────────────────────────────┤       │
│  │                                │  │                              │       │
│  │ Input: (batch, 60, features)  │  │ Input: (batch, 60, features) │       │
│  │   ↓                            │  │   ↓                          │       │
│  │ LSTM 128 + Dropout(0.2)       │  │ GRU 128 + Dropout(0.2)      │       │
│  │   ↓                            │  │   ↓                          │       │
│  │ LSTM 64 + Dropout(0.2)        │  │ GRU 64 + Dropout(0.2)       │       │
│  │   ↓                            │  │   ↓                          │       │
│  │ LSTM 32 + Dropout(0.2)        │  │ GRU 32 + Dropout(0.2)       │       │
│  │   ↓                            │  │   ↓                          │       │
│  │ Dense 1 (Linear)              │  │ Dense 1 (Linear)             │       │
│  │   ↓                            │  │   ↓                          │       │
│  │ Output: predicted_price       │  │ Output: predicted_price      │       │
│  │                                │  │                              │       │
│  │ Training:                      │  │ Training:                    │       │
│  │ • Optimizer: Adam(lr=0.001)   │  │ • Optimizer: Adam(lr=0.001) │       │
│  │ • Loss: MSE                    │  │ • Loss: MSE                  │       │
│  │ • Batch: 32                    │  │ • Batch: 32                  │       │
│  │ • Epochs: 100                  │  │ • Epochs: 100                │       │
│  │ • Early Stop: patience=15      │  │ • Early Stop: patience=15    │       │
│  │                                │  │                              │       │
│  │ Callbacks:                     │  │ Callbacks:                   │       │
│  │ • Early Stopping               │  │ • Early Stopping             │       │
│  │ • Reduce LR on Plateau         │  │ • Reduce LR on Plateau      │       │
│  │ • Model Checkpoint             │  │ • Model Checkpoint          │       │
│  │                                │  │                              │       │
│  │ Save: models/saved_models/     │  │ Save: models/saved_models/  │       │
│  │        {symbol}.keras          │  │        {symbol}.keras       │       │
│  └────────────────────────────────┘  └──────────────────────────────┘       │
│           │                                     │                             │
│           └──────────────────┬──────────────────┘                             │
│                              │                                               │
│                              ▼                                               │
│                    ┌─────────────────────┐                                   │
│                    │ ModelEvaluator      │                                   │
│                    │ Metrics:            │                                   │
│                    │ • MAE               │                                   │
│                    │ • MSE               │                                   │
│                    │ • RMSE              │                                   │
│                    │ • MAPE              │                                   │
│                    └─────────────────────┘                                   │
│                                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                    PREDICTION & SIGNAL LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  New Data (Unseen)                                                            │
│     │                                                                         │
│     ├──────────→ Normalize (load {symbol}_scaler.pkl)                         │
│     │                                                                         │
│     ├──────────→ ModelEvaluator.predict_ensemble()                           │
│     │              │                                                          │
│     │              ├─→ Load LSTM model                                        │
│     │              ├─→ Load GRU model                                         │
│     │              ├─→ lstm_pred = LSTM.predict(X)                           │
│     │              ├─→ gru_pred = GRU.predict(X)                             │
│     │              └─→ ensemble = 0.5*lstm_pred + 0.5*gru_pred               │
│     │                                                                         │
│     ▼                                                                         │
│  ┌────────────────────────────────────────────────────────┐                  │
│  │ SignalGenerator.generate_signal()                      │                  │
│  │                                                         │                  │
│  │ predicted_return =                                     │                  │
│  │   (predicted_price - current_price) / current_price   │                  │
│  │                                                         │                  │
│  │ if predicted_return >= 3%:  → BUY signal               │                  │
│  │ elif predicted_return <= -3%: → SELL signal            │                  │
│  │ else: → HOLD signal                                    │                  │
│  │                                                         │                  │
│  │ Return:                                                 │                  │
│  │ {signal, strength, target_price, stop_loss, tp}       │                  │
│  └────────────────────────────────────────────────────────┘                  │
│                                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                       API & SERVICE LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  FastAPI Application (src/api/)                                              │
│  Modular route structure with 4 specialized modules:                        │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ main.py - Application Entry Point                                      │ │
│  │ • Initializes FastAPI app                                              │ │
│  │ • Includes route modules                                                │ │
│  │ • Lifecycle management (startup/shutdown)                              │ │
│  │ • Scheduler initialization                                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ routes/predictions.py - Prediction & Signal Routes                     │ │
│  │ ┌─ GET /api/v1/predictions/{symbol} ────────────────────────────┐     │ │
│  │ │ Response: {symbol, current_price, predicted_price,             │     │ │
│  │ │            confidence, timestamp}                              │     │ │
│  │ └──────────────────────────────────────────────────────────────┘      │ │
│  │ ┌─ GET /api/v1/signals/{symbol} ────────────────────────────────┐     │ │
│  │ │ Response: {symbol, signal, strength, target_price,             │     │ │
│  │ │            stop_loss, take_profit}                             │     │ │
│  │ └──────────────────────────────────────────────────────────────┘      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ routes/training.py - Model Training Routes                             │ │
│  │ ┌─ POST /api/v1/training/train ──────────────────────────────┐        │ │
│  │ │ Request: {symbol, models, fetch_new_data}                   │        │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  │ ┌─ POST /api/v1/training/batch-train ────────────────────────┐        │ │
│  │ │ Request: {symbols[], models, fetch_new_data}                │        │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  │ ┌─ GET /api/v1/training/history/{symbol} ────────────────────┐        │ │
│  │ │ Response: Training history records                          │        │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  │ ┌─ GET /api/v1/training/stats ────────────────────────────────┐       │ │
│  │ │ Response: Training statistics and metrics                   │       │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ routes/monitoring.py - Monitoring & Market Routes                      │ │
│  │ ┌─ GET /api/v1/monitoring/health ────────────────────────────┐        │ │
│  │ │ Response: {status, models_loaded, data_updated}             │        │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  │ ┌─ GET /api/v1/market/check/{market} ────────────────────────┐        │ │
│  │ │ Response: {event_detected, drop_percentage, should_retrain} │        │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  │ ┌─ GET /api/v1/market/events ─────────────────────────────────┐       │ │
│  │ │ Response: Market event history                               │       │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ routes/scheduler.py - Scheduler Control Routes                         │ │
│  │ ┌─ GET /api/v1/scheduler/status ──────────────────────────────┐       │ │
│  │ │ Response: {running, jobs[], next_run_time}                   │       │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  │ ┌─ POST /api/v1/scheduler/start ──────────────────────────────┐       │ │
│  │ │ Response: {status: "success"}                                │       │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  │ ┌─ POST /api/v1/scheduler/stop ───────────────────────────────┐       │ │
│  │ │ Response: {status: "success"}                                │       │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  │ ┌─ POST /api/v1/scheduler/trigger-retraining ─────────────────┐       │ │
│  │ │ Response: {status: "success"}                                │       │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  │ ┌─ POST /api/v1/scheduler/trigger-market-check ───────────────┐       │ │
│  │ │ Response: {status: "success"}                                │       │ │
│  │ └──────────────────────────────────────────────────────────┘          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                    MONITORING & UTILITIES LAYER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐ │
│  │ DriftDetector        │  │ PerformanceMonitor   │  │ AuditLogger        │ │
│  │                      │  │                      │  │                    │ │
│  │ • KS Test            │  │ • Track metrics      │  │ • Log predictions  │ │
│  │ • Chi-square         │  │ • Alert on drop      │  │ • Log signals      │ │
│  │ • PSI                │  │ • Performance stats  │  │ • Log trades       │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────┘ │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────┐            │
│  │ Settings Management                                           │            │
│  │ • Load YAML configs (config/*.yaml)                           │            │
│  │ • Environment variables override                              │            │
│  │ • Data paths, API config, model config                        │            │
│  └──────────────────────────────────────────────────────────────┘            │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────┐            │
│  │ Logging System                                                │            │
│  │ • JSON format logs                                            │            │
│  │ • Console & file handlers                                     │            │
│  │ • Daily rotation                                              │            │
│  └──────────────────────────────────────────────────────────────┘            │
│                                                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Training to Prediction

```
┌──────────────┐
│ Yahoo Finance│
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│ 1. DOWNLOAD & VALIDATE              │
│ • download_historical_data.py      │
│ • Fetches OHLCV data               │
│ • Validates quality                │
│ • Saves to data/raw/               │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 2. PREPROCESSING                    │
│ • train_models.py                  │
│ • Add technical indicators          │
│ • Normalize features                │
│ • Create 60-day sequences           │
│ • Split train/val/test (70/15/15)  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 3. MODEL TRAINING                   │
│ • ModelTrainer.train_all()         │
│ ├─ LSTMModel.train()               │
│ └─ GRUModel.train()                │
│ • Early stopping callbacks          │
│ • Save to models/saved_models/     │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 4. MODEL EVALUATION                 │
│ • Evaluate on test set              │
│ • Calculate MAE, MSE, RMSE, MAPE   │
│ • Log metrics                       │
└──────────┬──────────────────────────┘
           │
           ├──────────────┐
           │              │
           ▼              ▼
      ┌─────────┐   ┌────────────┐
      │ Backtest│   │ API Server │
      │ Engine  │   │ (uvicorn)  │
      └────┬────┘   └────┬───────┘
           │             │
           │             ▼
           │        ┌──────────────────────┐
           │        │ 5. REAL-TIME PREDICT │
           │        │ • Load new data      │
           │        │ • Normalize          │
           │        │ • Ensemble predict   │
           │        │ • Generate signal    │
           │        │ • Return via API     │
           │        └──────────────────────┘
           │
           ▼
      ┌──────────────────────┐
      │ 6. RESULT DISPLAY    │
      │ • Backtest report    │
      │ • Performance metrics│
      │ • Dashboard views    │
      └──────────────────────┘
```

## Component Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                      ENTRY POINTS                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  scripts/download_historical_data.py                        │
│  └─→ YahooDataFetcher ─→ DataValidator ─→ DataStorage      │
│                                                              │
│  scripts/train_models.py                                    │
│  └─→ DataStorage ─→ DataProcessor ─→ ModelTrainer          │
│                     └─→ TechnicalIndicators                │
│                     └─→ SlidingWindowGenerator             │
│                     └─→ LSTMModel, GRUModel                │
│                                                              │
│  src/api/main.py (FastAPI)                                 │
│  └─→ Settings ─→ ModelEvaluator ─→ LSTMModel, GRUModel    │
│                └─→ SignalGenerator                         │
│                └─→ DriftDetector, PerformanceMonitor       │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      SHARED UTILITIES                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  settings.py (Configuration Management)                    │
│  ├─ Loads config/*.yaml files                              │
│  ├─ Provides path configs                                  │
│  └─ Used by all components                                 │
│                                                              │
│  logger.py (Logging)                                        │
│  ├─ JSON logging                                            │
│  ├─ Console & file output                                  │
│  └─ LoggerMixin for all classes                            │
│                                                              │
│  exceptions.py (Error Handling)                             │
│  ├─ DataFetchError                                          │
│  └─ Custom exceptions                                      │
│                                                              │
│  constants.py (Constants)                                   │
│  ├─ Signal types (BUY, SELL, HOLD)                         │
│  └─ Thresholds and defaults                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Hierarchy

```
Settings (Environment Variables & config.yaml)
│
├─ config.yaml (Main Configuration)
│  ├─ data.*
│  ├─ preprocessing.*
│  ├─ technical_indicators.*
│  ├─ models.*
│  ├─ ensemble.*
│  ├─ system.*
│  ├─ monitoring.*
│  └─ notifications.*
│
├─ model_config.yaml (Model Architecture)
│  ├─ lstm.*
│  ├─ gru.*
│  ├─ transformer.* (disabled)
│  ├─ evaluation.*
│  └─ hyperparameter_tuning.* (disabled)
│
├─ trading_config.yaml (Trading Rules)
│  ├─ risk_management.*
│  ├─ position_sizing.*
│  └─ thresholds.*
│
├─ logging_config.yaml (Logging Setup)
│  ├─ handlers.*
│  ├─ formatters.*
│  └─ rotation.*
│
└─ vietnam_stocks.yaml (Stock List)
   ├─ banking.*
   ├─ technology.*
   └─ sectors.*
```

## Storage Architecture

```
Project Root
├── models/
│   ├── saved_models/
│   │   ├── AAPL.keras (TensorFlow SavedModel)
│   │   ├── VCB.VN.keras
│   │   └── ...
│   ├── scalers/
│   │   ├── AAPL_scaler.pkl (MinMaxScaler)
│   │   ├── VCB.VN_scaler.pkl
│   │   └── ...
│   └── mlflow/
│       └── (MLflow experiment artifacts)
│
├── data/
│   ├── raw/
│   │   ├── AAPL.csv (Original OHLCV)
│   │   ├── VCB.VN.csv
│   │   └── ...
│   ├── processed/
│   │   ├── AAPL_processed.csv (+ indicators)
│   │   ├── VCB.VN_processed.csv
│   │   └── ...
│   └── features/
│       ├── AAPL_features.csv (Normalized)
│       ├── VCB.VN_features.csv
│       └── ...
│
└── logs/
    ├── application/
    │   └── app_*.log
    ├── trading/
    │   └── trading_*.log
    └── audit/
        └── audit_*.log
```

## Model Selection & Deployment

```
Development & Testing
  │
  ├─ Train LSTM
  ├─ Train GRU
  └─ Evaluate both
       │
       ▼
  Best Model Selection
  (Usually ensemble both)
       │
       ├─→ Save to models/saved_models/
       ├─→ Save scaler to models/scalers/
       └─→ Log metrics
            │
            ▼
  API Deployment
  (Load both models in memory)
       │
       ├─→ GET /api/v1/predictions/
       ├─→ GET /api/v1/signals/
       └─→ Both models used for ensemble
            │
            ▼
  Monitoring in Production
  ├─ Track prediction accuracy
  ├─ Detect model drift
  ├─ Monitor signal performance
  └─ Log all decisions (audit trail)
```

## Performance Characteristics

| Component | Typical Time | Notes |
|-----------|--------------|-------|
| Data Download | 2-10s | Depends on data size & network |
| Preprocessing | 5-30s | Adding indicators, normalization |
| Model Training | 2-10 min | With early stopping on good hardware |
| Model Prediction | 100-500ms | Per symbol, including ensemble |
| API Response | 500ms-1s | Full round-trip (load model, predict) |
| Backtest (1 year) | 1-5 min | Depends on strategy complexity |

## Scalability Considerations

### Current Limitations
- Single process API (use gunicorn for multi-worker)
- In-memory model loading (suitable for 2-3 symbols)
- No distributed training (single GPU/CPU)
- CSV-based storage (OK for <1GB data)

### Future Enhancements
- Load balancing with multiple API instances
- Database backend (PostgreSQL/MongoDB)
- Model registry service
- Distributed training with Ray or Horovod
- Real-time data streaming (Kafka)
- Model serving framework (BentoML/KServe)

