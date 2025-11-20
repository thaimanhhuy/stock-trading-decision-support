"""Portfolio management API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

from src.services.portfolio_service import PortfolioService, Position, Trade
from src.utils.logger import get_logger
from src.utils.exceptions import PortfolioError

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])

# Initialize portfolio service (singleton)
portfolio_service = PortfolioService()


# Request/Response Models
class BuyRequest(BaseModel):
    """Buy stock request model."""

    symbol: str = Field(..., description="Stock symbol")
    quantity: float = Field(..., gt=0, description="Number of shares to buy")
    price: Optional[float] = Field(None, description="Buy price (uses current if not provided)")


class SellRequest(BaseModel):
    """Sell stock request model."""

    symbol: str = Field(..., description="Stock symbol")
    quantity: float = Field(..., gt=0, description="Number of shares to sell")
    price: Optional[float] = Field(None, description="Sell price (uses current if not provided)")


class PositionResponse(BaseModel):
    """Position response model."""

    symbol: str
    quantity: float
    entry_price: float
    entry_date: str
    current_price: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float


class TradeResponse(BaseModel):
    """Trade response model."""

    trade_id: str
    symbol: str
    action: str
    quantity: float
    price: float
    total_value: float
    timestamp: str
    commission: float
    notes: str


class PortfolioSummaryResponse(BaseModel):
    """Portfolio summary response model."""

    timestamp: str
    cash: float
    equity: float
    total_value: float
    initial_value: float
    total_return: float
    total_return_percent: float
    unrealized_pnl: float
    invested_capital: float
    positions_count: int
    total_trades: int
    buy_trades: int
    sell_trades: int
    created_at: str
    last_updated: str


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response model."""

    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    total_return: float


# Routes
@router.post("/buy", response_model=TradeResponse)
async def buy_stock(request: BuyRequest) -> TradeResponse:
    """Execute a buy order.

    Args:
        request: Buy request with symbol, quantity, and optional price

    Returns:
        Trade confirmation

    Raises:
        HTTPException: If buy fails
    """
    try:
        logger.info(f"Buy request: {request.quantity} shares of {request.symbol}")

        trade = portfolio_service.buy_stock(
            symbol=request.symbol.upper(),
            quantity=request.quantity,
            price=request.price
        )

        return TradeResponse(
            trade_id=trade.trade_id,
            symbol=trade.symbol,
            action=trade.action,
            quantity=trade.quantity,
            price=trade.price,
            total_value=trade.total_value,
            timestamp=trade.timestamp,
            commission=trade.commission,
            notes=trade.notes
        )

    except PortfolioError as e:
        logger.error(f"Buy failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in buy: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/sell", response_model=TradeResponse)
async def sell_stock(request: SellRequest) -> TradeResponse:
    """Execute a sell order.

    Args:
        request: Sell request with symbol, quantity, and optional price

    Returns:
        Trade confirmation

    Raises:
        HTTPException: If sell fails
    """
    try:
        logger.info(f"Sell request: {request.quantity} shares of {request.symbol}")

        trade = portfolio_service.sell_stock(
            symbol=request.symbol.upper(),
            quantity=request.quantity,
            price=request.price
        )

        return TradeResponse(
            trade_id=trade.trade_id,
            symbol=trade.symbol,
            action=trade.action,
            quantity=trade.quantity,
            price=trade.price,
            total_value=trade.total_value,
            timestamp=trade.timestamp,
            commission=trade.commission,
            notes=trade.notes
        )

    except PortfolioError as e:
        logger.error(f"Sell failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in sell: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions() -> List[PositionResponse]:
    """Get all current positions.

    Returns:
        List of positions

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info("Positions requested")

        positions = portfolio_service.get_positions(update_prices=True)

        return [
            PositionResponse(
                symbol=pos.symbol,
                quantity=pos.quantity,
                entry_price=pos.entry_price,
                entry_date=pos.entry_date,
                current_price=pos.current_price,
                current_value=pos.current_value,
                unrealized_pnl=pos.unrealized_pnl,
                unrealized_pnl_percent=pos.unrealized_pnl_percent
            )
            for pos in positions
        ]

    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary() -> PortfolioSummaryResponse:
    """Get portfolio summary with key metrics.

    Returns:
        Portfolio summary

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info("Portfolio summary requested")

        summary = portfolio_service.get_portfolio_summary()

        return PortfolioSummaryResponse(**summary)

    except Exception as e:
        logger.error(f"Failed to get portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/performance", response_model=PerformanceMetricsResponse)
async def get_performance_metrics() -> PerformanceMetricsResponse:
    """Get advanced performance metrics.

    Returns:
        Performance metrics

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info("Performance metrics requested")

        metrics = portfolio_service.get_performance_metrics()

        return PerformanceMetricsResponse(**metrics)

    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/trades", response_model=List[TradeResponse])
async def get_trade_history(
    symbol: Optional[str] = None,
    limit: int = 100
) -> List[TradeResponse]:
    """Get trade history.

    Args:
        symbol: Filter by symbol (optional)
        limit: Maximum number of trades to return

    Returns:
        List of trades

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info(f"Trade history requested (symbol={symbol}, limit={limit})")

        trades = portfolio_service.get_trade_history(
            symbol=symbol.upper() if symbol else None,
            limit=limit
        )

        return [
            TradeResponse(
                trade_id=trade.trade_id,
                symbol=trade.symbol,
                action=trade.action,
                quantity=trade.quantity,
                price=trade.price,
                total_value=trade.total_value,
                timestamp=trade.timestamp,
                commission=trade.commission,
                notes=trade.notes
            )
            for trade in trades
        ]

    except Exception as e:
        logger.error(f"Failed to get trade history: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/reset")
async def reset_portfolio(initial_cash: float = 100000.0) -> Dict[str, str]:
    """Reset portfolio to initial state.

    Args:
        initial_cash: Starting cash amount

    Returns:
        Success message

    Raises:
        HTTPException: If reset fails

    Warning:
        This deletes all positions and trade history!
    """
    try:
        logger.warning(f"Portfolio reset requested with ${initial_cash:,.2f} initial cash")

        portfolio_service.reset_portfolio(initial_cash=initial_cash)

        return {
            "message": f"Portfolio reset successfully with ${initial_cash:,.2f} initial cash",
            "warning": "All positions and trade history have been deleted"
        }

    except Exception as e:
        logger.error(f"Failed to reset portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/export")
async def export_portfolio() -> Dict[str, str]:
    """Export portfolio data to CSV files.

    Returns:
        Success message with file paths

    Raises:
        HTTPException: If export fails
    """
    try:
        logger.info("Portfolio export requested")

        portfolio_service.export_to_csv()

        return {
            "message": "Portfolio exported successfully",
            "output_dir": "data",
            "files": ["positions_YYYYMMDD.csv", "trades_YYYYMMDD.csv"]
        }

    except Exception as e:
        logger.error(f"Failed to export portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
