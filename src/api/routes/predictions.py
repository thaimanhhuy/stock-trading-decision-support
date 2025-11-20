"""Prediction and signal routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
import re
from typing import List, Dict
from src.utils.logger import get_logger
from src.services.prediction_service import PredictionService
from src.utils.exceptions import ModelNotFoundError, PredictionError

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["predictions"])

# Initialize prediction service (singleton)
prediction_service = PredictionService()


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

        # Use PredictionService to generate real prediction
        result = prediction_service.get_prediction(symbol)

        return PredictionResponse(
            symbol=result["symbol"],
            current_price=result["current_price"],
            predicted_price=result["predicted_price"],
            confidence=result["confidence"],
            timestamp=result["timestamp"],
        )

    except ValueError as e:
        logger.error(f"Invalid symbol {symbol}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ModelNotFoundError as e:
        logger.error(f"Models not found for {symbol}: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"No trained models found for {symbol}. Please train models first."
        )
    except PredictionError as e:
        logger.error(f"Prediction failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error for {symbol}: {e}")
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

        # Use PredictionService to generate real signal
        result = prediction_service.get_signal(symbol)

        return SignalResponse(
            symbol=result["symbol"],
            signal=result["signal"],
            strength=result["strength"],
            target_price=result["target_price"],
            stop_loss=result["stop_loss"],
            take_profit=result["take_profit"],
        )

    except ValueError as e:
        logger.error(f"Invalid symbol {symbol}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ModelNotFoundError as e:
        logger.error(f"Models not found for {symbol}: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"No trained models found for {symbol}. Please train models first."
        )
    except PredictionError as e:
        logger.error(f"Signal generation failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Signal generation error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Response Models for new endpoints
class AvailableSymbolsResponse(BaseModel):
    """Available symbols response model."""

    symbols: List[str]
    count: int


@router.get("/available-symbols", response_model=AvailableSymbolsResponse)
async def get_available_symbols() -> AvailableSymbolsResponse:
    """Get list of symbols with trained models available.

    Returns:
        List of available symbols

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info("Available symbols requested")
        symbols = prediction_service.get_available_symbols()

        return AvailableSymbolsResponse(
            symbols=symbols,
            count=len(symbols)
        )

    except Exception as e:
        logger.error(f"Failed to get available symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/clear-cache")
async def clear_prediction_cache(symbol: str = None) -> Dict[str, str]:
    """Clear prediction service cache.

    Args:
        symbol: Optional symbol to clear. If not provided, clears all caches.

    Returns:
        Success message

    Raises:
        HTTPException: If cache clear fails
    """
    try:
        prediction_service.clear_cache(symbol)

        if symbol:
            logger.info(f"Cache cleared for {symbol}")
            return {"message": f"Cache cleared for {symbol}"}
        else:
            logger.info("All caches cleared")
            return {"message": "All caches cleared"}

    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
