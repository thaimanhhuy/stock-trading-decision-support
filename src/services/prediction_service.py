"""Prediction service for real-time stock price predictions.

This service loads trained models and generates predictions for stock symbols.
It handles the complete pipeline: data fetching → preprocessing → prediction → signal generation.
"""

import os
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from src.models.lstm_model import LSTMModel
from src.models.gru_model import GRUModel
from src.preprocessing.data_processor import DataProcessor
from src.data_ingestion.yahoo_finance_fetcher import YahooDataFetcher
from src.trading_engine.signal_generator import SignalGenerator
from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.exceptions import ModelNotFoundError, PredictionError

logger = get_logger(__name__)
settings = get_settings()


class PredictionService:
    """Service for generating stock price predictions and trading signals."""

    def __init__(self):
        """Initialize the prediction service."""
        self.models_cache: Dict[str, Dict[str, any]] = {}
        self.scalers_cache: Dict[str, any] = {}
        self.data_fetcher = YahooDataFetcher()
        self.data_processor = DataProcessor()
        self.signal_generator = SignalGenerator()
        self.sequence_length = 60  # 60 days lookback

        logger.info("PredictionService initialized")

    def _get_model_paths(self, symbol: str) -> Dict[str, str]:
        """Get file paths for models and scaler.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with paths for lstm, gru, and scaler
        """
        models_dir = settings.model_saved_path
        scalers_dir = settings.model_scaler_path

        return {
            "lstm": os.path.join(models_dir, f"{symbol}_lstm.h5"),
            "gru": os.path.join(models_dir, f"{symbol}_gru.h5"),
            "scaler": os.path.join(scalers_dir, f"{symbol}_scaler.pkl"),
        }

    def _check_models_exist(self, symbol: str) -> Tuple[bool, bool, bool]:
        """Check if models and scaler exist for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Tuple of (lstm_exists, gru_exists, scaler_exists)
        """
        paths = self._get_model_paths(symbol)
        return (
            os.path.exists(paths["lstm"]),
            os.path.exists(paths["gru"]),
            os.path.exists(paths["scaler"]),
        )

    def _load_models(self, symbol: str) -> Dict[str, any]:
        """Load trained models for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with loaded models

        Raises:
            ModelNotFoundError: If models don't exist
        """
        # Check cache first
        if symbol in self.models_cache:
            logger.debug(f"Using cached models for {symbol}")
            return self.models_cache[symbol]

        lstm_exists, gru_exists, scaler_exists = self._check_models_exist(symbol)

        if not lstm_exists and not gru_exists:
            raise ModelNotFoundError(
                f"No trained models found for {symbol}. "
                f"Please train models first using: python scripts/train_models.py --symbols {symbol}"
            )

        if not scaler_exists:
            raise ModelNotFoundError(
                f"Scaler not found for {symbol}. "
                f"Please retrain models to generate scaler."
            )

        models = {}
        paths = self._get_model_paths(symbol)

        # Load LSTM model
        if lstm_exists:
            try:
                lstm_model = LSTMModel(symbol=symbol)
                lstm_model.load(paths["lstm"])
                models["lstm"] = lstm_model
                logger.info(f"Loaded LSTM model for {symbol}")
            except Exception as e:
                logger.error(f"Failed to load LSTM model for {symbol}: {e}")

        # Load GRU model
        if gru_exists:
            try:
                gru_model = GRUModel(symbol=symbol)
                gru_model.load(paths["gru"])
                models["gru"] = gru_model
                logger.info(f"Loaded GRU model for {symbol}")
            except Exception as e:
                logger.error(f"Failed to load GRU model for {symbol}: {e}")

        if not models:
            raise ModelNotFoundError(f"Failed to load any models for {symbol}")

        # Cache models
        self.models_cache[symbol] = models
        return models

    def _load_scaler(self, symbol: str):
        """Load scaler for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Loaded scaler

        Raises:
            ModelNotFoundError: If scaler doesn't exist
        """
        # Check cache first
        if symbol in self.scalers_cache:
            logger.debug(f"Using cached scaler for {symbol}")
            return self.scalers_cache[symbol]

        try:
            scaler = self.data_processor.load_scaler(symbol)
            self.scalers_cache[symbol] = scaler
            logger.info(f"Loaded scaler for {symbol}")
            return scaler
        except FileNotFoundError as e:
            raise ModelNotFoundError(f"Scaler not found for {symbol}: {e}")

    def _fetch_latest_data(self, symbol: str, days_needed: int = 100) -> pd.DataFrame:
        """Fetch latest historical data for a symbol.

        Args:
            symbol: Stock symbol
            days_needed: Number of days to fetch (need extra for technical indicators)

        Returns:
            DataFrame with historical data

        Raises:
            PredictionError: If data fetching fails
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_needed)

            logger.info(f"Fetching data for {symbol} from {start_date.date()} to {end_date.date()}")

            data = self.data_fetcher.fetch(
                symbol=symbol,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )

            if data is None or len(data) < self.sequence_length:
                raise PredictionError(
                    f"Insufficient data for {symbol}. "
                    f"Got {len(data) if data is not None else 0} days, need at least {self.sequence_length}"
                )

            logger.info(f"Fetched {len(data)} days of data for {symbol}")
            return data

        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            raise PredictionError(f"Data fetching failed for {symbol}: {str(e)}")

    def _preprocess_data(self, data: pd.DataFrame, scaler) -> np.ndarray:
        """Preprocess data for prediction.

        Args:
            data: Raw historical data
            scaler: Fitted scaler

        Returns:
            Preprocessed sequence ready for prediction

        Raises:
            PredictionError: If preprocessing fails
        """
        try:
            # Add technical indicators
            processed_data = self.data_processor.process(data)

            # Normalize using loaded scaler (fit=False)
            normalized_data = self.data_processor.normalize(processed_data, scaler=scaler, fit=False)

            # Create sequences - get the last sequence for prediction
            X, _ = self.data_processor.create_sequences(
                normalized_data,
                sequence_length=self.sequence_length,
                target_column_idx=3  # close price index
            )

            if len(X) == 0:
                raise PredictionError("No sequences created from data")

            # Return only the last sequence
            return X[-1:], processed_data

        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            raise PredictionError(f"Preprocessing failed: {str(e)}")

    def _denormalize_prediction(self, prediction: float, scaler) -> float:
        """Denormalize prediction to actual price.

        Args:
            prediction: Normalized prediction value
            scaler: Scaler used for normalization

        Returns:
            Denormalized price
        """
        try:
            # Close price is at index 3 in OHLC
            if hasattr(scaler, "data_min_") and hasattr(scaler, "data_max_"):
                close_min = scaler.data_min_[3]
                close_max = scaler.data_max_[3]
                return prediction * (close_max - close_min) + close_min
            else:
                logger.warning("Scaler doesn't have min/max attributes, returning raw prediction")
                return prediction
        except Exception as e:
            logger.error(f"Denormalization failed: {e}")
            return prediction

    def _ensemble_predict(self, models: Dict[str, any], X: np.ndarray, scaler) -> float:
        """Generate ensemble prediction from multiple models.

        Args:
            models: Dictionary of loaded models
            X: Input sequence
            scaler: Scaler for denormalization

        Returns:
            Ensemble prediction (average of all models)
        """
        predictions = []

        for model_name, model in models.items():
            try:
                # Get prediction
                pred = model.predict(X)

                # Denormalize
                denorm_pred = self._denormalize_prediction(pred[0][0], scaler)
                predictions.append(denorm_pred)

                logger.debug(f"{model_name.upper()} prediction: ${denorm_pred:.2f}")

            except Exception as e:
                logger.error(f"Prediction failed for {model_name}: {e}")

        if not predictions:
            raise PredictionError("All model predictions failed")

        # Return average (ensemble)
        ensemble_pred = np.mean(predictions)
        logger.info(f"Ensemble prediction: ${ensemble_pred:.2f} (from {len(predictions)} models)")

        return ensemble_pred

    def get_prediction(self, symbol: str) -> Dict:
        """Get price prediction for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with prediction results

        Raises:
            ModelNotFoundError: If models don't exist
            PredictionError: If prediction fails
        """
        try:
            logger.info(f"Generating prediction for {symbol}")

            # Load models and scaler
            models = self._load_models(symbol)
            scaler = self._load_scaler(symbol)

            # Fetch latest data (need extra days for technical indicators)
            data = self._fetch_latest_data(symbol, days_needed=100)

            # Get current price (last close)
            current_price = float(data['close'].iloc[-1])
            current_date = data.index[-1]

            # Preprocess data
            X, processed_data = self._preprocess_data(data, scaler)

            # Generate ensemble prediction
            predicted_price = self._ensemble_predict(models, X, scaler)

            # Calculate confidence (simple heuristic based on recent volatility)
            recent_returns = processed_data['close'].pct_change().tail(20)
            volatility = recent_returns.std()
            # Lower volatility = higher confidence (inverse relationship)
            confidence = max(0.5, min(0.95, 1 - (volatility * 10)))

            result = {
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "predicted_price": round(predicted_price, 2),
                "confidence": round(confidence, 2),
                "timestamp": datetime.now().isoformat(),
                "current_date": current_date.strftime("%Y-%m-%d"),
                "models_used": list(models.keys()),
                "change_percent": round(((predicted_price - current_price) / current_price) * 100, 2)
            }

            logger.info(
                f"Prediction for {symbol}: ${current_price:.2f} → ${predicted_price:.2f} "
                f"({result['change_percent']:+.2f}%) [confidence: {confidence:.1%}]"
            )

            return result

        except (ModelNotFoundError, PredictionError) as e:
            logger.error(f"Prediction failed for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in prediction for {symbol}: {e}")
            raise PredictionError(f"Unexpected error: {str(e)}")

    def get_signal(self, symbol: str) -> Dict:
        """Get trading signal for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with signal information

        Raises:
            ModelNotFoundError: If models don't exist
            PredictionError: If signal generation fails
        """
        try:
            logger.info(f"Generating signal for {symbol}")

            # Get prediction first
            prediction = self.get_prediction(symbol)

            # Fetch technical data for signal context
            data = self._fetch_latest_data(symbol, days_needed=100)
            processed_data = self.data_processor.process(data)

            # Get latest technical indicators
            latest_data = processed_data.iloc[-1]

            # Generate signal using SignalGenerator
            signal_result = self.signal_generator.generate_signal(
                prediction=prediction["predicted_price"],
                current_price=prediction["current_price"],
                technical_data={
                    "rsi": float(latest_data.get("rsi", 50)),
                    "macd": float(latest_data.get("macd", 0)),
                    "sma_20": float(latest_data.get("sma_20", prediction["current_price"])),
                }
            )

            # Calculate risk levels
            current_price = prediction["current_price"]
            predicted_price = prediction["predicted_price"]

            # Stop loss: 3% below current price for BUY, 3% above for SELL
            if signal_result["signal"] == "buy":
                stop_loss = current_price * 0.97
                take_profit = predicted_price * 1.02  # 2% above prediction
            elif signal_result["signal"] == "sell":
                stop_loss = current_price * 1.03
                take_profit = predicted_price * 0.98  # 2% below prediction
            else:  # hold
                stop_loss = current_price * 0.97
                take_profit = current_price * 1.03

            result = {
                "symbol": symbol,
                "signal": signal_result["signal"],
                "strength": round(signal_result["strength"], 2),
                "target_price": round(predicted_price, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "current_price": round(current_price, 2),
                "predicted_return": round(signal_result["predicted_return"] * 100, 2),
                "confidence": prediction["confidence"],
                "timestamp": datetime.now().isoformat(),
                "technical_context": {
                    "rsi": round(float(latest_data.get("rsi", 50)), 2),
                    "macd": round(float(latest_data.get("macd", 0)), 4),
                }
            }

            logger.info(
                f"Signal for {symbol}: {signal_result['signal'].upper()} "
                f"(strength: {signal_result['strength']:.2f}, return: {result['predicted_return']:+.2f}%)"
            )

            return result

        except (ModelNotFoundError, PredictionError) as e:
            logger.error(f"Signal generation failed for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in signal generation for {symbol}: {e}")
            raise PredictionError(f"Unexpected error: {str(e)}")

    def get_available_symbols(self) -> List[str]:
        """Get list of symbols with trained models.

        Returns:
            List of available symbols
        """
        try:
            models_dir = settings.model_saved_path

            if not os.path.exists(models_dir):
                return []

            # Find all .h5 files
            model_files = [f for f in os.listdir(models_dir) if f.endswith('.h5')]

            # Extract unique symbols
            symbols = set()
            for file in model_files:
                # Format: {symbol}_lstm.h5 or {symbol}_gru.h5
                symbol = file.rsplit('_', 1)[0]
                symbols.add(symbol)

            return sorted(list(symbols))

        except Exception as e:
            logger.error(f"Failed to get available symbols: {e}")
            return []

    def clear_cache(self, symbol: Optional[str] = None):
        """Clear cached models and scalers.

        Args:
            symbol: If provided, clear only this symbol's cache. Otherwise clear all.
        """
        if symbol:
            if symbol in self.models_cache:
                del self.models_cache[symbol]
                logger.info(f"Cleared model cache for {symbol}")
            if symbol in self.scalers_cache:
                del self.scalers_cache[symbol]
                logger.info(f"Cleared scaler cache for {symbol}")
        else:
            self.models_cache.clear()
            self.scalers_cache.clear()
            logger.info("Cleared all model and scaler caches")
