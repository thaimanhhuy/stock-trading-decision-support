# System Design

## Architecture Overview

The Stock Trading Decision Support System follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                      │
│          (Dashboard, API, CLI Scripts)                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                 Application Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Trading    │  │  Backtesting │  │  Monitoring  │ │
│  │    Engine    │  │    Engine    │  │   System     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                   Model Layer                           │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────────┐ │
│  │ ARIMA  │  │  LSTM  │  │  GRU   │  │   Ensemble   │ │
│  └────────┘  └────────┘  └────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              Data Processing Layer                      │
│  ┌──────────────────┐  ┌──────────────────────────────┐│
│  │  Preprocessing   │  │  Feature Engineering         ││
│  │  & Validation    │  │  (Technical Indicators)      ││
│  └──────────────────┘  └──────────────────────────────┘│
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                  Data Layer                             │
│  ┌──────────────────┐  ┌──────────────────────────────┐│
│  │  Data Ingestion  │  │    Data Storage              ││
│  │  (Yahoo Finance) │  │  (CSV, SQLite future)        ││
│  └──────────────────┘  └──────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Data Layer

#### Data Ingestion (`src/data_ingestion/`)
- **yahoo_fetcher.py**: Fetches OHLCV data from Yahoo Finance
- **data_validator.py**: Validates data quality and completeness
- **data_storage.py**: Handles data persistence

**Key Features**:
- Automatic retry logic
- Data quality checks (missing values, outliers)
- Support for multiple symbols
- Incremental updates

#### Data Storage
- **Raw Data**: CSV files in `data/raw/`
- **Processed Data**: Normalized data in `data/processed/`
- **Features**: Engineered features in `data/features/`

### 2. Data Processing Layer

#### Preprocessing (`src/preprocessing/`)
- **data_processor.py**: Data cleaning and normalization
- **technical_indicators.py**: Calculate technical indicators
- **sliding_window.py**: Create sequences for LSTM/GRU

**Technical Indicators Implemented**:
- Moving Averages: SMA, EMA, WMA
- Momentum: RSI, Stochastic, ROC
- Volatility: Bollinger Bands, ATR
- Trend: MACD, ADX
- Volume: OBV, VWAP

### 3. Model Layer

#### Models (`src/models/`)

**Base Model** (`base_model.py`):
- Abstract base class
- Common interface for all models
- Standard methods: train(), predict(), evaluate(), save(), load()

**ARIMA** (`arima_model.py`):
- Statistical time series model
- Auto-selection of (p,d,q) parameters using AIC
- Handles non-stationarity via differencing

**LSTM** (`lstm_model.py`):
```python
Architecture:
- Input: Sliding window of features (e.g., 60 days)
- LSTM Layer 1: 128 units, return sequences
- Dropout: 0.2
- LSTM Layer 2: 64 units, return sequences
- Dropout: 0.2
- LSTM Layer 3: 32 units
- Dropout: 0.2
- Dense Output: 1 unit (price prediction)

Optimizer: Adam
Loss: MSE (Mean Squared Error)
```

**GRU** (`gru_model.py`):
- Similar architecture to LSTM but with GRU layers
- Faster training, fewer parameters
- Comparable performance to LSTM

**Model Trainer** (`model_trainer.py`):
- Centralized training orchestration
- Hyperparameter management
- Cross-validation
- Model versioning

**Model Evaluator** (`model_evaluator.py`):
- Ensemble predictions
- Confidence intervals
- Performance metrics

### 4. Application Layer

#### Trading Engine (`src/trading_engine/`)

**Signal Generator** (`signal_generator.py`):
```python
Signal Logic:
1. Get ensemble prediction
2. Calculate expected return
3. Check technical confirmation
4. Apply filters (volume, volatility)
5. Generate signal: BUY, SELL, HOLD

Signal Strength: 0.0 to 1.0
```

**Risk Manager** (`risk_manager.py`):
```python
Risk Controls:
- Position sizing (Kelly Criterion, Fixed Percentage)
- Stop-loss calculation
- Portfolio risk limits
- Maximum drawdown monitoring
- Correlation analysis
```

**Order Manager** (`order_manager.py`):
- Order generation and tracking
- Execution simulation
- Order history

#### Backtesting Engine (`src/backtesting/`)

**Backtest Engine** (`backtest_engine.py`):
```python
Backtesting Process:
1. Load historical data
2. Walk-forward: for each day:
   a. Train/update models on past data
   b. Generate prediction
   c. Generate signal
   d. Simulate trade execution
   e. Update portfolio
3. Calculate performance metrics
4. Generate report
```

**Performance Metrics** (`performance_metrics.py`):
- Return metrics: Total, Annual, CAGR
- Risk metrics: Sharpe, Sortino, Calmar
- Drawdown: Max, Average, Duration
- Trade metrics: Win rate, Profit factor, Avg trade

#### Monitoring System (`src/monitoring/`)

**Drift Detector** (`drift_detector.py`):
- Detects distribution changes in input data
- Statistical tests (KS test, Chi-square)
- Alert when drift exceeds threshold

**Performance Monitor** (`performance_monitor.py`):
- Tracks prediction accuracy over time
- Alerts on performance degradation
- Compares to baseline

**Audit Logger** (`audit_logger.py`):
- Logs all predictions and trades
- Compliance and debugging
- Structured logging format

### 5. User Interface Layer

#### REST API (`src/api/`)

**Framework**: FastAPI

**Endpoints**:
```python
GET /api/v1/predictions/{symbol}
POST /api/v1/predictions/batch
GET /api/v1/signals/{symbol}
GET /api/v1/signals/portfolio
GET /api/v1/monitoring/health
GET /api/v1/monitoring/metrics
GET /api/v1/monitoring/drift
```

**Middleware**:
- Request logging
- Error handling
- Rate limiting (future)
- Authentication (future)

#### Dashboard (`src/dashboard/`)

**Framework**: Streamlit

**Pages**:
- Home: Overview and summary
- Signals: Real-time trading signals
- Performance: Portfolio tracking
- Monitoring: Model health

### 6. Utilities (`src/utils/`)

- **logger.py**: Centralized logging
- **exceptions.py**: Custom exceptions
- **constants.py**: System-wide constants

## Data Flow

### Training Pipeline
```
1. Download Data (yahoo_fetcher)
   ↓
2. Validate & Clean (data_validator, data_processor)
   ↓
3. Engineer Features (technical_indicators)
   ↓
4. Create Sequences (sliding_window)
   ↓
5. Train Models (model_trainer)
   ↓
6. Evaluate & Save (model_evaluator)
```

### Prediction Pipeline
```
1. Fetch Latest Data
   ↓
2. Preprocess & Features
   ↓
3. Load Models
   ↓
4. Generate Predictions (each model)
   ↓
5. Ensemble Prediction
   ↓
6. Generate Signal (signal_generator)
   ↓
7. Apply Risk Management (risk_manager)
   ↓
8. Output Signal & Position Size
```

### Backtesting Pipeline
```
1. Load Historical Data
   ↓
2. For each day:
   ├─ Update models (if needed)
   ├─ Generate prediction
   ├─ Generate signal
   ├─ Simulate execution
   └─ Update portfolio
   ↓
3. Calculate Metrics
   ↓
4. Generate Report
```

## Technology Stack

### Core Python Libraries
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation
- **SciPy**: Statistical functions

### Machine Learning
- **TensorFlow/Keras**: Deep learning (LSTM, GRU)
- **statsmodels**: Time series (ARIMA)
- **scikit-learn**: Preprocessing, metrics

### Data & APIs
- **yfinance**: Yahoo Finance API
- **requests**: HTTP client

### Web & API
- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server
- **Streamlit**: Dashboard framework

### Utilities
- **PyYAML**: Configuration files
- **python-dotenv**: Environment variables
- **MLflow**: Experiment tracking (optional)

### Testing
- **pytest**: Test framework
- **pytest-cov**: Coverage reporting

### DevOps
- **Docker**: Containerization
- **docker-compose**: Multi-container orchestration

## Database Design (Future)

Currently using file-based storage. Future enhancement:

```sql
-- Predictions table
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    date DATE,
    model TEXT,
    predicted_price REAL,
    actual_price REAL,
    error REAL,
    timestamp DATETIME
);

-- Trades table
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    date DATE,
    action TEXT,
    price REAL,
    quantity INTEGER,
    pnl REAL,
    timestamp DATETIME
);

-- Model performance table
CREATE TABLE model_performance (
    id INTEGER PRIMARY KEY,
    model TEXT,
    symbol TEXT,
    date DATE,
    mae REAL,
    rmse REAL,
    direction_accuracy REAL,
    timestamp DATETIME
);
```

## Scalability Considerations

### Current Limitations
- Single-threaded processing
- File-based storage
- No caching layer
- Manual scaling

### Future Enhancements
- **Horizontal Scaling**: Multiple worker processes
- **Caching**: Redis for predictions and data
- **Database**: PostgreSQL for structured data
- **Message Queue**: Celery for async tasks
- **Load Balancer**: Nginx for API
- **Microservices**: Separate services for predictions, signals, monitoring

## Security Considerations

### Current Implementation
- Environment variables for sensitive config
- No authentication (local use only)
- Input validation in API

### Production Requirements
- **Authentication**: JWT tokens, API keys
- **Authorization**: Role-based access control
- **Encryption**: HTTPS, encrypted storage
- **Rate Limiting**: Prevent abuse
- **Audit Logging**: All access logged
- **Input Sanitization**: Prevent injection attacks

## Performance Optimization

### Model Inference
- Model caching in memory
- Batch predictions
- Model quantization (future)
- ONNX conversion (future)

### Data Processing
- Vectorized operations (NumPy)
- Lazy loading
- Data chunking for large datasets
- Parallel processing for multiple symbols

### API
- Response caching
- Async endpoints
- Connection pooling
- Compression

## Error Handling

### Strategy
1. **Fail Fast**: Validate inputs early
2. **Graceful Degradation**: Fallback to simpler models if needed
3. **Comprehensive Logging**: All errors logged with context
4. **User-Friendly Messages**: Clear error messages in API

### Error Types
- `DataValidationError`: Invalid or missing data
- `ModelNotFoundError`: Model file not found
- `PredictionError`: Prediction failed
- `RiskLimitExceeded`: Risk management constraint violated

## Configuration Management

### Hierarchy
1. Default values (in code)
2. Config files (config/*.yaml)
3. Environment variables (.env)
4. Command-line arguments

### Best Practices
- Never commit secrets
- Use .env.example as template
- Validate configuration on startup
- Allow runtime configuration updates (where safe)

## Testing Strategy

### Unit Tests
- Individual functions and classes
- Mock external dependencies
- Fast execution (<1s per test)

### Integration Tests
- Component interactions
- Real data processing
- End-to-end workflows

### Backtesting as Validation
- Historical performance
- Walk-forward validation
- Out-of-sample testing

## Deployment Architecture

### Docker Deployment
```yaml
services:
  api:
    - FastAPI application
    - Port 8000
    - Auto-restart

  dashboard:
    - Streamlit application
    - Port 8501
    - Auto-restart

  training:
    - Scheduled model training
    - Cron-based execution
```

### Production Considerations
- Load balancing
- Health checks
- Auto-scaling
- Monitoring (Prometheus, Grafana)
- Centralized logging (ELK stack)

## Monitoring & Observability

### Metrics to Track
- API response times
- Prediction accuracy
- Model drift
- Error rates
- Resource usage (CPU, memory)

### Alerting
- Performance degradation
- Data quality issues
- System errors
- Risk limit breaches

## Future Architecture Enhancements

1. **Microservices**: Separate services for each component
2. **Event-Driven**: Kafka for real-time data streams
3. **Cloud Native**: Kubernetes deployment
4. **Multi-Asset**: Portfolio-level optimization
5. **Real-Time**: WebSocket for live updates
6. **Advanced ML**: Reinforcement learning, transformer models

---

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for development setup and contribution guidelines.
