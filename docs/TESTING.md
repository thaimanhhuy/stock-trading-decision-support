# Testing Documentation

This document describes the test suite for the Stock Trading Decision Support System.

## Overview

The test suite has been updated to match the refactored codebase, including:
- New 3-layer LSTM/GRU model architectures
- Modular API route structure
- Enhanced fixtures and test utilities

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── unit/                            # Unit tests
│   ├── test_lstm_model.py          # LSTM model tests (NEW)
│   ├── test_gru_model.py           # GRU model tests (NEW)
│   ├── test_api_routes.py          # API route tests (NEW)
│   ├── test_base_model.py          # Base model tests
│   ├── test_data_processor.py      # Data processor tests
│   ├── test_technical_indicators.py# Technical indicators tests
│   ├── test_signal_generator.py    # Signal generator tests
│   └── ...                         # Other existing tests
└── integration/                     # Integration tests
    └── test_backtest_integration.py
```

## New Test Files

### 1. test_lstm_model.py

Tests for the refactored 3-layer LSTM model.

**Test Coverage:**
- Model initialization and architecture
- 3-layer structure validation (128→64→32)
- Training with/without validation data
- Default configuration parameters (batch_size=32, epochs=100, patience=15)
- Prediction functionality
- Model saving and loading
- Early stopping callbacks
- Evaluation metrics
- Error handling without TensorFlow
- Different sequence lengths and feature counts

**Key Test Classes:**
- `TestLSTMModel` - Main test suite for LSTM functionality
- `TestLSTMModelWithoutTensorFlow` - Tests for graceful degradation

**Example Usage:**
```bash
# Run LSTM tests only
pytest tests/unit/test_lstm_model.py -v

# Run with coverage
pytest tests/unit/test_lstm_model.py --cov=src/models/lstm_model

# Skip if TensorFlow not available
pytest tests/unit/test_lstm_model.py -v -m "not tensorflow"
```

### 2. test_gru_model.py

Tests for the refactored 3-layer GRU model.

**Test Coverage:**
- Model initialization and architecture
- 3-layer structure validation (128→64→32)
- Training with/without validation data
- Default configuration parameters
- Prediction functionality
- Model saving and loading
- Early stopping callbacks
- Evaluation metrics
- Error handling without TensorFlow
- GRU vs LSTM architecture comparison

**Key Test Classes:**
- `TestGRUModel` - Main test suite for GRU functionality
- `TestGRUModelWithoutTensorFlow` - Tests for graceful degradation

**Example Usage:**
```bash
# Run GRU tests only
pytest tests/unit/test_gru_model.py -v

# Run with coverage
pytest tests/unit/test_gru_model.py --cov=src/models/gru_model
```

### 3. test_api_routes.py

Comprehensive tests for all modular API routes.

**Test Coverage:**

#### Health Routes
- Root endpoint (`/`)
- Health check endpoint (`/health`)

#### Prediction Routes (`src/api/routes/predictions.py`)
- Valid US stock symbols (AAPL, MSFT, etc.)
- Valid Vietnamese symbols (VCB.VN, FPT.VN, etc.)
- Symbol case handling (lowercase → uppercase)
- Invalid symbol format validation
- Empty and malformed symbols
- Signal generation endpoints
- Symbol validation function testing

#### Training Routes (`src/api/routes/training.py`)
- Single model training
- Batch training multiple symbols
- Training history retrieval
- Training statistics
- Different model configurations

#### Monitoring Routes (`src/api/routes/monitoring.py`)
- System health monitoring
- Market drop detection (US & Vietnam)
- Market event history
- Event filtering by market

#### Scheduler Routes (`src/api/routes/scheduler.py`)
- Scheduler status checking
- Start/stop scheduler
- Manual retraining triggers
- Market check triggers

**Key Test Classes:**
- `TestHealthRoutes` - Health check endpoints
- `TestPredictionRoutes` - Prediction and signal endpoints
- `TestTrainingRoutes` - Model training endpoints
- `TestMonitoringRoutes` - Monitoring endpoints
- `TestSchedulerRoutes` - Scheduler control endpoints
- `TestSymbolValidation` - Symbol validation logic

**Example Usage:**
```bash
# Run all API tests
pytest tests/unit/test_api_routes.py -v

# Run specific test class
pytest tests/unit/test_api_routes.py::TestPredictionRoutes -v

# Run with coverage
pytest tests/unit/test_api_routes.py --cov=src/api
```

## Updated Fixtures (conftest.py)

### New Fixtures

1. **`sample_training_data`**
   - Returns: `(X_train, y_train, X_test, y_test)`
   - Shape: (200, 60, 5) for training, (50, 60, 5) for testing
   - Use: LSTM/GRU model testing

2. **`sample_sequences`**
   - Returns: `(X, y)` sequences
   - Shape: (100, 60, 5)
   - Use: Sequence generation testing

3. **`sample_us_symbols`**
   - Returns: List of US stock symbols
   - Values: ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

4. **`sample_vn_symbols`**
   - Returns: List of Vietnamese stock symbols
   - Values: ["VCB.VN", "FPT.VN", "CTG.VN", "BID.VN", "MBB.VN"]

5. **`mock_model_config`**
   - Returns: Model configuration dict
   - Contains: LSTM and GRU default parameters

### Existing Fixtures

1. **`sample_ohlcv_data`** - OHLCV DataFrame for testing
2. **`sample_symbol`** - Default "TEST" symbol

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Files
```bash
# Model tests
pytest tests/unit/test_lstm_model.py -v
pytest tests/unit/test_gru_model.py -v

# API tests
pytest tests/unit/test_api_routes.py -v

# Existing tests
pytest tests/unit/test_data_processor.py -v
```

### Run with Coverage
```bash
# Full coverage report
pytest tests/ --cov=src --cov-report=html

# Coverage for specific modules
pytest tests/unit/test_lstm_model.py --cov=src/models/lstm_model
pytest tests/unit/test_api_routes.py --cov=src/api
```

### Run with Markers
```bash
# Skip TensorFlow-dependent tests
pytest tests/ -m "not tensorflow"

# Run only fast tests
pytest tests/ -m "fast"
```

### Run with Verbose Output
```bash
pytest tests/ -v --tb=short
```

## Test Dependencies

Tests require the following packages (from `requirements.txt`):
- `pytest>=7.4.0`
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-mock>=3.11.0` - Mocking utilities

Install test dependencies:
```bash
pip install -r requirements.txt
```

Or install only test dependencies:
```bash
pip install pytest pytest-cov pytest-mock
```

## Test Categories

### Unit Tests

Test individual components in isolation:
- Model classes (LSTM, GRU, BaseModel)
- Data processors
- Technical indicators
- Signal generators
- API routes (with mocked services)

### Integration Tests

Test component interactions:
- End-to-end backtesting
- Full prediction pipeline
- API + service integration

## Writing New Tests

### Model Tests Template

```python
import pytest
import numpy as np
from src.models.your_model import YourModel

class TestYourModel:
    @pytest.fixture
    def model(self):
        return YourModel(symbol="TEST")

    @pytest.fixture
    def sample_data(self):
        X = np.random.randn(100, 60, 5)
        y = np.random.randn(100)
        return X, y

    def test_initialization(self, model):
        assert model.symbol == "TEST"
        assert model.is_trained is False

    def test_training(self, model, sample_data):
        X, y = sample_data
        model.train(X, y)
        assert model.is_trained is True
```

### API Tests Template

```python
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

class TestYourRoute:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_endpoint(self, client):
        response = client.get("/your/endpoint")
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data
```

## Coverage Goals

| Module | Target Coverage | Status |
|--------|----------------|--------|
| Models (LSTM/GRU) | 90% | ✅ Covered |
| API Routes | 85% | ✅ Covered |
| Data Processing | 80% | ✅ Existing |
| Technical Indicators | 80% | ✅ Existing |
| Signal Generation | 75% | ✅ Existing |

## CI/CD Integration

Tests should be run automatically on:
- Pull requests
- Commits to main branch
- Nightly builds

### GitHub Actions Example

```yaml
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
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### TensorFlow Not Available

If TensorFlow is not installed:
- Model tests will be skipped automatically
- Use `@pytest.mark.skipif(not TENSORFLOW_AVAILABLE)`

### Import Errors

Ensure the project root is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

Or use pytest's import mode:
```bash
pytest tests/ --import-mode=importlib
```

### Slow Tests

Use pytest-xdist for parallel execution:
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

## Best Practices

1. **Isolation**: Tests should not depend on external services or file systems
2. **Mocking**: Use `unittest.mock` or `pytest-mock` for external dependencies
3. **Fixtures**: Use fixtures for common test data and setup
4. **Descriptive Names**: Test names should clearly describe what they test
5. **Documentation**: Add docstrings to test classes and complex tests
6. **Fast Tests**: Keep unit tests fast (< 1 second each)
7. **Coverage**: Aim for high coverage but prioritize critical paths

## Migration Notes

### From Old Tests

If you have existing tests for the old model architecture:
1. Update expected layer counts (1 → 3 layers)
2. Update default parameters (batch_size: 64→32, epochs: 50→100)
3. Update import paths if routes were reorganized

### API Route Changes

Old API structure:
```python
from src.api.main import app
```

New modular structure:
```python
from src.api.main import app  # Still the main app
# Routes are now in separate modules but registered with main app
```

## Future Improvements

- [ ] Add performance benchmarking tests
- [ ] Add stress tests for API endpoints
- [ ] Add integration tests for full trading pipeline
- [ ] Add property-based testing with Hypothesis
- [ ] Add mutation testing with mutmut
- [ ] Add load testing with Locust

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [TensorFlow Testing Best Practices](https://www.tensorflow.org/guide/test)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
