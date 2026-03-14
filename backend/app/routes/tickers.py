from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct
from app.database import get_db
from app.models import Price
from app.schemas import TickerResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/tickers", response_model=TickerResponse)
async def get_tickers(db: AsyncSession = Depends(get_db)):
    """Get distinct tickers from prices table"""
    try:
        stmt = select(distinct(Price.ticker)).order_by(Price.ticker)
        result = await db.execute(stmt)
        tickers = [row[0] for row in result.fetchall()]
        
        return TickerResponse(tickers=tickers)
    except Exception as e:
        logger.error(f"Error fetching tickers: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tickers",
        )
