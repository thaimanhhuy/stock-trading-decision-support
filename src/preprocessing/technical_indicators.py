"""Technical indicators calculation."""

import pandas as pd
import numpy as np
from src.utils.logger import LoggerMixin


class TechnicalIndicators(LoggerMixin):
    """Calculate technical indicators for stock data."""

    def calculate_sma(self, data: pd.DataFrame, period: int = 20, column: str = "close") -> pd.Series:
        """Calculate Simple Moving Average."""
        return data[column].rolling(window=period).mean()

    def calculate_ema(self, data: pd.DataFrame, period: int = 20, column: str = "close") -> pd.Series:
        """Calculate Exponential Moving Average."""
        return data[column].ewm(span=period, adjust=False).mean()

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14, column: str = "close") -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = data[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, column: str = "close") -> pd.DataFrame:
        """Calculate MACD."""
        ema_fast = data[column].ewm(span=fast, adjust=False).mean()
        ema_slow = data[column].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return pd.DataFrame({"macd": macd, "signal": signal_line, "histogram": histogram})

    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: float = 2, column: str = "close") -> pd.DataFrame:
        """Calculate Bollinger Bands."""
        sma = data[column].rolling(window=period).mean()
        std = data[column].rolling(window=period).std()
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        return pd.DataFrame({"bb_middle": sma, "bb_upper": upper, "bb_lower": lower})

    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high_low = data["high"] - data["low"]
        high_close = (data["high"] - data["close"].shift()).abs()
        low_close = (data["low"] - data["close"].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def add_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to dataframe."""
        df = data.copy()

        # Moving averages
        df["sma_20"] = self.calculate_sma(df, 20)
        df["sma_50"] = self.calculate_sma(df, 50)
        df["ema_12"] = self.calculate_ema(df, 12)
        df["ema_26"] = self.calculate_ema(df, 26)

        # Momentum
        df["rsi"] = self.calculate_rsi(df)

        # MACD
        macd_data = self.calculate_macd(df)
        df["macd"] = macd_data["macd"]
        df["macd_signal"] = macd_data["signal"]

        # Bollinger Bands
        bb_data = self.calculate_bollinger_bands(df)
        df["bb_middle"] = bb_data["bb_middle"]
        df["bb_upper"] = bb_data["bb_upper"]
        df["bb_lower"] = bb_data["bb_lower"]

        # Volatility
        df["atr"] = self.calculate_atr(df)

        # Returns
        df["returns"] = df["close"].pct_change()
        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

        return df
