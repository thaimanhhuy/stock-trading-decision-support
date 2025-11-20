"""Streamlit dashboard application."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
import os
from typing import Optional, Dict, Any

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Stock Trading Dashboard",
    page_icon="📈",
    layout="wide",
)


# ========== API Integration Functions ==========

def check_api_health() -> bool:
    """Check if API is healthy and reachable.

    Returns:
        bool: True if API is healthy, False otherwise
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_prediction(symbol: str) -> Optional[Dict[str, Any]]:
    """Get prediction for a symbol from API.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        Dict with prediction data or None if failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/predictions/{symbol}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to fetch prediction for {symbol}: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def get_signal(symbol: str) -> Optional[Dict[str, Any]]:
    """Get trading signal for a symbol from API.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        Dict with signal data or None if failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/signals/{symbol}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to fetch signal for {symbol}: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def get_multiple_signals(symbols: list) -> pd.DataFrame:
    """Get trading signals for multiple symbols.

    Args:
        symbols: List of stock symbols

    Returns:
        DataFrame with signals data
    """
    signals_data = []

    for symbol in symbols:
        signal_data = get_signal(symbol)
        if signal_data:
            signals_data.append({
                "Symbol": signal_data.get("symbol", symbol),
                "Signal": signal_data.get("signal", "N/A").upper(),
                "Strength": signal_data.get("strength", 0.0),
                "Current": signal_data.get("target_price", 0.0) / 1.03,  # Approximate current
                "Target": signal_data.get("target_price", 0.0),
                "Stop Loss": signal_data.get("stop_loss", 0.0),
                "Take Profit": signal_data.get("take_profit", 0.0),
            })

    return pd.DataFrame(signals_data) if signals_data else pd.DataFrame()


def get_portfolio_summary() -> Optional[Dict[str, Any]]:
    """Get portfolio summary from API.

    Returns:
        Dict with portfolio summary or None if failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/portfolio/summary",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to fetch portfolio summary: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def get_portfolio_positions() -> pd.DataFrame:
    """Get portfolio positions from API.

    Returns:
        DataFrame with positions
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/portfolio/positions",
            timeout=10
        )
        response.raise_for_status()
        positions = response.json()

        if positions:
            return pd.DataFrame(positions)
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to fetch positions: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return pd.DataFrame()


def get_performance_metrics() -> Optional[Dict[str, Any]]:
    """Get performance metrics from API.

    Returns:
        Dict with performance metrics or None if failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/portfolio/performance",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to fetch performance metrics: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


# ========== Initialize Session State ==========

if "api_health" not in st.session_state:
    st.session_state.api_health = check_api_health()

if "default_symbols" not in st.session_state:
    st.session_state.default_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]


# ========== Title and Sidebar ==========

st.title("📈 Stock Trading Decision Support Dashboard")

# Check API connection status
if not st.session_state.api_health:
    st.error(
        f"⚠️ Cannot connect to API at {API_BASE_URL}. "
        "Please ensure the API service is running."
    )
    if st.button("Retry Connection"):
        st.session_state.api_health = check_api_health()
        st.rerun()

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Home", "Predictions", "Signals", "Performance", "Monitoring"]
)

# API Status indicator in sidebar
api_status = "🟢 Connected" if st.session_state.api_health else "🔴 Disconnected"
st.sidebar.markdown(f"**API Status:** {api_status}")
st.sidebar.markdown(f"**API URL:** `{API_BASE_URL}`")


# ========== Home Page ==========

if page == "Home":
    st.header("Welcome to the Stock Trading Decision Support System")

    st.info(
        "This dashboard provides real-time stock predictions and trading signals "
        "powered by LSTM and GRU machine learning models."
    )

    # Fetch portfolio summary
    if st.session_state.api_health:
        with st.spinner("Fetching portfolio summary..."):
            portfolio_summary = get_portfolio_summary()

            if portfolio_summary:
                col1, col2, col3 = st.columns(3)

                with col1:
                    total_value = portfolio_summary.get("total_value", 0)
                    total_return_pct = portfolio_summary.get("total_return_percent", 0)
                    st.metric(
                        "Portfolio Value",
                        f"${total_value:,.2f}",
                        f"{total_return_pct:+.2f}%"
                    )

                with col2:
                    total_return = portfolio_summary.get("total_return", 0)
                    st.metric(
                        "Total Return",
                        f"${total_return:,.2f}",
                        f"{total_return_pct:+.2f}%"
                    )

                with col3:
                    positions_count = portfolio_summary.get("positions_count", 0)
                    st.metric("Active Positions", positions_count)
            else:
                st.warning("⚠️ Unable to fetch portfolio summary")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Portfolio Value", "$0.00", "0.0%")
            st.caption("⚠️ API not connected")

        with col2:
            st.metric("Total Return", "$0.00")
            st.caption("⚠️ API not connected")

        with col3:
            st.metric("Active Positions", "0")
            st.caption("⚠️ API not connected")

    st.subheader("Recent Signals")

    if st.session_state.api_health:
        with st.spinner("Fetching recent signals..."):
            # Fetch signals for default symbols
            signals_df = get_multiple_signals(st.session_state.default_symbols[:3])

            if not signals_df.empty:
                # Display only key columns on home page
                display_df = signals_df[["Symbol", "Signal", "Strength", "Target"]]
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("⚠️ No signals available. API may be using placeholder data.")
    else:
        st.error("❌ Cannot fetch signals. API is not connected.")


# ========== Predictions Page ==========

elif page == "Predictions":
    st.header("Price Predictions")

    st.info(
        "Enter a stock symbol to get ML-powered price predictions. "
        "Supports US stocks (e.g., AAPL) and Vietnamese stocks (e.g., VCB.VN)."
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        symbol = st.text_input(
            "Enter Symbol",
            value="AAPL",
            placeholder="E.g., AAPL, MSFT, GOOGL, VCB.VN"
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        predict_button = st.button("Get Prediction", type="primary")

    if predict_button:
        if not st.session_state.api_health:
            st.error("❌ API is not connected. Please check the connection.")
        elif not symbol.strip():
            st.warning("⚠️ Please enter a valid stock symbol.")
        else:
            with st.spinner(f"Fetching prediction for {symbol.upper()}..."):
                prediction = get_prediction(symbol.upper())

                if prediction:
                    st.success(f"✅ Prediction for {prediction['symbol']}")

                    # Calculate metrics
                    current_price = prediction.get("current_price", 0.0)
                    predicted_price = prediction.get("predicted_price", 0.0)
                    confidence = prediction.get("confidence", 0.0)

                    # Calculate change percentage
                    if current_price > 0:
                        change_pct = ((predicted_price - current_price) / current_price) * 100
                        direction = "UP ↑" if change_pct > 0 else "DOWN ↓"
                        direction_delta = f"+{change_pct:.2f}%" if change_pct > 0 else f"{change_pct:.2f}%"
                    else:
                        change_pct = 0
                        direction = "N/A"
                        direction_delta = "0%"

                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Current Price", f"${current_price:.2f}")

                    with col2:
                        st.metric(
                            "Predicted Price",
                            f"${predicted_price:.2f}",
                            direction_delta
                        )

                    with col3:
                        st.metric("Confidence", f"{confidence * 100:.1f}%")

                    with col4:
                        st.metric("Direction", direction)

                    # Timestamp
                    st.caption(f"Prediction time: {prediction.get('timestamp', 'N/A')}")

                    # Warning about placeholder data
                    if current_price == 150.0 and predicted_price == 155.0:
                        st.warning(
                            "⚠️ **Note:** This is placeholder data from the API. "
                            "The prediction models are not yet fully integrated."
                        )


# ========== Signals Page ==========

elif page == "Signals":
    st.header("Trading Signals")

    st.info(
        "Real-time trading signals based on model predictions and technical analysis. "
        "Signals include entry/exit recommendations and risk management levels."
    )

    # Symbol input
    st.subheader("Get Signals for Multiple Symbols")

    symbols_input = st.text_input(
        "Enter symbols (comma-separated)",
        value=", ".join(st.session_state.default_symbols),
        placeholder="E.g., AAPL, MSFT, GOOGL"
    )

    if st.button("Fetch Signals", type="primary"):
        if not st.session_state.api_health:
            st.error("❌ API is not connected. Please check the connection.")
        else:
            # Parse symbols
            symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

            if not symbols:
                st.warning("⚠️ Please enter at least one symbol.")
            else:
                with st.spinner(f"Fetching signals for {len(symbols)} symbols..."):
                    signals_df = get_multiple_signals(symbols)

                    if not signals_df.empty:
                        st.success(f"✅ Fetched {len(signals_df)} signals")

                        # Display signals table
                        st.dataframe(signals_df, use_container_width=True)

                        # Signal distribution
                        st.subheader("Signal Distribution")
                        signal_counts = signals_df["Signal"].value_counts()

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            buy_count = signal_counts.get("BUY", 0)
                            st.metric("BUY Signals", buy_count)

                        with col2:
                            hold_count = signal_counts.get("HOLD", 0)
                            st.metric("HOLD Signals", hold_count)

                        with col3:
                            sell_count = signal_counts.get("SELL", 0)
                            st.metric("SELL Signals", sell_count)

                        # Warning about placeholder data
                        if len(signals_df) > 0 and signals_df.iloc[0]["Signal"] == "BUY":
                            st.warning(
                                "⚠️ **Note:** API is using placeholder data. "
                                "Signal generation logic is not yet fully integrated."
                            )
                    else:
                        st.error("❌ Failed to fetch signals. Please try again.")


# ========== Performance Page ==========

elif page == "Performance":
    st.header("Performance Metrics")

    if st.session_state.api_health:
        with st.spinner("Fetching performance metrics..."):
            portfolio_summary = get_portfolio_summary()
            performance_metrics = get_performance_metrics()

            if portfolio_summary and performance_metrics:
                # Key metrics row
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    total_return_pct = portfolio_summary.get("total_return_percent", 0)
                    st.metric("Total Return", f"{total_return_pct:.2f}%")

                with col2:
                    sharpe_ratio = performance_metrics.get("sharpe_ratio", 0)
                    st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")

                with col3:
                    max_drawdown = performance_metrics.get("max_drawdown", 0)
                    st.metric("Max Drawdown", f"{max_drawdown:.2f}%")

                with col4:
                    win_rate = performance_metrics.get("win_rate", 0)
                    st.metric("Win Rate", f"{win_rate:.1%}")

                # Portfolio breakdown
                st.subheader("Portfolio Breakdown")
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Cash", f"${portfolio_summary.get('cash', 0):,.2f}")
                    st.metric("Equity Value", f"${portfolio_summary.get('equity', 0):,.2f}")

                with col2:
                    st.metric("Total Value", f"${portfolio_summary.get('total_value', 0):,.2f}")
                    st.metric("Unrealized P&L", f"${portfolio_summary.get('unrealized_pnl', 0):,.2f}")

                # Positions table
                st.subheader("Current Positions")
                positions_df = get_portfolio_positions()

                if not positions_df.empty:
                    # Format numeric columns
                    display_df = positions_df.copy()
                    display_df['entry_price'] = display_df['entry_price'].apply(lambda x: f"${x:.2f}")
                    display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:.2f}")
                    display_df['current_value'] = display_df['current_value'].apply(lambda x: f"${x:,.2f}")
                    display_df['unrealized_pnl'] = display_df['unrealized_pnl'].apply(lambda x: f"${x:+,.2f}")
                    display_df['unrealized_pnl_percent'] = display_df['unrealized_pnl_percent'].apply(lambda x: f"{x:+.2f}%")

                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.info("No active positions")

                # Trading activity
                st.subheader("Trading Activity")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Trades", portfolio_summary.get("total_trades", 0))

                with col2:
                    st.metric("Buy Trades", portfolio_summary.get("buy_trades", 0))

                with col3:
                    st.metric("Sell Trades", portfolio_summary.get("sell_trades", 0))

                # Note about chart
                st.info("📊 **Historical portfolio value chart** requires tracking daily snapshots and will be implemented in future updates.")

            else:
                st.warning("⚠️ Unable to fetch performance data")
    else:
        st.error("❌ API not connected. Cannot fetch performance metrics.")


# ========== Monitoring Page ==========

elif page == "Monitoring":
    st.header("System Monitoring")

    # Check API health
    current_health = check_api_health()

    if current_health:
        st.success("✅ System Health: All systems operational")
    else:
        st.error("❌ System Health: API service is unreachable")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("API Status")
        st.info(f"Endpoint: {API_BASE_URL}")

        if current_health:
            st.success("✅ API: Healthy")
        else:
            st.error("🔴 API: Unreachable")

        if st.button("Refresh API Status"):
            st.session_state.api_health = check_api_health()
            st.rerun()

    with col2:
        st.subheader("Trained Models")

        if st.session_state.api_health:
            try:
                response = requests.get(f"{API_BASE_URL}/api/v1/monitoring/models", timeout=10)
                if response.status_code == 200:
                    models_data = response.json()

                    if models_data.get("exists"):
                        st.metric("Total Symbols", models_data.get("total_symbols", 0))
                        st.metric("Total Model Files", models_data.get("total_files", 0))

                        # Show symbols with models
                        if models_data.get("models"):
                            symbols = [m["symbol"] for m in models_data["models"]]
                            st.caption(f"Symbols: {', '.join(symbols[:5])}")
                    else:
                        st.warning("No trained models found")
                else:
                    st.error("Failed to fetch models status")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.caption("⚠️ API not connected")

    # System Metrics
    st.subheader("System Metrics")

    if st.session_state.api_health:
        try:
            response = requests.get(f"{API_BASE_URL}/api/v1/monitoring/system", timeout=10)
            if response.status_code == 200:
                system_data = response.json()

                col1, col2, col3 = st.columns(3)

                with col1:
                    cpu_percent = system_data.get("cpu", {}).get("percent", 0)
                    st.metric("CPU Usage", f"{cpu_percent:.1f}%")

                with col2:
                    memory_percent = system_data.get("memory", {}).get("percent", 0)
                    st.metric("Memory Usage", f"{memory_percent:.1f}%")

                with col3:
                    disk_percent = system_data.get("disk", {}).get("percent", 0)
                    st.metric("Disk Usage", f"{disk_percent:.1f}%")

                # Detailed system info
                with st.expander("System Details"):
                    st.json(system_data)
            else:
                st.warning("Unable to fetch system metrics")
        except Exception as e:
            st.error(f"Error fetching system metrics: {str(e)}")
    else:
        st.caption("⚠️ API not connected")

    # Data Quality Check
    st.subheader("Data Quality Check")

    if st.session_state.api_health:
        symbol_to_check = st.text_input("Enter symbol to check data quality", value="AAPL")

        if st.button("Check Data Quality"):
            with st.spinner(f"Checking data quality for {symbol_to_check}..."):
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/api/v1/monitoring/data-quality/{symbol_to_check.upper()}",
                        timeout=15
                    )
                    if response.status_code == 200:
                        quality_data = response.json()

                        status = quality_data.get("status", "unknown")
                        quality_score = quality_data.get("quality_score", 0)

                        if status == "healthy":
                            st.success(f"✅ Data Quality: {status.upper()} (Score: {quality_score:.1f}/100)")
                        else:
                            st.warning(f"⚠️ Data Quality: {status.upper()} (Score: {quality_score:.1f}/100)")

                        # Show metrics
                        metrics = quality_data.get("metrics", {})
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Total Rows", metrics.get("total_rows", 0))

                        with col2:
                            st.metric("Missing Values", metrics.get("missing_values", 0))

                        with col3:
                            completeness = metrics.get("completeness_percent", 0)
                            st.metric("Completeness", f"{completeness:.1f}%")

                        # Date range
                        date_range = metrics.get("date_range", {})
                        st.caption(f"Data range: {date_range.get('start')} to {date_range.get('end')}")
                    else:
                        st.error("Failed to check data quality")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.caption("⚠️ API not connected")

    # System Information
    st.subheader("System Information")
    st.code(f"""
API Base URL: {API_BASE_URL}
Dashboard Version: 1.0.0
Current Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
API Status: {"Connected" if st.session_state.api_health else "Disconnected"}
    """)


# ========== Footer ==========

st.sidebar.markdown("---")
st.sidebar.info("⚠️ For educational purposes only. Not financial advice.")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
