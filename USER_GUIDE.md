# User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Downloading Data](#downloading-data)
5. [Training Models](#training-models)
6. [Generating Predictions](#generating-predictions)
7. [Backtesting](#backtesting)
8. [Using the API](#using-the-api)
9. [Using the Dashboard](#using-the-dashboard)
10. [Monitoring](#monitoring)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- 8GB+ RAM recommended
- GPU optional (for faster deep learning training)
- Internet connection for data download

### Quick Start
```bash
# Clone and install
git clone <repository-url>
cd stock-trading-decision-support
pip install -r requirements.txt
cp .env.example .env

# Download data
python scripts/download_historical_data.py --symbols AAPL

# Train models
python scripts/train_models.py --symbol AAPL

# Run backtest
python scripts/run_backtest.py --symbol AAPL
```

## Installation

### Option 1: pip install
```bash
pip install -r requirements.txt
```

### Option 2: Development mode
```bash
pip install -e .
```

### Option 3: Docker
```bash
cd docker
docker-compose up -d
```

## Configuration

### Environment Variables (.env)
```bash
# Data sources
YAHOO_FINANCE_API_KEY=optional

# Model settings
MODEL_PATH=./models/saved_models
SCALER_PATH=./models/scalers

# Trading settings
MAX_POSITION_SIZE=0.05  # 5% of portfolio
STOP_LOSS_PERCENT=0.02  # 2%
TAKE_PROFIT_PERCENT=0.05  # 5%

# Risk management
MAX_DRAWDOWN=0.20  # 20%
MAX_DAILY_LOSS=0.05  # 5%

# Logging
LOG_LEVEL=INFO
```

### Configuration Files

#### config/config.yaml
Main application configuration
```yaml
data:
  source: yahoo_finance
  lookback_period: 252  # trading days (1 year)
  update_frequency: daily

models:
  retrain_frequency: monthly
  validation_split: 0.15
  test_split: 0.15
```

#### config/model_config.yaml
Model hyperparameters
```yaml
lstm:
  units: [128, 64, 32]
  dropout: 0.2
  learning_rate: 0.001
  epochs: 100
  batch_size: 32
```

#### config/trading_config.yaml
Trading strategy parameters
```yaml
signals:
  buy_threshold: 0.02  # 2% predicted gain
  sell_threshold: -0.01  # 1% predicted loss

risk_management:
  position_sizing: kelly_criterion
  max_position: 0.05
```

## Downloading Data

### Basic Usage
```bash
python scripts/download_historical_data.py --symbols AAPL,MSFT,GOOGL
```

### Advanced Options
```bash
# Specify date range
python scripts/download_historical_data.py \
  --symbols AAPL \
  --start 2020-01-01 \
  --end 2024-01-01

# Multiple symbols from file
python scripts/download_historical_data.py --symbols-file sp500.txt

# Update existing data
python scripts/download_historical_data.py --symbols AAPL --update
```

### Programmatic Usage
```python
from src.data_ingestion.yahoo_fetcher import YahooDataFetcher

fetcher = YahooDataFetcher()
data = fetcher.fetch_data(
    symbol="AAPL",
    start_date="2020-01-01",
    end_date="2024-01-01"
)
```

## Training Models

### Training All Models
```bash
python scripts/train_models.py --symbol AAPL --models all
```

### Training Specific Models
```bash
# Train only LSTM
python scripts/train_models.py --symbol AAPL --models lstm

# Train LSTM and GRU
python scripts/train_models.py --symbol AAPL --models lstm,gru
```

### Advanced Training Options
```bash
# Custom hyperparameters
python scripts/train_models.py \
  --symbol AAPL \
  --models lstm \
  --epochs 200 \
  --batch-size 64 \
  --learning-rate 0.0005

# With GPU
python scripts/train_models.py --symbol AAPL --models lstm --gpu

# Enable MLflow tracking
python scripts/train_models.py --symbol AAPL --models all --mlflow
```

### Programmatic Training
```python
from src.models.model_trainer import ModelTrainer

trainer = ModelTrainer(symbol="AAPL")

# Train LSTM
lstm_model = trainer.train_lstm(
    epochs=100,
    batch_size=32,
    validation_split=0.15
)

# Train GRU
gru_model = trainer.train_gru()

# Save models
trainer.save_models()
```

## Generating Predictions

### Command Line
```bash
# Get predictions for today
python -c "
from src.models.model_evaluator import ModelEvaluator
evaluator = ModelEvaluator(symbol='AAPL')
predictions = evaluator.predict()
print(predictions)
"
```

### Python API
```python
from src.models.model_evaluator import ModelEvaluator

# Load trained models
evaluator = ModelEvaluator(symbol="AAPL")

# Get ensemble prediction
prediction = evaluator.predict_ensemble(days_ahead=5)

print(f"Predicted prices: {prediction['prices']}")
print(f"Confidence intervals: {prediction['confidence']}")
print(f"Direction: {prediction['direction']}")
```

### Understanding Predictions
```python
{
  'symbol': 'AAPL',
  'current_price': 150.25,
  'predictions': {
    'lstm': {'price': 152.00, 'change': 1.17},
    'gru': {'price': 151.75, 'change': 1.00},
    'ensemble': {'price': 151.88, 'change': 1.09}
  },
  'confidence': {
    'lower': 149.50,
    'upper': 154.00
  },
  'direction': 'up',
  'timestamp': '2024-01-15 16:00:00'
}
```

## Backtesting

### Basic Backtest
```bash
python scripts/run_backtest.py \
  --symbol AAPL \
  --start 2023-01-01 \
  --end 2024-01-01
```

### Advanced Backtesting
```bash
# Custom initial capital and commission
python scripts/run_backtest.py \
  --symbol AAPL \
  --start 2023-01-01 \
  --end 2024-01-01 \
  --initial-capital 100000 \
  --commission 0.001

# Multiple models comparison
python scripts/run_backtest.py \
  --symbol AAPL \
  --start 2023-01-01 \
  --end 2024-01-01 \
  --models lstm,gru,ensemble

# Generate detailed report
python scripts/run_backtest.py \
  --symbol AAPL \
  --start 2023-01-01 \
  --end 2024-01-01 \
  --output-report backtest_results.html
```

### Programmatic Backtesting
```python
from src.backtesting.backtest_engine import BacktestEngine

engine = BacktestEngine(
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2024-01-01",
    initial_capital=100000
)

# Run backtest
results = engine.run()

# Print results
print(f"Total Return: {results['total_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
print(f"Win Rate: {results['win_rate']:.2%}")
```

### Understanding Backtest Results
```python
{
  'total_return': 0.156,  # 15.6%
  'annual_return': 0.145,
  'sharpe_ratio': 1.23,
  'sortino_ratio': 1.45,
  'max_drawdown': 0.128,  # 12.8%
  'win_rate': 0.524,  # 52.4%
  'num_trades': 48,
  'avg_trade_return': 0.0032,
  'profit_factor': 1.45,
  'trades': [...]  # List of all trades
}
```

## Using the API

### Starting the API Server
```bash
# Development mode
uvicorn src.api.main:app --reload --port 8000

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints

#### Get Predictions
```bash
curl http://localhost:8000/api/v1/predictions/AAPL

# Response
{
  "symbol": "AAPL",
  "predictions": {...},
  "signals": "buy",
  "confidence": 0.75
}
```

#### Get Trading Signals
```bash
curl http://localhost:8000/api/v1/signals/AAPL

# Response
{
  "symbol": "AAPL",
  "signal": "buy",
  "strength": 0.85,
  "price_target": 155.00,
  "stop_loss": 145.00,
  "position_size": 0.05
}
```

#### Health Check
```bash
curl http://localhost:8000/api/v1/monitoring/health

# Response
{
  "status": "healthy",
  "models_loaded": true,
  "last_update": "2024-01-15T10:30:00"
}
```

### Python Client
```python
import requests

# Get prediction
response = requests.get("http://localhost:8000/api/v1/predictions/AAPL")
prediction = response.json()

# Get signal
response = requests.get("http://localhost:8000/api/v1/signals/AAPL")
signal = response.json()
```

## Using the Dashboard

### Starting the Dashboard
```bash
streamlit run src/dashboard/app.py
```

Access at: http://localhost:8501

### Dashboard Features

#### Home Page
- Overview of portfolio performance
- Recent signals
- Market summary

#### Signals Page
- Real-time trading signals
- Signal strength visualization
- Historical accuracy

#### Performance Page
- Portfolio value over time
- Performance metrics
- Trade history

#### Monitoring Page
- Model performance tracking
- Drift detection alerts
- System health

## Monitoring

### Model Performance Monitoring
```python
from src.monitoring.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor(symbol="AAPL")

# Check current performance
metrics = monitor.get_current_metrics()

# Check for degradation
if monitor.is_performance_degraded():
    print("Model performance has degraded - consider retraining")
```

### Drift Detection
```python
from src.monitoring.drift_detector import DriftDetector

detector = DriftDetector(symbol="AAPL")

# Check for drift
if detector.detect_drift():
    print("Data drift detected - model retraining recommended")
```

### Audit Logging
All trades and predictions are automatically logged to `logs/audit/`

## Best Practices

### 1. Data Management
- Download data regularly (daily)
- Validate data quality before training
- Keep backups of historical data

### 2. Model Training
- Retrain models monthly or when drift is detected
- Use walk-forward validation
- Monitor training metrics (loss curves)
- Save model versions for comparison

### 3. Risk Management
- Never risk more than 1-2% per trade
- Use stop-losses always
- Diversify across multiple stocks
- Monitor portfolio-level risk

### 4. Signal Validation
- Don't blindly follow signals
- Consider market context
- Check multiple timeframes
- Verify with technical indicators

### 5. Performance Tracking
- Log all predictions and actual outcomes
- Calculate rolling metrics
- Compare against buy-and-hold
- Track execution costs

## Troubleshooting

### Common Issues

#### Data Download Fails
```bash
# Check internet connection
# Verify Yahoo Finance is accessible
# Try different date range
python scripts/download_historical_data.py --symbols AAPL --start 2023-01-01
```

#### Model Training Fails
- Check if data exists in `data/processed/`
- Verify sufficient data (at least 1 year)
- Check GPU availability (if using --gpu)
- Review logs in `logs/application/`

#### Predictions are NaN
- Ensure models are trained
- Check data preprocessing
- Verify scaler files exist
- Review input data quality

#### API Not Responding
```bash
# Check if server is running
ps aux | grep uvicorn

# Check logs
tail -f logs/application/api.log

# Restart server
pkill -f uvicorn
uvicorn src.api.main:app --reload
```

### Getting Help

1. Check logs in `logs/` directory
2. Review error messages carefully
3. Verify configuration files
4. Check GitHub issues
5. Consult documentation

## Performance Tips

### Training Speed
- Use GPU for deep learning models
- Reduce batch size if out of memory
- Use GRU instead of LSTM for faster training
- Enable mixed precision training

### Prediction Speed
- Batch predictions when possible
- Cache frequently requested predictions
- Use lighter models for real-time needs
- Consider model quantization

### Resource Usage
- Clear old log files regularly
- Archive old backtest results
- Monitor disk space in `data/` and `models/`
- Use data compression for storage

## Next Steps

1. Read [RISK_DISCLOSURE.md](RISK_DISCLOSURE.md) carefully
2. Review [ASSUMPTIONS.md](ASSUMPTIONS.md)
3. Start with paper trading
4. Monitor performance closely
5. Adjust parameters based on results
6. Consult [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for customization

---

**Remember**: This system is for educational purposes. Always conduct your own research and consult financial advisors before making investment decisions.
