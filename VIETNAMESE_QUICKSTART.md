# Hướng Dẫn Nhanh - Cổ Phiếu Việt Nam

## Vietnamese Stock Trading Decision Support System
## Hệ Thống Hỗ Trợ Quyết Định Giao Dịch Chứng Khoán Việt Nam

---

## 📋 Mục Lục

1. [Giới Thiệu](#giới-thiệu)
2. [Cài Đặt](#cài-đặt)
3. [Sử Dụng Cơ Bản](#sử-dụng-cơ-bản)
4. [Các Mã Cổ Phiếu Phổ Biến](#các-mã-cổ-phiếu-phổ-biến)
5. [Ví Dụ Thực Tế](#ví-dụ-thực-tế)
6. [Lưu Ý Quan Trọng](#lưu-ý-quan-trọng)

---

## 🎯 Giới Thiệu

Hệ thống này giúp bạn:
- ✅ Tải và phân tích dữ liệu cổ phiếu Việt Nam từ Yahoo Finance
- ✅ Huấn luyện mô hình AI (LSTM, GRU, ARIMA) để dự đoán giá
- ✅ Tạo tín hiệu giao dịch (Mua/Bán/Giữ)
- ✅ Kiểm tra hiệu suất chiến lược (Backtesting)
- ✅ Theo dõi danh mục đầu tư

### Định Dạng Mã Cổ Phiếu

- **Sàn HOSE** (TP. Hồ Chí Minh): Thêm `.VN` sau mã
  - Ví dụ: `VCB.VN`, `FPT.VN`, `CTG.VN`

- **Sàn HNX** (Hà Nội): Thêm `.HNX` sau mã
  - Ví dụ: Các mã niêm yết trên HNX

---

## 🚀 Cài Đặt

### Yêu Cầu Hệ Thống
- Python 3.8 trở lên
- pip hoặc conda
- Kết nối internet

### Các Bước Cài Đặt

```bash
# 1. Clone repository
git clone <repository-url>
cd stock-trading-decision-support

# 2. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 3. Tạo file cấu hình
cp .env.example .env
# Chỉnh sửa .env nếu cần
```

---

## 💡 Sử Dụng Cơ Bản

### 1. Kiểm Tra Hệ Thống

Trước tiên, chạy script test để đảm bảo hệ thống hoạt động tốt:

```bash
python scripts/test_vietnamese_stocks.py
```

Script này sẽ:
- ✅ Kiểm tra kết nối Yahoo Finance
- ✅ Tải dữ liệu mẫu của 5 cổ phiếu (VCB, FPT, CTG, NVL, HPG)
- ✅ Hiển thị thông tin giá và khối lượng giao dịch

### 2. Tải Dữ Liệu Lịch Sử

#### Tải một cổ phiếu:
```bash
python scripts/download_historical_data.py --symbols VCB.VN --period 2y
```

#### Tải nhiều cổ phiếu:
```bash
python scripts/download_historical_data.py --symbols VCB.VN,FPT.VN,CTG.VN,NVL.VN --period 2y
```

#### Tải với khoảng thời gian cụ thể:
```bash
python scripts/download_historical_data.py \
  --symbols VCB.VN,FPT.VN \
  --start 2023-01-01 \
  --end 2024-12-31
```

**Tham số `period`:**
- `1y` - 1 năm
- `2y` - 2 năm
- `5y` - 5 năm
- `max` - Tất cả dữ liệu có sẵn

### 3. Huấn Luyện Mô Hình

Sau khi có dữ liệu, huấn luyện mô hình AI:

```bash
# Huấn luyện mô hình LSTM cho VCB
python scripts/train_models.py --symbol VCB.VN --models lstm

# Huấn luyện nhiều mô hình cùng lúc
python scripts/train_models.py --symbol VCB.VN --models lstm,gru,arima
```

### 4. Chạy Backtest

Kiểm tra hiệu suất chiến lược trên dữ liệu lịch sử:

```bash
python scripts/run_backtest.py \
  --symbol VCB.VN \
  --start 2023-01-01 \
  --end 2024-01-01
```

### 5. Khởi Động API Server

Để sử dụng qua API:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Truy cập: http://localhost:8000/docs

### 6. Khởi Động Dashboard

Giao diện web trực quan:

```bash
streamlit run src.dashboard/app.py
```

Truy cập: http://localhost:8501

---

## 📊 Các Mã Cổ Phiếu Phổ Biến

### Ngân Hàng (Banking)
```
VCB.VN  - Vietcombank (Ngân hàng Ngoại thương)
CTG.VN  - VietinBank (Ngân hàng Công Thương)
BID.VN  - BIDV (Ngân hàng Đầu tư và Phát triển)
TCB.VN  - Techcombank (Ngân hàng Kỹ Thương)
MBB.VN  - MBBank (Ngân hàng Quân Đội)
ACB.VN  - ACB (Ngân hàng Á Châu)
VPB.VN  - VPBank (Ngân hàng Việt Nam Thịnh Vượng)
```

### Công Nghệ (Technology)
```
FPT.VN  - FPT Corporation
```

### Bất Động Sản (Real Estate)
```
VIC.VN  - Vingroup
VHM.VN  - Vinhomes
NVL.VN  - Novaland
VRE.VN  - Vincom Retail
```

### Sản Xuất (Manufacturing)
```
HPG.VN  - Hòa Phát (Thép)
GAS.VN  - PV Gas (Khí đốt)
MSN.VN  - Masan Group
VHC.VN  - Vinalines Container
```

### Bán Lẻ (Retail)
```
MWG.VN  - Thế Giới Di Động
FRT.VN  - FPT Retail
```

### Hàng Tiêu Dùng (Consumer Goods)
```
VNM.VN  - Vinamilk
SAB.VN  - Sabeco
```

### Chứng Khoán (Securities)
```
SSI.VN  - SSI
VND.VN  - VNDirect
HCM.VN  - Chứng khoán TPHCM
```

📄 **Xem chi tiết**: `config/vietnam_stocks.yaml`

---

## 🎓 Ví Dụ Thực Tế

### Ví Dụ 1: Phân Tích VCB (Vietcombank)

```bash
# Bước 1: Tải dữ liệu 5 năm
python scripts/download_historical_data.py --symbols VCB.VN --period 5y

# Bước 2: Huấn luyện mô hình
python scripts/train_models.py --symbol VCB.VN --models lstm,gru,arima

# Bước 3: Chạy backtest
python scripts/run_backtest.py --symbol VCB.VN --start 2023-01-01 --end 2024-01-01

# Bước 4: Xem kết quả trong logs/ và models/
```

### Ví Dụ 2: Danh Mục Ngân Hàng

```bash
# Tải dữ liệu các ngân hàng lớn
python scripts/download_historical_data.py \
  --symbols VCB.VN,CTG.VN,BID.VN,TCB.VN,MBB.VN \
  --period 2y

# Huấn luyện mô hình cho từng cổ phiếu
python scripts/train_models.py --symbol VCB.VN --models lstm
python scripts/train_models.py --symbol CTG.VN --models lstm
python scripts/train_models.py --symbol BID.VN --models lstm
python scripts/train_models.py --symbol TCB.VN --models lstm
python scripts/train_models.py --symbol MBB.VN --models lstm
```

### Ví Dụ 3: So Sánh FPT với Tech Stocks Mỹ

```bash
# Tải cả cổ phiếu Việt Nam và Mỹ
python scripts/download_historical_data.py \
  --symbols FPT.VN,AAPL,MSFT,GOOGL \
  --period 2y

# Phân tích từng cổ phiếu
python scripts/train_models.py --symbol FPT.VN --models lstm,gru
python scripts/train_models.py --symbol AAPL --models lstm,gru
```

### Ví Dụ 4: Chiến Lược Đa Dạng Hóa

```bash
# Danh mục đa dạng ngành
python scripts/download_historical_data.py \
  --symbols VCB.VN,FPT.VN,VNM.VN,VHM.VN,HPG.VN,GAS.VN,MWG.VN,SSI.VN \
  --period 2y

# Backtest từng mã
for symbol in VCB.VN FPT.VN VNM.VN VHM.VN HPG.VN GAS.VN MWG.VN SSI.VN
do
  python scripts/train_models.py --symbol $symbol --models lstm
  python scripts/run_backtest.py --symbol $symbol --start 2023-01-01 --end 2024-01-01
done
```

---

## ⚠️ Lưu Ý Quan Trọng

### Về Thị Trường Việt Nam

1. **Biên Độ Giao Dịch**
   - Hầu hết cổ phiếu: ±7% mỗi phiên
   - Một số cổ phiếu: ±10%
   - Giá tham chiếu = giá đóng cửa phiên trước

2. **Giờ Giao Dịch**
   - Buổi sáng: 09:00 - 11:30
   - Buổi chiều: 13:00 - 14:45
   - Múi giờ: UTC+7 (Giờ Việt Nam)

3. **Thanh Toán**
   - T+2: Thanh toán sau 2 ngày làm việc
   - Cần đủ tiền trong tài khoản khi đặt lệnh

4. **Room Ngoại**
   - Giới hạn sở hữu nước ngoài: thường 30-49%
   - Kiểm tra room trước khi giao dịch

5. **Đơn Vị Giao Dịch**
   - Lô chẵn: 100 cổ phiếu
   - Lô lẻ: 10 cổ phiếu

### Về Dữ Liệu

6. **Yahoo Finance**
   - Dữ liệu có thể có độ trễ
   - Nên cross-check với nguồn khác
   - Không phải tất cả mã đều có dữ liệu đầy đủ

7. **Chất Lượng Dữ Liệu**
   - Luôn kiểm tra dữ liệu sau khi tải
   - Chú ý các ngày nghỉ lễ
   - Xem xét tính liên tục của dữ liệu

### Về Giao Dịch

8. **Rủi Ro**
   ⚠️ **CẢNH BÁO**:
   - Hệ thống này CHỈ phục vụ mục đích học tập và nghiên cứu
   - KHÔNG bảo đảm lợi nhuận
   - Kết quả quá khứ KHÔNG đại diện cho tương lai
   - Luôn tham khảo chuyên gia tài chính
   - Chỉ đầu tư số tiền bạn có thể chấp nhận mất

9. **Trước Khi Giao Dịch Thực**
   - Test kỹ trên dữ liệu lịch sử
   - Hiểu rõ các chỉ báo kỹ thuật
   - Đặt stop-loss hợp lý
   - Quản lý vốn cẩn thận
   - Không all-in vào một mã

10. **Thuế và Phí**
    - Phí giao dịch: thường 0.15% - 0.3%
    - Thuế: 0.1% giá trị bán
    - Tính toán phí khi backtest

---

## 📚 Tài Liệu Tham Khảo

### File Cấu Hình
- `config/config.yaml` - Cấu hình chung
- `config/vietnam_stocks.yaml` - Danh sách cổ phiếu Việt Nam
- `config/model_config.yaml` - Tham số mô hình
- `config/trading_config.yaml` - Tham số giao dịch

### Scripts
- `scripts/download_historical_data.py` - Tải dữ liệu
- `scripts/train_models.py` - Huấn luyện mô hình
- `scripts/run_backtest.py` - Chạy backtest
- `scripts/test_vietnamese_stocks.py` - Test hệ thống

### Tài Liệu Khác
- `README.md` - Hướng dẫn tổng quan (English)
- `SYSTEM_DESIGN.md` - Thiết kế hệ thống
- `RISK_DISCLOSURE.md` - Cảnh báo rủi ro

---

## 🔧 Xử Lý Sự Cố

### Lỗi: "No module named 'yfinance'"
```bash
pip install yfinance
```

### Lỗi: "No data found for symbol"
- Kiểm tra mã cổ phiếu có đúng không (phải có .VN hoặc .HNX)
- Thử mã khác để kiểm tra kết nối
- Kiểm tra internet connection

### Lỗi: "Failed to fetch data"
- Yahoo Finance có thể bị block tạm thời
- Thử lại sau 5-10 phút
- Kiểm tra firewall/proxy

### Dữ Liệu Thiếu/Không Đầy Đủ
- Một số mã mới có thể không có dữ liệu lịch sử đầy đủ
- Giảm `period` xuống (ví dụ: từ 5y xuống 1y)
- Chọn các blue-chip stocks (VCB, FPT, CTG, etc.)

---

## 💬 Hỗ Trợ

Nếu gặp vấn đề:
1. Xem phần [Xử Lý Sự Cố](#xử-lý-sự-cố) ở trên
2. Kiểm tra logs trong thư mục `logs/`
3. Đọc tài liệu chi tiết trong `README.md`
4. Tạo issue trên GitHub repository

---

## ✅ Checklist Bắt Đầu

- [ ] Cài đặt Python 3.8+
- [ ] Clone repository
- [ ] Cài đặt dependencies (`pip install -r requirements.txt`)
- [ ] Chạy test script (`python scripts/test_vietnamese_stocks.py`)
- [ ] Tải dữ liệu mẫu cho 1-2 cổ phiếu
- [ ] Thử huấn luyện mô hình đơn giản
- [ ] Chạy backtest đơn giản
- [ ] Đọc kỹ cảnh báo rủi ro

---

## 🎯 Bước Tiếp Theo

Sau khi làm quen với hệ thống:

1. **Tìm Hiểu Sâu Hơn**
   - Đọc về các chỉ báo kỹ thuật (RSI, MACD, Bollinger Bands)
   - Tìm hiểu về các mô hình ML (LSTM, GRU, ARIMA)
   - Học về quản lý rủi ro và vốn

2. **Thử Nghiệm**
   - Test nhiều chiến lược khác nhau
   - So sánh hiệu suất các mô hình
   - Tối ưu hóa tham số

3. **Mở Rộng**
   - Thêm các chỉ báo tùy chỉnh
   - Tích hợp dữ liệu từ nguồn khác
   - Phát triển chiến lược riêng

---

**Chúc bạn đầu tư thành công! 🚀📈**

*Nhớ: Luôn quản lý rủi ro và chỉ đầu tư số tiền bạn có thể chấp nhận mất.*
