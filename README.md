# Stock Trading Decision Support System

A comprehensive machine learning-based stock trading decision support system that combines deep learning models (LSTM, GRU) with technical analysis for generating trading signals.

## Overview

This system provides:
- **Multi-model predictions**: LSTM and GRU models for stock price forecasting
- **Technical indicators**: RSI, MACD, Bollinger Bands, and more
- **Risk management**: Position sizing, stop-loss, and portfolio risk controls
- **Backtesting engine**: Historical performance evaluation
- **Real-time monitoring**: Model drift detection and performance tracking
- **REST API**: FastAPI-based service for predictions and signals
- **Interactive dashboard**: Streamlit-based UI for visualization and analysis

## Features

### Data Ingestion
- Yahoo Finance integration for historical OHLCV data
- Data validation and quality checks
- Automated data updates

### Machine Learning Models
- **LSTM**: Deep learning model for sequential data
- **GRU**: Efficient recurrent neural network
- Ensemble prediction combining both models

### Trading Engine
- Signal generation based on model predictions and technical indicators
- Risk management with configurable parameters
- Order management (Buy/Sell/Hold signals)

### Backtesting
- Historical performance simulation
- Comprehensive metrics (Sharpe ratio, max drawdown, win rate, etc.)
- Portfolio tracking and analysis

### Monitoring
- Model drift detection
- Performance degradation alerts
- Audit logging for compliance

## Vietnamese Stock Market Support

🇻🇳 **Hỗ trợ Thị trường Chứng khoán Việt Nam**

The system now fully supports Vietnamese stocks through Yahoo Finance integration.

### Supported Markets

- **HOSE** (Ho Chi Minh Stock Exchange): Use `.VN` suffix
  - Example: `VCB.VN`, `FPT.VN`, `CTG.VN`
- **HNX** (Hanoi Stock Exchange): Use `.HNX` suffix
  - Example: Stocks listed on HNX

### Popular Vietnamese Stocks

#### Banking Sector (Ngân hàng)
- `VCB.VN` - Vietcombank
- `CTG.VN` - VietinBank
- `BID.VN` - BIDV
- `TCB.VN` - Techcombank
- `MBB.VN` - MBBank
- `ACB.VN` - ACB

#### Technology (Công nghệ)
- `FPT.VN` - FPT Corporation

#### Real Estate (Bất động sản)
- `VIC.VN` - Vingroup
- `VHM.VN` - Vinhomes
- `NVL.VN` - Novaland

#### Manufacturing (Sản xuất)
- `HPG.VN` - Hoa Phat Group
- `GAS.VN` - PV Gas

#### Retail (Bán lẻ)
- `MWG.VN` - Mobile World

See `config/vietnam_stocks.yaml` for a comprehensive list of Vietnamese stocks organized by sector.

### Quick Examples for Vietnamese Stocks

```bash
# Test Vietnamese stock data fetching
python scripts/test_vietnamese_stocks.py

# Download Vietnamese stock data
python scripts/download_historical_data.py --symbols VCB.VN,FPT.VN,CTG.VN --period 2y

# Download Vietnamese banking sector
python scripts/download_historical_data.py --symbols VCB.VN,CTG.VN,BID.VN,TCB.VN,MBB.VN --period 5y

# Train model for Vietnamese stocks
python scripts/train_models.py --symbol VCB.VN --models lstm,gru

# Run backtest on Vietnamese stock
python scripts/run_backtest.py --symbol VCB.VN --start 2023-01-01 --end 2024-01-01

# Mix US and Vietnamese stocks
python scripts/download_historical_data.py --symbols AAPL,MSFT,VCB.VN,FPT.VN --period 1y
```

### Vietnamese Market Configuration

The system includes market-specific configurations for Vietnam in `config/config.yaml`:
- **Timezone**: Asia/Ho_Chi_Minh (UTC+7)
- **Currency**: VND (Vietnamese Dong)
- **Trading Hours**:
  - Morning: 09:00 - 11:30
  - Afternoon: 13:00 - 14:45

### Important Notes for Vietnamese Stocks

⚠️ **Lưu ý quan trọng**:
- Vietnamese market has ±7% daily price limits (±10% for some stocks)
- Settlement is T+2 (2 business days)
- Foreign ownership limits typically range from 30-49%
- Yahoo Finance data may have some delay
- Always verify data before live trading

For detailed Vietnamese stock information, see:
- `config/vietnam_stocks.yaml` - Comprehensive stock listings by sector
- `scripts/test_vietnamese_stocks.py` - Test script with examples

## Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd stock-trading-decision-support

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

### Download Historical Data

```bash
python scripts/download_historical_data.py --symbols AAPL,MSFT,GOOGL --start 2020-01-01
```

### Train Models

```bash
python scripts/train_models.py --symbol AAPL --models lstm,gru
```

### Run Backtesting

```bash
python scripts/run_backtest.py --symbol AAPL --start 2023-01-01 --end 2024-01-01
```

### Start API Server

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Launch Dashboard

```bash
streamlit run src/dashboard/app.py
```

## Docker Deployment

```bash
cd docker
docker-compose up -d
```

This will start:
- API service on port 8000
- Dashboard on port 8501
- Training service (on-demand)

## Project Structure

```
stock-trading-decision-support/
├── config/                 # Configuration files
├── data/                   # Data storage
├── models/                 # Trained models
├── logs/                   # Application logs
├── notebooks/              # Jupyter notebooks for analysis
├── scripts/                # Executable scripts
├── src/                    # Source code
│   ├── data_ingestion/    # Data fetching and validation
│   ├── preprocessing/      # Feature engineering
│   ├── models/            # ML models
│   ├── trading_engine/    # Signal generation and risk management
│   ├── backtesting/       # Performance evaluation
│   ├── monitoring/        # Model monitoring
│   ├── api/               # REST API
│   └── dashboard/         # Web UI
└── tests/                 # Unit and integration tests
```

## Documentation

- [System Design](SYSTEM_DESIGN.md) - Architecture and technical details
- [User Guide](USER_GUIDE.md) - How to use the system
- [Developer Guide](DEVELOPER_GUIDE.md) - Development setup and contribution
- [Task Breakdown](TASK_BREAKDOWN.md) - Implementation roadmap
- [Test Report](TEST_REPORT.md) - Testing results
- [Risk Disclosure](RISK_DISCLOSURE.md) - Important risk warnings
- [Assumptions](ASSUMPTIONS.md) - Key assumptions and limitations
- [Thesis Summary](THESIS_SUMMARY.md) - Research background

## API Endpoints

### Predictions
- `GET /api/v1/predictions/{symbol}` - Get price predictions
- `POST /api/v1/predictions/batch` - Batch predictions

### Trading Signals
- `GET /api/v1/signals/{symbol}` - Get trading signals
- `GET /api/v1/signals/portfolio` - Portfolio-level signals

### Monitoring
- `GET /api/v1/monitoring/health` - System health check
- `GET /api/v1/monitoring/metrics` - Model performance metrics
- `GET /api/v1/monitoring/drift` - Model drift detection

## Configuration

Configuration files in `config/`:
- `config.yaml` - General application settings
- `model_config.yaml` - Model hyperparameters
- `trading_config.yaml` - Trading strategy parameters
- `logging_config.yaml` - Logging configuration
- `vietnam_stocks.yaml` - Vietnamese stock market configuration and listings

## Testing

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## Risk Warning

⚠️ **IMPORTANT**: This system is for educational and research purposes only. Trading stocks involves significant risk of loss. Past performance does not guarantee future results. Always:
- Conduct your own research
- Consult with financial advisors
- Only invest what you can afford to lose
- Understand the risks involved

See [RISK_DISCLOSURE.md](RISK_DISCLOSURE.md) for detailed risk information.

## Technology Stack

- **Python 3.8+**: Core language
- **TensorFlow/Keras**: Deep learning models
- **pandas/numpy**: Data manipulation
- **FastAPI**: REST API framework
- **Streamlit**: Dashboard framework
- **MLflow**: Experiment tracking
- **Docker**: Containerization
- **pytest**: Testing framework

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please read [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for development setup and guidelines.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check existing documentation
- Review the user guide

## Acknowledgments

Based on research in machine learning for stock market prediction and quantitative trading strategies.
