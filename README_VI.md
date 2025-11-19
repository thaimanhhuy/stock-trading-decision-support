# Hệ Thống Hỗ Trợ Quyết Định Giao Dịch Chứng Khoán

[English](README.md) | **Tiếng Việt**

Hệ thống hỗ trợ quyết định giao dịch chứng khoán dựa trên học máy (Machine Learning), kết hợp các mô hình dự đoán chuỗi thời gian (ARIMA, LSTM, GRU) với phân tích kỹ thuật để tạo tín hiệu giao dịch.

## Tổng Quan

Hệ thống cung cấp:
- **Dự đoán đa mô hình**: Sử dụng ARIMA, LSTM, và GRU để dự báo giá cổ phiếu
- **Chỉ báo kỹ thuật**: RSI, MACD, Bollinger Bands và nhiều chỉ báo khác
- **Quản lý rủi ro**: Tính toán kích thước vị thế, cắt lỗ, và kiểm soát rủi ro danh mục
- **Backtesting**: Đánh giá hiệu suất giao dịch trên dữ liệu lịch sử
- **Giám sát real-time**: Phát hiện model drift và theo dõi hiệu suất
- **REST API**: Dịch vụ API dựa trên FastAPI cho dự đoán và tín hiệu
- **Dashboard tương tác**: Giao diện web Streamlit để trực quan hóa và phân tích

## Hỗ Trợ Thị Trường Chứng Khoán Việt Nam

### Sàn Giao Dịch Được Hỗ Trợ

- **HOSE** (Sở Giao dịch Chứng khoán TP.HCM): Sử dụng đuôi `.VN`
  - Ví dụ: `VCB.VN`, `FPT.VN`, `CTG.VN`
- **HNX** (Sở Giao dịch Chứng khoán Hà Nội): Sử dụng đuôi `.HNX`

### Cổ Phiếu Việt Nam Phổ Biến

#### Ngân hàng
- `VCB.VN` - Vietcombank (Ngân hàng TMCP Ngoại thương Việt Nam)
- `CTG.VN` - VietinBank (Ngân hàng TMCP Công Thương Việt Nam)
- `BID.VN` - BIDV (Ngân hàng TMCP Đầu tư và Phát triển Việt Nam)
- `TCB.VN` - Techcombank (Ngân hàng TMCP Kỹ Thương Việt Nam)
- `MBB.VN` - MBBank (Ngân hàng TMCP Quân đội)
- `ACB.VN` - ACB (Ngân hàng TMCP Á Châu)
- `VPB.VN` - VPBank (Ngân hàng TMCP Việt Nam Thịnh Vượng)

#### Công nghệ
- `FPT.VN` - FPT Corporation (Tập đoàn FPT)

#### Bất động sản
- `VIC.VN` - Vingroup (Tập đoàn Vingroup)
- `VHM.VN` - Vinhomes (Công ty CP Vinhomes)
- `NVL.VN` - Novaland (Tập đoàn Novaland)

#### Sản xuất
- `HPG.VN` - Hòa Phát Group (Tập đoàn Hòa Phát)
- `GAS.VN` - PV Gas (Tổng Công ty Khí Việt Nam)
- `VNM.VN` - Vinamilk (Công ty CP Sữa Việt Nam)

#### Bán lẻ
- `MWG.VN` - Mobile World (Công ty CP Đầu tư Thế giới Di động)

Xem file `config/vietnam_stocks.yaml` để có danh sách đầy đủ các cổ phiếu Việt Nam được phân loại theo ngành.

### Ví Dụ Sử Dụng Nhanh

```bash
# Kiểm tra tải dữ liệu cổ phiếu Việt Nam
python scripts/test_vietnamese_stocks.py

# Tải dữ liệu cổ phiếu Việt Nam
python scripts/download_historical_data.py --symbols VCB.VN,FPT.VN,CTG.VN --period 2y

# Tải dữ liệu ngành ngân hàng Việt Nam
python scripts/download_historical_data.py --symbols VCB.VN,CTG.VN,BID.VN,TCB.VN,MBB.VN --period 5y

# Huấn luyện mô hình cho cổ phiếu Việt Nam
python scripts/train_models.py --symbol VCB.VN --models lstm,gru

# Chạy backtest trên cổ phiếu Việt Nam
python scripts/run_backtest.py --symbol VCB.VN --start 2023-01-01 --end 2024-01-01

# Kết hợp cổ phiếu Mỹ và Việt Nam
python scripts/download_historical_data.py --symbols AAPL,MSFT,VCB.VN,FPT.VN --period 1y
```

### Cấu Hình Thị Trường Việt Nam

Hệ thống bao gồm cấu hình đặc thù cho thị trường Việt Nam trong `config/config.yaml`:
- **Múi giờ**: Asia/Ho_Chi_Minh (UTC+7)
- **Đơn vị tiền tệ**: VND (Đồng Việt Nam)
- **Giờ giao dịch**:
  - Buổi sáng: 09:00 - 11:30
  - Buổi chiều: 13:00 - 14:45

### Lưu Ý Quan Trọng

⚠️ **Những điều cần biết**:
- Thị trường Việt Nam có biên độ giá ±7% mỗi ngày (±10% cho một số cổ phiếu)
- Thanh toán theo T+2 (2 ngày làm việc)
- Hạn mức sở hữu nước ngoài thường từ 30-49%
- Dữ liệu từ Yahoo Finance có thể có độ trễ
- Luôn kiểm tra dữ liệu trước khi giao dịch thực

## Tính Năng Chính

### Thu Thập Dữ Liệu
- Tích hợp Yahoo Finance để lấy dữ liệu OHLCV lịch sử
- Kiểm tra và xác thực chất lượng dữ liệu
- Cập nhật dữ liệu tự động

### Mô Hình Machine Learning
- **ARIMA**: Mô hình thống kê chuỗi thời gian
- **LSTM**: Mô hình deep learning cho dữ liệu tuần tự
- **GRU**: Mạng nơ-ron hồi quy hiệu quả
- Dự đoán kết hợp từ nhiều mô hình (ensemble)

### Công Cụ Giao Dịch
- Tạo tín hiệu giao dịch dựa trên dự đoán mô hình và chỉ báo kỹ thuật
- Quản lý rủi ro với các tham số có thể cấu hình
- Quản lý lệnh (Mua/Bán/Giữ)

### Backtesting
- Mô phỏng hiệu suất trên dữ liệu lịch sử
- Các chỉ số toàn diện (Sharpe ratio, max drawdown, tỷ lệ thắng, v.v.)
- Theo dõi và phân tích danh mục đầu tư

### Giám Sát
- Phát hiện model drift (thay đổi phân phối dữ liệu)
- Cảnh báo suy giảm hiệu suất
- Ghi log kiểm toán để tuân thủ quy định

## Hướng Dẫn Bắt Đầu Nhanh

### Yêu Cầu Hệ Thống
- Python 3.8 trở lên
- pip hoặc conda
- 4GB RAM khả dụng (khuyến nghị 8GB)
- 2GB dung lượng đĩa

### Cài Đặt

```bash
# Clone repository
git clone <repository-url>
cd stock-trading-decision-support

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# Hoặc cài đặt ở chế độ phát triển
pip install -e .

# Sao chép file cấu hình mẫu
cp .env.example .env
# Chỉnh sửa file .env theo cấu hình của bạn
```

### Tải Dữ Liệu Lịch Sử

```bash
# Tải dữ liệu cổ phiếu Mỹ
python scripts/download_historical_data.py --symbols AAPL,MSFT,GOOGL --start 2020-01-01

# Tải dữ liệu cổ phiếu Việt Nam
python scripts/download_historical_data.py --symbols VCB.VN,FPT.VN,CTG.VN --period 2y
```

### Huấn Luyện Mô Hình

```bash
# Huấn luyện tất cả các mô hình
python scripts/train_models.py --symbol AAPL --models lstm,gru,arima

# Huấn luyện mô hình cho cổ phiếu Việt Nam
python scripts/train_models.py --symbol VCB.VN --models lstm,gru
```

### Chạy Backtesting

```bash
# Backtest trên cổ phiếu Mỹ
python scripts/run_backtest.py --symbol AAPL --start 2023-01-01 --end 2024-01-01

# Backtest trên cổ phiếu Việt Nam
python scripts/run_backtest.py --symbol VCB.VN --start 2023-01-01 --end 2024-01-01
```

### Khởi Động API Server

```bash
# Chạy API server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Hoặc với auto-reload cho development
uvicorn src.api.main:app --reload
```

API sẽ khả dụng tại: http://localhost:8000

Xem tài liệu API: http://localhost:8000/docs

### Khởi Chạy Dashboard

```bash
streamlit run src/dashboard/app.py
```

Dashboard sẽ mở tại: http://localhost:8501

## Triển Khai Bằng Docker

### Sử Dụng Docker Compose (Khuyến nghị)

```bash
# Khởi động tất cả các dịch vụ
cd docker
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng các dịch vụ
docker-compose down
```

Sau khi khởi động:
- API service: http://localhost:8000
- Dashboard: http://localhost:8501

### Build Docker Image Riêng Lẻ

```bash
# Build API image
docker build -f docker/Dockerfile.api -t stock-trading-api .

# Build Dashboard image
docker build -f docker/Dockerfile.dashboard -t stock-trading-dashboard .

# Chạy API container
docker run -p 8000:8000 stock-trading-api

# Chạy Dashboard container
docker run -p 8501:8501 stock-trading-dashboard
```

## Cấu Trúc Dự Án

```
stock-trading-decision-support/
├── config/                 # File cấu hình
│   ├── config.yaml        # Cấu hình chung
│   ├── model_config.yaml  # Tham số mô hình
│   ├── trading_config.yaml # Tham số giao dịch
│   ├── logging_config.yaml # Cấu hình logging
│   └── vietnam_stocks.yaml # Danh sách cổ phiếu VN
├── data/                   # Lưu trữ dữ liệu
│   ├── raw/               # Dữ liệu thô
│   ├── processed/         # Dữ liệu đã xử lý
│   ├── features/          # Features đã tạo
│   └── backtest/          # Kết quả backtest
├── models/                 # Mô hình đã huấn luyện
│   └── saved_models/      # Các mô hình đã lưu
├── logs/                   # Application logs
├── notebooks/              # Jupyter notebooks phân tích
├── scripts/                # Script thực thi
│   ├── download_historical_data.py
│   ├── train_models.py
│   ├── run_backtest.py
│   └── test_vietnamese_stocks.py
├── src/                    # Source code
│   ├── data_ingestion/    # Thu thập và xác thực dữ liệu
│   ├── preprocessing/      # Kỹ thuật tạo features
│   ├── models/            # Các mô hình ML
│   ├── trading_engine/    # Tạo tín hiệu và quản lý rủi ro
│   ├── backtesting/       # Đánh giá hiệu suất
│   ├── monitoring/        # Giám sát mô hình
│   ├── api/               # REST API
│   ├── dashboard/         # Web UI
│   └── config/            # Quản lý cấu hình
├── tests/                 # Unit và integration tests
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
└── docker/                # Docker configuration
    ├── Dockerfile.api
    ├── Dockerfile.dashboard
    └── docker-compose.yml
```

## Tài Liệu

### Tài Liệu Tiếng Anh
- [System Design](SYSTEM_DESIGN.md) - Kiến trúc và chi tiết kỹ thuật
- [User Guide](USER_GUIDE.md) - Hướng dẫn sử dụng hệ thống
- [Developer Guide](DEVELOPER_GUIDE.md) - Hướng dẫn phát triển
- [API Documentation](API_DOCUMENTATION.md) - Tài liệu API chi tiết
- [Task Breakdown](TASK_BREAKDOWN.md) - Lộ trình triển khai
- [Test Report](TEST_REPORT.md) - Kết quả kiểm thử
- [Risk Disclosure](RISK_DISCLOSURE.md) - Cảnh báo rủi ro quan trọng
- [Assumptions](ASSUMPTIONS.md) - Các giả định và giới hạn
- [Thesis Summary](THESIS_SUMMARY.md) - Nền tảng nghiên cứu
- [Docker Deployment](DOCKER_DEPLOYMENT.md) - Hướng dẫn triển khai Docker
- [Heroku Deployment](HEROKU_DEPLOYMENT.md) - Hướng dẫn triển khai Heroku

### Tài Liệu Tiếng Việt
- [Hướng dẫn Sử dụng (Tiếng Việt)](USERGUIDE_VI.md) - Chi tiết cách sử dụng
- [Hướng dẫn Nhanh VN](VIETNAMESE_QUICKSTART.md) - Bắt đầu nhanh với thị trường VN

## API Endpoints

### Dự Đoán
- `GET /api/v1/predictions/{symbol}` - Lấy dự đoán giá
- `POST /api/v1/predictions/batch` - Dự đoán hàng loạt

### Tín Hiệu Giao Dịch
- `GET /api/v1/signals/{symbol}` - Lấy tín hiệu giao dịch
- `GET /api/v1/signals/portfolio` - Tín hiệu cấp danh mục

### Giám Sát
- `GET /api/v1/monitoring/health` - Kiểm tra sức khỏe hệ thống
- `GET /api/v1/monitoring/metrics` - Các chỉ số hiệu suất mô hình
- `GET /api/v1/monitoring/drift` - Phát hiện model drift

Xem [API_DOCUMENTATION.md](API_DOCUMENTATION.md) để biết chi tiết đầy đủ.

## Cấu Hình

### File Cấu Hình

**config/config.yaml** - Cấu hình chung:
```yaml
data:
  raw_data_path: data/raw
  processed_data_path: data/processed
  features_path: data/features

market:
  timezone: Asia/Ho_Chi_Minh  # UTC+7 cho VN
  currency: VND
  trading_hours:
    morning: "09:00-11:30"
    afternoon: "13:00-14:45"
```

**config/model_config.yaml** - Tham số mô hình:
```yaml
lstm:
  units: 128
  dropout: 0.2
  learning_rate: 0.001
  batch_size: 64
  epochs: 50
```

**config/trading_config.yaml** - Tham số giao dịch:
```yaml
risk_management:
  max_position_size: 0.1  # 10% danh mục
  stop_loss: 0.05         # 5%
  take_profit: 0.10       # 10%

signals:
  buy_threshold: 0.03     # 3% dự đoán tăng
  sell_threshold: -0.03   # 3% dự đoán giảm
```

## Kiểm Thử

```bash
# Chạy tất cả tests
pytest tests/

# Chạy chỉ unit tests
pytest tests/unit/

# Chạy integration tests
pytest tests/integration/

# Chạy với coverage
pytest --cov=src tests/

# Chạy test cụ thể
pytest tests/unit/test_models.py -v
```

## Cảnh Báo Rủi Ro

⚠️ **QUAN TRỌNG**: Hệ thống này chỉ phục vụ mục đích giáo dục và nghiên cứu. Giao dịch chứng khoán có rủi ro mất vốn đáng kể. Hiệu suất trong quá khứ không đảm bảo kết quả tương lai.

### Luôn Nhớ:
- Tự nghiên cứu kỹ lưỡng
- Tham khảo ý kiến chuyên gia tài chính
- Chỉ đầu tư số tiền bạn có thể chấp nhận mất
- Hiểu rõ các rủi ro liên quan
- Không dựa hoàn toàn vào tín hiệu tự động
- Kiểm tra kỹ dữ liệu trước khi giao dịch thực

Xem [RISK_DISCLOSURE.md](RISK_DISCLOSURE.md) để biết thông tin chi tiết về rủi ro.

## Các Giả Định và Giới Hạn

### Giả Định
- Dữ liệu từ Yahoo Finance là chính xác và đầy đủ
- Thị trường hiệu quả ở mức độ hợp lý
- Chi phí giao dịch không được tính trong backtesting
- Không có trượt giá (slippage)
- Thanh khoản đủ để thực hiện lệnh

### Giới Hạn
- Mô hình có thể không dự đoán chính xác biến động đột ngột
- Không tính các sự kiện bất thường (tin tức, earnings, v.v.)
- Cần huấn luyện lại định kỳ
- Không phải lời khuyên đầu tư chuyên nghiệp

Xem [ASSUMPTIONS.md](ASSUMPTIONS.md) để biết chi tiết đầy đủ.

## Công Nghệ Sử Dụng

- **Python 3.8+**: Ngôn ngữ lập trình chính
- **TensorFlow/Keras**: Mô hình deep learning
- **statsmodels**: Triển khai ARIMA
- **pandas/numpy**: Xử lý dữ liệu
- **FastAPI**: Framework REST API
- **Streamlit**: Framework dashboard
- **MLflow**: Theo dõi thí nghiệm
- **Docker**: Đóng gói ứng dụng
- **pytest**: Framework kiểm thử
- **yfinance**: Lấy dữ liệu từ Yahoo Finance

## Câu Hỏi Thường Gặp (FAQ)

### 1. Hệ thống có miễn phí không?
Có, hệ thống hoàn toàn miễn phí và mã nguồn mở (MIT License).

### 2. Tôi có thể giao dịch thực với hệ thống này không?
Hệ thống chỉ phục vụ mục đích giáo dục. Không khuyến nghị sử dụng trực tiếp cho giao dịch thực mà không có kiểm tra kỹ lưỡng.

### 3. Độ chính xác của mô hình là bao nhiêu?
Độ chính xác phụ thuộc vào nhiều yếu tố và thường dao động 70-85% trên dữ liệu test. Không có mô hình nào hoàn hảo.

### 4. Tôi có thể thêm chỉ báo kỹ thuật mới không?
Có, xem [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) để biết cách thêm chỉ báo tùy chỉnh.

### 5. Hệ thống có hỗ trợ cryptocurrency không?
Hiện tại chưa, nhưng có thể mở rộng trong tương lai.

### 6. Làm thế nào để cải thiện hiệu suất mô hình?
- Thu thập thêm dữ liệu huấn luyện
- Điều chỉnh hyperparameters
- Thêm features mới
- Sử dụng ensemble của nhiều mô hình
- Huấn luyện lại định kỳ

### 7. Dữ liệu được cập nhật như thế nào?
Hệ thống tải dữ liệu từ Yahoo Finance. Bạn cần chạy script download định kỳ để cập nhật.

### 8. Tôi có thể triển khai lên cloud không?
Có, xem hướng dẫn triển khai Heroku hoặc sử dụng Docker cho AWS/GCP/Azure.

## Đóng Góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng đọc [CONTRIBUTING.md](CONTRIBUTING.md) để biết hướng dẫn phát triển và quy tắc đóng góp.

### Cách Đóng Góp

1. Fork repository
2. Tạo branch cho feature (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## Giấy Phép

Dự án này được phát hành dưới giấy phép MIT - xem file [LICENSE](LICENSE) để biết chi tiết.

## Hỗ Trợ

Để được hỗ trợ và giải đáp thắc mắc:
- Tạo issue trên GitHub repository
- Kiểm tra tài liệu hiện có
- Xem hướng dẫn sử dụng
- Tham gia discussions trên GitHub

## Lời Cảm Ơn

Dự án dựa trên nghiên cứu về machine learning cho dự đoán thị trường chứng khoán và các chiến lược giao dịch định lượng.

### Tài Liệu Tham Khảo

- Research papers on LSTM/GRU for stock prediction
- Technical analysis methodologies
- Risk management frameworks
- Quantitative trading strategies

## Roadmap

### Phiên bản hiện tại (0.1.0)
- ✅ Mô hình ARIMA, LSTM, GRU
- ✅ Backtesting engine
- ✅ REST API
- ✅ Dashboard Streamlit
- ✅ Hỗ trợ thị trường Việt Nam

### Kế hoạch tương lai
- [ ] WebSocket real-time streaming
- [ ] Phân tích sentiment từ tin tức
- [ ] Tối ưu hóa danh mục đầu tư nâng cao
- [ ] Hỗ trợ cryptocurrency
- [ ] Mobile app
- [ ] Thông báo qua email/Telegram
- [ ] Tích hợp với sàn giao dịch
- [ ] Multi-language support mở rộng
- [ ] Mô hình deep learning nâng cao (Transformer, Attention)
- [ ] Backtesting nâng cao với các loại lệnh phức tạp

## Liên Hệ

- GitHub Issues: Báo cáo bug và yêu cầu tính năng
- Discussions: Thảo luận và chia sẻ ý tưởng

---

**Lưu ý**: Hệ thống này KHÔNG phải là lời khuyên đầu tư tài chính. Luôn tự nghiên cứu và tham khảo chuyên gia trước khi đầu tư.
