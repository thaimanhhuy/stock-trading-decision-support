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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Portfolio Value", "$100,000", "+5.2%")
        st.caption("⚠️ Demo value - Not connected to live portfolio")

    with col2:
        st.metric("Total Return", "15.6%", "+2.1%")
        st.caption("⚠️ Demo value")

    with col3:
        st.metric("Active Positions", "5", "+1")
        st.caption("⚠️ Demo value")

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

    st.warning(
        "⚠️ **Portfolio performance tracking is not yet implemented.** "
        "The charts below show sample data for demonstration purposes."
    )

    # Sample data for demonstration
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    portfolio_values = pd.Series(
        100000 * (1 + pd.Series(range(100)) * 0.001),
        index=dates
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=portfolio_values,
            mode="lines",
            name="Portfolio Value",
            line=dict(color="#1f77b4", width=2)
        )
    )
    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Return", "15.6%")
        st.caption("⚠️ Demo value")

    with col2:
        st.metric("Sharpe Ratio", "1.23")
        st.caption("⚠️ Demo value")

    with col3:
        st.metric("Max Drawdown", "-8.5%")
        st.caption("⚠️ Demo value")


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
        st.subheader("Model Status")
        st.info("LSTM: ✅ Loaded")
        st.info("GRU: ✅ Loaded")
        st.caption("⚠️ Model status monitoring not yet implemented")

    st.subheader("Data Status")
    st.info("Last Update: 2024-01-15 10:30:00")
    st.info("Data Quality: ✅ Good")
    st.info("Drift Detected: ❌ No")
    st.caption("⚠️ Real-time data monitoring not yet implemented")

    # System info
    st.subheader("System Information")
    st.code(f"""
API Base URL: {API_BASE_URL}
Dashboard Version: 1.0.0
Current Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """)


# ========== Footer ==========

st.sidebar.markdown("---")
st.sidebar.info("⚠️ For educational purposes only. Not financial advice.")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
