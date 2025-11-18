# Backtesting Module

This module provides comprehensive backtesting capabilities for evaluating trained stock prediction models.

## Overview

The backtesting system implements walk-forward validation to assess model performance on historical data, calculating key performance metrics aligned with the thesis requirements.

## Components

### 1. `run_backtest.py` - Main Backtest Script

Comprehensive backtest script that:
- Loads trained models (ARIMA, LSTM, GRU)
- Runs walk-forward validation on historical data
- Calculates performance metrics
- Saves results to JSON format

### 2. `backtest_engine.py` - Backtest Engine

Core backtesting logic for simulating trading strategies.

### 3. `performance_metrics.py` - Performance Metrics Calculator

Calculates trading performance metrics including:
- Sharpe ratio
- Maximum drawdown
- Win rate
- Annual returns

## Usage

### Basic Usage

```bash
# Run backtest for a symbol (default period: 1 year)
python -m src.backtesting.run_backtest --symbol AAPL

# Run backtest with specific date range
python -m src.backtesting.run_backtest --symbol AAPL --start-date 2023-01-01 --end-date 2023-12-31

# Run backtest with custom capital
python -m src.backtesting.run_backtest --symbol GOOGL --initial-capital 50000

# Run backtest with different period
python -m src.backtesting.run_backtest --symbol MSFT --period 2y
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--symbol` | Stock symbol to backtest | AAPL |
| `--start-date` | Start date (YYYY-MM-DD) | None |
| `--end-date` | End date (YYYY-MM-DD) | None |
| `--period` | Period if dates not specified (1y, 2y, 5y) | 1y |
| `--initial-capital` | Initial portfolio capital | 100000.0 |
| `--transaction-cost` | Transaction cost as percentage | 0.001 (0.1%) |
| `--output-dir` | Output directory for results | results |

### Python API Usage

```python
from src.backtesting.run_backtest import BacktestRunner

# Create backtest runner
runner = BacktestRunner(
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2023-12-31",
    initial_capital=100000.0,
    transaction_cost=0.001,  # 0.1%
    slippage=0.0005,  # 0.05%
)

# Load trained models
models = runner.load_models()

# Load historical data
data = runner.load_data()

# Run backtest
results = runner.run_backtest(models, data)

# Save results
runner.save_results(results, output_dir="results")

# Print summary
runner.print_summary(results)
```

## Prerequisites

Before running backtests, you must have:

1. **Trained Models**: Models should be saved in `models/saved_models/` with naming convention:
   - `{SYMBOL}_arima.pkl` - ARIMA model
   - `{SYMBOL}_lstm.h5` - LSTM model
   - `{SYMBOL}_gru.h5` - GRU model

2. **Scalers** (optional): Saved in `models/scalers/`:
   - `{SYMBOL}_scaler.pkl` - Data scaler for normalization

## Output

### Results Files

Backtest results are saved in two formats:

1. **Timestamped File**: `results/backtest_{SYMBOL}_{TIMESTAMP}.json`
   - Unique file for each backtest run
   - Preserves historical backtest results

2. **Summary File**: `results/backtest_summary.json`
   - Latest backtest results
   - Overwritten with each run

### Results Structure

```json
{
  "symbol": "AAPL",
  "backtest_period": {
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "total_days": 252,
    "trading_years": 1.0
  },
  "portfolio": {
    "initial_capital": 100000.0,
    "final_capital": 115000.0,
    "cash": 50000.0,
    "position_shares": 100
  },
  "returns": {
    "total_return": 15.0,
    "annual_return": 15.0,
    "total_pnl": 15000.0
  },
  "risk_metrics": {
    "sharpe_ratio": 1.2,
    "sortino_ratio": 1.5,
    "calmar_ratio": 0.8,
    "max_drawdown": 12.5,
    "volatility": 18.2
  },
  "trading": {
    "num_trades": 45,
    "winning_trades": 28,
    "losing_trades": 17,
    "win_rate": 62.22,
    "avg_pnl_per_trade": 333.33
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## Performance Metrics

### Return Metrics
- **Total Return**: Total percentage return over the backtest period
- **Annual Return (CAGR)**: Compound annual growth rate
- **Total P&L**: Total profit/loss in dollars

### Risk Metrics
- **Sharpe Ratio**: Risk-adjusted return (using 4% risk-free rate)
- **Sortino Ratio**: Return/downside deviation (penalizes only downside volatility)
- **Calmar Ratio**: Annual return / maximum drawdown
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Volatility**: Annualized standard deviation of returns

### Trading Metrics
- **Number of Trades**: Total buy/sell transactions
- **Winning Trades**: Number of profitable trades
- **Losing Trades**: Number of losing trades
- **Win Rate**: Percentage of winning trades
- **Average P&L per Trade**: Average profit/loss per trade

## Backtesting Methodology

### Walk-Forward Validation

The backtest uses walk-forward validation:

1. **For each day in the test period**:
   - Use historical data to generate prediction
   - Generate trading signal based on prediction
   - Execute trade (if signal is BUY/SELL)
   - Update portfolio value
   - Calculate returns

2. **Transaction Costs**:
   - Transaction cost: 0.1% per trade (configurable)
   - Slippage: 0.05% per trade (configurable)
   - Costs applied to both buy and sell orders

3. **Position Sizing**:
   - Integrated with Risk Manager
   - Considers signal strength
   - Respects capital constraints

## Alignment with Thesis

The backtest script implements metrics as specified in THESIS_SUMMARY.md:

- **Annual Return**: CAGR calculation
- **Maximum Drawdown**: Peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted returns (252 trading days per year)
- **Win Rate**: Percentage of profitable trades

Additional metrics (Sortino, Calmar) provide enhanced risk analysis.

## Testing

### Unit Tests

```bash
# Run unit tests
pytest tests/unit/test_run_backtest.py -v

# Run with coverage
pytest tests/unit/test_run_backtest.py --cov=src.backtesting --cov-report=html
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/test_backtest_integration.py -v
```

## Examples

### Example 1: Quick Backtest

```bash
python -m src.backtesting.run_backtest --symbol AAPL
```

### Example 2: Multi-Year Backtest

```bash
python -m src.backtesting.run_backtest \
  --symbol GOOGL \
  --start-date 2020-01-01 \
  --end-date 2023-12-31 \
  --initial-capital 200000
```

### Example 3: Low Capital Backtest

```bash
python -m src.backtesting.run_backtest \
  --symbol TSLA \
  --period 1y \
  --initial-capital 10000 \
  --transaction-cost 0.002  # Higher cost for small account
```

## Troubleshooting

### Common Issues

1. **"No trained models found"**
   - Ensure models are trained and saved in `models/saved_models/`
   - Check model file naming convention

2. **"Failed to load scaler"**
   - Warning only - backtest will continue with fresh normalization
   - To fix: Save scaler during model training

3. **"No data found for symbol"**
   - Check internet connection
   - Verify symbol is valid
   - Try different date range

4. **Low number of trades**
   - Check signal thresholds in `signal_generator.py`
   - Verify model predictions are reasonable
   - Review transaction costs (high costs = fewer trades)

## Advanced Usage

### Custom Signal Thresholds

Modify signal generation thresholds in the code:

```python
runner = BacktestRunner(...)
runner.signal_generator.buy_threshold = 0.05  # 5% predicted gain
runner.signal_generator.sell_threshold = -0.05  # 5% predicted loss
```

### Custom Risk Management

```python
runner = BacktestRunner(...)
runner.risk_manager.max_position_size = 0.20  # 20% of capital
runner.risk_manager.stop_loss_percent = 0.03  # 3% stop loss
```

## References

- **SYSTEM_DESIGN.md**: System architecture and component design
- **THESIS_SUMMARY.md**: Research methodology and metrics
- **USER_GUIDE.md**: User documentation
- **DEVELOPER_GUIDE.md**: Development setup

## License

See project LICENSE file.
