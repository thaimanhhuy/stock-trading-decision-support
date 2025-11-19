#!/usr/bin/env python3
"""Test script for Vietnamese stocks data fetching.

Script kiểm tra tải dữ liệu cổ phiếu Việt Nam.

This script demonstrates how to fetch and validate Vietnamese stock data
from Yahoo Finance using the .VN suffix for HOSE stocks.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion.yahoo_fetcher import YahooDataFetcher
from src.data_ingestion.data_validator import DataValidator
from src.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def test_vietnamese_stocks():
    """Test fetching Vietnamese stock data.

    Kiểm tra tải dữ liệu cổ phiếu Việt Nam.
    """
    # Vietnamese stocks to test
    # Các mã cổ phiếu Việt Nam để test
    test_stocks = {
        "VCB.VN": "Vietcombank - Ngân hàng TMCP Ngoại thương Việt Nam",
        "FPT.VN": "FPT Corporation - Tập đoàn FPT",
        "CTG.VN": "VietinBank - Ngân hàng TMCP Công Thương Việt Nam",
        "NVL.VN": "Novaland - Tập đoàn Đầu tư Địa ốc No Va",
        "HPG.VN": "Hoa Phat Group - Tập đoàn Hòa Phát",
    }

    fetcher = YahooDataFetcher()
    validator = DataValidator()

    print("\n" + "="*80)
    print("KIỂM TRA DỮ LIỆU CỔ PHIẾU VIỆT NAM")
    print("TESTING VIETNAMESE STOCK DATA FETCHING")
    print("="*80 + "\n")

    results = {}

    for symbol, name in test_stocks.items():
        print(f"\n📊 Testing: {symbol} - {name}")
        print("-" * 80)

        try:
            # Fetch data for last 30 days
            logger.info(f"Fetching data for {symbol}")
            data = fetcher.fetch_data(symbol, period="1mo")

            if data is not None and not data.empty:
                # Validate data
                validated_data = validator.validate(data, symbol)

                # Get latest data
                latest = validated_data.iloc[-1]

                print(f"✅ SUCCESS / THÀNH CÔNG")
                print(f"   Records fetched: {len(validated_data)}")
                print(f"   Date range: {validated_data['date'].min()} to {validated_data['date'].max()}")
                print(f"   Latest close: {latest['close']:,.2f} VND")
                print(f"   Latest volume: {latest['volume']:,.0f}")

                # Calculate basic statistics
                avg_volume = validated_data['volume'].mean()
                price_change = ((latest['close'] - validated_data['close'].iloc[0]) /
                               validated_data['close'].iloc[0] * 100)

                print(f"   Average volume: {avg_volume:,.0f}")
                print(f"   Price change: {price_change:+.2f}%")

                results[symbol] = {
                    'status': 'success',
                    'records': len(validated_data),
                    'latest_close': latest['close'],
                    'price_change_pct': price_change
                }
            else:
                print(f"❌ FAILED / THẤT BẠI: No data returned")
                results[symbol] = {'status': 'no_data'}

        except Exception as e:
            print(f"❌ ERROR / LỖI: {str(e)}")
            logger.error(f"Failed to fetch {symbol}: {e}")
            results[symbol] = {'status': 'error', 'message': str(e)}

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY / TÓM TẮT")
    print("="*80)

    successful = sum(1 for r in results.values() if r.get('status') == 'success')
    failed = len(results) - successful

    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")

    if successful > 0:
        print("\n📈 Successfully fetched stocks:")
        for symbol, result in results.items():
            if result.get('status') == 'success':
                print(f"   {symbol}: {result['records']} records, "
                      f"Latest: {result['latest_close']:,.2f} VND, "
                      f"Change: {result['price_change_pct']:+.2f}%")

    if failed > 0:
        print("\n❌ Failed stocks:")
        for symbol, result in results.items():
            if result.get('status') != 'success':
                print(f"   {symbol}: {result.get('message', result.get('status'))}")

    print("\n" + "="*80)
    print("TEST COMPLETED / HOÀN THÀNH KIỂM TRA")
    print("="*80 + "\n")

    return results


def test_portfolio_download():
    """Test downloading a Vietnamese stock portfolio.

    Kiểm tra tải danh mục cổ phiếu Việt Nam.
    """
    print("\n" + "="*80)
    print("PORTFOLIO DOWNLOAD TEST")
    print("KIỂM TRA TẢI DANH MỤC ĐẦU TƯ")
    print("="*80 + "\n")

    # Banking sector portfolio
    banking_portfolio = [
        "VCB.VN",  # Vietcombank
        "CTG.VN",  # VietinBank
        "BID.VN",  # BIDV
        "TCB.VN",  # Techcombank
        "MBB.VN",  # MBBank
    ]

    fetcher = YahooDataFetcher()

    print(f"Downloading {len(banking_portfolio)} banking stocks...")
    print(f"Đang tải {len(banking_portfolio)} cổ phiếu ngân hàng...\n")

    # Fetch all stocks
    results = fetcher.fetch_multiple(banking_portfolio, period="1mo")

    print(f"\n✅ Successfully downloaded: {len(results)}/{len(banking_portfolio)} stocks")
    print(f"✅ Đã tải thành công: {len(results)}/{len(banking_portfolio)} cổ phiếu\n")

    for symbol, data in results.items():
        if not data.empty:
            latest_close = data['close'].iloc[-1]
            print(f"   {symbol}: {len(data)} records, Latest: {latest_close:,.2f} VND")

    return results


def main():
    """Main function."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           VIETNAMESE STOCK MARKET DATA FETCHING TEST                       ║
║           KIỂM TRA TẢI DỮ LIỆU THỊ TRƯỜNG CHỨNG KHOÁN VIỆT NAM            ║
║                                                                            ║
║  This script tests the ability to fetch Vietnamese stock data from        ║
║  Yahoo Finance using the .VN suffix.                                      ║
║                                                                            ║
║  Script này kiểm tra khả năng tải dữ liệu cổ phiếu Việt Nam từ           ║
║  Yahoo Finance sử dụng định dạng .VN                                      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Test 1: Individual stock fetching
        print("\n🔍 TEST 1: Individual Stock Fetching")
        print("🔍 KIỂM TRA 1: Tải dữ liệu từng cổ phiếu\n")
        individual_results = test_vietnamese_stocks()

        # Test 2: Portfolio fetching
        print("\n🔍 TEST 2: Portfolio Fetching")
        print("🔍 KIỂM TRA 2: Tải danh mục đầu tư\n")
        portfolio_results = test_portfolio_download()

        # Overall summary
        print("\n" + "="*80)
        print("OVERALL SUMMARY / TỔNG KẾT CHUNG")
        print("="*80)
        print("\n✅ All tests completed successfully!")
        print("✅ Tất cả các kiểm tra đã hoàn thành thành công!")
        print("\nThe system is ready to work with Vietnamese stocks.")
        print("Hệ thống đã sẵn sàng làm việc với cổ phiếu Việt Nam.\n")

        print("Next steps / Các bước tiếp theo:")
        print("1. Use download_historical_data.py to download Vietnamese stocks")
        print("   Sử dụng download_historical_data.py để tải dữ liệu cổ phiếu Việt Nam")
        print("\n2. Example command / Ví dụ lệnh:")
        print("   python scripts/download_historical_data.py --symbols VCB.VN,FPT.VN --period 2y")
        print("\n3. Train models with Vietnamese stocks:")
        print("   Huấn luyện mô hình với cổ phiếu Việt Nam:")
        print("   python scripts/train_model.py --symbols VCB.VN --models lstm,gru")
        print()

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed with error: {e}")
        print(f"❌ Kiểm tra thất bại với lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
