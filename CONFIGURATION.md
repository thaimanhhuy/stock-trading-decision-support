# Configuration Guide

Complete guide to configuring the Stock Trading Decision Support System.

## Table of Contents

1. [Overview](#overview)
2. [Configuration Files](#configuration-files)
3. [Environment Variables](#environment-variables)
4. [Model Configuration](#model-configuration)
5. [Trading Configuration](#trading-configuration)
6. [Market-Specific Settings](#market-specific-settings)
7. [Logging Configuration](#logging-configuration)
8. [Advanced Settings](#advanced-settings)

---

## Overview

The system uses a hierarchical configuration approach:

1. **Default values** in code
2. **YAML configuration files** in `config/` directory
3. **Environment variables** from `.env` file
4. **Runtime parameters** passed via command-line arguments

Configuration priority: Runtime parameters > Environment variables > YAML files > Default values

---

## Configuration Files

### File Structure

```
config/
├── config.yaml              # General application settings
├── model_config.yaml        # Model hyperparameters
├── trading_config.yaml      # Trading strategy parameters
├── logging_config.yaml      # Logging configuration
└── vietnam_stocks.yaml      # Vietnamese stock listings
```

### config.yaml

Main application configuration file.

```yaml
# Data paths
data:
  raw_data_path: data/raw
  processed_data_path: data/processed
  features_path: data/features
  backtest_path: data/backtest

# Model paths
models:
  saved_models_path: models/saved_models
  checkpoints_path: models/checkpoints

# Market settings
market:
  default_market: US
  timezone: America/New_York
  currency: USD
  trading_hours:
    start: "09:30"
    end: "16:00"

# Vietnamese market settings
vietnam_market:
  timezone: Asia/Ho_Chi_Minh
  currency: VND
  trading_hours:
    morning:
      start: "09:00"
      end: "11:30"
    afternoon:
      start: "13:00"
      end: "14:45"
  price_limits:
    standard: 0.07      # ±7%
    special: 0.10       # ±10%
  settlement: T+2

# Data fetching
data_fetching:
  source: yahoo_finance
  update_frequency: daily
  retry_attempts: 3
  retry_delay: 5        # seconds

# API settings
api:
  host: 0.0.0.0
  port: 8000
  workers: 4
  reload: false
  log_level: info
  cors_origins:
    - "*"

# Dashboard settings
dashboard:
  port: 8501
  title: Stock Trading Decision Support
  refresh_interval: 60  # seconds
  max_symbols: 50

# Monitoring
monitoring:
  enable_drift_detection: true
  drift_threshold: 0.05
  performance_window: 30  # days
  alert_threshold: -0.10  # -10% performance drop

# MLflow (optional)
mlflow:
  enabled: false
  tracking_uri: http://localhost:5000
  experiment_name: stock-trading-models

# Feature flags
features:
  enable_sentiment_analysis: false
  enable_news_integration: false
  enable_portfolio_optimization: false
  enable_multi_asset: false
```

**Key Settings Explained:**

- **data.raw_data_path**: Where raw OHLCV data is stored
- **market.timezone**: Timezone for market data (US: America/New_York, VN: Asia/Ho_Chi_Minh)
- **api.workers**: Number of API workers (recommended: number of CPU cores)
- **dashboard.refresh_interval**: Auto-refresh interval in seconds
- **monitoring.drift_threshold**: Threshold for detecting model drift (0.05 = 5%)

---

### model_config.yaml

Model-specific hyperparameters.

```yaml
# General model settings
general:
  random_seed: 42
  validation_split: 0.15
  test_split: 0.15
  lookback_period: 60      # days

# LSTM configuration
lstm:
  units: 128
  dropout: 0.2
  learning_rate: 0.001
  batch_size: 64
  epochs: 50
  early_stopping:
    enabled: true
    patience: 8
    min_delta: 0.0001
  optimizer: adam
  loss: mse
  metrics:
    - mae
    - mse

# GRU configuration
gru:
  units: 128
  dropout: 0.2
  learning_rate: 0.001
  batch_size: 64
  epochs: 50
  early_stopping:
    enabled: true
    patience: 8
    min_delta: 0.0001
  optimizer: adam
  loss: mse
  metrics:
    - mae
    - mse

# ARIMA configuration
arima:
  max_p: 5
  max_d: 2
  max_q: 5
  seasonal: false
  m: 1
  information_criterion: aic

# Ensemble configuration
ensemble:
  method: weighted_average
  weights:
    arima: 0.33
    lstm: 0.34
    gru: 0.33
  min_confidence: 0.5

# Preprocessing
preprocessing:
  normalization: minmax    # minmax or standard
  feature_scaling: true
  handle_missing: forward_fill
  outlier_detection:
    enabled: true
    method: iqr
    threshold: 3.0
```

**Key Parameters:**

- **lookback_period**: Number of past days used for prediction (60 = 2 months)
- **lstm.units**: Number of LSTM units (higher = more complex, slower)
- **batch_size**: Training batch size (higher = faster but more memory)
- **epochs**: Maximum training iterations
- **early_stopping.patience**: Epochs to wait before stopping if no improvement
- **ensemble.weights**: How to combine model predictions

**Tuning Tips:**

- Increase `units` (128 → 256) for more complex patterns but slower training
- Increase `epochs` if model is still improving
- Decrease `batch_size` if running out of memory
- Adjust `lookback_period` based on your trading timeframe (day trading: 20-30, swing trading: 60-90)

---

### trading_config.yaml

Trading strategy and risk management parameters.

```yaml
# Capital management
capital:
  initial_capital: 100000
  currency: USD
  min_cash_reserve: 0.1    # Keep 10% in cash

# Position sizing
position_sizing:
  method: fixed_percentage  # fixed_percentage, volatility_based, kelly
  max_position_size: 0.1    # 10% of portfolio per position
  max_portfolio_positions: 10
  min_position_value: 1000

# Risk management
risk_management:
  stop_loss: 0.05          # 5%
  take_profit: 0.10        # 10%
  trailing_stop: 0.03      # 3%
  max_daily_loss: 0.02     # 2% of portfolio
  max_drawdown: 0.15       # 15%

# Signal generation
signals:
  buy_threshold: 0.03      # Buy if predicted return >= 3%
  sell_threshold: -0.03    # Sell if predicted return <= -3%
  min_signal_strength: 0.5 # Minimum confidence to act
  confirmation_required: true

# Technical indicators confirmation
technical_confirmation:
  use_rsi: true
  rsi_buy_threshold: 30
  rsi_sell_threshold: 70
  use_macd: true
  use_bollinger: true

# Order execution
orders:
  order_type: market       # market, limit, stop
  time_in_force: day       # day, gtc, ioc
  slippage_tolerance: 0.01 # 1%

# Backtesting
backtesting:
  commission: 0.001        # 0.1% per trade
  slippage: 0.0005        # 0.05%
  margin_requirement: 1.0  # 1.0 = no leverage

# Vietnamese market specific
vietnam_trading:
  max_foreign_ownership: 0.49  # 49%
  price_limit_protection: true
  t_plus_2_settlement: true
```

**Risk Levels Presets:**

**Conservative:**
```yaml
risk_management:
  max_position_size: 0.05  # 5%
  stop_loss: 0.03          # 3%
  take_profit: 0.06        # 6%
signals:
  buy_threshold: 0.05      # 5%
  min_signal_strength: 0.7
```

**Moderate (Default):**
```yaml
risk_management:
  max_position_size: 0.1   # 10%
  stop_loss: 0.05          # 5%
  take_profit: 0.10        # 10%
signals:
  buy_threshold: 0.03      # 3%
  min_signal_strength: 0.5
```

**Aggressive:**
```yaml
risk_management:
  max_position_size: 0.2   # 20%
  stop_loss: 0.07          # 7%
  take_profit: 0.15        # 15%
signals:
  buy_threshold: 0.02      # 2%
  min_signal_strength: 0.3
```

---

### logging_config.yaml

Logging configuration.

```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'

  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: detailed
    filename: logs/error.log
    maxBytes: 10485760
    backupCount: 5

loggers:
  src:
    level: DEBUG
    handlers: [console, file, error_file]
    propagate: false

  uvicorn:
    level: INFO
    handlers: [console, file]
    propagate: false

root:
  level: INFO
  handlers: [console, file, error_file]
```

---

## Environment Variables

### .env File

Create `.env` file in project root:

```env
# Environment
ENVIRONMENT=development  # development, staging, production

# Data paths
DATA_RAW_PATH=data/raw
DATA_PROCESSED_PATH=data/processed
DATA_FEATURES_PATH=data/features

# Model paths
MODELS_PATH=models/saved_models

# API configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=true

# Dashboard
DASHBOARD_PORT=8501

# Database (future)
DATABASE_URL=postgresql://user:password@localhost:5432/trading_db

# External APIs
YAHOO_FINANCE_API_KEY=  # Optional
ALPHA_VANTAGE_API_KEY=  # Optional

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=stock-trading-models

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/app.log

# Security (production)
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here

# Feature flags
ENABLE_SENTIMENT=false
ENABLE_NEWS=false
ENABLE_NOTIFICATIONS=false

# Email notifications (optional)
EMAIL_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
EMAIL_FROM=noreply@tradingsystem.com
EMAIL_TO=alerts@tradingsystem.com

# Slack notifications (optional)
SLACK_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Environment-Specific Configurations

**Development (.env.development):**
```env
ENVIRONMENT=development
API_RELOAD=true
LOG_LEVEL=DEBUG
MLFLOW_ENABLED=true
```

**Production (.env.production):**
```env
ENVIRONMENT=production
API_RELOAD=false
LOG_LEVEL=WARNING
API_WORKERS=8
ENABLE_NOTIFICATIONS=true
```

---

## Model Configuration

### Adjusting Model Architecture

Edit `src/models/lstm_model.py` or `src/models/gru_model.py`:

```python
# Example: Adding more layers
def _build_model(self):
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=self.input_shape),
        Dropout(0.2),
        LSTM(64, return_sequences=True),  # Additional layer
        Dropout(0.2),
        LSTM(32),                         # Additional layer
        Dropout(0.2),
        Dense(1)
    ])
    return model
```

### Custom Technical Indicators

Add to `src/preprocessing/technical_indicators.py`:

```python
def custom_indicator(self, period=14):
    """Your custom indicator logic"""
    # Implementation
    return indicator_values

# Register in compute_all_indicators()
def compute_all_indicators(self, data):
    # ... existing indicators
    data['custom'] = self.custom_indicator()
    return data
```

---

## Trading Configuration

### Position Sizing Methods

**1. Fixed Percentage:**
```yaml
position_sizing:
  method: fixed_percentage
  max_position_size: 0.1  # 10% per position
```

**2. Volatility-Based (ATR):**
```yaml
position_sizing:
  method: volatility_based
  risk_per_trade: 0.02    # 2% risk per trade
  atr_multiplier: 2.0
```

**3. Kelly Criterion:**
```yaml
position_sizing:
  method: kelly
  kelly_fraction: 0.5     # Half Kelly
  max_position_size: 0.2  # Cap at 20%
```

### Stop Loss Strategies

**1. Fixed Percentage:**
```yaml
risk_management:
  stop_loss: 0.05  # 5% below entry
```

**2. ATR-Based:**
```yaml
risk_management:
  stop_loss_method: atr
  atr_multiplier: 2.0
```

**3. Support/Resistance:**
```yaml
risk_management:
  stop_loss_method: technical
  use_support_resistance: true
```

---

## Market-Specific Settings

### US Market

```yaml
market:
  default_market: US
  timezone: America/New_York
  currency: USD
  trading_hours:
    start: "09:30"
    end: "16:00"
  pre_market:
    enabled: false
    start: "04:00"
    end: "09:30"
  after_hours:
    enabled: false
    start: "16:00"
    end: "20:00"
```

### Vietnamese Market

```yaml
vietnam_market:
  timezone: Asia/Ho_Chi_Minh
  currency: VND
  exchanges:
    - HOSE
    - HNX
    - UPCOM
  trading_hours:
    morning:
      start: "09:00"
      end: "11:30"
    afternoon:
      start: "13:00"
      end: "14:45"
  price_limits:
    standard: 0.07      # ±7%
    special: 0.10       # ±10% for some stocks
  settlement: T+2
  min_lot_size: 100     # Shares
  foreign_ownership:
    default: 0.49       # 49%
    banking: 0.30       # 30% for banks
```

---

## Logging Configuration

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages, but application continues
- **ERROR**: Error messages, some functionality may be impaired
- **CRITICAL**: Critical errors, application may not continue

### Custom Logging

```python
import logging
from src.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

---

## Advanced Settings

### Caching

```yaml
cache:
  enabled: true
  backend: redis  # redis, memory
  redis_url: redis://localhost:6379/0
  ttl: 300        # seconds
  max_size: 1000  # items
```

### Database (Future)

```yaml
database:
  engine: postgresql
  host: localhost
  port: 5432
  name: trading_db
  user: postgres
  password: password
  pool_size: 10
  max_overflow: 20
```

### Performance Tuning

```yaml
performance:
  enable_multiprocessing: true
  max_workers: 4
  batch_prediction_size: 100
  cache_predictions: true
  async_data_fetching: true
```

---

## Configuration Best Practices

1. **Never commit secrets**: Use `.env` for sensitive data, add to `.gitignore`
2. **Environment-specific configs**: Use separate configs for dev/staging/prod
3. **Document changes**: Comment why you changed default values
4. **Test configurations**: Validate configs before deploying
5. **Version control**: Track config changes in git
6. **Backup configs**: Keep backups of working configurations

---

## Validation

Validate your configuration:

```bash
python -c "from src.config.settings import get_settings; settings = get_settings(); print('Config valid!')"
```

Or run the validation script:

```bash
python scripts/validate_config.py
```

---

## Troubleshooting

### Configuration Not Loading

1. Check file paths are correct
2. Ensure YAML syntax is valid (use yamllint)
3. Verify environment variables are set
4. Check file permissions

### Invalid Values

1. Review data types (string vs int vs float)
2. Check value ranges (0-1 for percentages, positive for counts)
3. Ensure required fields are present

### Priority Issues

Remember the priority order:
1. Runtime parameters (highest)
2. Environment variables
3. YAML files
4. Default values (lowest)

---

## Example Configurations

### Day Trading Setup

```yaml
# Shorter lookback, tighter stops
model_config:
  general:
    lookback_period: 20

trading_config:
  risk_management:
    stop_loss: 0.02
    take_profit: 0.04
  signals:
    buy_threshold: 0.01
```

### Long-Term Investment

```yaml
# Longer lookback, wider stops
model_config:
  general:
    lookback_period: 90

trading_config:
  risk_management:
    stop_loss: 0.10
    take_profit: 0.25
  signals:
    buy_threshold: 0.05
```

---

For more information, see:
- [User Guide](USER_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
