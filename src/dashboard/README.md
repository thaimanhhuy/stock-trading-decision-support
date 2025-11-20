# Stock Trading Decision Support Dashboard

## Overview

This is a Streamlit-based dashboard for the Stock Trading Decision Support System. It provides real-time stock predictions and trading signals powered by LSTM and GRU machine learning models.

## Recent Fixes (2025-11-20)

### Issues Fixed

1. **API Integration**: The dashboard was showing hardcoded sample data instead of connecting to the FastAPI backend
2. **Environment Variable Usage**: Added proper use of `API_BASE_URL` environment variable
3. **Error Handling**: Implemented comprehensive error handling for API failures
4. **Connection Status**: Added real-time API health monitoring with visual indicators
5. **Session State**: Implemented session state management for better performance

### Changes Made

#### API Integration Layer (`src/dashboard/app.py`)

Added the following functions for API communication:

- `check_api_health()`: Verifies API connectivity
- `get_prediction(symbol)`: Fetches price predictions from `/api/v1/predictions/{symbol}`
- `get_signal(symbol)`: Fetches trading signals from `/api/v1/signals/{symbol}`
- `get_multiple_signals(symbols)`: Batch fetches signals for multiple symbols

#### Enhanced Features

1. **Connection Status Indicator**: Shows API connection status in sidebar (🟢 Connected / 🔴 Disconnected)
2. **Error Messages**: User-friendly error messages when API is unreachable or requests fail
3. **Loading States**: Spinners and progress indicators during API calls
4. **Data Validation**: Proper handling of missing or invalid API responses
5. **Retry Mechanism**: "Retry Connection" button on the home page
6. **Warning Messages**: Clear indicators when placeholder data is being displayed

#### Page Updates

**Home Page:**
- Now fetches real signals from API for default symbols (AAPL, MSFT, GOOGL)
- Shows connection status
- Displays demo value warnings for portfolio metrics

**Predictions Page:**
- Integrated with `/api/v1/predictions/{symbol}` endpoint
- Dynamic price calculation and change percentages
- Support for both US and Vietnamese stocks
- Real-time data fetching with loading indicators

**Signals Page:**
- Integrated with `/api/v1/signals/{symbol}` endpoint
- Supports multiple symbol input (comma-separated)
- Displays signal distribution (BUY/HOLD/SELL counts)
- Shows all signal details: target price, stop loss, take profit

**Monitoring Page:**
- Real-time API health checks
- Refresh button to re-check API status
- System information display

## Configuration

### Environment Variables

The dashboard uses the following environment variable:

```bash
API_BASE_URL=http://api:8000  # In Docker
# or
API_BASE_URL=http://localhost:8000  # For local development
```

If not set, it defaults to `http://localhost:8000`.

### Docker Configuration

The dashboard is configured in `docker/docker-compose.yml`:

```yaml
dashboard:
  environment:
    - API_BASE_URL=http://api:8000
```

## Running the Dashboard

### Using Docker Compose (Recommended)

```bash
# Start both API and Dashboard
cd docker
docker-compose up -d

# Access dashboard at http://localhost:8501
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export API_BASE_URL=http://localhost:8000

# Start the API first (in another terminal)
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Start the dashboard
streamlit run src/dashboard/app.py
```

## API Endpoints Used

The dashboard connects to the following API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API health |
| `/api/v1/predictions/{symbol}` | GET | Get price prediction |
| `/api/v1/signals/{symbol}` | GET | Get trading signal |

## Current Limitations

### Known Issues

1. **Placeholder Data**: The API endpoints (`/api/v1/predictions/` and `/api/v1/signals/`) currently return placeholder data because the actual model integration is not complete (see TODO comments in `src/api/routes/predictions.py`)

2. **Portfolio Metrics**: The Home and Performance pages still show hardcoded portfolio values because there's no portfolio tracking system implemented yet

3. **Model Status**: The Monitoring page shows static model status as the actual model health monitoring is not yet implemented

### Next Steps for Full Integration

To complete the dashboard integration:

1. **Implement Model Integration in API**:
   - Update `src/api/routes/predictions.py` to load and use trained LSTM/GRU models
   - Replace placeholder data with real model predictions

2. **Add Portfolio Tracking**:
   - Implement portfolio management system
   - Store and track positions, P&L, and performance metrics

3. **Real-time Monitoring**:
   - Implement model drift detection integration
   - Add data quality monitoring
   - Track prediction accuracy over time

4. **Historical Data**:
   - Store prediction history
   - Implement backtesting results display

## Testing the Dashboard

### Manual Testing Checklist

- [ ] Dashboard loads without errors
- [ ] API connection status is displayed correctly
- [ ] Home page shows recent signals (if API is running)
- [ ] Predictions page can fetch predictions for different symbols
- [ ] Signals page can fetch signals for multiple symbols
- [ ] Monitoring page shows API health status
- [ ] Error messages display when API is not reachable
- [ ] Retry connection button works

### Testing with API Running

```bash
# Terminal 1: Start API
python -m uvicorn src.api.main:app --reload

# Terminal 2: Start Dashboard
streamlit run src/dashboard/app.py

# Access at http://localhost:8501
```

## Troubleshooting

### "Cannot connect to API" Error

1. Verify the API is running: `curl http://localhost:8000/health`
2. Check the `API_BASE_URL` environment variable
3. Ensure there are no firewall/network issues
4. Check API logs for errors

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Dashboard Not Loading

```bash
# Check Streamlit installation
streamlit --version

# Clear Streamlit cache
streamlit cache clear

# Run with verbose logging
streamlit run src/dashboard/app.py --logger.level=debug
```

## Architecture

```
┌─────────────────────────────────────┐
│   Streamlit Dashboard (Port 8501)  │
│                                     │
│  Pages:                             │
│  - Home                             │
│  - Predictions                      │
│  - Signals                          │
│  - Performance                      │
│  - Monitoring                       │
└──────────────┬──────────────────────┘
               │
               │ HTTP Requests
               │ (requests library)
               │
┌──────────────▼──────────────────────┐
│   FastAPI Backend (Port 8000)       │
│                                     │
│  Endpoints:                         │
│  - /health                          │
│  - /api/v1/predictions/{symbol}     │
│  - /api/v1/signals/{symbol}         │
│  - /api/v1/training/*               │
│  - /api/v1/monitoring/*             │
└──────────────┬──────────────────────┘
               │
               │
┌──────────────▼──────────────────────┐
│   ML Models & Trading Logic         │
│                                     │
│  - LSTM Model                       │
│  - GRU Model                        │
│  - Signal Generator                 │
│  - Data Ingestion                   │
└─────────────────────────────────────┘
```

## Dependencies

Key dependencies used by the dashboard:

- `streamlit>=1.27.0` - Web framework
- `requests>=2.31.0` - HTTP client for API calls
- `pandas>=2.0.0` - Data manipulation
- `plotly>=5.17.0` - Interactive charts

See `requirements.txt` for the complete list.

## Support

For issues or questions:

1. Check the API logs: `docker-compose logs api`
2. Check the dashboard logs: `docker-compose logs dashboard`
3. Refer to the main project README for general setup instructions

---

**Last Updated**: 2025-11-20
**Version**: 1.0.0 (Fixed API Integration)
