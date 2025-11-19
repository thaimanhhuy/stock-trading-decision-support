# Hướng dẫn Retraining Model / Model Retraining Guide

[Tiếng Việt](#tiếng-việt) | [English](#english)

---

## Tiếng Việt

### Tổng quan

Hệ thống hỗ trợ 3 phương thức retraining model:

1. **Retraining tự động theo lịch** - Mỗi 3 tháng một lần
2. **Retraining dựa trên sự kiện thị trường** - Khi thị trường giảm >5%
3. **Retraining thủ công** - Qua API hoặc command line

### 1. Retraining Tự động theo Lịch (Scheduled Retraining)

#### Cấu hình

Chỉnh sửa file `config/config.yaml`:

```yaml
models:
  auto_retrain: true
  retrain_interval_months: 3  # Retraining mỗi 3 tháng

  monitored_symbols:
    - "AAPL"
    - "MSFT"
    - "VCB.VN"
    - "FPT.VN"
```

#### Cách hoạt động

- Scheduler chạy kiểm tra mỗi ngày lúc 2:00 AM (UTC)
- Tự động xác định các model cần retraining dựa trên thời gian training lần cuối
- Tải dữ liệu mới nhất và training lại model
- Lưu lịch sử training vào `models/training_history.json`

#### Khởi động Scheduler

**Qua API:**
```bash
curl -X POST http://localhost:8000/api/v1/scheduler/start
```

**Trong code:**
```python
from src.services.scheduler_service import SchedulerService

scheduler = SchedulerService(
    symbols=["AAPL", "VCB.VN"],
    retraining_interval_months=3
)
scheduler.start()
```

#### Kiểm tra trạng thái

```bash
curl http://localhost:8000/api/v1/scheduler/status
```

### 2. Retraining dựa trên Sự kiện Thị trường

#### Cấu hình

Trong file `config/config.yaml`:

```yaml
models:
  market_event_retraining:
    enabled: true
    check_interval_hours: 24  # Kiểm tra mỗi 24 giờ
    drop_threshold_percentage: 5.0  # Ngưỡng giảm 5%
    lookback_days: 5  # Xem xét 5 ngày gần nhất
```

#### Cách hoạt động

- Scheduler kiểm tra thị trường mỗi 24 giờ
- Theo dõi các chỉ số:
  - **Thị trường Mỹ:** S&P 500 (^GSPC)
  - **Thị trường Việt Nam:** VN-Index hoặc VCB.VN (proxy)
- Nếu phát hiện giảm >5% trong 5 ngày gần nhất:
  - Tự động trigger retraining cho các symbol liên quan
  - Ghi nhận sự kiện vào `models/market_events.json`

#### Kiểm tra thị trường thủ công

```bash
# Kiểm tra thị trường Mỹ
curl "http://localhost:8000/api/v1/market/check/us?threshold=5.0&lookback_days=5"

# Kiểm tra thị trường Việt Nam
curl "http://localhost:8000/api/v1/market/check/vietnam?threshold=5.0&lookback_days=5"
```

#### Xem lịch sử sự kiện thị trường

```bash
curl "http://localhost:8000/api/v1/market/events?market=us&limit=50"
```

### 3. Retraining Thủ công (Manual Training)

#### 3.1. Qua API

**Training một symbol:**

```bash
curl -X POST http://localhost:8000/api/v1/training/train \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "models": "all",
    "fetch_new_data": true
  }'
```

**Training nhiều symbols:**

```bash
curl -X POST http://localhost:8000/api/v1/training/batch-train \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT", "VCB.VN"],
    "models": "all",
    "fetch_new_data": true
  }'
```

**Chỉ training model LSTM:**

```bash
curl -X POST http://localhost:8000/api/v1/training/train \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "models": "lstm",
    "fetch_new_data": true
  }'
```

#### 3.2. Qua Command Line

```bash
# Training model cho AAPL
python scripts/train_models.py --symbol AAPL --models all

# Chỉ training LSTM
python scripts/train_models.py --symbol AAPL --models lstm

# Training GRU
python scripts/train_models.py --symbol AAPL --models gru
```

#### 3.3. Qua Python Code

```python
from src.services.retraining_service import RetrainingService

service = RetrainingService()

# Training một symbol
result = service.retrain_model(
    symbol="AAPL",
    trigger="manual",
    models="all",
    fetch_new_data=True
)

# Training nhiều symbols
results = service.retrain_multiple(
    symbols=["AAPL", "MSFT", "VCB.VN"],
    trigger="manual"
)
```

### Theo dõi và Giám sát

#### Xem lịch sử training

```bash
# Lịch sử cho một symbol
curl http://localhost:8000/api/v1/training/history/AAPL?limit=50

# Thống kê training
curl http://localhost:8000/api/v1/training/stats

# Thống kê cho symbol cụ thể
curl "http://localhost:8000/api/v1/training/stats?symbol=AAPL"
```

#### File dữ liệu

- **Training History:** `models/training_history.json`
- **Market Events:** `models/market_events.json`
- **Trained Models:** `models/saved_models/{symbol}.keras`
- **Scalers:** `models/scalers/{symbol}_scaler.pkl`

### API Endpoints Đầy đủ

#### Training Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/v1/training/train` | POST | Training một symbol |
| `/api/v1/training/batch-train` | POST | Training nhiều symbols |
| `/api/v1/training/history/{symbol}` | GET | Lịch sử training |
| `/api/v1/training/stats` | GET | Thống kê training |

#### Market Monitoring Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/v1/market/check/{market}` | GET | Kiểm tra sự kiện thị trường |
| `/api/v1/market/events` | GET | Lịch sử sự kiện thị trường |

#### Scheduler Control Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/v1/scheduler/status` | GET | Trạng thái scheduler |
| `/api/v1/scheduler/start` | POST | Khởi động scheduler |
| `/api/v1/scheduler/stop` | POST | Dừng scheduler |
| `/api/v1/scheduler/trigger-retraining` | POST | Trigger scheduled retraining |
| `/api/v1/scheduler/trigger-market-check` | POST | Trigger market check |

### Best Practices

1. **Dữ liệu mới:** Luôn `fetch_new_data=true` khi training để có data mới nhất
2. **Monitoring:** Theo dõi training history để phát hiện lỗi sớm
3. **Backup:** Backup models trước khi retraining quan trọng
4. **Testing:** Test model mới trước khi deploy vào production
5. **Scheduling:** Chạy scheduled retraining vào giờ ít hoạt động (2-4 AM)

### Troubleshooting

#### Scheduler không chạy

```bash
# Kiểm tra status
curl http://localhost:8000/api/v1/scheduler/status

# Khởi động lại
curl -X POST http://localhost:8000/api/v1/scheduler/start
```

#### Training bị lỗi

Kiểm tra logs tại `logs/` directory và training history:

```bash
curl http://localhost:8000/api/v1/training/history/AAPL
```

#### Market check không phát hiện sự kiện

- Kiểm tra threshold có phù hợp không (mặc định 5%)
- Kiểm tra lookback_days (mặc định 5 ngày)
- Xem market events history

---

## English

### Overview

The system supports 3 retraining methods:

1. **Scheduled Automatic Retraining** - Every 3 months
2. **Market Event-based Retraining** - When market drops >5%
3. **Manual Retraining** - Via API or command line

### 1. Scheduled Automatic Retraining

#### Configuration

Edit `config/config.yaml`:

```yaml
models:
  auto_retrain: true
  retrain_interval_months: 3  # Retrain every 3 months

  monitored_symbols:
    - "AAPL"
    - "MSFT"
    - "VCB.VN"
    - "FPT.VN"
```

#### How it works

- Scheduler runs daily checks at 2:00 AM (UTC)
- Automatically identifies models needing retraining based on last training date
- Fetches latest data and retrains models
- Saves training history to `models/training_history.json`

#### Starting the Scheduler

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/scheduler/start
```

**In code:**
```python
from src.services.scheduler_service import SchedulerService

scheduler = SchedulerService(
    symbols=["AAPL", "VCB.VN"],
    retraining_interval_months=3
)
scheduler.start()
```

#### Check status

```bash
curl http://localhost:8000/api/v1/scheduler/status
```

### 2. Market Event-based Retraining

#### Configuration

In `config/config.yaml`:

```yaml
models:
  market_event_retraining:
    enabled: true
    check_interval_hours: 24  # Check every 24 hours
    drop_threshold_percentage: 5.0  # 5% drop threshold
    lookback_days: 5  # Look at last 5 days
```

#### How it works

- Scheduler checks markets every 24 hours
- Monitors market indices:
  - **US Market:** S&P 500 (^GSPC)
  - **Vietnam Market:** VN-Index or VCB.VN (proxy)
- If detects >5% drop in last 5 days:
  - Automatically triggers retraining for related symbols
  - Records event to `models/market_events.json`

#### Manual market check

```bash
# Check US market
curl "http://localhost:8000/api/v1/market/check/us?threshold=5.0&lookback_days=5"

# Check Vietnam market
curl "http://localhost:8000/api/v1/market/check/vietnam?threshold=5.0&lookback_days=5"
```

#### View market event history

```bash
curl "http://localhost:8000/api/v1/market/events?market=us&limit=50"
```

### 3. Manual Retraining

#### 3.1. Via API

**Train single symbol:**

```bash
curl -X POST http://localhost:8000/api/v1/training/train \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "models": "all",
    "fetch_new_data": true
  }'
```

**Train multiple symbols:**

```bash
curl -X POST http://localhost:8000/api/v1/training/batch-train \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT", "VCB.VN"],
    "models": "all",
    "fetch_new_data": true
  }'
```

**Train only LSTM model:**

```bash
curl -X POST http://localhost:8000/api/v1/training/train \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "models": "lstm",
    "fetch_new_data": true
  }'
```

#### 3.2. Via Command Line

```bash
# Train models for AAPL
python scripts/train_models.py --symbol AAPL --models all

# Train only LSTM
python scripts/train_models.py --symbol AAPL --models lstm

# Train GRU
python scripts/train_models.py --symbol AAPL --models gru
```

#### 3.3. Via Python Code

```python
from src.services.retraining_service import RetrainingService

service = RetrainingService()

# Train single symbol
result = service.retrain_model(
    symbol="AAPL",
    trigger="manual",
    models="all",
    fetch_new_data=True
)

# Train multiple symbols
results = service.retrain_multiple(
    symbols=["AAPL", "MSFT", "VCB.VN"],
    trigger="manual"
)
```

### Monitoring and Tracking

#### View training history

```bash
# History for a symbol
curl http://localhost:8000/api/v1/training/history/AAPL?limit=50

# Training statistics
curl http://localhost:8000/api/v1/training/stats

# Stats for specific symbol
curl "http://localhost:8000/api/v1/training/stats?symbol=AAPL"
```

#### Data files

- **Training History:** `models/training_history.json`
- **Market Events:** `models/market_events.json`
- **Trained Models:** `models/saved_models/{symbol}.keras`
- **Scalers:** `models/scalers/{symbol}_scaler.pkl`

### Complete API Endpoints

#### Training Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/training/train` | POST | Train single symbol |
| `/api/v1/training/batch-train` | POST | Train multiple symbols |
| `/api/v1/training/history/{symbol}` | GET | Training history |
| `/api/v1/training/stats` | GET | Training statistics |

#### Market Monitoring Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/market/check/{market}` | GET | Check market events |
| `/api/v1/market/events` | GET | Market event history |

#### Scheduler Control Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scheduler/status` | GET | Scheduler status |
| `/api/v1/scheduler/start` | POST | Start scheduler |
| `/api/v1/scheduler/stop` | POST | Stop scheduler |
| `/api/v1/scheduler/trigger-retraining` | POST | Trigger scheduled retraining |
| `/api/v1/scheduler/trigger-market-check` | POST | Trigger market check |

### Best Practices

1. **Fresh Data:** Always use `fetch_new_data=true` when training for latest data
2. **Monitoring:** Track training history to detect issues early
3. **Backup:** Backup models before important retraining
4. **Testing:** Test new models before production deployment
5. **Scheduling:** Run scheduled retraining during low-activity hours (2-4 AM)

### Troubleshooting

#### Scheduler not running

```bash
# Check status
curl http://localhost:8000/api/v1/scheduler/status

# Restart
curl -X POST http://localhost:8000/api/v1/scheduler/start
```

#### Training failures

Check logs in `logs/` directory and training history:

```bash
curl http://localhost:8000/api/v1/training/history/AAPL
```

#### Market check not detecting events

- Check if threshold is appropriate (default 5%)
- Check lookback_days (default 5 days)
- Review market events history
