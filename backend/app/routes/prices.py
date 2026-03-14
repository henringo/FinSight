from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models import Price
from app.schemas import PricesListResponse, PriceResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/prices", response_model=PricesListResponse)
async def get_prices(
    ticker: str = Query(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    from_date: Optional[datetime] = Query(None, alias="from", description="Start date (ISO format)"),
    to_date: Optional[datetime] = Query(None, alias="to", description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
):
    """Get price data for a ticker with optional date range filtering"""
    try:
        # Build query
        conditions = [Price.ticker == ticker.upper()]
        
        if from_date:
            conditions.append(Price.ts >= from_date)
        if to_date:
            conditions.append(Price.ts <= to_date)
        
        # Count total
        count_stmt = select(func.count()).select_from(Price).where(and_(*conditions))
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # Get prices
        stmt = (
            select(Price)
            .where(and_(*conditions))
            .order_by(Price.ts.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await db.execute(stmt)
        prices = result.scalars().all()
        
        return PricesListResponse(
            prices=[PriceResponse.model_validate(p) for p in prices],
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Error fetching prices: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch prices",
        )
