"""Prediction and signal routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
import re
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["predictions"])


def validate_symbol(symbol: str) -> str:
    """Validate stock symbol format.

    Args:
        symbol: Stock symbol to validate

    Returns:
        Validated symbol in uppercase

    Raises:
        ValueError: If symbol format is invalid
    """
    symbol = symbol.upper().strip()

    # Allow US symbols (letters only) and Vietnamese symbols (with .VN suffix)
    if not re.match(r"^[A-Z]{1,5}(\.VN)?$", symbol):
        raise ValueError(
            f"Invalid symbol format: {symbol}. "
            "Must be 1-5 letters (e.g., AAPL) or Vietnamese format (e.g., VCB.VN)"
        )

    return symbol


# Response Models
class PredictionResponse(BaseModel):
    """Prediction response model."""

    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    timestamp: str


class SignalResponse(BaseModel):
    """Signal response model."""

    symbol: str
    signal: str
    strength: float
    target_price: float
    stop_loss: float
    take_profit: float


# Routes
@router.get("/predictions/{symbol}", response_model=PredictionResponse)
async def get_prediction(symbol: str) -> PredictionResponse:
    """Get price prediction for a symbol.

    Args:
        symbol: Stock symbol

    Returns:
        Prediction response

    Raises:
        HTTPException: If symbol is invalid or prediction fails
    """
    try:
        # Validate symbol format
        symbol = validate_symbol(symbol)
        logger.info(f"Prediction requested for {symbol}")

        # TODO: Implement actual prediction logic
        # This is a placeholder - integrate with trained models
        logger.warning(
            f"Using placeholder implementation for {symbol} - integrate with trained models"
        )

        return PredictionResponse(
            symbol=symbol,
            current_price=150.0,
            predicted_price=155.0,
            confidence=0.75,
            timestamp="2024-01-01T00:00:00",
        )
    except ValueError as e:
        logger.error(f"Invalid symbol {symbol}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/signals/{symbol}", response_model=SignalResponse)
async def get_signal(symbol: str) -> SignalResponse:
    """Get trading signal for a symbol.

    Args:
        symbol: Stock symbol

    Returns:
        Signal response

    Raises:
        HTTPException: If symbol is invalid or signal generation fails
    """
    try:
        # Validate symbol format
        symbol = validate_symbol(symbol)
        logger.info(f"Signal requested for {symbol}")

        # TODO: Implement actual signal generation logic
        # This is a placeholder - integrate with SignalGenerator
        logger.warning(
            f"Using placeholder implementation for {symbol} - integrate with SignalGenerator"
        )

        return SignalResponse(
            symbol=symbol,
            signal="buy",
            strength=0.8,
            target_price=155.0,
            stop_loss=145.0,
            take_profit=160.0,
        )
    except ValueError as e:
        logger.error(f"Invalid symbol {symbol}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Signal generation failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
