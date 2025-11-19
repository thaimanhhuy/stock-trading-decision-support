"""Model retraining service."""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data_ingestion.data_fetcher import YahooDataFetcher
from src.data_ingestion.data_storage import DataStorage
from src.preprocessing.data_processor import DataProcessor
from src.models.model_trainer import ModelTrainer
from src.utils.logger import LoggerMixin


class RetrainingService(LoggerMixin):
    """Service for managing model retraining."""

    def __init__(self):
        """Initialize retraining service."""
        self.data_fetcher = YahooDataFetcher()
        self.data_storage = DataStorage()
        self.data_processor = DataProcessor()
        self.training_history_file = Path("models/training_history.json")
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Ensure training history file exists."""
        if not self.training_history_file.exists():
            self.training_history_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_history([])

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load training history."""
        try:
            with open(self.training_history_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load training history: {e}")
            return []

    def _save_history(self, history: List[Dict[str, Any]]):
        """Save training history."""
        try:
            with open(self.training_history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save training history: {e}")

    def _add_training_record(
        self,
        symbol: str,
        trigger: str,
        status: str,
        metrics: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        """Add a training record to history."""
        history = self._load_history()
        record = {
            "symbol": symbol,
            "trigger": trigger,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics or {},
            "error": error,
        }
        history.append(record)
        self._save_history(history)

    def get_last_training_date(self, symbol: str) -> Optional[datetime]:
        """Get the last successful training date for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Last training date or None if never trained
        """
        history = self._load_history()
        successful_trainings = [
            record
            for record in history
            if record["symbol"] == symbol and record["status"] == "success"
        ]
        if successful_trainings:
            last_training = sorted(
                successful_trainings, key=lambda x: x["timestamp"], reverse=True
            )[0]
            return datetime.fromisoformat(last_training["timestamp"])
        return None

    def should_retrain_scheduled(
        self, symbol: str, interval_months: int = 3
    ) -> bool:
        """Check if model should be retrained based on schedule.

        Args:
            symbol: Stock symbol
            interval_months: Retraining interval in months

        Returns:
            True if retraining is needed
        """
        last_training = self.get_last_training_date(symbol)
        if last_training is None:
            self.logger.info(f"{symbol}: No previous training found, retraining needed")
            return True

        months_since_training = (
            datetime.now() - last_training
        ).days / 30.44  # Average days per month
        should_retrain = months_since_training >= interval_months

        self.logger.info(
            f"{symbol}: Last training {months_since_training:.1f} months ago, "
            f"threshold {interval_months} months, should_retrain={should_retrain}"
        )
        return should_retrain

    def retrain_model(
        self,
        symbol: str,
        trigger: str = "manual",
        models: str = "all",
        fetch_new_data: bool = True,
    ) -> Dict[str, Any]:
        """Retrain model for a symbol.

        Args:
            symbol: Stock symbol
            trigger: Training trigger (manual, scheduled, market_event)
            models: Models to train (comma-separated or 'all')
            fetch_new_data: Whether to fetch new data before training

        Returns:
            Training result dictionary
        """
        self.logger.info(
            f"Starting retraining for {symbol} (trigger: {trigger}, "
            f"fetch_new_data: {fetch_new_data})"
        )

        try:
            # Fetch new data if requested
            if fetch_new_data:
                self.logger.info(f"Fetching latest data for {symbol}")
                data = self.data_fetcher.fetch_data(symbol, period="2y")
                self.data_storage.save_raw(data, symbol)
            else:
                # Load existing data
                self.logger.info(f"Loading existing data for {symbol}")
                data = self.data_storage.load_raw(symbol)

            # Process data
            self.logger.info(f"Processing data for {symbol}")
            data = self.data_processor.process(data, symbol)

            # Prepare for training
            X_train = data[["close"]].values
            y_train = data["close"].values

            # Train models
            self.logger.info(f"Training models for {symbol}")
            trainer = ModelTrainer(symbol)

            if models == "all":
                trained_models = trainer.train_all(X_train, y_train)
            else:
                model_names = [m.strip() for m in models.split(",")]
                trained_models = {}
                for name in model_names:
                    if name == "lstm":
                        trained_models[name] = trainer.train_lstm(X_train, y_train)
                    elif name == "gru":
                        trained_models[name] = trainer.train_gru(X_train, y_train)

            # Record success
            metrics = {
                "models_trained": list(trained_models.keys()),
                "data_points": len(data),
                "fetch_new_data": fetch_new_data,
            }
            self._add_training_record(symbol, trigger, "success", metrics)

            self.logger.info(
                f"Retraining complete for {symbol}. Trained {len(trained_models)} models"
            )

            return {
                "status": "success",
                "symbol": symbol,
                "trigger": trigger,
                "models_trained": list(trained_models.keys()),
                "data_points": len(data),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Retraining failed for {symbol}: {error_msg}")
            self._add_training_record(symbol, trigger, "failed", error=error_msg)

            return {
                "status": "failed",
                "symbol": symbol,
                "trigger": trigger,
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
            }

    def retrain_multiple(
        self, symbols: List[str], trigger: str = "manual", **kwargs
    ) -> List[Dict[str, Any]]:
        """Retrain models for multiple symbols.

        Args:
            symbols: List of stock symbols
            trigger: Training trigger
            **kwargs: Additional arguments for retrain_model

        Returns:
            List of training results
        """
        self.logger.info(
            f"Starting batch retraining for {len(symbols)} symbols (trigger: {trigger})"
        )
        results = []

        for symbol in symbols:
            result = self.retrain_model(symbol, trigger=trigger, **kwargs)
            results.append(result)

        successful = sum(1 for r in results if r["status"] == "success")
        self.logger.info(
            f"Batch retraining complete: {successful}/{len(symbols)} successful"
        )

        return results

    def get_training_history(
        self, symbol: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get training history.

        Args:
            symbol: Optional symbol to filter by
            limit: Maximum number of records to return

        Returns:
            List of training records
        """
        history = self._load_history()

        if symbol:
            history = [r for r in history if r["symbol"] == symbol]

        # Sort by timestamp descending
        history = sorted(history, key=lambda x: x["timestamp"], reverse=True)

        return history[:limit]

    def get_training_stats(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get training statistics.

        Args:
            symbol: Optional symbol to filter by

        Returns:
            Training statistics
        """
        history = self.get_training_history(symbol)

        if not history:
            return {
                "total_trainings": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
            }

        total = len(history)
        successful = sum(1 for r in history if r["status"] == "success")
        failed = total - successful

        stats = {
            "total_trainings": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0.0,
        }

        if history:
            stats["last_training"] = history[0]["timestamp"]
            stats["last_status"] = history[0]["status"]

        # Trigger breakdown
        trigger_counts = {}
        for record in history:
            trigger = record["trigger"]
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        stats["by_trigger"] = trigger_counts

        return stats
