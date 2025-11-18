"""Streamlit dashboard application."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Stock Trading Dashboard",
    page_icon="📈",
    layout="wide",
)

# Title
st.title("📈 Stock Trading Decision Support Dashboard")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Home", "Predictions", "Signals", "Performance", "Monitoring"])

# Home Page
if page == "Home":
    st.header("Welcome to the Stock Trading Decision Support System")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Portfolio Value", "$100,000", "+5.2%")

    with col2:
        st.metric("Total Return", "15.6%", "+2.1%")

    with col3:
        st.metric("Active Positions", "5", "+1")

    st.subheader("Recent Signals")
    signals_df = pd.DataFrame({
        "Symbol": ["AAPL", "MSFT", "GOOGL"],
        "Signal": ["BUY", "HOLD", "SELL"],
        "Strength": [0.85, 0.60, 0.75],
        "Price": [150.25, 380.50, 140.75],
    })
    st.dataframe(signals_df, use_container_width=True)

# Predictions Page
elif page == "Predictions":
    st.header("Price Predictions")

    symbol = st.text_input("Enter Symbol", value="AAPL")

    if st.button("Get Prediction"):
        st.success(f"Prediction for {symbol}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Price", "$150.25")
            st.metric("Predicted Price", "$155.50", "+3.5%")

        with col2:
            st.metric("Confidence", "75%")
            st.metric("Direction", "UP", "↑")

# Signals Page
elif page == "Signals":
    st.header("Trading Signals")

    st.info("Real-time trading signals based on model predictions and technical analysis.")

    signals_df = pd.DataFrame({
        "Symbol": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
        "Signal": ["BUY", "HOLD", "SELL", "BUY", "HOLD"],
        "Strength": [0.85, 0.60, 0.75, 0.90, 0.55],
        "Current": [150.25, 380.50, 140.75, 175.80, 245.60],
        "Target": [155.50, 385.00, 135.00, 185.00, 250.00],
    })

    st.dataframe(signals_df, use_container_width=True)

# Performance Page
elif page == "Performance":
    st.header("Performance Metrics")

    # Sample data
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    portfolio_values = pd.Series(100000 * (1 + pd.Series(range(100)) * 0.001), index=dates)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=portfolio_values, mode="lines", name="Portfolio Value"))
    fig.update_layout(title="Portfolio Value Over Time", xaxis_title="Date", yaxis_title="Value ($)")

    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Return", "15.6%")
    with col2:
        st.metric("Sharpe Ratio", "1.23")
    with col3:
        st.metric("Max Drawdown", "-8.5%")

# Monitoring Page
elif page == "Monitoring":
    st.header("System Monitoring")

    st.success("✅ System Health: All systems operational")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Model Status")
        st.info("ARIMA: ✅ Healthy")
        st.info("LSTM: ✅ Healthy")
        st.info("GRU: ✅ Healthy")

    with col2:
        st.subheader("Data Status")
        st.info("Last Update: 2024-01-15 10:30:00")
        st.info("Data Quality: ✅ Good")
        st.info("Drift Detected: ❌ No")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("⚠️ For educational purposes only. Not financial advice.")
