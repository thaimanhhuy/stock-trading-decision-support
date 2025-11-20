"""Custom exceptions for the trading system."""


class TradingSystemError(Exception):
    """Base exception for trading system errors."""

    pass


class DataValidationError(TradingSystemError):
    """Raised when data validation fails."""

    pass


class DataFetchError(TradingSystemError):
    """Raised when data fetching fails."""

    pass


class ModelNotFoundError(TradingSystemError):
    """Raised when a model file is not found."""

    pass


class ModelTrainingError(TradingSystemError):
    """Raised when model training fails."""

    pass


class PredictionError(TradingSystemError):
    """Raised when prediction generation fails."""

    pass


class RiskLimitExceeded(TradingSystemError):
    """Raised when a risk limit is exceeded."""

    pass


class ConfigurationError(TradingSystemError):
    """Raised when configuration is invalid."""

    pass


class InsufficientDataError(TradingSystemError):
    """Raised when insufficient data is available."""

    pass


class SignalGenerationError(TradingSystemError):
    """Raised when signal generation fails."""

    pass


class BacktestError(TradingSystemError):
    """Raised when backtesting encounters an error."""

    pass


class PortfolioError(TradingSystemError):
    """Raised when portfolio operations fail."""

    pass
