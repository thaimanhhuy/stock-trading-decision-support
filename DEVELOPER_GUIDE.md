# Developer Guide

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool (venv, conda)
- IDE (VS Code, PyCharm recommended)

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd stock-trading-decision-support

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks (if available)
pre-commit install
```

### Environment Configuration
```bash
cp .env.example .env
# Edit .env with your settings
```

## Project Structure

```
src/
├── config/              # Configuration management
├── data_ingestion/      # Data fetching and validation
├── preprocessing/       # Feature engineering
├── models/              # ML models (ARIMA, LSTM, GRU)
├── trading_engine/      # Signal generation and risk management
├── backtesting/         # Performance evaluation
├── monitoring/          # Model monitoring and drift detection
├── api/                 # FastAPI REST API
├── dashboard/           # Streamlit dashboard
└── utils/               # Utilities
```

## Coding Standards

### Python Style Guide
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings (Google style)

### Example
```python
from typing import List, Dict, Optional
import numpy as np

def calculate_returns(prices: np.ndarray, periods: int = 1) -> np.ndarray:
    """Calculate returns over specified periods.

    Args:
        prices: Array of prices
        periods: Number of periods for return calculation

    Returns:
        Array of returns

    Raises:
        ValueError: If prices array is empty
    """
    if len(prices) == 0:
        raise ValueError("Prices array cannot be empty")

    returns = np.diff(prices, n=periods) / prices[:-periods]
    return returns
```

### Import Organization
```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import numpy as np
import pandas as pd
import tensorflow as tf

# Local
from src.utils.logger import get_logger
from src.config.settings import Settings
```

## Adding New Models

### Step 1: Create Model Class
```python
# src/models/my_model.py
from src.models.base_model import BaseModel
import numpy as np

class MyModel(BaseModel):
    """Description of your model."""

    def __init__(self, symbol: str, **kwargs):
        super().__init__(symbol)
        self.param1 = kwargs.get('param1', default_value)

    def train(self, data: np.ndarray, **kwargs) -> None:
        """Train the model."""
        # Implementation
        pass

    def predict(self, data: np.ndarray, steps: int = 1) -> np.ndarray:
        """Generate predictions."""
        # Implementation
        pass

    def evaluate(self, data: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance."""
        # Implementation
        pass
```

### Step 2: Add to Model Trainer
```python
# src/models/model_trainer.py
from src.models.my_model import MyModel

class ModelTrainer:
    def train_my_model(self, **kwargs):
        model = MyModel(self.symbol, **kwargs)
        model.train(self.train_data)
        return model
```

### Step 3: Add Configuration
```yaml
# config/model_config.yaml
my_model:
  param1: value1
  param2: value2
```

### Step 4: Add Tests
```python
# tests/unit/test_my_model.py
import pytest
from src.models.my_model import MyModel

def test_my_model_training():
    model = MyModel("AAPL")
    # Test implementation
    assert model is not None
```

## Adding New Features

### Technical Indicators
```python
# src/preprocessing/technical_indicators.py

def calculate_my_indicator(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate custom technical indicator.

    Args:
        data: DataFrame with OHLCV data
        period: Lookback period

    Returns:
        Series with indicator values
    """
    # Implementation
    result = data['Close'].rolling(window=period).mean()
    return result
```

### Add to Feature Engineering Pipeline
```python
# src/preprocessing/data_processor.py

def engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
    # Existing features
    data['RSI'] = self.indicators.calculate_rsi(data)

    # Add new feature
    data['MyIndicator'] = self.indicators.calculate_my_indicator(data)

    return data
```

## Testing

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_models.py

# With coverage
pytest --cov=src --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Writing Tests

#### Unit Test Example
```python
import pytest
import numpy as np
from src.preprocessing.technical_indicators import TechnicalIndicators

class TestTechnicalIndicators:
    @pytest.fixture
    def sample_data(self):
        return pd.DataFrame({
            'Close': [100, 102, 101, 103, 105, 104, 106]
        })

    def test_rsi_calculation(self, sample_data):
        indicators = TechnicalIndicators()
        rsi = indicators.calculate_rsi(sample_data, period=3)

        assert len(rsi) == len(sample_data)
        assert rsi.iloc[-1] >= 0 and rsi.iloc[-1] <= 100

    def test_rsi_with_invalid_period(self, sample_data):
        indicators = TechnicalIndicators()
        with pytest.raises(ValueError):
            indicators.calculate_rsi(sample_data, period=-1)
```

#### Integration Test Example
```python
from src.data_ingestion.yahoo_fetcher import YahooDataFetcher
from src.preprocessing.data_processor import DataProcessor

def test_data_pipeline():
    # Fetch data
    fetcher = YahooDataFetcher()
    data = fetcher.fetch_data("AAPL", start_date="2023-01-01", end_date="2023-12-31")

    # Process data
    processor = DataProcessor()
    processed = processor.process(data)

    # Assertions
    assert len(processed) > 0
    assert 'RSI' in processed.columns
    assert processed['RSI'].notna().any()
```

## API Development

### Adding New Endpoint
```python
# src/api/routes/my_route.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class MyRequest(BaseModel):
    symbol: str
    parameter: int

class MyResponse(BaseModel):
    result: float

@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest) -> MyResponse:
    """Endpoint description."""
    try:
        # Implementation
        result = perform_calculation(request.symbol, request.parameter)
        return MyResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Register Router
```python
# src/api/main.py
from src.api.routes.my_route import router as my_router

app.include_router(my_router, prefix="/api/v1", tags=["my_feature"])
```

### Testing API
```bash
# Start server
uvicorn src.api.main:app --reload

# Test with curl
curl -X POST http://localhost:8000/api/v1/my-endpoint \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "parameter": 10}'

# Or use pytest
pytest tests/integration/test_api.py
```

## Dashboard Development

### Adding New Page
```python
# src/dashboard/pages/my_page.py
import streamlit as st
import plotly.graph_objects as go

def render():
    """Render the page."""
    st.title("My Feature Page")

    # User inputs
    symbol = st.text_input("Symbol", value="AAPL")

    # Fetch data
    data = get_data(symbol)

    # Create visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Price'))
    st.plotly_chart(fig)
```

### Register Page
```python
# src/dashboard/app.py
from src.dashboard.pages import my_page

page = st.sidebar.selectbox("Page", ["Home", "My Feature"])

if page == "My Feature":
    my_page.render()
```

## Logging

### Setup Logger
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception occurred")  # Includes traceback
```

### Custom Logger Configuration
```yaml
# config/logging_config.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: default
    level: INFO
  file:
    class: logging.FileHandler
    filename: logs/application/app.log
    formatter: default
    level: DEBUG
loggers:
  src:
    level: DEBUG
    handlers: [console, file]
```

## Performance Profiling

### Using cProfile
```bash
python -m cProfile -o profile.stats scripts/train_models.py
python -m pstats profile.stats
# In pstats shell:
# sort cumulative
# stats 10
```

### Using line_profiler
```python
# Install: pip install line_profiler
@profile
def my_function():
    # Code to profile
    pass

# Run: kernprof -l -v my_script.py
```

## Debugging

### Using pdb
```python
import pdb

def my_function():
    x = 10
    pdb.set_trace()  # Breakpoint
    y = x * 2
    return y
```

### VS Code Debug Configuration
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Train Models",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/scripts/train_models.py",
            "args": ["--symbol", "AAPL"],
            "console": "integratedTerminal"
        }
    ]
}
```

## CI/CD (Future)

### GitHub Actions Example
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src tests/
```

## Documentation

### Generating API Docs
```bash
# FastAPI automatically generates docs
# Visit: http://localhost:8000/docs
```

### Code Documentation
Use Google-style docstrings:
```python
def function(param1: int, param2: str = "default") -> bool:
    """Brief description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is negative

    Example:
        >>> function(10, "test")
        True
    """
    pass
```

## Contributing

### Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes
4. Add tests
5. Run tests: `pytest`
6. Commit: `git commit -m "Add my feature"`
7. Push: `git push origin feature/my-feature`
8. Create Pull Request

### Commit Message Convention
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Example:
```
feat(models): add transformer model

Implement transformer-based model for stock prediction.
Uses multi-head attention mechanism.

Closes #123
```

## Common Tasks

### Adding a New Symbol
```python
# Download data
python scripts/download_historical_data.py --symbols TSLA

# Train models
python scripts/train_models.py --symbol TSLA --models all

# Run backtest
python scripts/run_backtest.py --symbol TSLA
```

### Retraining Models
```bash
# Retrain all models for a symbol
python scripts/train_models.py --symbol AAPL --models all --retrain

# Retrain only LSTM
python scripts/train_models.py --symbol AAPL --models lstm --retrain
```

### Updating Dependencies
```bash
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure package is installed in development mode
pip install -e .

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

#### TensorFlow GPU Issues
```bash
# Check GPU availability
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Install CUDA-compatible TensorFlow
pip install tensorflow-gpu
```

#### Memory Issues
- Reduce batch size
- Use data generators instead of loading all data
- Clear session between model trainings
- Use mixed precision training

## Resources

### Documentation
- [TensorFlow Guide](https://www.tensorflow.org/guide)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### Books
- "Python for Finance" by Yves Hilpisch
- "Machine Learning for Algorithmic Trading" by Stefan Jansen
- "Advances in Financial Machine Learning" by Marcos López de Prado

### Papers
- LSTM for Time Series: Hochreiter & Schmidhuber (1997)
- Financial Time Series Forecasting: Recent advances

---

For questions or issues, please open a GitHub issue or contact the maintainers.
