# Hướng Dẫn Sử Dụng Chi Tiết

[English](USER_GUIDE.md) | **Tiếng Việt**

Tài liệu này cung cấp hướng dẫn chi tiết về cách sử dụng Hệ thống Hỗ trợ Quyết định Giao dịch Chứng khoán.

## Mục Lục

1. [Bắt Đầu](#bắt-đầu)
2. [Thu Thập Dữ Liệu](#thu-thập-dữ-liệu)
3. [Huấn Luyện Mô Hình](#huấn-luyện-mô-hình)
4. [Tạo Dự Đoán](#tạo-dự-đoán)
5. [Sử Dụng Tín Hiệu Giao Dịch](#sử-dụng-tín-hiệu-giao-dịch)
6. [Chạy Backtesting](#chạy-backtesting)
7. [Sử Dụng Dashboard](#sử-dụng-dashboard)
8. [Sử Dụng API](#sử-dụng-api)
9. [Giám Sát Hệ Thống](#giám-sát-hệ-thống)
10. [Xử Lý Sự Cố](#xử-lý-sự-cố)

---

## Bắt Đầu

### Yêu Cầu Hệ Thống

- **Hệ điều hành**: Windows 10+, macOS 10.14+, hoặc Linux (Ubuntu 18.04+)
- **Python**: Phiên bản 3.8 trở lên (khuyến nghị 3.10)
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB trở lên)
- **Ổ cứng**: Ít nhất 2GB dung lượng trống
- **Kết nối Internet**: Để tải dữ liệu từ Yahoo Finance

### Cài Đặt

#### Bước 1: Clone Repository

```bash
git clone <repository-url>
cd stock-trading-decision-support
```

#### Bước 2: Tạo Virtual Environment (Khuyến nghị)

```bash
# Sử dụng venv
python -m venv venv

# Kích hoạt trên Windows
venv\Scripts\activate

# Kích hoạt trên macOS/Linux
source venv/bin/activate
```

#### Bước 3: Cài Đặt Dependencies

```bash
# Cài đặt từ requirements.txt
pip install -r requirements.txt

# Hoặc cài đặt ở chế độ development
pip install -e .
```

#### Bước 4: Cấu Hình

```bash
# Sao chép file cấu hình mẫu
cp .env.example .env

# Chỉnh sửa file .env theo nhu cầu
# Sử dụng editor yêu thích: nano, vim, vscode, v.v.
nano .env
```

**Cấu hình cơ bản trong .env:**

```env
# Đường dẫn dữ liệu
DATA_RAW_PATH=data/raw
DATA_PROCESSED_PATH=data/processed

# Cấu hình API
API_HOST=0.0.0.0
API_PORT=8000

# Cấu hình Dashboard
DASHBOARD_PORT=8501

# Logging
LOG_LEVEL=INFO
```

---

## Thu Thập Dữ Liệu

### Tải Dữ Liệu Cổ Phiếu Đơn Lẻ

```bash
python scripts/download_historical_data.py \
  --symbols AAPL \
  --start 2020-01-01 \
  --end 2024-01-01
```

**Tham số:**
- `--symbols`: Mã cổ phiếu (có thể nhiều mã, cách nhau bằng dấu phẩy)
- `--start`: Ngày bắt đầu (format: YYYY-MM-DD)
- `--end`: Ngày kết thúc (tùy chọn, mặc định là ngày hiện tại)
- `--period`: Thay vì start/end, có thể dùng period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

### Tải Nhiều Cổ Phiếu Cùng Lúc

```bash
python scripts/download_historical_data.py \
  --symbols AAPL,MSFT,GOOGL,AMZN \
  --period 2y
```

### Tải Dữ Liệu Cổ Phiếu Việt Nam

```bash
# Một cổ phiếu
python scripts/download_historical_data.py \
  --symbols VCB.VN \
  --period 2y

# Nhiều cổ phiếu
python scripts/download_historical_data.py \
  --symbols VCB.VN,FPT.VN,CTG.VN,BID.VN \
  --period 5y

# Cả cổ phiếu Mỹ và Việt Nam
python scripts/download_historical_data.py \
  --symbols AAPL,MSFT,VCB.VN,FPT.VN \
  --period 1y
```

### Kiểm Tra Dữ Liệu Đã Tải

```bash
# Liệt kê các file dữ liệu
ls -lh data/raw/

# Xem nhanh dữ liệu
head -20 data/raw/AAPL.csv
```

**Định dạng dữ liệu:**
```csv
Date,Open,High,Low,Close,Volume
2020-01-02,74.06,75.15,73.80,75.09,135480400
2020-01-03,74.29,75.14,74.13,74.36,146322800
...
```

---

## Huấn Luyện Mô Hình

### Huấn Luyện Mô Hình Đơn Lẻ

#### LSTM Model

```bash
python scripts/train_models.py \
  --symbol AAPL \
  --models lstm \
  --epochs 50 \
  --batch-size 64
```

#### GRU Model

```bash
python scripts/train_models.py \
  --symbol AAPL \
  --models gru \
  --epochs 50
```

#### ARIMA Model

```bash
python scripts/train_models.py \
  --symbol AAPL \
  --models arima
```

### Huấn Luyện Tất Cả Các Mô Hình

```bash
python scripts/train_models.py \
  --symbol AAPL \
  --models lstm,gru,arima
```

### Huấn Luyện Cho Cổ Phiếu Việt Nam

```bash
python scripts/train_models.py \
  --symbol VCB.VN \
  --models lstm,gru \
  --epochs 100
```

### Tham Số Huấn Luyện

| Tham số | Mô tả | Mặc định |
|---------|-------|----------|
| `--symbol` | Mã cổ phiếu | Bắt buộc |
| `--models` | Mô hình cần huấn luyện | lstm,gru,arima |
| `--epochs` | Số epochs (LSTM/GRU) | 50 |
| `--batch-size` | Batch size | 64 |
| `--learning-rate` | Learning rate | 0.001 |
| `--validation-split` | Tỷ lệ validation | 0.15 |
| `--test-split` | Tỷ lệ test | 0.15 |
| `--lookback` | Số ngày lookback | 60 |

### Đầu Ra Huấn Luyện

```
Training LSTM model for AAPL...
Epoch 1/50
████████████████ 100% | Loss: 0.0023 | Val Loss: 0.0031
...
Epoch 50/50
████████████████ 100% | Loss: 0.0008 | Val Loss: 0.0012

Model Performance:
- MAE: 1.23
- RMSE: 1.87
- MAPE: 0.69%

Model saved to: models/saved_models/AAPL_lstm.keras
```

### Xem Mô Hình Đã Lưu

```bash
ls -lh models/saved_models/
```

Kết quả:
```
AAPL_lstm.keras
AAPL_gru.keras
AAPL_arima.pkl
VCB.VN_lstm.keras
...
```

---

## Tạo Dự Đoán

### Sử Dụng Python Script

```python
from src.models.lstm_model import LSTMModel
from src.preprocessing.data_processor import DataProcessor
import pandas as pd

# Tải dữ liệu
symbol = "AAPL"
data = pd.read_csv(f"data/processed/{symbol}_processed.csv")

# Tải mô hình đã huấn luyện
model = LSTMModel()
model.load(f"models/saved_models/{symbol}_lstm.keras")

# Tạo dự đoán
processor = DataProcessor()
features = processor.prepare_features(data)
prediction = model.predict(features)

print(f"Giá hiện tại: ${data['Close'].iloc[-1]:.2f}")
print(f"Giá dự đoán: ${prediction[0]:.2f}")
```

### Sử Dụng API

```bash
# Lấy dự đoán cho một cổ phiếu
curl http://localhost:8000/api/v1/predictions/AAPL

# Lấy dự đoán với mô hình cụ thể
curl "http://localhost:8000/api/v1/predictions/AAPL?model=lstm"

# Dự đoán nhiều ngày
curl "http://localhost:8000/api/v1/predictions/AAPL?days_ahead=5"
```

**Kết quả:**
```json
{
  "symbol": "AAPL",
  "current_price": 178.50,
  "predicted_price": 180.20,
  "predicted_return": 0.95,
  "confidence": 0.75,
  "direction": "up",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Sử Dụng Tín Hiệu Giao Dịch

### Lấy Tín Hiệu Qua API

```bash
curl "http://localhost:8000/api/v1/signals/AAPL?capital=10000"
```

**Kết quả:**
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
  "confidence": 0.75,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Hiểu Các Loại Tín Hiệu

| Tín Hiệu | Ý Nghĩa | Điều Kiện |
|----------|---------|-----------|
| `buy` | Nên mua | Dự đoán tăng ≥ 3% |
| `sell` | Nên bán | Dự đoán giảm ≤ -3% |
| `hold` | Giữ nguyên | Dự đoán trong khoảng -3% đến 3% |

### Độ Mạnh Tín Hiệu (Strength)

- **0.0 - 0.3**: Tín hiệu yếu (cân nhắc kỹ trước khi hành động)
- **0.3 - 0.7**: Tín hiệu trung bình (có thể hành động với thận trọng)
- **0.7 - 1.0**: Tín hiệu mạnh (độ tin cậy cao)

### Sử Dụng Tín Hiệu Trong Trading

```python
import requests

def get_trading_signal(symbol, capital):
    url = f"http://localhost:8000/api/v1/signals/{symbol}"
    params = {"capital": capital}
    response = requests.get(url, params=params)
    return response.json()

# Lấy tín hiệu
signal = get_trading_signal("AAPL", 10000)

# Quyết định giao dịch
if signal['signal'] == 'buy' and signal['strength'] > 0.7:
    print(f"MUA {signal['position_size']['shares']} cổ phiếu")
    print(f"Giá mục tiêu: ${signal['target_price']:.2f}")
    print(f"Stop loss: ${signal['stop_loss']:.2f}")

elif signal['signal'] == 'sell' and signal['strength'] > 0.7:
    print(f"BÁN cổ phiếu {symbol}")

else:
    print("GIỮ - Không có tín hiệu mạnh")
```

---

## Chạy Backtesting

### Backtest Cơ Bản

```bash
python scripts/run_backtest.py \
  --symbol AAPL \
  --start 2023-01-01 \
  --end 2024-01-01 \
  --initial-capital 100000
```

### Backtest Với Tham Số Tùy Chỉnh

```bash
python scripts/run_backtest.py \
  --symbol VCB.VN \
  --start 2022-01-01 \
  --end 2024-01-01 \
  --initial-capital 1000000000 \
  --max-position-size 0.1 \
  --stop-loss 0.05 \
  --take-profit 0.10
```

### Tham Số Backtesting

| Tham số | Mô tả | Mặc định |
|---------|-------|----------|
| `--symbol` | Mã cổ phiếu | Bắt buộc |
| `--start` | Ngày bắt đầu | Bắt buộc |
| `--end` | Ngày kết thúc | Ngày hiện tại |
| `--initial-capital` | Vốn ban đầu | 100000 |
| `--max-position-size` | Kích thước vị thế tối đa (%) | 0.1 (10%) |
| `--stop-loss` | Stop loss (%) | 0.05 (5%) |
| `--take-profit` | Take profit (%) | 0.10 (10%) |

### Kết Quả Backtest

```
=== BACKTEST RESULTS FOR AAPL ===

Period: 2023-01-01 to 2024-01-01
Initial Capital: $100,000.00
Final Capital: $127,450.00

Performance Metrics:
--------------------
Total Return: 27.45%
Sharpe Ratio: 1.85
Max Drawdown: -8.23%
Win Rate: 68.5%
Profit Factor: 2.34

Trades Summary:
--------------
Total Trades: 45
Winning Trades: 31
Losing Trades: 14
Average Win: $1,234.56
Average Loss: $456.78

Best Trade: +$3,456.78 (2023-05-15)
Worst Trade: -$1,234.56 (2023-08-22)
```

### Hiểu Các Chỉ Số

- **Total Return**: Tổng lợi nhuận (%)
- **Sharpe Ratio**: Tỷ lệ rủi ro/lợi nhuận (>1.0 là tốt, >2.0 là rất tốt)
- **Max Drawdown**: Mức sụt giảm lớn nhất từ đỉnh
- **Win Rate**: Tỷ lệ giao dịch thắng (%)
- **Profit Factor**: Tổng lãi / Tổng lỗ (>1.5 là tốt)

---

## Sử Dụng Dashboard

### Khởi Động Dashboard

```bash
streamlit run src/dashboard/app.py
```

Dashboard sẽ mở tại: http://localhost:8501

### Các Trang Dashboard

#### 1. Trang Home (Trang Chủ)

- Hiển thị tổng quan danh mục
- Giá trị danh mục hiện tại
- Tổng lợi nhuận
- Số vị thế đang mở
- Bảng tín hiệu gần đây

#### 2. Trang Predictions (Dự Đoán)

**Cách sử dụng:**
1. Nhập mã cổ phiếu (ví dụ: AAPL, VCB.VN)
2. Chọn mô hình (ARIMA, LSTM, GRU, hoặc Ensemble)
3. Nhấn "Get Prediction"

**Hiển thị:**
- Giá hiện tại
- Giá dự đoán
- % Thay đổi dự kiến
- Độ tin cậy
- Biểu đồ giá lịch sử và dự đoán

#### 3. Trang Signals (Tín Hiệu)

**Cách sử dụng:**
1. Nhập danh sách cổ phiếu quan tâm
2. Nhập tổng vốn khả dụng
3. Chọn mức độ rủi ro (Conservative/Moderate/Aggressive)

**Hiển thị:**
- Bảng tín hiệu cho tất cả cổ phiếu
- Loại tín hiệu (Buy/Sell/Hold)
- Độ mạnh tín hiệu
- Giá mục tiêu
- Stop loss & Take profit
- Kích thước vị thế đề xuất

#### 4. Trang Performance (Hiệu Suất)

**Hiển thị:**
- Biểu đồ giá trị danh mục theo thời gian
- Các chỉ số hiệu suất:
  - Total Return
  - Sharpe Ratio
  - Max Drawdown
  - Win Rate
- Lịch sử giao dịch

#### 5. Trang Monitoring (Giám Sát)

**Hiển thị:**
- Trạng thái hệ thống (System Health)
- Trạng thái các mô hình
- Cảnh báo drift detection
- Hiệu suất API
- Logs gần đây

### Tính Năng Dashboard

#### Làm Mới Tự Động
- Dashboard tự động làm mới dữ liệu mỗi 60 giây
- Có thể tùy chỉnh trong Settings

#### Xuất Dữ Liệu
- Xuất dự đoán ra CSV
- Xuất tín hiệu ra CSV
- Xuất kết quả backtest ra PDF

#### Tùy Chỉnh
- Chọn theme (Light/Dark)
- Cấu hình tham số rủi ro
- Thiết lập cảnh báo

---

## Sử Dụng API

### Khởi Động API Server

```bash
# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Development mode (auto-reload)
uvicorn src.api.main:app --reload
```

### Truy Cập API Documentation

Mở trình duyệt và truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Ví Dụ Sử Dụng API

#### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Health check
health = requests.get(f"{BASE_URL}/health")
print(health.json())

# 2. Lấy dự đoán
prediction = requests.get(f"{BASE_URL}/api/v1/predictions/AAPL")
print(f"Dự đoán AAPL: {prediction.json()['predicted_price']}")

# 3. Dự đoán hàng loạt
batch_data = {
    "symbols": ["AAPL", "MSFT", "GOOGL"],
    "model": "ensemble"
}
batch_pred = requests.post(
    f"{BASE_URL}/api/v1/predictions/batch",
    json=batch_data
)
for pred in batch_pred.json()['predictions']:
    print(f"{pred['symbol']}: ${pred['predicted_price']:.2f}")

# 4. Lấy tín hiệu giao dịch
signal = requests.get(
    f"{BASE_URL}/api/v1/signals/AAPL",
    params={"capital": 10000}
)
print(f"Tín hiệu: {signal.json()['signal']}")
```

#### JavaScript

```javascript
const BASE_URL = 'http://localhost:8000';

// Lấy dự đoán
async function getPrediction(symbol) {
  const response = await fetch(
    `${BASE_URL}/api/v1/predictions/${symbol}`
  );
  const data = await response.json();
  console.log(`${symbol} dự đoán: $${data.predicted_price}`);
}

// Lấy tín hiệu
async function getSignal(symbol, capital) {
  const response = await fetch(
    `${BASE_URL}/api/v1/signals/${symbol}?capital=${capital}`
  );
  const data = await response.json();
  console.log(`Tín hiệu ${symbol}: ${data.signal}`);
}

getPrediction('AAPL');
getSignal('AAPL', 10000);
```

Xem [API_DOCUMENTATION.md](API_DOCUMENTATION.md) để biết chi tiết đầy đủ về API.

---

## Giám Sát Hệ Thống

### Kiểm Tra Sức Khỏe Hệ Thống

```bash
curl http://localhost:8000/api/v1/monitoring/health
```

### Theo Dõi Hiệu Suất Mô Hình

```bash
curl "http://localhost:8000/api/v1/monitoring/metrics?model=ensemble&period=30d"
```

### Phát Hiện Model Drift

```bash
curl "http://localhost:8000/api/v1/monitoring/drift?model=lstm"
```

### Xem Logs

```bash
# Xem logs realtime
tail -f logs/app.log

# Xem logs lỗi
tail -f logs/error.log

# Tìm kiếm trong logs
grep "ERROR" logs/app.log
```

### Cảnh Báo Tự Động

Hệ thống tự động cảnh báo khi:
- Model drift vượt ngưỡng (>0.05)
- Hiệu suất giảm >10% so với baseline
- API response time >2 giây
- Lỗi trong quá trình dự đoán

---

## Xử Lý Sự Cố

### Lỗi Thường Gặp

#### 1. Lỗi Tải Dữ Liệu

**Lỗi:**
```
Error: No data found for symbol AAPL
```

**Giải pháp:**
- Kiểm tra kết nối internet
- Xác nhận mã cổ phiếu đúng
- Thử lại sau vài phút (Yahoo Finance có thể tạm thời không khả dụng)
- Đối với cổ phiếu VN, đảm bảo có đuôi `.VN` hoặc `.HNX`

#### 2. Lỗi Huấn Luyện Mô Hình

**Lỗi:**
```
ValueError: Not enough data to train model
```

**Giải pháp:**
- Tải thêm dữ liệu lịch sử (ít nhất 6 tháng)
- Giảm lookback period
- Kiểm tra dữ liệu không bị thiếu quá nhiều

#### 3. Lỗi API

**Lỗi:**
```
Connection refused on port 8000
```

**Giải pháp:**
- Kiểm tra API server đã khởi động chưa
- Xác nhận port 8000 không bị chiếm bởi ứng dụng khác
- Kiểm tra firewall settings

#### 4. Lỗi Dashboard

**Lỗi:**
```
Streamlit error: Cannot connect to API
```

**Giải pháp:**
- Đảm bảo API server đang chạy
- Kiểm tra API_URL trong config
- Xác nhận không có lỗi CORS

### Debugging

#### Bật Debug Mode

```bash
# Trong file .env
LOG_LEVEL=DEBUG

# Hoặc khi chạy
export LOG_LEVEL=DEBUG
python scripts/train_models.py --symbol AAPL --models lstm
```

#### Kiểm Tra Phiên Bản

```bash
python --version
pip list | grep -E "tensorflow|pandas|numpy|fastapi|streamlit"
```

#### Xóa Cache và Thử Lại

```bash
# Xóa cached models
rm -rf models/saved_models/*.keras

# Xóa cached data
rm -rf data/processed/*

# Huấn luyện lại
python scripts/train_models.py --symbol AAPL --models lstm
```

### Nhận Hỗ Trợ

Nếu gặp vấn đề không giải quyết được:

1. Kiểm tra [GitHub Issues](https://github.com/your-repo/issues)
2. Tạo issue mới với:
   - Mô tả chi tiết vấn đề
   - Log errors
   - Các bước tái hiện
   - Môi trường (OS, Python version, v.v.)
3. Tham khảo tài liệu có sẵn

---

## Tips & Best Practices

### 1. Thu Thập Dữ Liệu

✅ **Nên:**
- Tải ít nhất 2 năm dữ liệu lịch sử
- Cập nhật dữ liệu hàng ngày
- Kiểm tra quality trước khi huấn luyện

❌ **Không nên:**
- Sử dụng dữ liệu quá ít (<6 tháng)
- Bỏ qua bước validation
- Giả định dữ liệu luôn chính xác

### 2. Huấn Luyện Mô Hình

✅ **Nên:**
- Sử dụng ensemble của nhiều mô hình
- Huấn luyện lại định kỳ (mỗi tháng)
- Monitor validation loss
- Sử dụng early stopping

❌ **Không nên:**
- Overtrain (quá nhiều epochs)
- Sử dụng mô hình cũ quá lâu
- Bỏ qua test set performance

### 3. Sử Dụng Tín Hiệu

✅ **Nên:**
- Kết hợp nhiều chỉ báo
- Chỉ giao dịch với tín hiệu mạnh (>0.7)
- Luôn đặt stop loss
- Quản lý vốn cẩn thận

❌ **Không nên:**
- Tin tưởng 100% vào tín hiệu tự động
- All-in vào một lệnh
- Bỏ qua quản lý rủi ro
- Giao dịch cảm tính

### 4. Backtesting

✅ **Nên:**
- Test trên nhiều khoảng thời gian
- Bao gồm chi phí giao dịch
- Kiểm tra trên nhiều cổ phiếu
- Phân tích cả thắng lẫn thua

❌ **Không nên:**
- Cherry-pick kết quả tốt
- Optimize quá mức (overfitting)
- Bỏ qua slippage và chi phí
- Giả định backtest = kết quả thực

### 5. Production Deployment

✅ **Nên:**
- Sử dụng Docker cho consistency
- Implement proper logging
- Monitor system health
- Có backup và rollback plan

❌ **Không nên:**
- Deploy không test kỹ
- Bỏ qua monitoring
- Không có error handling
- Run với quyền root

---

## Kết Luận

Hệ thống Hỗ trợ Quyết định Giao dịch Chứng khoán là một công cụ mạnh mẽ nhưng cần được sử dụng một cách có trách nhiệm. Luôn nhớ:

1. **Đây là công cụ hỗ trợ**, không phải thay thế cho phán đoán của bạn
2. **Luôn tự nghiên cứu** trước khi đưa ra quyết định
3. **Quản lý rủi ro** là ưu tiên hàng đầu
4. **Không đầu tư** số tiền bạn không thể mất
5. **Tham khảo chuyên gia** khi cần thiết

Chúc bạn giao dịch thành công! 📈

---

**Lưu ý**: Tài liệu này được cập nhật thường xuyên. Vui lòng kiểm tra phiên bản mới nhất trên GitHub.
