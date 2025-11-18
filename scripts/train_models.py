#!/usr/bin/env python3
"""Train prediction models."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion.data_storage import DataStorage
from src.preprocessing.data_processor import DataProcessor
from src.models.model_trainer import ModelTrainer
from src.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Train prediction models")
    parser.add_argument("--symbol", required=True, help="Stock symbol")
    parser.add_argument("--models", default="all", help="Models to train (comma-separated or 'all')")

    args = parser.parse_args()

    try:
        # Load data
        logger.info(f"Loading data for {args.symbol}")
        storage = DataStorage()
        data = storage.load_raw(args.symbol)

        # Process data
        logger.info("Processing data")
        processor = DataProcessor()
        data = processor.process(data, args.symbol)

        # Prepare for training (simplified)
        X_train = data[["close"]].values
        y_train = data["close"].values

        # Train models
        logger.info("Training models")
        trainer = ModelTrainer(args.symbol)

        if args.models == "all":
            models = trainer.train_all(X_train, y_train)
        else:
            model_names = [m.strip() for m in args.models.split(",")]
            models = {}
            for name in model_names:
                if name == "arima":
                    models[name] = trainer.train_arima(X_train, y_train)
                elif name == "lstm":
                    models[name] = trainer.train_lstm(X_train, y_train)
                elif name == "gru":
                    models[name] = trainer.train_gru(X_train, y_train)

        logger.info(f"Training complete. Trained {len(models)} models")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
