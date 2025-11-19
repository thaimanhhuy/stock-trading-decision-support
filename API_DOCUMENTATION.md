# API Documentation

## Overview

The Stock Trading Decision Support System provides a RESTful API built with FastAPI. The API enables programmatic access to predictions, trading signals, and system monitoring capabilities.

**Base URL**: `http://localhost:8000`

**API Version**: v1

## Authentication

Currently, the API does not require authentication. For production deployments, implement API key authentication or OAuth 2.0.

## Rate Limiting

No rate limiting is currently enforced. Consider implementing rate limiting for production use.

## Response Format

All API responses follow this standard format:

```json
{
  "status": "success" | "error",
  "data": { ... },
  "message": "Optional message",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Handling

Error responses include:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

- `400` - Bad Request: Invalid parameters
- `404` - Not Found: Resource not found
- `422` - Unprocessable Entity: Validation error
- `500` - Internal Server Error: Server error

---

## Endpoints

### Root & Health Check

#### GET `/`

Returns API status and basic information.

**Response:**
```json
{
  "message": "Stock Trading Decision Support API",
  "version": "0.1.0",
  "status": "running"
}
```

#### GET `/health`

Health check endpoint for monitoring and load balancers.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": "ok",
    "models": "ok",
    "api": "ok"
  }
}
```

---

## Prediction Endpoints

### GET `/api/v1/predictions/{symbol}`

Get stock price prediction for a single symbol.

**Parameters:**

| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `symbol` | string | path | Yes | Stock ticker symbol (e.g., AAPL, VCB.VN) |
| `days_ahead` | integer | query | No | Number of days to predict (default: 1, max: 30) |
| `model` | string | query | No | Model to use: "lstm", "gru", "ensemble" (default: "ensemble") |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/predictions/AAPL?days_ahead=5&model=ensemble"
```

**Response:**
```json
{
  "symbol": "AAPL",
  "current_price": 178.50,
  "predicted_price": 182.30,
  "predicted_return": 2.13,
  "confidence": 0.75,
  "direction": "up",
  "model_used": "ensemble",
  "predictions": [
    {
      "date": "2024-01-16",
      "predicted_price": 179.20,
      "confidence": 0.82
    },
    {
      "date": "2024-01-17",
      "predicted_price": 180.10,
      "confidence": 0.78
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Field Descriptions:**

- `symbol`: Stock ticker symbol
- `current_price`: Latest closing price
- `predicted_price`: Predicted price for next day (or specified days ahead)
- `predicted_return`: Expected return percentage
- `confidence`: Model confidence score (0-1)
- `direction`: Price direction ("up", "down", "neutral")
- `model_used`: Model used for prediction
- `predictions`: Array of multi-day predictions (if days_ahead > 1)
- `timestamp`: Prediction timestamp

---

### POST `/api/v1/predictions/batch`

Get predictions for multiple symbols in one request.

**Request Body:**
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL", "VCB.VN"],
  "days_ahead": 1,
  "model": "ensemble"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbols` | array[string] | Yes | List of stock symbols (max: 50) |
| `days_ahead` | integer | No | Days to predict (default: 1, max: 30) |
| `model` | string | No | Model to use (default: "ensemble") |

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/predictions/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT", "VCB.VN"],
    "days_ahead": 1,
    "model": "ensemble"
  }'
```

**Response:**
```json
{
  "predictions": [
    {
      "symbol": "AAPL",
      "current_price": 178.50,
      "predicted_price": 180.20,
      "predicted_return": 0.95,
      "confidence": 0.75,
      "direction": "up"
    },
    {
      "symbol": "MSFT",
      "current_price": 385.30,
      "predicted_price": 387.80,
      "predicted_return": 0.65,
      "confidence": 0.72,
      "direction": "up"
    },
    {
      "symbol": "VCB.VN",
      "current_price": 92500,
      "predicted_price": 93800,
      "predicted_return": 1.41,
      "confidence": 0.68,
      "direction": "up"
    }
  ],
  "model_used": "ensemble",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Trading Signal Endpoints

### GET `/api/v1/signals/{symbol}`

Get trading signal for a specific symbol.

**Parameters:**

| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `symbol` | string | path | Yes | Stock ticker symbol |
| `risk_level` | string | query | No | Risk level: "conservative", "moderate", "aggressive" (default: "moderate") |
| `capital` | float | query | No | Available capital for position sizing |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/signals/AAPL?risk_level=moderate&capital=10000"
```

**Response:**
```json
{
  "symbol": "AAPL",
  "signal": "buy",
  "strength": 0.78,
  "current_price": 178.50,
  "target_price": 185.20,
  "stop_loss": 169.58,
  "take_profit": 196.35,
  "position_size": {
    "shares": 55,
    "value": 9817.50,
    "percentage": 98.18
  },
  "risk_reward_ratio": 2.5,
  "confidence": 0.75,
  "technical_indicators": {
    "rsi": 62.5,
    "macd": "bullish",
    "bollinger_position": "middle",
    "trend": "uptrend"
  },
  "reasoning": [
    "Strong upward momentum detected",
    "RSI in bullish territory",
    "MACD bullish crossover",
    "Price above 50-day MA"
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Signal Types:**

- `buy`: Strong buy signal (predicted return ≥ 3%)
- `sell`: Strong sell signal (predicted return ≤ -3%)
- `hold`: Hold current position (return between -3% and 3%)

**Strength Values:**

- `0.0 - 0.3`: Weak signal
- `0.3 - 0.7`: Moderate signal
- `0.7 - 1.0`: Strong signal

---

### GET `/api/v1/signals/portfolio`

Get trading signals for an entire portfolio.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbols` | string | No | Comma-separated symbols (e.g., "AAPL,MSFT,GOOGL") |
| `risk_level` | string | No | Risk level for position sizing |
| `total_capital` | float | No | Total portfolio capital |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/signals/portfolio?symbols=AAPL,MSFT,GOOGL&total_capital=50000&risk_level=moderate"
```

**Response:**
```json
{
  "portfolio_signals": [
    {
      "symbol": "AAPL",
      "signal": "buy",
      "strength": 0.78,
      "allocation": 0.35,
      "position_size": {
        "shares": 97,
        "value": 17314.50
      }
    },
    {
      "symbol": "MSFT",
      "signal": "hold",
      "strength": 0.45,
      "allocation": 0.30,
      "current_value": 15000.00
    },
    {
      "symbol": "GOOGL",
      "signal": "sell",
      "strength": 0.62,
      "allocation": 0.35,
      "position_size": {
        "shares": -125,
        "value": -17500.00
      }
    }
  ],
  "portfolio_summary": {
    "total_capital": 50000,
    "invested": 32314.50,
    "cash": 17685.50,
    "recommended_actions": {
      "buy": 1,
      "sell": 1,
      "hold": 1
    }
  },
  "risk_metrics": {
    "portfolio_risk": 0.15,
    "sharpe_ratio": 1.45,
    "max_drawdown": 0.08
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Monitoring Endpoints

### GET `/api/v1/monitoring/health`

Get detailed system health status.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "api": {
      "status": "up",
      "uptime": 86400,
      "requests_per_minute": 45
    },
    "models": {
      "arima": {
        "status": "loaded",
        "last_trained": "2024-01-10T08:00:00Z",
        "accuracy": 0.85
      },
      "lstm": {
        "status": "loaded",
        "last_trained": "2024-01-10T08:00:00Z",
        "accuracy": 0.87
      },
      "gru": {
        "status": "loaded",
        "last_trained": "2024-01-10T08:00:00Z",
        "accuracy": 0.86
      }
    },
    "data": {
      "status": "ok",
      "last_update": "2024-01-15T09:00:00Z",
      "symbols_tracked": 150
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### GET `/api/v1/monitoring/metrics`

Get model performance metrics.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | No | Specific model ("lstm", "gru", "ensemble") |
| `period` | string | No | Time period: "1d", "7d", "30d", "90d" (default: "30d") |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/metrics?model=ensemble&period=30d"
```

**Response:**
```json
{
  "model": "ensemble",
  "period": "30d",
  "metrics": {
    "accuracy": 0.78,
    "mae": 2.45,
    "rmse": 3.21,
    "mape": 1.85,
    "directional_accuracy": 0.72
  },
  "performance_trend": {
    "improving": true,
    "change_percentage": 5.3
  },
  "predictions_made": 1250,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### GET `/api/v1/monitoring/drift`

Get model drift detection status.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | No | Model to check for drift |
| `threshold` | float | No | Drift threshold (default: 0.05) |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/drift?model=lstm"
```

**Response:**
```json
{
  "model": "lstm",
  "drift_detected": false,
  "drift_score": 0.023,
  "threshold": 0.05,
  "last_check": "2024-01-15T10:00:00Z",
  "recommendation": "No action required",
  "details": {
    "feature_drift": {
      "price": 0.015,
      "volume": 0.032,
      "rsi": 0.018
    },
    "prediction_drift": 0.021,
    "performance_degradation": false
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Drift Detection Thresholds:**

- `< 0.05`: No drift - Model performing well
- `0.05 - 0.10`: Moderate drift - Monitor closely
- `> 0.10`: Significant drift - Retrain model recommended

---

## Data Models

### PredictionResponse

```typescript
{
  symbol: string;
  current_price: number;
  predicted_price: number;
  predicted_return: number;
  confidence: number;  // 0.0 to 1.0
  direction: "up" | "down" | "neutral";
  timestamp: string;  // ISO 8601 format
}
```

### SignalResponse

```typescript
{
  symbol: string;
  signal: "buy" | "sell" | "hold";
  strength: number;  // 0.0 to 1.0
  current_price: number;
  target_price: number;
  stop_loss: number;
  take_profit: number;
  position_size: {
    shares: number;
    value: number;
    percentage: number;
  };
  timestamp: string;
}
```

---

## Code Examples

### Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Get prediction
def get_prediction(symbol: str, model: str = "ensemble"):
    url = f"{BASE_URL}/api/v1/predictions/{symbol}"
    params = {"model": model}
    response = requests.get(url, params=params)
    return response.json()

# Get trading signal
def get_signal(symbol: str, capital: float = 10000):
    url = f"{BASE_URL}/api/v1/signals/{symbol}"
    params = {"capital": capital}
    response = requests.get(url, params=params)
    return response.json()

# Batch predictions
def batch_predictions(symbols: list):
    url = f"{BASE_URL}/api/v1/predictions/batch"
    data = {"symbols": symbols, "model": "ensemble"}
    response = requests.post(url, json=data)
    return response.json()

# Usage
prediction = get_prediction("AAPL")
print(f"Predicted price: {prediction['predicted_price']}")

signal = get_signal("MSFT", capital=50000)
print(f"Signal: {signal['signal']}, Strength: {signal['strength']}")

batch = batch_predictions(["AAPL", "MSFT", "GOOGL", "VCB.VN"])
for pred in batch['predictions']:
    print(f"{pred['symbol']}: {pred['predicted_price']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Get prediction
async function getPrediction(symbol, model = 'ensemble') {
  const response = await axios.get(
    `${BASE_URL}/api/v1/predictions/${symbol}`,
    { params: { model } }
  );
  return response.data;
}

// Get trading signal
async function getSignal(symbol, capital = 10000) {
  const response = await axios.get(
    `${BASE_URL}/api/v1/signals/${symbol}`,
    { params: { capital } }
  );
  return response.data;
}

// Batch predictions
async function batchPredictions(symbols) {
  const response = await axios.post(
    `${BASE_URL}/api/v1/predictions/batch`,
    { symbols, model: 'ensemble' }
  );
  return response.data;
}

// Usage
(async () => {
  const prediction = await getPrediction('AAPL');
  console.log(`Predicted price: ${prediction.predicted_price}`);

  const signal = await getSignal('MSFT', 50000);
  console.log(`Signal: ${signal.signal}, Strength: ${signal.strength}`);

  const batch = await batchPredictions(['AAPL', 'MSFT', 'GOOGL']);
  batch.predictions.forEach(pred => {
    console.log(`${pred.symbol}: ${pred.predicted_price}`);
  });
})();
```

### cURL

```bash
# Get prediction
curl -X GET "http://localhost:8000/api/v1/predictions/AAPL?model=ensemble"

# Get trading signal
curl -X GET "http://localhost:8000/api/v1/signals/MSFT?capital=50000"

# Batch predictions
curl -X POST "http://localhost:8000/api/v1/predictions/batch" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL"], "model": "ensemble"}'

# Check system health
curl -X GET "http://localhost:8000/api/v1/monitoring/health"

# Get model metrics
curl -X GET "http://localhost:8000/api/v1/monitoring/metrics?model=ensemble&period=30d"
```

---

## Best Practices

### Performance

1. **Use batch endpoints** for multiple symbols to reduce API calls
2. **Cache predictions** client-side (predictions valid for ~5 minutes)
3. **Implement connection pooling** for high-volume applications
4. **Use async/await** patterns for concurrent requests

### Error Handling

```python
import requests
from requests.exceptions import RequestException

def safe_api_call(url, **kwargs):
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API Error: {e}")
        return None
    except ValueError as e:
        print(f"JSON Parse Error: {e}")
        return None

# Usage
data = safe_api_call(f"{BASE_URL}/api/v1/predictions/AAPL")
if data:
    print(data)
```

### Rate Limiting (Future)

When rate limiting is implemented:

- Include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers
- Implement exponential backoff on 429 responses
- Consider API key tiers for different usage levels

---

## WebSocket API (Future)

Real-time streaming API for live updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/signals');

ws.onmessage = (event) => {
  const signal = JSON.parse(event.data);
  console.log('New signal:', signal);
};

ws.send(JSON.stringify({
  action: 'subscribe',
  symbols: ['AAPL', 'MSFT', 'GOOGL']
}));
```

---

## API Versioning

The API uses URL-based versioning (`/api/v1/`). Breaking changes will be introduced in new versions (v2, v3, etc.) while maintaining backward compatibility for older versions.

---

## Support

For API issues or questions:
- Check this documentation
- Review error messages in responses
- Create an issue on GitHub
- Check system health endpoint

---

## Changelog

### Version 0.1.0 (Current)
- Initial API release
- Prediction endpoints
- Signal generation endpoints
- Monitoring endpoints
- Basic health checks

### Planned Features
- Authentication and API keys
- Rate limiting
- WebSocket streaming
- Historical data endpoints
- Backtesting API
- Portfolio management endpoints
